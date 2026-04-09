import streamlit as st
import requests
from datetime import date
import json
import os

SPORT_KEY = st.secrets.get("API_KEY")
ODDS_KEY = st.secrets.get("ODDS_KEY")

BASE = "https://sportapi7.p.rapidapi.com"

HEADERS = {
    "X-RapidAPI-Key": SPORT_KEY,
    "X-RapidAPI-Host": "sportapi7.p.rapidapi.com",
}

CACHE_FILE = "matches_cache.json"

# -----------------------
# CACHE SAVE / LOAD
# -----------------------
def save_cache(data):
    with open(CACHE_FILE, "w") as f:
        json.dump(data, f)

def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            return json.load(f)
    return []

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

        events = r.json().get("events", [])

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

        if matches:
            save_cache(matches)

        return matches

    except:
        return []

# -----------------------
# ODDS API MULTI
# -----------------------
def fetch_odds():
    sports = [
        "soccer_epl",
        "soccer_spain_la_liga",
        "soccer_italy_serie_a",
        "soccer_germany_bundesliga",
        "soccer_france_ligue_one",
        "soccer_uefa_champs_league",
        "soccer_uefa_europa_league"
    ]

    matches = []

    for sport in sports:
        try:
            url = f"https://api.the-odds-api.com/v4/sports/{sport}/odds/?apiKey={ODDS_KEY}&regions=eu&markets=h2h"
            r = requests.get(url, timeout=10)

            if r.status_code != 200:
                continue

            data = r.json()

            for g in data:
                matches.append({
                    "home": g["home_team"],
                    "away": g["away_team"],
                    "league": g.get("sport_title", sport),
                    "country": "Unknown"
                })

        except:
            continue

    if matches:
        save_cache(matches)

    return matches

# -----------------------
# FALLBACK FINAL
# -----------------------
def fallback_matches():
    return [
        {"home": "Liverpool", "away": "Brighton", "league": "Premier League", "country": "England"},
        {"home": "Atalanta", "away": "Roma", "league": "Serie A", "country": "Italy"},
        {"home": "Leverkusen", "away": "Dortmund", "league": "Bundesliga", "country": "Germany"}
    ]

# -----------------------
# GENIE ENGINE (CLAVE)
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

    return f"""
After weighing up the data, here’s how I’d approach it:

📊 Match: {home} vs {away}

🔎 Expected Pattern:
This game projects as a **{tempo} contest**, where tempo will dictate trading opportunities.

⚙️ Tactical Outlook:
Expect phases of control rather than constant dominance.

📈 Market Behaviour:
Price movement likely tied to first real momentum swing.

⏱ Entry Guidance:
Wait 10–15 minutes → confirm tempo before acting.

💰 Trade Idea:
Focus on **{angle}** depending on early match flow.

🛑 Risk Profile:
{risk} — avoid forcing trades without confirmation.

📌 Key Insight:
This is a **reaction-based setup**, not a pre-match edge.
"""

# -----------------------
# UI
# -----------------------
st.set_page_config(layout="wide")
st.title("🔥 GENIE PRO REAL — BLINDADO")

matches = fetch_sportapi()

if not matches:
    st.warning("SportAPI empty → trying OddsAPI")
    matches = fetch_odds()

if not matches:
    st.warning("APIs empty → using cache")
    matches = load_cache()

if not matches:
    st.warning("No cache → using fallback dataset")
    matches = fallback_matches()

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
