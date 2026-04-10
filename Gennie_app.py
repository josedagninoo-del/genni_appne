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
