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
# FETCH MATCHES
# -----------------------
def fetch_matches():
    today = date.today().strftime("%Y-%m-%d")

    try:
        r = requests.get(
            f"{BASE}/api/v1/sport/football/scheduled-events/{today}",
            headers=HEADERS,
            timeout=15
        )
        data = r.json()
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
# FETCH ODDS
# -----------------------
def fetch_odds():
    url = f"https://api.the-odds-api.com/v4/sports/soccer/odds/?apiKey={ODDS_KEY}&regions=eu&markets=h2h"

    odds_map = {}

    try:
        r = requests.get(url, timeout=10)

        if r.status_code != 200:
            return {}

        data = r.json()

        for g in data:
            key = f"{g['home_team']} vs {g['away_team']}"

            try:
                outcomes = g["bookmakers"][0]["markets"][0]["outcomes"]

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
    leagues = [
        "Premier League","LaLiga","Serie A",
        "Bundesliga","Ligue 1",
        "UEFA Europa League","UEFA Champions League",
        "Copa Libertadores","Copa Sudamericana"
    ]
    return [m for m in matches if m["league"] in leagues]

# -----------------------
# GENIE ENGINE (NARRATIVO)
# -----------------------
def genie_analysis(match, odds):

    home = match["home"]
    away = match["away"]

    attacking = ["Liverpool","Atalanta","Leverkusen","Brighton"]
    defensive = ["Getafe","Torino"]

    # perfil
    if any(t in home for t in attacking) or any(t in away for t in attacking):
        tempo = "High tempo"
        strategy = "Lay Under / Over goals"
        confidence = 8
    elif any(t in home for t in defensive) and any(t in away for t in defensive):
        tempo = "Low block"
        strategy = "Wait / Possible draw"
        confidence = 4
    else:
        tempo = "Balanced"
        strategy = "Momentum trading"
        confidence = 6

    if odds:
        confidence += 1

    # narrativa tipo Genie
    text = f"""
    After weighing up the data, here's how I'd play it:

    🔹 Strategy: Momentum Method  
    🔹 Market: Match Odds / Goals  

    📊 Rationale:  
    This fixture between {home} and {away} projects as a **{tempo} match**.  
    The tactical setup suggests that the tempo will define the opportunity window.

    📈 Market Insight:  
    {'The presence of live odds indicates a reactive market.' if odds else 'Limited odds data – caution advised.'}

    ⏱ Entry Plan:  
    Wait first 10–15 minutes to confirm tempo.

    💰 Exit Plan:  
    Trade the first major market movement (goal / pressure shift).

    ⚠️ Risk Level:  
    {'Medium' if confidence >=7 else 'Controlled'}

    """

    return {
        "confidence": confidence,
        "strategy": strategy,
        "tempo": tempo,
        "text": text,
        "tradeable": confidence >= 7
    }

# -----------------------
# UI
# -----------------------
st.set_page_config(layout="wide")
st.title("🔥 GENIE PRO REAL")

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

    analysis = genie_analysis(m, odds)

    data.append({
        "match": key,
        "analysis": analysis,
        "odds": odds,
        "raw": m
    })

# -----------------------
# FILTRO PRO
# -----------------------
tradeable = [d for d in data if d["analysis"]["tradeable"]]

if not tradeable:
    st.warning("No strong edges → fallback to all matches")
    tradeable = data

# -----------------------
# RANKING
# -----------------------
ranked = sorted(tradeable, key=lambda x: x["analysis"]["confidence"], reverse=True)

st.markdown("## 🏆 TOP MATCHES")
for i, r in enumerate(ranked[:5]):
    st.write(f"{i+1}. {r['match']} → {r['analysis']['confidence']}")

# -----------------------
# SELECTOR SEGURO
# -----------------------
options = [d["match"] for d in ranked]

if not options:
    st.error("No matches available")
    st.stop()

selected = st.selectbox("Selecciona partido", options)

sel = next((d for d in ranked if d["match"] == selected), None)

if not sel:
    st.stop()

# -----------------------
# OUTPUT GENIE STYLE
# -----------------------
st.subheader(selected)

st.write(f"League: {sel['raw']['league']} ({sel['raw']['country']})")

st.markdown("### 💰 Odds")
st.write(sel["odds"] if sel["odds"] else "No odds available")

st.markdown("### 🧠 Genie Insight")
st.write(sel["analysis"]["text"])

st.markdown("### 📈 Confidence")
st.write(sel["analysis"]["confidence"])

st.markdown("### ⚠️ Tradeable")
st.write("YES" if sel["analysis"]["tradeable"] else "NO")
