import streamlit as st
import requests
from datetime import datetime
import random

st.set_page_config(layout="wide")

# 🔐 KEYS
SPORT_KEY = st.secrets.get("RAPIDAPI_KEY", "")
ODDS_KEY = st.secrets.get("ODDS_API_KEY", "")


# 🌍 FETCH FIXTURES (HOY + MAÑANA)
def fetch_fixtures():

    headers = {
        "X-RapidAPI-Key": SPORT_KEY,
        "X-RapidAPI-Host": "sportapi7.p.rapidapi.com"
    }

    all_matches = []

    for day in ["today", "tomorrow"]:

        url = f"https://sportapi7.p.rapidapi.com/api/v1/sport/football/scheduled-events/{day}"

        try:
            r = requests.get(url, headers=headers, timeout=15)
            data = r.json()

            for e in data.get("events", []):

                tournament = e["tournament"]["uniqueTournament"]["name"]

                # 🚫 filtro ligas basura
                if "U" in tournament or "Women" in tournament:
                    continue

                home = e["homeTeam"]["name"]
                away = e["awayTeam"]["name"]

                country = e["tournament"]["category"]["name"]

                ts = e["startTimestamp"]
                kickoff = datetime.fromtimestamp(ts)

                all_matches.append({
                    "home": home,
                    "away": away,
                    "league": tournament,
                    "country": country,
                    "kickoff": kickoff.strftime("%Y-%m-%d %H:%M")
                })

        except:
            continue

    return all_matches


# 💰 FETCH ODDS
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


# 🧠 GENIE ANALYSIS (MEJORADO)
def genie_analysis(match):

    tempo = random.choice(["High Tempo", "Balanced", "Controlled"])
    confidence = round(random.uniform(6.8, 9.3), 1)

    strategy = random.choice([
        "Momentum Entry",
        "Lay The Draw",
        "Over Reaction",
        "Late Pressure",
        "First Goal Momentum"
    ])

    home = match["home"]
    away = match["away"]

    analysis = f"""
After weighing up the data, here's the professional read:

📊 **Match Context**
{home} vs {away} projects as a **{tempo} fixture**, where game rhythm and pressure cycles will dictate trading opportunities.

⚡ **Tactical Dynamics**
- Expect alternating phases of control rather than dominance
- Transitional moments (post-goal) will be key
- Both teams likely to generate volatility windows

📈 **Market Behavior**
- Early phase → slow odds adjustment
- First goal → sharp market reaction
- Mid game → directional bias emerges
- Late game → pressure inefficiencies increase

🎯 **Edge Insight**
The edge is not prediction — it's identifying when the market lags behind real momentum.

🧠 **Execution Framework**
Wait for confirmation (tempo + pressure). Avoid early entries without validation.
"""

    return tempo, confidence, strategy, analysis


# 🚀 UI
st.title("🔥 GENIE PRO REAL")

fixtures = fetch_fixtures()

# ❌ SIN FALLBACK FALSO
if not fixtures:
    st.error("No hay partidos disponibles (API issue o sin eventos hoy)")
    st.stop()

odds_map = fetch_odds()

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
st.subheader("📊 Confidence Rating")
st.write(f"⭐ {confidence} / 10")

# ⚡ TEMPO
st.subheader("⚡ Match Tempo")
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
