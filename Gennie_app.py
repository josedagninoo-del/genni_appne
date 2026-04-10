import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(layout="wide")
st.title("🔥 GENIE PRO REAL — ELITE")

# =========================================================
# 📥 DATA (BASE)
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
# 🧠 CORE ENGINE (TU BASE)
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

    return ph, pa, total_goals, xg_home, xg_away


# =========================================================
# 🧠 NUEVO: MATCH RATING SYSTEM (CLAVE)
# =========================================================
def classify_match(home, away, h, d, a):

    ph, pa, goals, xg_h, xg_a = genie_analysis(home, away, h, d, a)

    edge = abs(ph - pa)

    score = 0

    # ===== 1. CLARIDAD DE MERCADO
    if edge > 0.20:
        score += 3
    elif edge > 0.10:
        score += 2
    else:
        score += 1

    # ===== 2. EXPECTATIVA DE GOLES
    if goals > 2.7:
        score += 3
    elif goals > 2.4:
        score += 2
    else:
        score += 1

    # ===== 3. EQUILIBRIO VS CAOS
    if 1.7 < h < 2.8:
        score += 2
    elif h < 1.6:
        score += 1
    else:
        score += 1

    # ===== CLASIFICACIÓN FINAL
    if score >= 7:
        label = "🟢 ENTRADA"
    elif score >= 5:
        label = "🟡 LECTURA"
    else:
        label = "🔴 EVITAR"

    return label, score, goals, xg_h, xg_a


# =========================================================
# 📊 GENERAR LISTA GLOBAL (TIPO TU ANÁLISIS)
# =========================================================
st.subheader("🚨 CONCLUSIÓN OPERATIVA")

entradas = []
lectura = []
evitar = []

for _, r in df.iterrows():

    label, score, goals, xg_h, xg_a = classify_match(
        r.HomeTeam, r.AwayTeam, r.H, r.D, r.A
    )

    match = f"{r.HomeTeam} vs {r.AwayTeam}"

    if label == "🟢 ENTRADA":
        entradas.append(match)
    elif label == "🟡 LECTURA":
        lectura.append(match)
    else:
        evitar.append(match)

# =========================
# 🎯 DISPLAY TIPO PROFESIONAL
# =========================
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
# 🎯 SELECTOR NORMAL
# =========================================================
matches = [
    f"{r.HomeTeam} vs {r.AwayTeam} | {r.Div} | {r.Date.strftime('%d/%m/%Y')}"
    for _, r in df.iterrows()
]

selected = st.selectbox("Selecciona partido", matches)
row = df.iloc[matches.index(selected)]

home = row.HomeTeam
away = row.AwayTeam

label, score, goals, xg_h, xg_a = classify_match(
    home, away, row.H, row.D, row.A
)

# =========================================================
# 📊 DETALLE
# =========================================================
st.header(f"{home} vs {away}")
st.write(f"🌍 {row.Div}")
st.write(f"📅 {row.Date.strftime('%d/%m/%Y')}")

st.subheader("📊 Clasificación del Partido")
st.write(f"{label} | Score: {score}/9")

st.subheader("📈 xG")
st.write(f"{xg_h} vs {xg_a}")

st.subheader("⚡ Expectativa de Partido")
st.write(f"Goals Expectation: {round(goals,2)}")

# =========================================================
# 🧠 RESUMEN ESTILO TÚ
# =========================================================
st.subheader("🧠 LECTURA DE MERCADO")

st.markdown(f"""
Este partido entre **{home} y {away}** presenta una estructura de mercado clasificada como **{label}**.

El modelo detecta:
- Diferencial de probabilidad relevante → {round(abs((1/row.H)-(1/row.A)),2)}
- xG proyectado → {xg_h} vs {xg_a}
- Expectativa de goles → {round(goals,2)}

👉 Interpretación:
El valor no está en el resultado, sino en cómo reaccionará el mercado.

- Si el partido rompe temprano → oportunidad clara de trading
- Si el mercado se congela → evitar sobreexposición

🎯 Este es un partido tipo: **{label}**
""")
