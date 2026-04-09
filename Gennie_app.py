import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(layout="wide")

st.title("🔥 GENIE PRO REAL")

# =========================================================
# 📥 LOAD FIXTURES (FUENTE REAL)
# =========================================================
@st.cache_data
def load_data():
    url = "https://www.football-data.co.uk/fixtures.csv"
    df = pd.read_csv(url)

    df = df.dropna(subset=["HomeTeam", "AwayTeam", "PSH", "PSD", "PSA"])

    return df

df = load_data()

if df.empty:
    st.error("No fixtures available")
    st.stop()

# =========================================================
# 🧠 BUILD MATCH LIST
# =========================================================
matches = []

for _, row in df.iterrows():
    match = f"{row['HomeTeam']} vs {row['AwayTeam']} | {row['Div']}"
    matches.append(match)

selected = st.selectbox("Selecciona partido", matches)

row = df.iloc[matches.index(selected)]

home = row["HomeTeam"]
away = row["AwayTeam"]
league = row["Div"]

psh = float(row["PSH"])
psd = float(row["PSD"])
psa = float(row["PSA"])

# =========================================================
# 🧠 GENIE CORE ANALYSIS
# =========================================================

def analyze_match(psh, psd, psa):

    confidence = round(10 - ((psh + psa) / 2), 2)

    # 🎯 MARKET STRUCTURE
    if psh < 1.80:
        structure = "STRONG FAVORITE"
        tempo = "CONTROLLED"
        setup = "LAY DRAW / BACK FAVORITE"

    elif abs(psh - psa) < 0.40:
        structure = "BALANCED"
        tempo = "HIGH VARIANCE"
        setup = "OVER 2.5 / BTTS"

    elif psd > 3.60:
        structure = "CHAOTIC"
        tempo = "HIGH TEMPO"
        setup = "LAY DRAW / LATE GOAL TRADE"

    else:
        structure = "SEMI-BALANCED"
        tempo = "MEDIUM"
        setup = "WAIT / READ MARKET"

    # 💰 VALUE DETECTOR
    implied_home = 1 / psh
    implied_away = 1 / psa

    if implied_home > 0.60:
        value = "HOME VALUE"
    elif implied_away > 0.45:
        value = "AWAY VALUE"
    else:
        value = "NO CLEAR VALUE"

    return {
        "confidence": confidence,
        "structure": structure,
        "tempo": tempo,
        "setup": setup,
        "value": value
    }

analysis = analyze_match(psh, psd, psa)

# =========================================================
# 🎯 UI OUTPUT
# =========================================================

st.header(f"{home} vs {away}")

st.write(f"🌍 League: {league}")

# ❌ No fecha en dataset → se explica
st.write("📅 Date: Not provided (source limitation)")
st.write("⏰ Time: Not provided")

st.subheader("💰 Odds")
st.write(f"Home: {psh}")
st.write(f"Draw: {psd}")
st.write(f"Away: {psa}")

# =========================================================
# 🧠 GENIE ANALYSIS (ESTILO REAL)
# =========================================================

st.subheader("🧠 Genie Analysis")

st.markdown(f"""
**📊 Match Structure:** {analysis['structure']}

Este partido se define principalmente por la estructura del mercado.  
Las cuotas indican cómo el mercado percibe la superioridad relativa.

---

**⚡ Tempo Esperado:** {analysis['tempo']}

El ritmo esperado del partido viene determinado por la diferencia de fuerzas.  
Esto afecta directamente la velocidad del mercado en vivo.

---

**💰 Value Detectado:** {analysis['value']}

El análisis de probabilidades implícitas sugiere si existe ventaja estructural.  
No siempre implica apuesta directa, sino contexto.

---

**🎯 Setup Sugerido:**

👉 {analysis['setup']}

Este NO es un pick.  
Es un **escenario operativo esperado** basado en cómo se comporta el mercado típicamente bajo estas condiciones.

---

**📈 Lectura del Partido**

- Si el favorito domina → el mercado tenderá a comprimir líneas rápidamente  
- Si es balanceado → mayor volatilidad y oportunidades en goles  
- Si es caótico → errores defensivos + transiciones = oportunidades tardías  

---

**🧠 Interpretación Tipo Trader**

Este análisis no busca predecir el resultado.  
Busca definir **cómo se moverá el mercado**.

Tu ventaja está en ejecutar mejor que el mercado.
""")

# =========================================================
# ⭐ CONFIDENCE
# =========================================================
st.subheader("⭐ Confidence Rating")
st.write(f"{analysis['confidence']} / 10")
