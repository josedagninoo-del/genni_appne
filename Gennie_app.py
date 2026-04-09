import streamlit as st
import requests
from datetime import date

SPORT_KEY = st.secrets.get("API_KEY")
ODDS_KEY = st.secrets.get("ODDS_KEY")

BASE = "https://sportapi7.p.rapidapi.com"

HEADERS = {
    "X-RapidAPI-Key": SPORT_KEY,
    "X-RapidAPI-Host": "sportapi7.p.rapidapi.com",
}

# -----------------------
# SPORTAPI
# -----------------------
def fetch_sportapi():
    today = date.today().strftime("%Y-%m-%d")

    try:
        r = requests.get(
            f"{BASE}/api/v1/sport/football/scheduled-events/{today}",
            headers=HEADERS,
            timeout=10
        )

        data = r.json()
        events = data.get("events", [])

        matches = []

        for e in events:
            try:
                matches.append({
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
# ODDS API (FALLBACK)
# -----------------------
def fetch_odds_fallback():
    url = f"https://api.the-odds-api.com/v4/sports/soccer/odds/?apiKey={ODDS_KEY}&regions=eu"

    matches = []

    try:
        r = requests.get(url, timeout=10)

        if r.status_code != 200:
            return []

        data = r.json()

        for g in data:
            matches.append({
                "home": g["home_team"],
                "away": g["away_team"],
                "league": g.get("sport_title", "Unknown"),
                "country": "Unknown"
            })

        return matches

    except:
        return []

# -----------------------
# GENIE ENGINE REAL (LO IMPORTANTE)
# -----------------------
def genie(match):

    home = match["home"]
    away = match["away"]

    attacking = ["Liverpool","Atalanta","Leverkusen","Brighton"]
    defensive = ["Getafe","Torino"]

    if any(t in home for t in attacking) or any(t in away for t in attacking):
        tempo = "High tempo"
        angle = "Goals / Over markets"
        risk = "Medium"
    elif any(t in home for t in defensive) and any(t in away for t in defensive):
        tempo = "Low tempo"
        angle = "Draw / Under"
        risk = "Low"
    else:
        tempo = "Balanced"
        angle = "Momentum / Match odds"
        risk = "Controlled"

    # TEXTO GENIE (ESTO ES LO CLAVE)
    analysis = f"""
After weighing up the data, here’s how I’d approach it:

📊 Match: {home} vs {away}

🔎 Expected Pattern:
This game projects as a **{tempo} contest**, where the tempo will define trading opportunities.

⚙️ Tactical Expectation:
One side is likely to establish early control, but market confirmation is key.

📈 Market Behavior:
Expect price movement once the first real momentum shift appears.

⏱ Entry Guidance:
Wait 10–15 minutes → confirm intensity before involvement.

💰 Trade Idea:
Focus on **{angle}** depending on how early phases develop.

🛑 Risk Profile:
{risk} – avoid forcing entry without confirmation.

📌 Key Insight:
This is not a pre-match edge — it’s a **reaction-based trade setup**.
"""

    return analysis

# -----------------------
# UI
# -----------------------
st.set_page_config(layout="wide")
st.title("🔥 GENIE PRO REAL")

matches = fetch_sportapi()

# FALLBACK
if not matches:
    st.warning("SportAPI empty → using OddsAPI fallback")
    matches = fetch_odds_fallback()

if not matches:
    st.error("No matches available today")
    st.stop()

# -----------------------
# SELECTOR
# -----------------------
options = [f"{m['home']} vs {m['away']}" for m in matches]

selected = st.selectbox("Selecciona partido", options)

sel = next((m for m in matches if f"{m['home']} vs {m['away']}" == selected), None)

# -----------------------
# OUTPUT
# -----------------------
st.subheader(selected)

st.write(f"League: {sel['league']} ({sel['country']})")

st.markdown("### 🧠 Genie Analysis")
st.write(genie(sel))
