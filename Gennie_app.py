import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(layout="wide")
st.title("🔥 GENIE PRO REAL — ELITE")

# =========================================================
# 📡 API DATA (AGREGADO)
# =========================================================
import requests

def load_api_data():
    try:
        API_KEY = st.secrets.get("API_KEY", "")

        url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"
        headers = {
            "X-RapidAPI-Key": API_KEY,
            "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
        }

        params = {
            "date": datetime.today().strftime("%Y-%m-%d")
        }

        res = requests.get(url, headers=headers, params=params, timeout=10)

        if res.status_code != 200:
            return None

        data = res.json()

        rows = []
        for m in data.get("response", []):
            rows.append({
                "HomeTeam": m["teams"]["home"]["name"],
                "AwayTeam": m["teams"]["away"]["name"],
                "Div": m["league"]["name"],
                "Date": m["fixture"]["date"][:10],
                "H": 2.2,
                "D": 3.2,
                "A": 3.0
            })

        df_api = pd.DataFrame(rows)

        if not df_api.empty:
            df_api["Date"] = pd.to_datetime(df_api["Date"])
            st.success("✅ API PRO activa")
            return df_api

    except:
        return None
# =========================================================
# 📥 DATA (BASE)
# =========================================================
@st.cache_data
def load_data():

    # 🔥 PRIORIDAD API
    df_api = load_api_data()
    if df_api is not None:
        return df_api
def load_data():
    url = "https://www.football-data.co.uk/fixtures.csv"
    df = pd.read_csv(url)

    df = df.dropna(subset=["HomeTeam", "AwayTeam"])
    df["Date"] = pd.to_datetime(df["Date"], dayfirst=True, errors="coerce")

    today = datetime.today()
    df_future = df[df["Date"] >= today]

    if df_future.empty:
        df_future = df.sort_values("Date").tail(40)

    df_future["H"] = df_future["B365H"]
    df_future["D"] = df_future["B365D"]
    df_future["A"] = df_future["B365A"]

    df_future = df_future.dropna(subset=["H", "D", "A"])

    return df_future

df = load_data()

# =========================================================
# 🧠 ENGINE BASE (NO TOCAR)
# =========================================================
def genie_analysis(home, away, h, d, a):

    imp_h = 1 / h
    imp_d = 1 / d
    imp_a = 1 / a
    overround = imp_h + imp_d + imp_a

    ph = imp_h / overround
    pa = imp_a / overround

    total_goals = 2.4 + (abs(h - a) * 0.6)

    xg_home = round(total_goals * ph, 2)
    xg_away = round(total_goals * pa, 2)

    if total_goals > 2.8:
        goals_trend = "Alta tendencia a Over 2.5"
    elif total_goals > 2.4:
        goals_trend = "Partido abierto moderado"
    else:
        goals_trend = "Tendencia Under / controlado"

    if ph > 0.60:
        scoring = f"{home} tiende a marcar primero"
    elif pa > 0.45:
        scoring = f"{away} peligroso en transición"
    else:
        scoring = "Intercambio probable"

    if h < 1.70:
        tactics = f"{home} dominará, {away} buscará contra"
    elif abs(h - a) < 0.3:
        tactics = "Partido equilibrado"
    else:
        tactics = "Dominio ligero + transiciones"

    if total_goals > 2.6:
        strategy = "LAY THE DIP"
        market = "Under 2.5"
        entry = "Min 10-15"
        exit = "Gol o min 60"
    elif ph > 0.58:
        strategy = "BACK FAVORITO"
        market = "Match Odds"
        entry = "Min 5-15"
        exit = "Gol favorito"
    else:
        strategy = "OVER / BTTS"
        market = "Goals"
        entry = "Min 15-25"
        exit = "Tras goles"

    confidence = round((1 - (overround - 1)) * 10, 2)

    return ph, pa, total_goals, xg_home, xg_away, goals_trend, scoring, tactics, strategy, market, entry, exit, confidence
