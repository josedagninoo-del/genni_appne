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

    if "B365H" in df.columns:
        df_future["H"] = df_future["B365H"]
        df_future["D"] = df_future["B365D"]
        df_future["A"] = df_future["B365A"]
    else:
        df_future["H"] = df_future["PSH"]
        df_future["D"] = df_future["PSD"]
        df_future["A"] = df_future["PSA"]

    df_future = df_future.dropna(subset=["H", "D", "A"])

    return df_future


df = load_data()

# =========================================================
# 🧠 CORE ANALYSIS
# =========================================================
def analyze(psh, psd, psa):

    imp_h = 1 / psh
    imp_d = 1 / psd
    imp_a = 1 / psa

    overround = imp_h + imp_d + imp_a

    real_h = imp_h / overround
    real_d = imp_d / overround
    real_a = imp_a / overround

    confidence = round((1 - (overround - 1)) * 10, 2)

    # ESTRUCTURA
    if psh < 1.65:
        structure = "Strong Favorite"
        bias = "Home Control"
    elif abs(psh - psa) < 0.25:
        structure = "Even Match"
        bias = "No clear dominance"
    else:
        structure = "Moderate Edge"
        bias = "Slight advantage"

    # TEMPO
    volatility = abs(psh - psa)

    if volatility < 0.30:
        tempo = "High volatility"
    elif volatility < 0.80:
        tempo = "Balanced"
    else:
        tempo = "Controlled"

    # VALUE
    if real_h > 0.58:
        value = "Home side pressure"
    elif real_a > 0.42:
        value = "Away side threat"
    else:
        value = "Market efficient"

    # SETUPS
    setups = []

    if structure == "Strong Favorite":
        setups += [
            "Lay Draw (early phase)",
            "Back Favorite (price compression)",
            "Over 1.5 if dominance confirmed"
        ]

    if structure == "Even Match":
        setups += [
            "Over 2.5",
            "BTTS",
            "Momentum swings trading"
        ]

    if psd > 3.6:
        setups.append("Lay Draw late scenario")

    # SCENARIOS
    scenarios = [
        "Early goal → strong market reaction",
        "0-0 phase → odds drift and tension",
        "Underdog goal → sharp reversal"
    ]

    # RIESGOS
    risks = [
        "Low attacking efficiency",
        "False dominance (possession sin peligro)",
        "Unexpected red card / disruption"
    ]

    return {
        "confidence": confidence,
        "real_probs": (real_h, real_d, real_a),
        "structure": structure,
        "tempo": tempo,
        "value": value,
        "bias": bias,
        "setups": setups,
        "scenarios": scenarios,
        "risks": risks
    }


# =========================================================
# 🏆 RANKING
# =========================================================
ranking = []

for _, r in df.iterrows():
    a = analyze(r.H, r.D, r.A)
    score = a["confidence"]
    ranking.append({
        "match": f"{r.HomeTeam} vs {r.AwayTeam}",
        "score": score
    })

ranking_df = pd.DataFrame(ranking).sort_values(by="score", ascending=False)

st.subheader("🏆 TOP PARTIDOS")
st.dataframe(ranking_df.head(10))

# =========================================================
# 🎯 SELECT MATCH
# =========================================================
matches = [
    f"{r.HomeTeam} vs {r.AwayTeam} | {r.Div} | {r.Date.strftime('%d/%m')}"
    for _, r in df.iterrows()
]

selected = st.selectbox("Selecciona partido", matches)
row = df.iloc[matches.index(selected)]

analysis = analyze(row.H, row.D, row.A)

home = row.HomeTeam
away = row.AwayTeam

# =========================================================
# 🎯 OUTPUT
# =========================================================
st.header(f"{home} vs {away}")
st.write(f"🌍 {row.Div}")
st.write(f"📅 {row.Date.strftime('%d/%m/%Y')}")

st.subheader("💰 Odds")
st.write(f"{row.H} | {row.D} | {row.A}")

# =========================================================
# 🧠 ANALISIS DETALLADO
# =========================================================
h, d, a = analysis["real_probs"]

st.subheader("📊 Probabilidades Reales")
st.write(f"Home: {round(h*100,1)}%")
st.write(f"Draw: {round(d*100,1)}%")
st.write(f"Away: {round(a*100,1)}%")

st.subheader("🧠 Market Structure")
st.write(f"{analysis['structure']} → {analysis['bias']}")

st.subheader("⚡ Expected Tempo")
st.write(analysis["tempo"])

st.subheader("💰 Value Insight")
st.write(analysis["value"])

st.subheader("🎯 Trading Setups")
for s in analysis["setups"]:
    st.write(f"👉 {s}")

st.subheader("🎭 Match Scenarios")
for s in analysis["scenarios"]:
    st.write(f"- {s}")

st.subheader("⚠️ Risks")
for r in analysis["risks"]:
    st.write(f"- {r}")

# =========================================================
# 🧠 RESUMEN TIPO GENIE (LO IMPORTANTE)
# =========================================================
st.subheader("🧠 Professional Summary")

st.markdown(f"""
This fixture between **{home} and {away}** is structured as a **{analysis['structure']}** game.

From a market perspective, this implies **{analysis['bias']}**, meaning the price is likely to react to any confirmation of that dominance.

The expected tempo is **{analysis['tempo']}**, which suggests how quickly opportunities may appear.

In terms of value, the current read indicates:  
👉 **{analysis['value']}**

---

### 🎯 Trading Perspective

This is not about predicting the winner.

It is about understanding:

- Where pressure will come from  
- When the market is likely to react  
- How price inefficiencies may appear  

---

### 📈 Key Insight

The best opportunities will arise when:

- The match confirms its expected structure  
- The market reacts slower than the actual game dynamics  

---

👉 Your edge is not prediction.  
👉 Your edge is execution.
""")

st.subheader("⭐ Confidence")
st.write(f"{analysis['confidence']} / 10")
