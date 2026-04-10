import streamlit as st
import pandas as pd
import requests
from datetime import datetime

st.set_page_config(layout="wide")
st.title("🔥 GENIE PRO REAL — ELITE")

# =========================================================
# 🔑 CONFIG API (PON TU API KEY)
# =========================================================
API_KEY = st.secrets.get("API_KEY", "")

HEADERS = {
    "X-RapidAPI-Key": API_KEY,
    "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
}

# =========================================================
# 📥 FIXTURES API (PRINCIPAL)
# =========================================================
def get_api_matches():
    try:
        url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"
        params = {"date": datetime.today().strftime("%Y-%m-%d")}

        res = requests.get(url, headers=HEADERS, params=params, timeout=10)

        if res.status_code != 200:
            return []

        data = res.json()
        matches = []

        for m in data.get("response", []):
            matches.append({
                "home": m["teams"]["home"]["name"],
                "away": m["teams"]["away"]["name"],
                "league": m["league"]["name"],
                "date": m["fixture"]["date"],
                "odds_h": None,
                "odds_d": None,
                "odds_a": None
            })

        return matches

    except:
        return []


# =========================================================
# 📥 CSV FALLBACK
# =========================================================
def get_csv_matches():
    try:
        df = pd.read_csv("https://www.football-data.co.uk/fixtures.csv")

        df = df.dropna(subset=["HomeTeam", "AwayTeam"])
        df["Date"] = pd.to_datetime(df["Date"], dayfirst=True, errors="coerce")

        today = datetime.today()
        df = df[df["Date"] >= today]

        matches = []

        for _, r in df.iterrows():
            matches.append({
                "home": r["HomeTeam"],
                "away": r["AwayTeam"],
                "league": r["Div"],
                "date": str(r["Date"]),
                "odds_h": r.get("B365H"),
                "odds_d": r.get("B365D"),
                "odds_a": r.get("B365A")
            })

        return matches

    except:
        return []


# =========================================================
# 🔄 DATA SOURCE LOGIC (BLINDADO)
# =========================================================
matches = get_api_matches()

if not matches:
    st.warning("⚠️ API sin datos → usando CSV fallback")
    matches = get_csv_matches()

if not matches:
    st.error("❌ No hay datos disponibles (ni API ni CSV)")
    st.stop()

# =========================================================
# 🧠 GENIE ENGINE (TU BASE ORIGINAL + MEJORADO)
# =========================================================
def genie_analysis(home, away, h=None, d=None, a=None):

    if h and d and a:
        imp_h = 1 / h
        imp_d = 1 / d
        imp_a = 1 / a
        overround = imp_h + imp_d + imp_a

        ph = imp_h / overround
        pa = imp_a / overround
    else:
        ph = 0.45
        pa = 0.35

    total_goals = 2.4 + abs(ph - pa)

    xg_home = round(total_goals * ph, 2)
    xg_away = round(total_goals * pa, 2)

    # GOALS
    if total_goals > 2.8:
        goals_trend = "Alta probabilidad de Over 2.5"
    elif total_goals > 2.4:
        goals_trend = "Partido abierto moderado"
    else:
        goals_trend = "Tendencia Under"

    # FORM
    if ph > 0.55:
        form = f"{home} llega como favorito sólido"
    elif pa > 0.45:
        form = f"{away} competitivo"
    else:
        form = "Equipos equilibrados"

    # SCORING
    if ph > 0.6:
        scoring = f"{home} probable primer gol"
    else:
        scoring = "Ambos con opciones"

    # TACTICS
    if ph > 0.55:
        tactics = f"{home} dominará, {away} contraataque"
    else:
        tactics = "Partido táctico equilibrado"

    # =========================================================
    # 🎯 ESTRATEGIA REAL GENIE
    # =========================================================
    if total_goals > 2.6:

        strategy = "LAY THE DIP"
        market = "Under 2.5"
        entry = "Min 10-15 si 0-0"
        exit = "Tras primer gol"
        rationale = "Alta expectativa de gol genera caída de cuota"

    elif ph > 0.6:

        strategy = "BACK FAVORITO"
        market = "Match Odds"
        entry = "Min 5-15"
        exit = "Tras gol"
        rationale = "Dominio estructural del favorito"

    else:

        strategy = "OVER / BTTS"
        market = "Over 2.5"
        entry = "Min 15-25"
        exit = "Tras 1-2 goles"
        rationale = "Partido abierto"

    return {
        "xg_home": xg_home,
        "xg_away": xg_away,
        "goals": goals_trend,
        "form": form,
        "scoring": scoring,
        "tactics": tactics,
        "strategy": strategy,
        "market": market,
        "entry": entry,
        "exit": exit,
        "rationale": rationale
    }


# =========================================================
# 🎯 SELECTOR
# =========================================================
options = [
    f"{m['home']} vs {m['away']} | {m['league']} | {m['date'][:16]}"
    for m in matches
]

selected = st.selectbox("Selecciona partido", options)
match = matches[options.index(selected)]

analysis = genie_analysis(
    match["home"],
    match["away"],
    match["odds_h"],
    match["odds_d"],
    match["odds_a"]
)

# =========================================================
# 📊 DISPLAY
# =========================================================
st.header(f"{match['home']} vs {match['away']}")
st.write(f"🌍 {match['league']}")
st.write(f"📅 {match['date']}")

if match["odds_h"]:
    st.write(f"💰 Odds: {match['odds_h']} | {match['odds_d']} | {match['odds_a']}")

# =========================================================
# 🧠 ANALYSIS
# =========================================================
st.subheader("🧠 GENIE ANALYSIS")

st.markdown(f"""
### 📊 xG
- {analysis['xg_home']} vs {analysis['xg_away']}

### ⚽ Goal Trends
{analysis['goals']}

### 📈 Forma
{analysis['form']}

### 🎯 Scoring
{analysis['scoring']}

### 🧩 Táctica
{analysis['tactics']}
""")

# =========================================================
# 🎯 TRADING
# =========================================================
st.subheader("🎯 PLAN DE TRADING")

st.markdown(f"""
### 🔥 Estrategia: {analysis['strategy']}

**Mercado:** {analysis['market']}  
**Entrada:** {analysis['entry']}  
**Salida:** {analysis['exit']}  

**Racional:**  
{analysis['rationale']}
""")

# =========================================================
# 🧠 RESUMEN
# =========================================================
st.subheader("🧠 RESUMEN PROFESIONAL")

st.markdown(f"""
El partido entre **{match['home']} y {match['away']}** presenta un escenario donde el mercado anticipa un juego **{analysis['goals']}**.

El modelo proyecta un xG de **{analysis['xg_home']} vs {analysis['xg_away']}**, indicando cómo se distribuirán las ocasiones.

👉 Clave del trade:
- Ritmo inicial del partido  
- Reacción del mercado  
- Confirmación del patrón esperado  

🎯 Estrategia sugerida: **{analysis['strategy']}**

Esto no es predicción, es **lectura de mercado para trading**.
""")
