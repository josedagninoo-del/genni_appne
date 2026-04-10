import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(layout="wide")
st.title("🔥 GENIE PRO REAL — ELITE")

# =========================================================
# DATA
# =========================================================
@st.cache_data
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

if df.empty:
    st.error("No hay datos disponibles")
    st.stop()

# =========================================================
# ENGINE BASE
# =========================================================
def genie_analysis(home, away, h, d, a):

    imp_h = 1 / h
    imp_d = 1 / d
    imp_a = 1 / a
    overround = imp_h + imp_d + imp_a

    ph = imp_h / overround
    pa = imp_a / overround

    goals = 2.4 + abs(h - a) * 0.6

    xg_h = round(goals * ph, 2)
    xg_a = round(goals * pa, 2)

    return ph, pa, goals, xg_h, xg_a

# =========================================================
# CLASIFICACIÓN
# =========================================================
def classify(ph, pa, goals, h):

    score = 0

    if abs(ph - pa) > 0.2:
        score += 3
    elif abs(ph - pa) > 0.1:
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
# VALUE
# =========================================================
def detect_value(home, away, ph, pa, h, a):
    if ph > 0.55 and h > 2.0:
        return f"VALUE en {home}"
    elif pa > 0.45 and a > 2.2:
        return f"VALUE en {away}"
    return "Sin value claro"

# =========================================================
# ESTRATEGIA
# =========================================================
def strategy_engine(home, ph, goals):

    if goals > 2.7:
        return "🔥 Lay The Dip"
    elif ph > 0.6:
        return "⚡ Momentum Trade"
    elif ph > 0.52 and goals > 2.5:
        return "💣 Genie Gambit"
    else:
        return "🎯 Goals Flow"

# =========================================================
# NARRATIVA + EJECUCIÓN
# =========================================================
def narrative(home, away, ph, pa, goals, strat):

    dominance = f"{home} domina el escenario" if ph > 0.6 else "Partido equilibrado"

    tempo = "Ritmo alto con probabilidad de gol temprano" if goals > 2.7 else "Ritmo medio"

    if "Lay The Dip" in strat:
        execution = """
PLAN:
1. Esperar 10-15 min sin gol  
2. Lay Under 2.5  
3. Salida tras gol  

EDGE: caída artificial de cuota
"""
    elif "Momentum" in strat:
        execution = """
PLAN:
1. Confirmar dominio  
2. Back favorito  
3. Salida tras gol  

EDGE: anticipación de movimiento
"""
    elif "Gambit" in strat:
        execution = """
PLAN:
1. Stake dividido  
2. Favorito + Over  

EDGE: doble exposición
"""
    else:
        execution = """
PLAN:
1. Leer ritmo  
2. Entrar Over/BTTS  

EDGE: flujo ofensivo
"""

    return dominance, tempo, execution

# =========================================================
# CONCLUSIÓN GLOBAL
# =========================================================
st.subheader("🚨 CONCLUSIÓN OPERATIVA")

entradas, lectura, evitar = [], [], []

for _, r in df.iterrows():

    ph, pa, goals, _, _ = genie_analysis(r.HomeTeam, r.AwayTeam, r.H, r.D, r.A)
    label, _ = classify(ph, pa, goals, r.H)

    match = f"{r.HomeTeam} vs {r.AwayTeam}"

    if label == "🟢 ENTRADA":
        entradas.append(match)
    elif label == "🟡 LECTURA":
        lectura.append(match)
    else:
        evitar.append(match)

st.markdown("### 🟢 ENTRADA")
for m in entradas[:5]:
    st.write(m)

st.markdown("### 🟡 LECTURA")
for m in lectura[:5]:
    st.write(m)

st.markdown("### 🔴 EVITAR")
for m in evitar[:5]:
    st.write(m)

# =========================================================
# SELECTOR
# =========================================================
matches = df.apply(lambda r: f"{r.HomeTeam} vs {r.AwayTeam}", axis=1)

selected = st.selectbox("Selecciona partido", matches)

row = df.iloc[list(matches).index(selected)]

home, away = row.HomeTeam, row.AwayTeam

ph, pa, goals, xg_h, xg_a = genie_analysis(home, away, row.H, row.D, row.A)

label, score = classify(ph, pa, goals, row.H)

value = detect_value(home, away, ph, pa, row.H, row.A)

strat = strategy_engine(home, ph, goals)

dominance, tempo, execution = narrative(home, away, ph, pa, goals, strat)

# =========================================================
# DISPLAY
# =========================================================
st.header(f"{home} vs {away}")

st.subheader("📊 Clasificación")
st.write(f"{label} | Score {score}/9")

st.subheader("📈 xG")
st.write(f"{xg_h} vs {xg_a}")

st.subheader("💰 Value")
st.write(value)

st.subheader("🔥 Estrategia")
st.write(strat)

st.subheader("🧠 Lectura")
st.write(dominance)
st.write(tempo)

st.subheader("🎯 Ejecución")
st.write(execution)
