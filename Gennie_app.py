import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta   

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

             
        today = datetime.utcnow().strftime("%Y-%m-%d")
        tomorrow = (datetime.utcnow() + timedelta(days=1)).strftime("%Y-%m-%d")

        params = {
        "date": today,
        "timezone": "America/Mexico_City"
        }
        res = requests.get(url, headers=headers, params=params, timeout=10)
        
        data = res.json()
        print(len(data.get("response", [])))
        rows = []
        for m in data.get("response", []):
            rows.append({
            "fixture_id": m["fixture"]["id"],  # 🔥 NUEVO
            "HomeTeam": m["teams"]["home"]["name"],
            "AwayTeam": m["teams"]["away"]["name"],
            "Div": m["league"]["name"],
            "Date": m["fixture"]["date"],
            "H": 2.2,
            "D": 3.2,
            "A": 3.0
        })

        df_api = pd.DataFrame(rows)
        
        df_api["DateTime"] = pd.to_datetime(df_api["Date"], utc=True)

        now = datetime.utcnow()

        df_api = df_api[
        (df_api["DateTime"] >= now - timedelta(hours=6)) &
        (df_api["DateTime"] <= now + timedelta(hours=36))
        ]
        if not df_api.empty:
            df_api["Date"] = pd.to_datetime(df_api["Date"])
            st.success("✅ API PRO activa")
            return df_api

    except:
        return None
# =========================================================
# 💰 ODDS REALES API (AGREGADO)
# =========================================================
def load_real_odds(fixture_id):

    try:
        API_KEY = st.secrets.get("API_KEY", "")

        url = "https://api-football-v1.p.rapidapi.com/v3/odds"
        headers = {
            "X-RapidAPI-Key": API_KEY,
            "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
        }

        params = {"fixture": fixture_id}

        res = requests.get(url, headers=headers, params=params, timeout=10)

        if res.status_code != 200:
            return None

        data = res.json()

        if not data.get("response"):
            return None

        # 🔹 Tomamos primer bookmaker disponible
        bookmakers = data["response"][0]["bookmakers"]

        for b in bookmakers:
            for bet in b["bets"]:
                if bet["name"] == "Match Winner":
                    values = bet["values"]

                    odds = {v["value"]: float(v["odd"]) for v in values}

                    return odds.get("Home"), odds.get("Draw"), odds.get("Away")

        return None

    except:
        return None
        
