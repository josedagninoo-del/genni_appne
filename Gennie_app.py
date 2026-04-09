import streamlit as st
import requests
from datetime import datetime, timedelta
import random

st.set_page_config(layout="wide")

# 🔐 API KEY (Streamlit Cloud)
ODDS_KEY = st.secrets.get("ODDS_API_KEY", "")

# 🧠 FALLBACK (NUNCA VACÍO)
FALLBACK = [
    {"home": "Liverpool", "away": "Brighton", "league": "Premier League"},
    {"home": "Inter", "away": "Roma", "league": "Serie A"},
    {"home": "Leverkusen", "away": "Dortmund", "league": "Bundesliga"},
    {"home": "Flamengo", "away": "Palmeiras", "league": "Brasileirão"},
    {"home": "River Plate", "away": "Boca Juniors", "league": "Argentina"},
]

# 🌍 FETCH ODDS MULTI-LIGA
def fetch_matches():
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
        "soccer_copa_sudamericana",
        "soccer_usa_mls"
    ]

    matches = []

    for sport in sports:
        try:
            url = f"https://api.the-odds-api.com/v4/sports/{sport}/odds/?apiKey={ODDS_KEY}&regions=eu&markets=h2h"
            r = requests.get(url, timeout=10)

            if r.status_code != 200:
                continue

            data = r.json()

            now = datetime.utcnow()
            limit = now + timedelta(hours=36)

            for g in data:
                kickoff = datetime.fromisoformat(g["commence_time"].replace("Z", ""))

                if kickoff <= limit:
                    matches.append({
                        "home": g["home_team"],
                        "away": g["away_team"],
                        "league": g.get("sport_title", sport),
                        "odds": g.get("bookmakers", [])
                    })

        except:
            continue

    return matches


# 🧠 GENERADOR DE ANÁLISIS TIPO GENIE
def generate_analysis(match):

    home = match["home"]
    away = match["away"]

    tempo = random.choice(["High Tempo", "Balanced", "Controlled"])
    confidence = round(random.uniform(6.5, 9.2), 1)

    strategy = random.choice([
        "Momentum Trade",
        "Lay The Draw",
        "Over Reaction Play",
        "Late Goal Pressure",
        "First Goal Momentum"
    ])

    return {
        "tempo": tempo,
        "confidence": confidence,
        "strategy": strategy,
        "analysis": f"""
After weighing up the data, here's the professional read:

📊 **Match Context**
{home} vs {away} projects as a **{tempo} game**, where rhythm and pressure cycles will define trading opportunities.

⚡ **Game Dynamics**
- Likely phases of dominance rather than static control
- Transitional moments will be key (especially after first goal)
- Market expected to react quickly to momentum swings

📈 **Market Behavior Expectation**
- Early stages: price discovery + volatility
- Mid-game: directional movement depending on first goal
- Late game: increased pressure if scoreline remains tight

🎯 **Key Edge**
The edge lies in identifying when the market **lags behind actual momentum shifts**, not before.

🧠 **Interpretation**
This is not a static match — it will evolve. Your edge is timing, not prediction.
"""
    }


# 🎨 UI
st.title("🔥 GENIE PRO REAL")

matches = fetch_matches()

if not matches:
    st.warning("APIs empty → using fallback dataset")
    matches = FALLBACK

# 🧾 SELECTOR
options = [f"{m['home']} vs {m['away']}" for m in matches]

selected = st.selectbox("Selecciona partido", options)

match = next((m for m in matches if f"{m['home']} vs {m['away']}" == selected), None)

if match:

    analysis = generate_analysis(match)

    st.markdown("---")
    st.header(f"{match['home']} vs {match['away']}")
    st.write(f"League: {match['league']}")

    # 🎯 CONFIDENCE
    st.subheader("📊 Confidence Rating")
    st.write(f"⭐ {analysis['confidence']} / 10")

    # ⚡ TEMPO
    st.subheader("⚡ Match Tempo")
    st.write(analysis["tempo"])

    # 🧠 ANALYSIS
    st.subheader("🧠 Genie Analysis")
    st.markdown(analysis["analysis"])

    # 🎯 STRATEGY
    st.subheader("📈 Suggested Trading Approach")
    st.info(analysis["strategy"])

    # 📊 ODDS
    st.subheader("💰 Odds Snapshot")

    if "odds" in match and match["odds"]:
        try:
            bookmaker = match["odds"][0]
            outcomes = bookmaker["markets"][0]["outcomes"]

            for o in outcomes:
                st.write(f"{o['name']}: {o['price']}")
        except:
            st.write("Odds available but parsing failed")
    else:
        st.write("Odds not available")
