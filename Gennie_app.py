import streamlit as st
import requests
import pandas as pd
from datetime import datetime

st.set_page_config(layout="wide")
st.title("🔥 GENIE PRO REAL — ELITE")

# =========================
# 🔑 KEYS
# =========================
API_KEY = st.secrets.get("API_KEY", "")
ODDS_KEY = st.secrets.get("ODDS_API_KEY", "")

# =========================
# 📡 API FOOTBALL
# =========================
def get_api_matches():
    try:
        url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"
        headers = {
            "X-RapidAPI-Key": API_KEY,
            "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
        }
        params = {"date": datetime.today().strftime("%Y-%m-%d")}

        res = requests.get(url, headers=headers, params=params, timeout=10)

        if res.status_code != 200:
            return []

        data = res.json()

        return [
            {
                "home": m["teams"]["home"]["name"],
                "away": m["teams"]["away"]["name"],
                "league": m["league"]["name"],
                "date": m["fixture"]["date"],
                "odds_h": None,
                "odds_d": None,
                "odds_a": None
            }
            for m in data.get("response", [])
        ]

    except:
        return []


# =========================
# 📡 ODDS API (BACKUP REAL)
# =========================
def get_odds_matches():
    try:
        url = "https://api.the-odds-api.com/v4/sports/soccer/odds"
        params = {
            "apiKey": ODDS_KEY,
            "regions": "eu",
            "markets": "h2h"
        }

        res = requests.get(url, params=params, timeout=10)

        if res.status_code != 200:
            return []

        data = res.json()
        matches = []

        for m in data:
            try:
                outcomes = m["bookmakers"][0]["markets"][0]["outcomes"]
                odds = {o["name"]: o["price"] for o in outcomes}

                matches.append({
                    "home": m["home_team"],
                    "away": m["away_team"],
                    "league": m["sport_title"],
                    "date": m["commence_time"],
                    "odds_h": odds.get(m["home_team"]),
                    "odds_d": odds.get("Draw"),
                    "odds_a": odds.get(m["away_team"])
                })
            except:
                continue

        return matches

    except:
        return []


# =========================
# 📄 CSV FALLBACK (último nivel)
# =========================
def get_csv_matches():
    try:
        df = pd.read_csv("https://www.football-data.co.uk/fixtures.csv")

        df["DateTime"] = pd.to_datetime(df["Date"] + " " + df["Time"], errors="coerce")

        today = datetime.today().date()
        df = df[df["DateTime"].dt.date == today]

        matches = []

        for _, r in df.iterrows():
            matches.append({
                "home": r["HomeTeam"],
                "away": r["AwayTeam"],
                "league": r["Div"],
                "date": str(r["DateTime"]),
                "odds_h": r.get("B365H"),
                "odds_d": r.get("B365D"),
                "odds_a": r.get("B365A")
            })

        return matches

    except:
        return []


# =========================
# 🔄 PIPELINE BLINDADO
# =========================
matches = get_api_matches()

if matches:
    st.success("✅ Fuente: API-Football")
else:
    matches = get_odds_matches()
    if matches:
        st.warning("⚠️ API vacía → usando OddsAPI")
    else:
        matches = get_csv_matches()
        if matches:
            st.warning("⚠️ APIs vacías → usando CSV fallback")
        else:
            st.error("❌ Sin datos en ninguna fuente")
            st.stop()


# =========================
# 🧠 GENIE ENGINE ELITE
# =========================
def genie_analysis(m):

    h, d, a = m["odds_h"], m["odds_d"], m["odds_a"]

    if h and d and a:
        imp_h = 1 / h
        imp_d = 1 / d
        imp_a = 1 / a
        total = imp_h + imp_d + imp_a

        ph = imp_h / total
        pa = imp_a / total
    else:
        ph, pa = 0.45, 0.35

    goal_expectancy = 2.4 + abs(ph - pa)

    xg_home = round(goal_expectancy * ph, 2)
    xg_away = round(goal_expectancy * pa, 2)

    tempo = "High Tempo" if goal_expectancy > 2.6 else "Controlled Tempo"

    # VALUE DETECTOR
    value = "YES" if (h and ph > (1/h)) else "NO"

    # ESTRATEGIA
    if goal_expectancy > 2.7:
        strategy = "LAY THE DIP (Under 2.5)"
        entry = "Min 10"
        exit = "Gol temprano o min 60"
    else:
        strategy = "OVER 1.5 / BTTS"
        entry = "Min 15"
        exit = "Gol o min 70"

    return {
        "xg_home": xg_home,
        "xg_away": xg_away,
        "tempo": tempo,
        "strategy": strategy,
        "entry": entry,
        "exit": exit,
        "value": value,
        "confidence": round(6 + abs(ph - pa)*10, 1)
    }


# =========================
# 🎯 UI
# =========================
options = [
    f"{m['home']} vs {m['away']} | {m['league']} | {m['date'][:16]}"
    for m in matches
]

selected = st.selectbox("Selecciona partido", options)
m = matches[options.index(selected)]

a = genie_analysis(m)

# =========================
# 📊 DISPLAY ELITE
# =========================
st.header(f"{m['home']} vs {m['away']}")
st.write(f"🌍 {m['league']}")
st.write(f"📅 {m['date']}")

st.subheader("📊 Genie Key Stats")
st.write(f"xG: {a['xg_home']} vs {a['xg_away']}")
st.write(f"Tempo: {a['tempo']}")
st.write(f"Value Detected: {a['value']}")

st.subheader("🧠 Tactical Insight")
st.write("Equipo favorito dominará posesión y ritmo, rival buscará transición rápida.")
st.write("Alta probabilidad de gol temprano si el tempo es alto.")

st.subheader("📈 Goal Trends")
st.write("Partido proyectado con alta probabilidad de Over 1.5 / Over 2.5")

st.subheader("⚔️ Trading Strategy")
st.write(f"Estrategia: {a['strategy']}")
st.write(f"Entrada: {a['entry']}")
st.write(f"Salida: {a['exit']}")

st.subheader("💰 Bankroll")
st.write("Stake sugerido: 2–4%")

st.subheader("⭐ Confidence")
st.write(f"{a['confidence']} / 10")