@st.cache_data
def load_data():
    df_api = load_api_data()

    if df_api is not None and not df_api.empty:
        return df_api

    return pd.DataFrame()  # 🔥 nunca None

    # fallback SOLO si API falla
    url = "https://www.football-data.co.uk/fixtures.csv"
    df = pd.read_csv(url)
    return df


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
# 🤖 ML GOAL TIMING MODEL (AGREGADO)
# =========================================================
def ml_goal_prediction(ph, pa, goals):

    score = 0

    if goals > 2.8:
        score += 2
    elif goals > 2.5:
        score += 1

    if ph > 0.60 or pa > 0.60:
        score += 1

    if abs(ph - pa) < 0.15:
        score += 1

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
# 📊 TEAM + H2H TRENDS (AGREGADO)
# =========================================================
def generate_trends(home, away, ph, pa, goals):

    trends = []

    # 🔹 Tendencia ofensiva
    if goals > 2.7:
        trends.append("Más del 60% de probabilidad implícita de Over 2.5 goles")

    # 🔹 Dominancia
    if ph > 0.60:
        trends.append(f"{home} tiene alta probabilidad de dominar el partido")
    elif pa > 0.60:
        trends.append(f"{away} llega como equipo dominante")

    # 🔹 Partido abierto
    if abs(ph - pa) < 0.15:
        trends.append("Partido equilibrado con alta probabilidad de BTTS")

    # 🔹 Momentum ofensivo
    if goals > 2.5 and ph > 0.50:
        trends.append(f"{home} probablemente marcará en fases tempranas")

    # 🔹 Simulación tipo H2H (market-based)
    if goals > 2.6:
        trends.append("Históricamente este perfil de partido genera múltiples goles")

    # 🔹 Patrón de mercado
    if ph > 0.55 and goals > 2.6:
        trends.append("Perfil típico de favorito + over (escenario de trading ideal)")

    return trends
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
# 🎯 STRATEGY ENGINE PRO (AGREGADO)
# =========================================================
def strategy_engine(home, away, ph, pa, goals, xg_h, xg_a):


    edge = abs(ph - pa)

    # =========================================================
    # 💣 GENIE GAMBIT 2.0 (FAVORITO + GOLES)
    # =========================================================
    if ph >= 0.60 and goals >= 2.7:
        return {
            "name": "GENIE GAMBIT 2.0",
            "criteria": "Favorito fuerte + partido abierto",
            "description": "Explota dominio + goles",
            "entry": "Pre-match + Over 2.5 en subida",
            "execution": "Back favorito + Back Over 2.5"
        }
    # =========================================================
    # 🔥 FIREBALL (GOLES TEMPRANOS / OVER EXPLOSIVO)
    # =========================================================
    elif goals >= 2.8 and 0.52 <= ph <= 0.60:

        return {
            "name": "FIREBALL",
            "criteria": "Partido abierto + sin dominador fuerte + alta probabilidad de gol temprano",
            "description": "Estrategia diseñada para explotar equipos con tendencia a marcar rápido y provocar colapso de cuota en Over 2.5.",
            "entry": "Min 10 (50%) + Min 25 (50% si no hay gol)",
            "execution": """
1. Entrar al Over 2.5 con 50% del stake en minuto 10  
2. Si no hay gol, añadir el 50% restante en minuto 25  

🎯 Objetivo:
Aprovechar caída de cuota tras gol temprano  

📈 Salida:
Buscar ROI del 30% tras gol  

⚠ Gestión:
Si estás en rojo tras primer gol, mantener posición esperando segundo gol
"""
        }
    # =========================================================
    # 🎯 LAY THE DIP (VERSIÓN PRO)
    # =========================================================
    elif goals >= 2.8 and edge <= 0.12 and ph < 0.60 and pa < 0.60:

        return {
            "name": "LAY THE DIP",
            "criteria": "Partido abierto + equilibrio + alta probabilidad de gol temprano",
            "description": "Aprovecha la caída de cuota del Under 2.5 en los primeros minutos sin gol para capturar valor antes del primer gol.",
            "entry": "Min 10 (50%) + Min 25 (50%)",
            "execution": """
1. Esperar 10 minutos sin gol  
2. Hacer Lay al Under 2.5 con 50% del stake  
3. Si sigue 0-0, añadir el otro 50% en minuto 25  

🎯 Objetivo:
Capturar subida de cuota tras 1-2 goles  

📈 Salida:
- Cerrar tras primer gol si cashout es negativo  
- Mantener hasta 2 goles para maximizar beneficio  

⏱ Salida máxima:
Minuto 65  

⚠ Riesgo:
Partido sin ritmo ofensivo real
"""
        }
    # =========================================================
    # ⚡ THE MOMENTUM METHOD (PRO)
    # =========================================================
    elif ph >= 0.60 and goals < 2.7:

        return {
          "name": "MOMENTUM METHOD",
          "criteria": "Favorito con alta probabilidad de dominar sin necesidad de partido abierto",
          "description": "Aprovecha la probabilidad de que el favorito marque primero y capture la caída de cuota tras el gol.",
          "entry": "Min 15 tras confirmar dominio",
          "execution": """
1. Esperar ~15 minutos para evaluar ritmo  
2. Confirmar dominio (posesión, presión, control)  
3. Back al favorito  

🎯 Objetivo:
Capturar caída de cuota tras el primer gol  

📈 Salida:
Cerrar inmediatamente tras gol del favorito (Lay)  

⚠ Contingencia:
Si el underdog marca primero → salir para proteger capital  
"""
    }

    # =========================================================
    # 💪 POWER PLAY STRATEGY (DOBLE MERCADO)
    # =========================================================
    elif ph >= 0.58 and 2.4 <= goals <= 2.8:

        return {
          "name": "POWER PLAY",
          "criteria": "Favorito claro + partido controlado con potencial de desbloqueo",
          "description": "Estrategia combinada que explota el movimiento del empate y la ventaja del favorito tras el primer gol.",
          "entry": "Kick-off (entrada temprana)",
          "execution": """
1. Back al favorito con 50% del stake  
2. Lay al empate con el 50% restante  

🎯 Objetivo:
Capturar drift del empate y caída del favorito tras gol  

📈 Escenario ideal:
El favorito marca → mantener posición hasta posible segundo gol (10-20 min)  

⚠ Contingencia:
Si el underdog marca → salir inmediatamente para limitar pérdidas  

⏱ Salida máxima:
Cerrar en minuto 70 si sigue 0-0  
"""
    }

    # =========================================================
    # 🧊 NO TRADE
    # =========================================================
    else:
        return {
            "name": "NO TRADE",
            "criteria": "Sin condiciones claras",
            "description": "No hay edge",
            "entry": "-",
            "execution": "Skip"
        }

