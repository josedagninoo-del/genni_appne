import streamlit as st
import pandas as pd
from datetime import datetime
import requests

st.set_page_config(layout="wide")
st.title("🔥 GENIE PRO REAL — ELITE")

# =========================================================
# 📡 API DATA
# =========================================================
def load_api_data():
    try:
        API_KEY = st.secrets.get("API_KEY", "")
        url = "https://v3.football.api-sports.io/fixtures"
        headers = {"x-apisports-key": API_KEY}

        today = datetime.utcnow().strftime("%Y-%m-%d")

        params = {
            "date": today,
            "timezone": "America/Mexico_City"
        }

        res = requests.get(url, headers=headers, params=params, timeout=10)
        if res.status_code != 200:
            return None

        data = res.json()
        rows = []

        for m in data.get("response", []):
            rows.append({
                "fixture_id": m["fixture"]["id"],
                "HomeTeam": m["teams"]["home"]["name"],
                "AwayTeam": m["teams"]["away"]["name"],
                "Div": m["league"]["name"],
                "Date": m["fixture"]["date"],
                "H": 2.2,
                "D": 3.2,
                "A": 3.0
            })

        df_api = pd.DataFrame(rows)

        if not df_api.empty:
            df_api["Date"] = pd.to_datetime(df_api["Date"], utc=True)
            return df_api

    except:
        return None


# =========================================================
# 💰 ODDS REALES
# =========================================================
@st.cache_data(ttl=300)
def load_all_odds():
    try:
        API_KEY = st.secrets.get("API_KEY", "")
        url = "https://v3.football.api-sports.io/odds"
        headers = {"x-apisports-key": API_KEY}

        today = datetime.utcnow().strftime("%Y-%m-%d")
        params = {"date": today}

        res = requests.get(url, headers=headers, params=params, timeout=10)
        if res.status_code != 200:
            return {}

        data = res.json()
        odds_map = {}

        for match in data.get("response", []):
            fid = match["fixture"]["id"]
            odds_map[fid] = {}

            for b in match.get("bookmakers", []):
                for bet in b.get("bets", []):

                    if bet.get("name") == "Match Winner":
                        for v in bet.get("values", []):
                            odds_map[fid][v["value"].lower()] = float(v["odd"])

                    elif bet.get("name") == "Goals Over/Under":
                        for v in bet.get("values", []):
                            if v["value"] == "Over 2.5":
                                odds_map[fid]["over25"] = float(v["odd"])
                            elif v["value"] == "Under 2.5":
                                odds_map[fid]["under25"] = float(v["odd"])

        return odds_map

    except:
        return {}


# =========================================================
# 📥 DATA
# =========================================================
df = load_api_data()
odds_map = load_all_odds()

df = df[df["fixture_id"].isin(odds_map.keys())]

if df.empty:
    st.error("No hay partidos con odds reales")
    st.stop()


# =========================================================
# 🧠 ENGINE (MEJORADO)
# =========================================================
def genie_analysis(home, away, h, d, a, attack_factor=1.0, over25=None, under25=None):

    imp_h = 1 / h
    imp_d = 1 / d
    imp_a = 1 / a
    overround = imp_h + imp_d + imp_a

    ph = imp_h / overround
    pa = imp_a / overround

    scaled_attack = 1 + (attack_factor - 1) * 0.55

    # 🔥 MARKET GOALS REAL
    market_goals = 2.4

    if over25 and under25:
        prob_over = 1 / over25
        prob_under = 1 / under25
        total = prob_over + prob_under
        prob_over /= total

        market_goals = 2.2 + (prob_over * 1.2)

    total_goals = market_goals * scaled_attack

    xg_home = min(round(total_goals * ph, 2), 3.8)
    xg_away = min(round(total_goals * pa, 2), 3.8)

    confidence = round((1 - (overround - 1)) * 10, 2)

    return ph, pa, total_goals, xg_home, xg_away, confidence


# =========================================================
# 🧠 STRATEGY SELECTOR (ÚNICO)
# =========================================================
def select_best_strategy(ph, pa, goals):

    edge = abs(ph - pa)

    if ph >= 0.60 and goals >= 2.7:
        return "GENIE GAMBIT 2.0"

    elif goals >= 2.8 and 0.52 <= ph <= 0.60:
        return "FIREBALL"

    elif goals >= 2.8 and edge <= 0.12:
        return "LAY THE DIP"

    elif ph >= 0.60 and goals < 2.7:
        return "MOMENTUM METHOD"

    elif ph >= 0.58 and 2.4 <= goals <= 2.8:
        return "POWER PLAY"

    return "NO TRADE"


# =========================================================
# 🔥 RANKING
# =========================================================
matches_ranked = []

for _, r in df.iterrows():

    real = odds_map[r["fixture_id"]]

    h = real.get("home")
    d = real.get("draw")
    a = real.get("away")
    over25 = real.get("over25")
    under25 = real.get("under25")

    if not h or not d or not a:
        continue

    # 🔥 market context
    market_goals = 2.4

    if over25 and under25:
        prob_over = 1 / over25
        prob_under = 1 / under25
        total = prob_over + prob_under
        prob_over /= total

        market_goals = 2.2 + (prob_over * 1.2)

    attack_factor = market_goals / 2.4

    ph, pa, goals, _, _, _ = genie_analysis(
        r.HomeTeam, r.AwayTeam, h, d, a, attack_factor, over25, under25
    )

    edge = abs(ph - pa)

    strategy = select_best_strategy(ph, pa, goals)

    priority = (edge * 8) + (goals * 1.5) + (attack_factor * 2)

    if abs(h - a) < 0.15:
        priority -= 2

    matches_ranked.append({
        "match": f"{r.HomeTeam} vs {r.AwayTeam}",
        "priority": priority,
        "strategy": strategy
    })


matches_ranked = sorted(matches_ranked, key=lambda x: x["priority"], reverse=True)

st.subheader("🔥 TOP PARTIDOS")

for m in matches_ranked[:10]:
    st.write(m)
