import streamlit as st
import requests
from datetime import datetime
import json
import os

# -----------------------
# CONFIG
# -----------------------
API_KEY = os.getenv("API_KEY")  # usar Streamlit Secrets

URL_FIXTURES = "https://api-football-v1.p.rapidapi.com/v3/fixtures"
URL_ODDS = "https://api-football-v1.p.rapidapi.com/v3/odds"

HEADERS = {
    "X-RapidAPI-Key": API_KEY,
    "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
}

MODEL_FILE = "model_feedback.json"

# -----------------------
# MODEL MEMORY
# -----------------------
def load_model():
    if os.path.exists(MODEL_FILE):
        with open(MODEL_FILE, "r") as f:
            return json.load(f)
    return {"HIGH TEMPO": 1.0, "BALANCED": 1.0, "LOW BLOCK": 1.0}

def save_model(model):
    with open(MODEL_FILE, "w") as f:
        json.dump(model, f)

model_weights = load_model()

# -----------------------
# FALLBACK MATCHES
# -----------------------
def fallback_matches():
    return [
        {"id": 1, "league": "Europa League", "home": "Bologna", "away": "Aston Villa", "kickoff": "20:00"},
        {"id": 2, "league": "Europa League", "home": "Freiburg", "away": "Celta Vigo", "kickoff": "18:00"},
        {"id": 3, "league": "Conference League", "home": "Rayo Vallecano", "away": "AEK", "kickoff": "19:00"},
    ]

# -----------------------
# FETCH MATCHES
# -----------------------
def fetch_matches():
    today = datetime.now().strftime("%Y-%m-%d")
    params = {"date": today, "timezone": "America/Mexico_City"}

    try:
        res = requests.get(URL_FIXTURES, headers=HEADERS, params=params, timeout=15)

        if res.status_code != 200:
            return fallback_matches()

        data = res.json()

        if "response" not in data:
            return fallback_matches()

        matches = []

        for m in data["response"]:
            matches.append({
                "id": m["fixture"]["id"],
                "league": m["league"]["name"],
                "home": m["teams"]["home"]["name"],
                "away": m["teams"]["away"]["name"],
                "kickoff": m["fixture"]["date"]
            })

        return matches

    except:
        return fallback_matches()

# -----------------------
# FETCH ODDS
# -----------------------
def fetch_odds(fixture_id):
    try:
        params = {"fixture": fixture_id}
        res = requests.get(URL_ODDS, headers=HEADERS, params=params, timeout=10)
        data = res.json()

        if "response" not in data or not data["response"]:
            return {"home": None, "draw": None, "away": None}

        bets = data["response"][0]["bookmakers"][0]["bets"]

        for b in bets:
            if b["name"] == "Match Winner":
                odds = b["values"]
                return {
                    "home": float(odds[0]["odd"]),
                    "draw": float(odds[1]["odd"]),
                    "away": float(odds[2]["odd"])
                }

    except:
        pass

    return {"home": None, "draw": None, "away": None}

# -----------------------
# GENIE ENGINE
# -----------------------
def classify_match(home, away):
    offensive = ["Atalanta", "Leverkusen", "Liverpool", "Brighton", "Fiorentina", "Aston Villa"]
    defensive = ["Getafe", "Torino", "Strasbourg"]

    if any(t in home for t in offensive) or any(t in away for t in offensive):
        return "HIGH TEMPO"
    elif any(t in home for t in defensive) and any(t in away for t in defensive):
        return "LOW BLOCK"
    else:
        return "BALANCED"

def analyze(match, odds):
    game_type = classify_match(match["home"], match["away"])

    if game_type == "HIGH TEMPO":
        strategy = "Lay Under 2.5 / Over trading"
        confidence = 8
    elif game_type == "LOW BLOCK":
        strategy = "Wait / Draw angle"
        confidence = 5
    else:
        strategy = "Momentum trading"
        confidence = 6

    if odds["home"] and odds["home"] < 2:
        confidence += 1

    confidence *= model_weights.get(game_type, 1)

    return {
        "type": game_type,
        "strategy": strategy,
        "confidence": round(confidence, 1),
        "prophecy": f"Partido {game_type} condicionado por ritmo y primer gol.",
        "volatility": "HIGH" if game_type == "HIGH TEMPO" else "MEDIUM",
        "draw_risk": "HIGH" if game_type == "LOW BLOCK" else "MEDIUM",
        "early_goal": "HIGH" if game_type == "HIGH TEMPO" else "LOW"
    }

# -----------------------
# RANKING
# -----------------------
def rank_matches(data):
    return sorted(data, key=lambda x: x["analysis"]["confidence"], reverse=True)

# -----------------------
# UI
# -----------------------
st.set_page_config(layout="wide")
st.title("🔥 Football Trading Genie PRO")

matches = fetch_matches()

if not matches:
    st.error("No matches found")
    st.stop()

data = []

for m in matches:
    odds = fetch_odds(m["id"])
    analysis = analyze(m, odds)

    data.append({
        "match": f"{m['home']} vs {m['away']}",
        "league": m["league"],
        "raw": m,
        "analysis": analysis,
        "odds": odds
    })

# ranking
ranked = rank_matches(data)

st.markdown("## 🏆 TOP MATCHES")
for i, r in enumerate(ranked[:5]):
    st.write(f"{i+1}. {r['match']} → Score: {r['analysis']['confidence']}")

# selector
options = [d["match"] for d in data]
selected = st.selectbox("Selecciona partido", options)

selected_match = next(d for d in data if d["match"] == selected)

m = selected_match["raw"]
a = selected_match["analysis"]
o = selected_match["odds"]

# OUTPUT
st.subheader(selected)

st.write(f"League: {m['league']}")
st.write(f"Kickoff: {m['kickoff']}")

st.markdown("### 💰 Odds")
st.write(o)

st.markdown("### 🔮 Genie’s Prophecy")
st.write(a["prophecy"])

st.markdown("### 📊 Match Dynamics")
st.write(f"Type: {a['type']}")
st.write(f"Volatility: {a['volatility']}")
st.write(f"Draw Risk: {a['draw_risk']}")
st.write(f"Early Goal: {a['early_goal']}")

st.markdown("### 🎯 Strategy")
st.write(a["strategy"])

st.markdown("### 📈 Confidence")
st.write(a["confidence"])

st.markdown("### 📋 Trading Plan")
st.write("Entry: 10–25 min")
st.write("Trigger: ritmo + presión")
st.write("Exit: gol")
st.write("No Trade: partido muerto")

# -----------------------
# LEARNING
# -----------------------
st.markdown("### 🧠 Feedback")

if st.button("👍 Buen análisis"):
    model_weights[a["type"]] *= 1.05
    save_model(model_weights)

if st.button("👎 Mal análisis"):
    model_weights[a["type"]] *= 0.95
    save_model(model_weights)