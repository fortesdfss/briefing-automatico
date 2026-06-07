"""
MOTOR 3 — Exclusão causal estruturada
Quando há um achado anômalo (ex: deriva cardíaca alta numa sessão que deveria
ser estável), roda uma árvore de eliminação sobre os dados disponíveis para
DESCARTAR causas e isolar a(s) provável(is). Determinístico e auditável.

NÃO inventa diagnóstico. Produz: causas descartadas (com o dado que descartou),
causas sobreviventes, e o que confirmaria cada sobrevivente.
"""


def analisar_deriva_cardiaca(atividade: dict, contexto_recuperacao: dict) -> dict:
    """
    Árvore de exclusão para deriva cardíaca elevada (>5%) em sessão aeróbia.
    Causas candidatas (literatura): calor/ambiente, terreno, esforço excessivo
    (saída agressiva), desidratação, underfueling, fadiga residual.
    """
    deriva = (atividade.get("deriva") or {}).get("deriva_cardiaca_pct")
    familia = atividade.get("familia")

    # Só faz sentido para sessões aeróbias contínuas com deriva relevante
    if familia not in ("corrida", "ciclismo") or deriva is None or deriva <= 5:
        return {"aplicavel": False}

    descartadas = []
    sobreviventes = []
    confirmacao = {}

    # 1. CALOR / AMBIENTE
    temp = atividade.get("temperatura_c")
    umid = atividade.get("umidade_pct")
    if temp is not None:
        if temp < 22 and (umid is None or umid < 70):
            descartadas.append({
                "causa": "calor/ambiente",
                "descartado_por": f"temperatura amena ({temp}°C) e umidade não-crítica",
            })
        else:
            sobreviventes.append("calor/ambiente")
            confirmacao["calor/ambiente"] = f"temperatura de {temp}°C compatível com estresse térmico"
    # se temp ausente, fica como indeterminada (não descarta nem confirma)

    # 2. TERRENO / PERFIL
    elev = atividade.get("elevacao_ganho_m")
    dist = atividade.get("distancia_km")
    if elev is not None and dist:
        ganho_por_km = elev / dist
        if ganho_por_km < 10:  # <10 m/km = terreno essencialmente plano
            descartadas.append({
                "causa": "terreno/perfil",
                "descartado_por": f"terreno plano ({round(ganho_por_km)} m/km de ganho)",
            })
        else:
            sobreviventes.append("terreno/perfil")
            confirmacao["terreno/perfil"] = f"ganho de {round(ganho_por_km)} m/km pode explicar oscilação de FC"

    # 3. ESFORÇO EXCESSIVO (saída agressiva)
    splits = atividade.get("splits") or []
    rpe = atividade.get("rpe_borg")
    intencao = (atividade.get("_intencao") or {}).get("intencao_inferida", "")
    if rpe is not None:
        # Se RPE bate com a intenção leve, esforço excessivo é improvável
        if intencao in ("base_aerobia", "longo_aerobio", "recuperacao_curto") and rpe <= 4:
            descartadas.append({
                "causa": "esforço excessivo",
                "descartado_por": f"RPE baixo ({rpe}/10) coerente com sessão leve — não houve saída agressiva percebida",
            })
        elif rpe >= 6:
            sobreviventes.append("esforço excessivo / saída agressiva")
            confirmacao["esforço excessivo"] = f"RPE {rpe}/10 alto sugere intensidade real acima do planejado"

    # 4. FADIGA RESIDUAL (usa contexto de recuperação do dia)
    hrv_desvio = contexto_recuperacao.get("hrv_desvio_baseline_pct")
    readiness = contexto_recuperacao.get("readiness_score")
    if hrv_desvio is not None or readiness is not None:
        fadiga_sinal = (hrv_desvio is not None and hrv_desvio < -8) or (readiness is not None and readiness < 40)
        if fadiga_sinal:
            sobreviventes.append("fadiga residual")
            partes = []
            if hrv_desvio is not None and hrv_desvio < -8:
                partes.append(f"HRV {hrv_desvio}% abaixo do baseline")
            if readiness is not None and readiness < 40:
                partes.append(f"readiness {readiness}")
            confirmacao["fadiga residual"] = "; ".join(partes)
        else:
            descartadas.append({
                "causa": "fadiga residual",
                "descartado_por": "HRV e readiness dentro do normal hoje",
            })

    # 5. UNDERFUELING (geralmente sobra quando as outras caem; precisa de dado externo)
    # Não há marcador direto no relógio. Fica como sobrevivente SE as causas
    # ambientais/esforço/fadiga foram descartadas e a deriva persiste.
    ambientais_descartadas = any(d["causa"] in ("calor/ambiente", "terreno/perfil") for d in descartadas)
    esforco_descartado = any(d["causa"] == "esforço excessivo" for d in descartadas)
    fadiga_descartada = any(d["causa"] == "fadiga residual" for d in descartadas)
    if ambientais_descartadas and esforco_descartado and fadiga_descartada:
        sobreviventes.append("underfueling / hidratação")
        confirmacao["underfueling / hidratação"] = "única hipótese plausível após exclusão das demais; confirmaria com peso pré/pós treino e registro de ingestão de carboidrato/fluidos"

    return {
        "aplicavel": True,
        "achado": f"deriva cardíaca de {deriva}% em sessão {intencao or 'aeróbia'}",
        "causas_descartadas": descartadas,
        "causas_sobreviventes": sobreviventes,
        "como_confirmar": confirmacao,
        "conclusao_provavel": sobreviventes[0] if len(sobreviventes) == 1 else None,
    }


def rodar_exclusao(treino: dict, dados: dict) -> list:
    """Roda exclusão causal sobre todas as atividades elegíveis do dia."""
    contexto = {
        "hrv_desvio_baseline_pct": dados.get("hrv_desvio_baseline_pct"),
        "readiness_score": dados.get("readiness_score"),
    }
    resultados = []
    for ativ in treino.get("atividades", []):
        analise = analisar_deriva_cardiaca(ativ, contexto)
        if analise.get("aplicavel"):
            analise["atividade"] = ativ.get("nome") or ativ.get("tipo")
            resultados.append(analise)
    return resultados
