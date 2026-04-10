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
# 🧠 NUEVO: VALUE + ESTRATEGIA PRO
# =========================================================
def elite_insight(home, away, ph, pa, goals, h, a):

    # VALUE
    value = "No claro"
    if ph > 0.55 and h > 2.0:
        value = f"VALUE en {home}"
    elif pa > 0.45 and a > 2.2:
        value = f"VALUE en {away}"

    # ESTRATEGIAS AVANZADAS
    if goals > 2.8:
        strat = "🔥 Lay The Dip"
        desc = "Esperar sin gol → Lay Under cuando baje cuota"
    elif ph > 0.60:
        strat = "⚡ Momentum Trade"
        desc = f"Back {home} → salir tras gol"
    elif ph > 0.52 and goals > 2.5:
        strat = "💣 Genie Gambit"
        desc = "Favorito + Over 2.5"
    else:
        strat = "🎯 Goals Flow"
        desc = "Over / BTTS por dinámica abierta"

    return value, strat, desc

# =========================================================
# 🧠 NARRATIVA ELITE + PLAN DE EJECUCIÓN
# =========================================================
def narrative_engine(home, away, ph, pa, goals, xg_h, xg_a, strat, value):

    # ===== CONTEXTO NARRATIVO
    if ph > 0.60:
        dominance = f"{home} es claramente superior y debería imponer condiciones desde el inicio."
    elif pa > 0.55:
        dominance = f"{away} tiene ventaja estructural y puede controlar el ritmo del partido."
    else:
        dominance = "Partido equilibrado con potencial de intercambio constante."

    if goals > 2.8:
        tempo = "Se proyecta un partido de ritmo alto con múltiples situaciones de gol."
    elif goals > 2.4:
        tempo = "Ritmo medio con momentos de aceleración ofensiva."
    else:
        tempo = "Partido más táctico con menor volumen de ocasiones."

    # ===== LÓGICA DE MERCADO
    market_logic = f"""
El mercado está alineado con una probabilidad implícita donde:
- {home}: {round(ph*100,1)}%
- {away}: {round(pa*100,1)}%

Esto genera una estructura donde los movimientos de cuota estarán altamente influenciados por:
✔ Gol temprano  
✔ Dominio territorial inicial  
✔ Presión ofensiva sostenida  
"""

    # ===== EJECUCIÓN SEGÚN ESTRATEGIA
    if "Lay The Dip" in strat:
        execution = f"""
📌 PLAN OPERATIVO — LAY THE DIP

1. Esperar fase inicial (min 8–15) SIN gol.
2. Detectar caída de cuota en Under 2.5 (market complacency).
3. Ejecutar LAY cuando el mercado subestima el riesgo real de gol.

🎯 CLAVE:
El edge no está en el gol, sino en el DESAJUSTE de precio.

📈 GESTIÓN:
- Salida inmediata tras primer gol
- Si el gol no llega: cerrar en min 55–65

⚠ Riesgo:
Partido muerto / ritmo falso → salida rápida.
"""

    elif "Momentum" in strat:
        execution = f"""
📌 PLAN OPERATIVO — MOMENTUM TRADE

1. Esperar 10–15 min para validar dominio.
2. Confirmar presión (posesión + territorio).
3. BACK al favorito antes del gol.

🎯 CLAVE:
Entrar antes del movimiento fuerte de cuota.

📈 GESTIÓN:
- Salir tras gol (ideal)
- Si no domina → NO entrar

⚠ Riesgo:
Dominio falso → evitar entrada.
"""

    elif "Gambit" in strat:
        execution = f"""
📌 PLAN OPERATIVO — GENIE GAMBIT

1. Dividir stake:
   - 50% favorito
   - 50% Over 2.5
2. Buscar escenario de gol + control del favorito.

🎯 CLAVE:
Cobertura doble → dirección + goles.

📈 GESTIÓN:
- Green tras 1-0 o 2-0
- Ajuste si partido se abre

⚠ Riesgo:
Gol del underdog temprano.
"""

    else:
        execution = f"""
📌 PLAN OPERATIVO — GOALS FLOW

1. Esperar validación de ritmo (min 10–20)
2. Detectar intercambio ofensivo
3. Entrar en Over / BTTS

🎯 CLAVE:
Flujo de partido, no favorito.

📈 GESTIÓN:
- Salida tras 1–2 goles
- Reentrada posible si sigue presión

⚠ Riesgo:
Partido trabado / sin profundidad.
"""

    return dominance, tempo, market_logic, execution

# =========================================================
# 🧠 CLASIFICACIÓN (TUYA)
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
# 🚨 CONCLUSIÓN GLOBAL
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

value, elite_strat, strat_desc = elite_insight(home, away, ph, pa, goals, row.H, row.A)

# =========================================================
# 📊 DISPLAY FINAL (MEJORADO)
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

---

### 💰 VALUE
👉 {value}

---

### 🔥 ESTRATEGIA PRO
**{elite_strat}**

{strat_desc}
""")

st.subheader("🎯 ESTRATEGIA BASE")
st.markdown(f"""
Strategy: {strategy}  
Market: {market}  
Entry: {entry}  
Exit: {exit}  
""")

st.subheader("🧠 RESUMEN PROFESIONAL")

st.markdown(f"""
Este partido está clasificado como **{label}**.

- xG: {xg_h} vs {xg_a}
- Goles esperados: {round(goals,2)}

👉 El edge está en cómo reacciona el mercado, no en el resultado.

✔ Probabilidad implícita clara  
✔ Escenario táctico definido  
✔ Oportunidad de trading identificada  

🎯 Mejor enfoque:
**{elite_strat} + {strategy}**
""")

st.subheader("⭐ Confidence")
st.write(f"{confidence} / 10")
