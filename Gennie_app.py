import streamlit as st
import requests
from datetime import datetime
import os

# -----------------------
# CONFIG
# -----------------------
API_KEY = st.secrets.get("API_KEY")
ODDS_KEY = st.secrets.get("ODDS_KEY")

DEBUG = False  # poner True si quieres ver errores

# -----------------------
# FETCH MATCHES
# -----------------------
def fetch_matches():
    url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"

    headers = {
        "X-RapidAPI-Key": API_KEY,
        "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
    }

    today = datetime.now().strftime("%Y-%m-%d")

    try:
        res = requests.get(url, headers=headers, params={"date": today}, timeout=15)

        if DEBUG:
            st.write("STATUS:", res.status_code)
            st.write(res.text[:500])

        if res.status_code != 200:
            return []

        data = res.json()

        if "response" not in data or not data["response"]:
            return []

        matches = []

        for m in data["response"]:
            matches.append({
                "home": m["teams"]["home"]["name"],
                "away": m["teams"]["away"]["name"],
                "league": m["league"]["name"],
                "kickoff": m["fixture"]["date"]
            })

        return matches

    except Exception as e:
        if DEBUG:
            st.write("ERROR:", e)
        return []

# -----------------------
# FETCH ODDS (ODDS API)
# -----------------------
def fetch_odds():
    url = f"https://api.the-odds-api.com/v4/sports/soccer/odds/?apiKey={ODDS_KEY}&regions=eu&markets=h2h"

    odds_dict = {}

    try:
        res = requests.get(url, timeout=10)

        if res.status_code != 200:
            return {}

        data = res.json()

        for game in data:
            key = f"{game['home_team']} vs {game['away_team']}"

            try:
                market = game["bookmakers"][0]["markets"][0]["outcomes"]

                odds_dict[key] = {
                    "home": market[0]["price"],
                    "away": market[1]["price"]
                }
            except:
                continue

        return odds_dict

    except:
        return {}

# -----------------------
# CLASSIFICATION ENGINE
# -----------------------
def classify(home, away):
    attack = ["Liverpool", "Leverkusen", "Atalanta", "Brighton", "Fiorentina"]
    defense = ["Getafe", "Torino", "Strasbourg"]

    if any(t in home for t in attack) or any(t in away for t in attack):
        return "HIGH TEMPO"
    elif any(t in home for t in defense) and any(t in away for t in defense):
        return "LOW BLOCK"
    else:
        return "BALANCED"

# -----------------------
# ANALYSIS ENGINE
# -----------------------
def analyze(match, odds):
    game_type = classify(match["home"], match["away"])

    base_score = {
        "HIGH TEMPO": 8,
        "BALANCED": 6,
        "LOW BLOCK": 4
    }[game_type]

    # boost si hay cuotas reales
    if odds:
        base_score += 1

    return {
        "type": game_type,
        "confidence": base_score,
        "strategy": {
            "HIGH TEMPO": "Lay Under / Over trading",
            "BALANCED": "Momentum Match Odds",
            "LOW BLOCK": "Wait / Draw"
        }[game_type],
        "prophecy": f"Partido {game_type} condicionado por ritmo, presión y primer gol."
    }

# -----------------------
# UI
# -----------------------
st.set_page_config(layout="wide")
st.title("🔥 GENIE PRO REAL")

matches = fetch_matches()

# -----------------------
# FALLBACK INTELIGENTE
# -----------------------
if not matches:
    st.warning("⚠️ API sin datos → usando partidos simulados")

    matches = [
        {"home": "Liverpool", "away": "Brighton", "league": "Premier League", "kickoff": "20:00"},
        {"home": "Atalanta", "away": "Roma", "league": "Serie A", "kickoff": "18:00"},
        {"home": "Leverkusen", "away": "Dortmund", "league": "Bundesliga", "kickoff": "19:30"},
    ]

# -----------------------
# ODDS
# -----------------------
odds_data = fetch_odds()

# -----------------------
# BUILD DATASET
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
# VALIDACIÓN FINAL
# -----------------------
if not data:
    st.error("No matches available")
    st.stop()

# -----------------------
# RANKING
# -----------------------
ranked = sorted(data, key=lambda x: x["analysis"]["confidence"], reverse=True)

st.markdown("## 🏆 TOP MATCHES")
for i, r in enumerate(ranked[:5]):
    st.write(f"{i+1}. {r['match']} → Score: {r['analysis']['confidence']}")

# -----------------------
# SELECTOR SEGURO
# -----------------------
options = [d["match"] for d in data]

if not options:
    st.warning("No matches to display")
    st.stop()

selected = st.selectbox("Selecciona partido", options)

# -----------------------
# SAFE MATCH FIND
# -----------------------
sel = next((d for d in data if d["match"] == selected), None)

if not sel:
    st.error("Match not found")
    st.stop()

# -----------------------
# OUTPUT
# -----------------------
st.subheader(selected)

st.write(f"League: {sel['raw']['league']}")
st.write(f"Kickoff: {sel['raw']['kickoff']}")

st.markdown("### 💰 Odds")
if sel["odds"]:
    st.write(sel["odds"])
else:
    st.write("No odds available")

st.markdown("### 🔮 Genie Insight")
st.write(sel["analysis"]["prophecy"])

st.markdown("### 📊 Match Type")
st.write(sel["analysis"]["type"])

st.markdown("### 🎯 Strategy")
st.write(sel["analysis"]["strategy"])

st.markdown("### 📈 Confidence")
st.write(sel["analysis"]["confidence"])
