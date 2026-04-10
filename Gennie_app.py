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

    total_goals = 2.4 + (abs(h - a) * 0.6)

    xg_home = round(total_goals * ph, 2)
    xg_away = round(total_goals * pa, 2)

    goals_trend = "Alta tendencia a Over 2.5" if total_goals > 2.8 else "Partido abierto moderado"

    scoring = f"{home} tiende a marcar primero" if ph > 0.60 else "Intercambio probable"

    tactics = f"{home} dominará el juego" if h < 1.7 else "Partido equilibrado"

    strategy = "LAY THE DIP" if total_goals > 2.6 else "OVER / BTTS"

    confidence = round((1 - (overround - 1)) * 10, 2)

    return ph, pa, total_goals, xg_home, xg_away, goals_trend, scoring, tactics, strategy, confidence


# =========================================================
# NARRATIVA
# =========================================================
def narrative_engine(home, away, ph, pa, goals, strat):

    dominance = f"{home} domina el escenario" if ph > 0.6 else "Partido equilibrado"

    tempo = "Ritmo alto" if goals > 2.7 else "Ritmo medio"

    if strat == "LAY THE DIP":
        execution = """
✔ Esperar 10-15 min  
✔ Entrar Lay Under  
✔ Salir tras gol  
"""
    else:
        execution = """
✔ Esperar validación  
✔ Entrar Over  
✔ Salir tras goles  
"""

    return dominance, tempo, execution


# =========================================================
# SELECTOR
# =========================================================
matches = df.apply(lambda r: f"{r.HomeTeam} vs {r.AwayTeam} | {r.Div}", axis=1)

selected = st.selectbox("Selecciona partido", matches)

row = df.iloc[list(matches).index(selected)]

home, away = row.HomeTeam, row.AwayTeam

# =========================================================
# ANALISIS
# =========================================================
ph, pa, goals, xg_h, xg_a, goals_trend, scoring, tactics, strategy, confidence = genie_analysis(
    home, away, row.H, row.D, row.A
)

dominance, tempo, execution = narrative_engine(home, away, ph, pa, goals, strategy)

# =========================================================
# DISPLAY
# =========================================================
st.header(f"{home} vs {away}")

st.subheader("📊 xG")
st.write(f"{xg_h} vs {xg_a}")

st.subheader("⚽ Goal Trend")
st.write(goals_trend)

st.subheader("🎯 Estrategia")
st.write(strategy)

st.subheader("🧠 Lectura")
st.write(dominance)
st.write(tempo)

st.subheader("📈 Ejecución")
st.write(execution)

st.subheader("⭐ Confidence")
st.write(confidence)
