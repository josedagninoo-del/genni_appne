import streamlit as st
import requests
from datetime import date

# -----------------------
# CONFIG
# -----------------------
SPORT_KEY = st.secrets.get("API_KEY")
ODDS_KEY = st.secrets.get("ODDS_KEY")

BASE = "https://sportapi7.p.rapidapi.com"

HEADERS = {
    "X-RapidAPI-Key": SPORT_KEY,
    "X-RapidAPI-Host": "sportapi7.p.rapidapi.com",
}

# -----------------------
# FETCH MATCHES (SPORTAPI)
# -----------------------
def fetch_matches():
    today = date.today().strftime("%Y-%m-%d")

    try:
        resp = requests.get(
            f"{BASE}/api/v1/sport/football/scheduled-events/{today}",
            headers=HEADERS,
            timeout=15
        )

        data = resp.json()
        events = data.get("events", [])

        matches = []

        for e in events:
            try:
                matches.append({
                    "id": e["id"],
                    "home": e["homeTeam"]["name"],
                    "away": e["awayTeam"]["name"],
                    "league": e["tournament"]["name"],
                    "country": e["tournament"]["category"]["name"]
                })
            except:
                continue

        return matches

    except:
        return []

# -----------------------
# FETCH ODDS (ODDS API)
# -----------------------
def fetch_odds():
    url = f"https://api.the-odds-api.com/v4/sports/soccer/odds/?apiKey={ODDS_KEY}&regions=eu&markets=h2h"

    odds_map = {}

    try:
        res = requests.get(url, timeout=10)

        if res.status_code != 200:
            return {}

        data = res.json()

        for game in data:
            key = f"{game['home_team']} vs {game['away_team']}"

            try:
                outcomes = game["bookmakers"][0]["markets"][0]["outcomes"]

                odds_map[key] = {
                    "home": outcomes[0]["price"],
                    "away": outcomes[1]["price"]
                }
            except:
                continue

        return odds_map

    except:
        return {}

# -----------------------
# FILTRO LIGAS
# -----------------------
def filter_matches(matches):
    good = [
        "Premier League",
        "LaLiga",
        "Serie A",
        "Bundesliga",
        "Ligue 1",
        "UEFA Europa League",
        "UEFA Champions League",
        "Copa Libertadores",
        "Copa Sudamericana"
    ]

    return [m for m in matches if m["league"] in good]

# -----------------------
# GENIE ENGINE PRO (REAL)
# -----------------------
def analyze(match, odds):

    home = match["home"]
    away = match["away"]

    attacking = ["Liverpool", "Atalanta", "Leverkusen", "Brighton"]
    defensive = ["Getafe", "Torino"]

    # tipo de partido
    if any(t in home for t in attacking) or any(t in away for t in attacking):
        tempo = "HIGH"
        score = 8
    elif any(t in home for t in defensive) and any(t in away for t in defensive):
        tempo = "LOW"
        score = 4
    else:
        tempo = "MID"
        score = 6

    # señal de mercado
    if odds:
        score += 1

    # EDGE FILTER
    tradeable = score >= 7

    return {
        "tempo": tempo,
        "confidence": score,
        "tradeable": tradeable,
        "strategy": {
            "HIGH": "Over / Lay Under",
            "MID": "Momentum Match Odds",
            "LOW": "Wait / No Trade"
        }[tempo]
    }

# -----------------------
# UI
# -----------------------
st.set_page_config(layout="wide")
st.title("🔥 GENIE PRO REAL (FULL SYSTEM)")

matches = fetch_matches()

if not matches:
    st.error("No matches from API")
    st.stop()

matches = filter_matches(matches)

odds_data = fetch_odds()

# -----------------------
# BUILD DATA
# -----------------------
data = []

for m in matches:
    key = f"{m['home']} vs {m['away']}"
    odds = odds_data.get(key)

    analysis = analyze(m, odds)

    data.append({
        "match": key,
        "analysis": analysis,
        "odds": odds,
        "raw": m
    })

# -----------------------
# FILTRO PRO (CLAVE)
# -----------------------
tradeable = [d for d in data if d["analysis"]["tradeable"]]

if not tradeable:
    st.warning("No strong edges today → showing all matches")
    tradeable = data

# -----------------------
# RANKING
# -----------------------
ranked = sorted(tradeable, key=lambda x: x["analysis"]["confidence"], reverse=True)

st.markdown("## 🏆 TOP TRADEABLE MATCHES")
for i, r in enumerate(ranked[:5]):
    st.write(f"{i+1}. {r['match']} → {r['analysis']['confidence']}")

# -----------------------
# SELECTOR
# -----------------------
options = [d["match"] for d in ranked]

selected = st.selectbox("Selecciona partido", options)

sel = next((d for d in ranked if d["match"] == selected), None)

if not sel:
    st.stop()

# -----------------------
# OUTPUT
# -----------------------
st.subheader(selected)

st.write(f"League: {sel['raw']['league']} ({sel['raw']['country']})")

st.markdown("### 💰 Odds")
st.write(sel["odds"] if sel["odds"] else "No odds")

st.markdown("### 🔮 Match Type")
st.write(sel["analysis"]["tempo"])

st.markdown("### 🎯 Strategy")
st.write(sel["analysis"]["strategy"])

st.markdown("### 📈 Confidence")
st.write(sel["analysis"]["confidence"])

st.markdown("### ⚠️ Tradeable")
st.write("YES" if sel["analysis"]["tradeable"] else "NO")