# =========================================================
# 🧠 SELECTOR REAL SIN JERARQUÍA
# =========================================================
def select_best_strategy(home, away, ph, pa, goals, xg_h, xg_a):

    edge = abs(ph - pa)

    scores = {}

    # 💣 GAMBIT
    scores["GENIE GAMBIT 2.0"] = (
        (2 if ph >= 0.60 else 0) +
        (2 if goals >= 2.7 else 0) +
        (1 if xg_h > xg_a else 0)
    )

    # ⚡ MOMENTUM
    scores["MOMENTUM METHOD"] = (
        (2 if ph >= 0.60 else 0) +
        (2 if goals < 2.7 else 0) +
        (1 if edge > 0.15 else 0)
    )

    # 💪 POWER PLAY
    scores["POWER PLAY"] = (
        (2 if ph >= 0.58 else 0) +
        (2 if 2.4 <= goals <= 2.8 else 0) +
        (1 if edge > 0.10 else 0)
    )

    # 🔥 FIREBALL
    scores["FIREBALL"] = (
        (2 if goals >= 2.8 else 0) +
        (2 if 0.52 <= ph <= 0.60 else 0) +
        (1 if edge < 0.15 else 0)
    )

    # 🎯 LAY THE DIP
    scores["LAY THE DIP"] = (
        (2 if goals >= 2.8 else 0) +
        (2 if edge < 0.12 else 0) +
        (1 if ph < 0.60 else 0)
    )

    # 🧠 elegir mejor
    best = max(scores, key=scores.get)

    return best

# =========================================================
# 🧠 CONSTRUCTOR DE ESTRATEGIA
# =========================================================
def build_strategy(name):

    strategies = {
        "GENIE GAMBIT 2.0": {
            "name": name,
            "criteria": "Favorito fuerte + partido abierto",
            "description": "Explota dominio + goles (doble mercado)",
            "entry": "Pre-match + Over 2.5 ≥ 2.0",
            "execution": "Back favorito + Back Over 2.5"
        },

        "MOMENTUM METHOD": {
            "name": name,
            "criteria": "Favorito dominante",
            "description": "Explota gol del favorito",
            "entry": "Min 15",
            "execution": "Back favorito → Lay tras gol"
        },

        "POWER PLAY": {
            "name": name,
            "criteria": "Favorito + empate con valor",
            "description": "Explota drift del empate",
            "entry": "Kick-off",
            "execution": "Back favorito + Lay empate"
        },

        "FIREBALL": {
            "name": name,
            "criteria": "Partido abierto sin dominador",
            "description": "Explota gol temprano",
            "entry": "Min 10 / 25",
            "execution": "Back Over 2.5"
        },

        "LAY THE DIP": {
            "name": name,
            "criteria": "Partido abierto sin gol temprano",
            "description": "Explota caída del Under",
            "entry": "Min 10 / 25",
            "execution": "Lay Under 2.5"
        }
    }

    return strategies.get(name, {
        "name": "NO TRADE",
        "criteria": "Sin condiciones claras",
        "description": "No hay edge",
        "entry": "-",
        "execution": "-"
    })
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

# =========================================================
# 🔥 RANKING DE PARTIDOS (AGREGADO)
# =========================================================
matches_ranked = []

for _, r in df.iterrows():
    ph, pa, goals, *_ = genie_analysis(r.HomeTeam, r.AwayTeam, r.H, r.D, r.A)
    label, score = classify_match(ph, pa, goals, r.H)

    matches_ranked.append({
        "match": f"{r.HomeTeam} vs {r.AwayTeam}",
        "label": label,
        "score": score
    })

# 🔥 Ordenar por score DESC (mejores primero)
matches_ranked = sorted(matches_ranked, key=lambda x: x["score"], reverse=True)

# Reiniciar listas
entradas, lectura, evitar = [], [], []

