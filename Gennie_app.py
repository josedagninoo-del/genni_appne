import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(layout="wide")
st.title("🔥 GENIE PRO REAL — ELITE")

# =========================================================
# 📥 DATA
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

# =========================================================
# 🧠 ENGINE GENIE
# =========================================================
def genie_analysis(home, away, h, d, a):

    imp_h = 1 / h
    imp_d = 1 / d
    imp_a = 1 / a
    overround = imp_h + imp_d + imp_a

    ph = imp_h / overround
    pd_ = imp_d / overround
    pa = imp_a / overround

    # ===== xG ESTIMADO (clave)
    total_goals = 2.4 + (abs(h - a) * 0.6)
    xg_home = round(total_goals * ph, 2)
    xg_away = round(total_goals * pa, 2)

    # ===== GOAL TRENDS
    if total_goals > 2.8:
        goals_trend = "Alta tendencia a Over 2.5"
    elif total_goals > 2.4:
        goals_trend = "Partido abierto moderado"
    else:
        goals_trend = "Tendencia Under / controlado"

    # ===== SCORING PATTERNS
    if ph > 0.60:
        scoring = f"{home} tiende a marcar primero y dominar fases iniciales"
    elif pa > 0.45:
        scoring = f"{away} peligroso en transiciones y gol temprano"
    else:
        scoring = "Ambos equipos con probabilidad de intercambio"

    # ===== TEAM TACTICS (lectura mercado)
    if h < 1.70:
        tactics = f"{home} dominará posesión y presión alta, {away} replegado + contra"
    elif abs(h - a) < 0.3:
        tactics = "Partido táctico equilibrado con presión media-alta de ambos"
    else:
        tactics = "Dominio ligero + transiciones rápidas"

    # ===== RECENT FORM (proxy inteligente)
    if h < 1.80:
        form = f"{home} llega en mejor forma estructural según mercado"
    elif a < 2.20:
        form = f"{away} competitivo y peligroso"
    else:
        form = "Forma inconsistente en ambos lados"

    # =========================================================
    # 🎯 ESTRATEGIA GENIE REAL
    # =========================================================
    if total_goals > 2.6:

        strategy = "LAY THE DIP"
        market = "Under 2.5 Goals"
        entry = "Minuto 10-15 si no hay gol"
        exit = "Tras primer gol o minuto 65"
        style = "Lay → Back"

        rationale = "Alta expectativa de gol genera caída artificial en Under"

    elif ph > 0.58:

        strategy = "FAVORITO PRESIÓN"
        market = "Match Odds"
        entry = "Minuto 5-15"
        exit = "Tras gol del favorito"
        style = "Back → Lay"

        rationale = "Dominio esperado del favorito con presión constante"

    else:

        strategy = "MOMENTUM / OVER"
        market = "Over 2.5 / BTTS"
        entry = "Lectura en vivo (15-25)"
        exit = "Tras 1-2 goles"
        style = "Back"

        rationale = "Partido abierto con intercambio de ocasiones"

    confidence = round((1 - (overround - 1)) * 10, 2)

    return {
        "xg_home": xg_home,
        "xg_away": xg_away,
        "goals_trend": goals_trend,
        "scoring": scoring,
        "tactics": tactics,
        "form": form,
        "strategy": strategy,
        "market": market,
        "entry": entry,
        "exit": exit,
        "style": style,
        "rationale": rationale,
        "confidence": confidence
    }


# =========================================================
# 🎯 SELECTOR
# =========================================================
matches = [
    f"{r.HomeTeam} vs {r.AwayTeam} | {r.Div} | {r.Date.strftime('%d/%m/%Y')}"
    for _, r in df.iterrows()
]

selected = st.selectbox("Selecciona partido", matches)
row = df.iloc[matches.index(selected)]

home = row.HomeTeam
away = row.AwayTeam

analysis = genie_analysis(home, away, row.H, row.D, row.A)

# =========================================================
# 📊 HEADER
# =========================================================
st.header(f"{home} vs {away}")
st.write(f"🌍 {row.Div}")
st.write(f"📅 {row.Date.strftime('%d/%m/%Y')}")

st.subheader("💰 Odds")
st.write(f"{row.H} | {row.D} | {row.A}")

# =========================================================
# 🧠 GENIE ANALYSIS
# =========================================================
st.subheader("🧠 GENIE ANALYSIS")

st.markdown(f"""
### 📊 xG Analysis
- {home}: **{analysis['xg_home']} xG**
- {away}: **{analysis['xg_away']} xG**

### ⚽ Goal Trends
{analysis['goals_trend']}

### 📈 Recent Form
{analysis['form']}

### 🎯 Scoring Patterns
{analysis['scoring']}

### 🧩 Team Tactics
{analysis['tactics']}
""")

# =========================================================
# 🎯 ESTRATEGIA DETALLADA
# =========================================================
st.subheader("🎯 ESTRATEGIA DE TRADING")

st.markdown(f"""
### 📌 Strategy: {analysis['strategy']}

**📊 Market:** {analysis['market']}  
**🎮 Style:** {analysis['style']}  

**⏱ Entry:** {analysis['entry']}  
**🏁 Exit:** {analysis['exit']}  

**🧠 Rationale:**  
{analysis['rationale']}
""")

# =========================================================
# 🧠 RESUMEN PROFESIONAL
# =========================================================
st.subheader("🧠 RESUMEN PROFESIONAL")

st.markdown(f"""
Este partido entre **{home} y {away}** presenta un escenario donde el mercado anticipa un encuentro **{analysis['goals_trend']}**.

El modelo proyecta un xG de **{analysis['xg_home']} vs {analysis['xg_away']}**, lo que indica que el partido puede desarrollarse con un ritmo definido por **{analysis['tactics']}**.

Desde la perspectiva de trading, el valor no está en predecir el resultado, sino en **cómo reaccionará el mercado ante los eventos clave**.

👉 La clave estará en:
- Confirmación temprana del ritmo esperado  
- Reacción del mercado al primer gol  
- Identificación de movimientos de cuota lentos  

🎯 **Estrategia recomendada:** {analysis['strategy']}

Este tipo de partido ofrece oportunidades claras si se ejecuta con disciplina y timing correcto.

👉 No es predicción. Es lectura de mercado.
""")

st.subheader("⭐ Confidence")
st.write(f"{analysis['confidence']} / 10")