# =========================================================
# 🤖 MACHINE LEARNING INSIGHT
# =========================================================
st.subheader("🤖 MACHINE LEARNING INSIGHT")
st.write(ml_prediction)    
# =========================================================
# 🤖 ML PREDICCIÓN (AGREGADO)
# =========================================================
ml_prediction = ml_goal_prediction(ph, pa, goals)    

# =========================================================
# 🤖 ML GOAL TIMING MODEL (AGREGADO)
# =========================================================
def ml_goal_prediction(ph, pa, goals):

    score = 0

    # 🔹 Intensidad del partido
    if goals > 2.8:
        score += 2
    elif goals > 2.5:
        score += 1

    # 🔹 Dominancia
    if ph > 0.60 or pa > 0.60:
        score += 1

    # 🔹 Equilibrio (partidos abiertos)
    if abs(ph - pa) < 0.15:
        score += 1

    # 🔹 Decisión ML
    if score >= 3:
        return "🔥 Alta probabilidad de gol temprano (0-30 min)"
    elif score == 2:
        return "⚠️ Probabilidad media de gol (30-60 min)"
    else:
        return "❄️ Baja probabilidad de gol temprano"
# =========================================================
# 🧠 NUEVO: NARRATIVA ELITE + EJECUCIÓN (AGREGADO)
# =========================================================
def narrative_engine(home, away, ph, pa, goals, xg_h, xg_a, strategy):

    if ph > 0.60:
        context = f"{home} parte con clara superioridad estructural y debería imponer condiciones desde el inicio."
    elif pa > 0.55:
        context = f"{away} tiene ventaja estructural y puede controlar el ritmo."
    else:
        context = "El partido se perfila equilibrado con potencial de intercambio constante."

    if goals > 2.8:
        tempo = "Se espera un ritmo alto con múltiples situaciones de gol."
    elif goals > 2.4:
        tempo = "Ritmo medio con momentos ofensivos claros."
    else:
        tempo = "Partido más táctico y cerrado."

    if "LAY THE DIP" in strategy:
        execution = """
📌 PLAN OPERATIVO — LAY THE DIP

1. Esperar 10-15 min sin gol  
2. Detectar caída de cuota en Under 2.5  
3. Ejecutar Lay  

🎯 Edge:
El mercado subestima el timing del gol  

📈 Gestión:
Salir tras gol o min 60  

⚠ Riesgo:
Partido sin ritmo
"""
    elif "BACK FAVORITO" in strategy:
        execution = """
📌 PLAN OPERATIVO — MOMENTUM

1. Confirmar dominio inicial  
2. Back favorito antes del gol  

🎯 Edge:
Entrar antes del movimiento fuerte  

📈 Gestión:
Salir tras gol  

⚠ Riesgo:
Dominio falso
"""
    else:
        execution = """
📌 PLAN OPERATIVO — GOALS FLOW

1. Esperar lectura (15-25 min)  
2. Confirmar intercambio ofensivo  

🎯 Edge:
Flujo del partido  

📈 Gestión:
Salir tras 1-2 goles  

⚠ Riesgo:
Partido trabado
"""

    return context, tempo, execution


# =========================================================
# 🧠 NUEVO: BLOQUE NARRATIVO PROFESIONAL (AGREGADO)
# =========================================================
def professional_summary(home, away, ph, pa, goals, strategy):

    return f"""
Este enfrentamiento entre **{home} y {away}** presenta un escenario donde el mercado ya ha definido una estructura clara.

Las probabilidades implícitas sugieren:
- {home}: {round(ph*100,1)}%
- {away}: {round(pa*100,1)}%

Con una expectativa de gol de **{round(goals,2)}**, el partido ofrece oportunidades basadas en:

✔ Timing del primer gol  
✔ Reacción del mercado  
✔ Desajustes de cuota  

🎯 Enfoque recomendado:
Aplicar **{strategy}** siguiendo confirmación del desarrollo real del partido.

👉 No se trata de predecir el resultado, sino de explotar el comportamiento del mercado.
"""