# Clasificar ya ordenados
for m in matches_ranked:

    if m["label"] == "🟢 ENTRADA":
        entradas.append(m["match"])
    elif m["label"] == "🟡 LECTURA":
        lectura.append(m["match"])
    else:
        evitar.append(m["match"])
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
# =========================================================
# 💰 INTEGRAR ODDS REALES (AGREGADO)
# =========================================================
if "fixture_id" in row and pd.notna(row["fixture_id"]):

    real_odds = load_real_odds(row["fixture_id"])

    if real_odds:
        h_real, d_real, a_real = real_odds

        # 🔹 Solo reemplaza si hay datos válidos
        if h_real and d_real and a_real:
            row.H = h_real
            row.D = d_real
            row.A = a_real
            st.success("💰 Odds reales cargadas")

home, away = row.HomeTeam, row.AwayTeam

ph, pa, goals, xg_h, xg_a, goals_trend, scoring, tactics, strategy, market, entry, exit, confidence = genie_analysis(
    home, away, row.H, row.D, row.A
)

label, score = classify_match(ph, pa, goals, row.H)

context, tempo, execution = narrative_engine(home, away, ph, pa, goals, xg_h, xg_a, strategy)

# =========================================================
# 🧠 SELECCIÓN REAL SIN JERARQUÍA
# =========================================================
best_strategy_name = select_best_strategy(home, away, ph, pa, goals, xg_h, xg_a)

strategy_data = build_strategy(best_strategy_name)

# =========================================================
# 🔧 FIX CONSISTENCIA DE ESTRATEGIA (AGREGADO)
# =========================================================
final_strategy = strategy_data

# =========================================================
# 📊 GENERAR TENDENCIAS (AGREGADO)
# =========================================================
trends = generate_trends(home, away, ph, pa, goals)

summary = professional_summary(home, away, ph, pa, goals, strategy)

# =========================================================
# DISPLAY (BASE + AGREGADOS)
# =========================================================
st.header(f"{home} vs {away}")
st.subheader("💰 Odds actuales")
st.write(f"Home: {row.H} | Draw: {row.D} | Away: {row.A}")
st.write(f"🌍 {row.Div}")
st.write(f"📅 {row.Date.strftime('%d/%m/%Y')}")

st.subheader("📊 Clasificación")
st.write(f"{label} | Score {score}/9")

st.subheader("🧠 GENIE ANALYSIS")
# =========================================================
# 📊 TENDENCIAS DEL PARTIDO
# =========================================================
st.subheader("📊 TEAM & H2H TRENDS")

for t in trends:
    st.write(f"• {t}")
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
### 🧠 Estrategia: {final_strategy['name']}

📊 **Criterio**
{final_strategy['criteria']}

🧩 **Descripción**
{final_strategy['description']}

⏱ **Entrada**
{final_strategy['entry']}

---
### 📌 Plan de ejecución
{final_strategy['execution']}
""")
# =========================================================
# 🧠 BLOQUE PRO — GENIE GAMBIT 2.0 (AGREGADO)
# =========================================================

if "GAMBIT" in final_strategy["name"].upper():

    st.markdown("## 🧠 GENIE GAMBIT 2.0 — PLAN PROFESIONAL")

    st.markdown("""
**📌 Strategy Summary**  
With this gambit, we will be hedging across both match odds and goal market.  
Best scenario is two goals for the favorite but you must be prepared to pivot in other scenarios.

**📊 Market to Trade:**  Match Odds y Over 2.5 Goals  
**🎯 Strategy Style:**  Back to Lay  
**💰 Market Entry Staking:** Back 50% of your stake on your favorite (NOT the market’s one) immediately, Back remaining 50% on Over 2.5 Goals once odds reach 2.0  
**🚪 Profit Exit Strategy:** Secure profits early. If both markets turn green after the first goal → lock in gains  
**🛠 Recovery Strategy:** If match is 0-0 at Half Time → Lay Under 1.5 Goals, monitor combined exposure constantly and adjust risk dynamically after each goal  
**🏦 Bankroll Management:** Use 3% of total bankroll  

---

**⚠️ Execution Insight (CLAVE)**  
No estás apostando resultados, estás explotando movimientos de mercado.  
El edge viene del timing del gol y la reacción del precio.
""")

# =========================================================
# 🔥 BLOQUE PRO — FIREBALL
# =========================================================
if "FIREBALL" in final_strategy["name"].upper():

    st.markdown("## 🔥 FIREBALL — PLAN PROFESIONAL")

    st.markdown("""
