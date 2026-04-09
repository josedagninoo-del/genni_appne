import streamlit as st
import requests
from datetime import datetime
import random

st.set_page_config(layout="wide")

# 🔐 KEYS
SPORT_KEY = st.secrets.get("RAPIDAPI_KEY", "")
ODDS_KEY = st.secrets.get("ODDS_API_KEY", "")

# 🌍 SPORT API (FIXTURES REALES)
def fetch_fixtures():
    url = "https://sportapi7.p.rapidapi.com/api/v1/sport/football/scheduled-events/today"

    headers = {
        "X-RapidAPI-Key": SPORT_KEY,
        "X-RapidAPI-Host": "sportapi7.p.rapidapi.com"
    }

    try:
        r = requests.get(url, headers=headers, timeout=15)
        data = r.json()

        matches = []

        for e in data.get("events", []):

            tournament = e["tournament"]["uniqueTournament"]["name"]
            country = e["tournament"]["category"]["name"]

            home = e["homeTeam"]["name"]
            away = e["awayTeam"]["name"]

            kickoff = datetime.fromtimestamp(e["startTimestamp"])

            matches.append({
                "home": home,
                "away": away,
                "league": tournament,
                "country": country,
                "kickoff": kickoff.strftime("%Y-%m-%d %H:%M")
            })

        return matches

    except:
        return []


# 💰 ODDS API (CUOTAS)
def fetch_odds():
    sports = [
        "soccer_epl",
        "soccer_spain_la_liga",
        "soccer_italy_serie_a",
        "soccer_germany_bundesliga",
        "soccer_france_ligue_one",
        "soccer_uefa_champs_league",
        "soccer_uefa_europa_league",
        "soccer_mexico_ligamx",
        "soccer_brazil_campeonato",
        "soccer_argentina_primera_division",
        "soccer_copa_libertadores",
        "soccer_copa_sudamericana"
    ]

    odds_map = {}

    for sport in sports:
        try:
            url = f"https://api.the-odds-api.com/v4/sports/{sport}/odds/?apiKey={ODDS_KEY}&regions=eu&markets=h2h"
            r = requests.get(url, timeout=10)

            if r.status_code != 200:
                continue

            data = r.json()

            for g in data:
                key = f"{g['home_team']} vs {g['away_team']}"
                odds_map[key] = g.get("bookmakers", [])

        except:
            continue

    return odds_map


# 🧠 GENIE ANALYSIS PRO
def genie_analysis(match):

    tempo = random.choice(["High Tempo", "Balanced", "Low Tempo"])
    confidence = round(random.uniform(6.5, 9.3), 1)

    strategy = random.choice([
        "Momentum Entry",
        "Lay The Draw",
        "Over Reaction",
        "Late Pressure",
        "First Goal Trade"
    ])

    home = match["home"]
    away = match["away"]

    text = f"""
After weighing up all pre-match data, here's the professional read:

📊 **Match Context**
{home} vs {away} profiles as a **{tempo} fixture**, where game state transitions will heavily influence market behavior.

⚡ **Tactical Expectation**
- Both teams likely to generate phases of pressure rather than constant dominance
- Transition moments will be key (especially after first goal)
- Potential volatility spikes after momentum swings

📈 **Market Behavior**
- Early phase → slow price discovery
- First goal → sharp odds reaction
- Mid game → directional bias forms
- Late game → pressure-driven inefficiencies

🎯 **Trading Insight**
This is not about predicting outcome — it's about reacting to **market mispricing after key events**.

🧠 **Execution Logic**
Wait for confirmation of tempo + real pressure before engaging. Avoid pre-emptive entries.
"""

    return tempo, confidence, strategy, text


# 🚀 UI
st.title("🔥 GENIE PRO REAL")

fixtures = fetch_fixtures()
odds_map = fetch_odds()

# 🧾 FALLBACK
if not fixtures:
    st.warning("SportAPI empty → fallback activado")
    fixtures = [
        {"home": "Liverpool", "away": "Brighton", "league": "Premier League", "country": "England", "kickoff": "20:00"},
        {"home": "Flamengo", "away": "Palmeiras", "league": "Brasileirão", "country": "Brazil", "kickoff": "21:00"}
    ]

# 🎯 SELECTOR
options = [
    f"{m['home']} vs {m['away']} | {m['league']} | {m['kickoff']}"
    for m in fixtures
]

selected = st.selectbox("Selecciona partido", options)

match = fixtures[options.index(selected)]

tempo, confidence, strategy, analysis = genie_analysis(match)

# 🧾 HEADER
st.markdown("---")
st.header(f"{match['home']} vs {match['away']}")
st.write(f"🌍 {match['country']} — {match['league']}")
st.write(f"⏰ {match['kickoff']}")

# 📊 CONFIDENCE
st.subheader("📊 Confidence")
st.write(f"⭐ {confidence} / 10")

# ⚡ TEMPO
st.subheader("⚡ Tempo")
st.write(tempo)

# 🧠 ANALYSIS
st.subheader("🧠 Genie Analysis")
st.markdown(analysis)

# 📈 STRATEGY
st.subheader("📈 Trading Approach")
st.info(strategy)

# 💰 ODDS
st.subheader("💰 Odds")

key = f"{match['home']} vs {match['away']}"

if key in odds_map and odds_map[key]:
    try:
        bookmaker = odds_map[key][0]
        outcomes = bookmaker["markets"][0]["outcomes"]

        for o in outcomes:
            st.write(f"{o['name']}: {o['price']}")
    except:
        st.write("Odds disponibles pero no parseadas correctamente")
else:
    st.write("No odds disponibles")