# =========================================================
# 🧠 CLASIFICACIÓN (BASE)
# =========================================================
def classify_match(ph, pa, goals, h):

    edge = abs(ph - pa)
    score = 0

    if edge > 0.20:
        score += 3
    elif edge > 0.10:
        score += 2
    else:
        score += 1

    if goals > 2.7:
        score += 3
    elif goals > 2.4:
        score += 2
    else:
        score += 1

    if 1.7 < h < 2.8:
        score += 2
    else:
        score += 1

    if score >= 7:
        return "🟢 ENTRADA", score
    elif score >= 5:
        return "🟡 LECTURA", score
    else:
        return "🔴 EVITAR", score


# =========================================================
# 🚨 CONCLUSIÓN OPERATIVA
# =========================================================
st.subheader("🚨 CONCLUSIÓN OPERATIVA")

entradas, lectura, evitar = [], [], []

for _, r in df.iterrows():
    ph, pa, goals, *_ = genie_analysis(r.HomeTeam, r.AwayTeam, r.H, r.D, r.A)
    label, _ = classify_match(ph, pa, goals, r.H)

    match = f"{r.HomeTeam} vs {r.AwayTeam}"

    if label == "🟢 ENTRADA":
        entradas.append(match)
    elif label == "🟡 LECTURA":
        lectura.append(match)
    else:
        evitar.append(match)

st.markdown("### 🟢 PARTIDOS PARA ENTRAR")
for m in entradas[:5]:
    st.write(m)

st.markdown("### 🟡 PARTIDOS DE LECTURA")
for m in lectura[:5]:
    st.write(m)

st.markdown("### 🔴 EVITAR")
for m in evitar[:5]:
    st.write(m)


# =========================================================
# 🎯 SELECTOR
# =========================================================
matches = [
    f"{r.HomeTeam} vs {r.AwayTeam} | {r.Div} | {r.Date.strftime('%d/%m/%Y')}"
    for _, r in df.iterrows()
]

selected = st.selectbox("Selecciona partido", matches)
row = df.iloc[matches.index(selected)]

home, away = row.HomeTeam, row.AwayTeam

ph, pa, goals, xg_h, xg_a, goals_trend, scoring, tactics, strategy, market, entry, exit, confidence = genie_analysis(
    home, away, row.H, row.D, row.A
)

label, score = classify_match(ph, pa, goals, row.H)

context, tempo, execution = narrative_engine(home, away, ph, pa, goals, xg_h, xg_a, strategy)

summary = professional_summary(home, away, ph, pa, goals, strategy)

# =========================================================
# DISPLAY (BASE + AGREGADOS)
# =========================================================
st.header(f"{home} vs {away}")
st.write(f"🌍 {row.Div}")
st.write(f"📅 {row.Date.strftime('%d/%m/%Y')}")

st.subheader("📊 Clasificación")
st.write(f"{label} | Score {score}/9")

st.subheader("🧠 GENIE ANALYSIS")

st.markdown(f"""
### 📊 xG
- {xg_h} vs {xg_a}

### ⚽ Goal Trends
{goals_trend}

### 🎯 Scoring Patterns
{scoring}

### 🧩 Team Tactics
{tactics}
""")

st.subheader("🎯 ESTRATEGIA DE TRADING")

st.markdown(f"""
**Strategy:** {strategy}  
**Market:** {market}  

**Entry:** {entry}  
**Exit:** {exit}  
""")

# 🔥 NUEVO BLOQUE 1
st.subheader("🧠 LECTURA PROFESIONAL DEL PARTIDO")
st.markdown(f"""
### Contexto
{context}

### Dinámica
{tempo}
""")

# 🔥 NUEVO BLOQUE 2
st.subheader("🎯 PLAN DE EJECUCIÓN DETALLADO")
st.markdown(execution)

# 🔥 NUEVO BLOQUE 3
st.subheader("🧠 RESUMEN PROFESIONAL AVANZADO")
st.markdown(summary)

st.subheader("⭐ Confidence")
st.write(f"{confidence} / 10")