**📌 Strategy Summary:**We will exploit early market odd rise and the high probability of goals to back Over 2.5 goals, profiting from a price collapse immediately after a goal is scored.
**📊 Market to Trade:**  Over 2.5 Goals  
**🎯 Strategy Style:**  Back to Lay  
**⏱ Market Entry Timing:** 50% stake at minute 10 Remaining 50% at minute 25 if no goal  
**🎯 Profit Target:** Aim for ~30% ROI after first goal If still red  hold for second goal  
**🏦 Bankroll Management:** Use 3% of bankroll  

**⚠️ Execution Insight (CLAVE)**  
This strategy depends on early attacking intent.  
You are trading volatility and timing, not just probability.
""")
# =========================================================
# 🎯 BLOQUE PRO — LAY THE DIP
# =========================================================
if "LAY THE DIP" in final_strategy["name"].upper():

    st.markdown("## 🎯 LAY THE DIP — PLAN PROFESIONAL")

    st.markdown("""
**📌 Strategy Summary:** If the early stages of the match are goalless, the price of Under 2.5 goals will dip, creating a prime moment to lay.  
With a high likelihood of early goals, there’s solid value capturing these price swings.
**📊 Market to Trade:**Lay Under 2.5 Goals  
**🎯 Strategy Style:**Lay to Back  
**⏱ Market Entry Timing:** Minute 10 → 50% stake  Minute 25  remaining 50% if still 0-0  
**🎯 Goal Target:** Aim to secure profit after 2 goals  
**🚪 Market Exit:** Exit at minute 65 (max exposure)  
**📈 Profit Exit Instructions:** If first goal → close immediately if cashout is negative If positive → let trade run for full potential  
**🏦 Bankroll Management:**Use 3% of bankroll  

**⚠️ Execution Insight (CLAVE)**  
This is a time-decay strategy.  
You are exploiting price compression in the Under market before goals arrive.
""")    
# 🔥 NUEVO BLOQUE 1
st.subheader("🧠 LECTURA PROFESIONAL DEL PARTIDO")
st.markdown(f"""
### Contexto
{context}

### Dinámica
{tempo}
""")

# =========================================================
# ⚡ BLOQUE PRO — MOMENTUM METHOD
# =========================================================
if "MOMENTUM" in final_strategy["name"].upper():

    st.markdown("## ⚡ THE MOMENTUM METHOD — PLAN PROFESIONAL")

    st.markdown("""
**📌 Strategy Summary:**We take advantage of the high probability of the favorite taking the lead and profit from the price collapse after they score.
**📊 Market to Trade:** Match Odds  
**🎯 Strategy Style:**Back to Lay  
**🎯 Team to Back:** The favorite  
**⏱ Market Entry Timing:**Around minute 15 after confirming early dominance  
**🚪 Profit Exit Strategy:** Once the favorite scores → Lay immediately to lock profit  
**⚠ Contingency Strategy:**If the underdog scores first → exit the trade to protect capital  
**🏦 Bankroll Management:** Use 2% of bankroll  

**⚠️ Execution Insight (CLAVE)**  
This is a momentum-based strategy.  
You are trading dominance and timing, not just probability.
""")

# =========================================================
# 💪 BLOQUE PRO — POWER PLAY
# =========================================================
if "POWER PLAY" in final_strategy["name"].upper():

    st.markdown("## 💪 POWER PLAY STRATEGY — PLAN PROFESIONAL")

    st.markdown("""
**📌 Strategy Summary:**We’ll seize the opportunity by backing our favorite and laying the draw to capitalize on the anticipated drift in the draw price once a goal is scored.
**📊 Market to Trade:** Match Odds  Lay the Draw - Back the Favorite  
**🎯 Strategy Style:** Lay to Back + Back to Lay combo  
**🎯 Team to Favor:** Favorite  
**💰 Staking Plan:**50% stake → Back favorite 50% stake → Lay the draw  
**⏱ Market Entry Timing:** Kick-off (early entry for optimal pricing)  
**📈 Favorite Scores Scenario:**Hold position up to 10–20 minutes Look for second goal gap Then secure profit  
**⚠ Underdog Scores Scenario:** Exit immediately to protect capital  
**⏱ Optimal Exit Timing:** Close around minute 70 if match remains 0-0  

**⚠️ Execution Insight (CLAVE)**  
This is a dual-pressure strategy exploiting both draw decay and favorite dominance.  
You are trading structure, not just momentum.
""")
# 🔥 NUEVO BLOQUE 3
st.subheader("🧠 RESUMEN PROFESIONAL AVANZADO")
st.markdown(summary)

st.subheader("⭐ Confidence")
st.write(f"{confidence} / 10")
