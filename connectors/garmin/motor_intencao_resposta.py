"""
MOTOR 1 — Inferência de intenção da sessão + modelo carga-resposta individual
Determinístico. Classifica o que cada treino FOI (duro/moderado/fácil/recuperação)
a partir de tipo, duração, distribuição de zonas e carga interna; e compara a
resposta fisiológica observada (queda de Body Battery, FCrep, HRV no dia seguinte)
com o padrão histórico do próprio atleta.

Honestidade: nas primeiras semanas, o padrão individual ainda não existe.
O motor reporta explicitamente o grau de confiança conforme o N de dias.
"""

from datetime import date, timedelta


def _tempo_zonas_altas(zonas: dict) -> float:
    """Fração do tempo em Z4+Z5 (alta intensidade)."""
    if not zonas:
        return 0.0
    total = sum(zonas.values())
    if not total:
        return 0.0
    altas = zonas.get("Z4", 0) + zonas.get("Z5", 0)
    return altas / total


def inferir_intencao(atividade: dict) -> dict:
    """
    Infere a INTENÇÃO fisiológica provável de uma sessão a partir do que foi executado.
    Não há prescrição formal: a intenção é deduzida da estrutura da sessão.
    Retorna rótulo + justificativa + sinais usados.
    """
    familia = atividade.get("familia", "outro")
    dur = atividade.get("duracao_min") or 0
    zonas = atividade.get("tempo_por_zona_s") or {}
    frac_altas = _tempo_zonas_altas(zonas)
    fc_max = atividade.get("fc_max")
    deriva = (atividade.get("deriva") or {}).get("deriva_cardiaca_pct")

    rotulo = "indeterminado"
    justificativa = []

    if familia == "forca":
        rotulo = "forca"
        justificativa.append("sessão de força (estímulo neuromuscular, não aeróbio)")

    elif familia in ("corrida", "ciclismo", "cardio", "natacao"):
        # Classificação por distribuição de intensidade
        if frac_altas >= 0.15:
            rotulo = "duro_intervalado"
            justificativa.append(f"{round(frac_altas*100)}% do tempo em Z4-Z5 (alta intensidade)")
        elif frac_altas >= 0.05:
            rotulo = "moderado_limiar"
            justificativa.append(f"presença relevante de Z4-Z5 ({round(frac_altas*100)}%) sugere trabalho de limiar/tempo")
        else:
            # Predominância aeróbia baixa: distinguir base de recuperação por duração
            if dur >= 75:
                rotulo = "longo_aerobio"
                justificativa.append(f"{round(dur)} min majoritariamente aeróbio (base/longo)")
            elif dur >= 35:
                rotulo = "base_aerobia"
                justificativa.append(f"{round(dur)} min em intensidade aeróbia baixa (Z2)")
            else:
                rotulo = "recuperacao_curto"
                justificativa.append(f"sessão curta ({round(dur)} min) e leve (recuperação/destravamento)")

        if deriva is not None and deriva > 5 and rotulo in ("base_aerobia", "longo_aerobio"):
            justificativa.append(f"deriva cardíaca de {deriva}% em sessão que deveria ser estável")

    # Desempate causal: cruzar RPE/feel subjetivo com a estrutura objetiva
    rpe = atividade.get("rpe_borg")
    feel = atividade.get("feel")
    if rpe is not None:
        # Sessao objetivamente leve (Z2/recuperacao) mas RPE alto = sinal de fadiga/estresse
        if rotulo in ("base_aerobia", "recuperacao_curto") and rpe >= 6:
            justificativa.append(f"RPE {rpe}/10 desproporcionalmente alto para sessão leve — possível fadiga subjacente, sono ruim ou underfueling")
        # Sessao objetivamente dura mas RPE baixo = boa forma/frescor
        elif rotulo == "duro_intervalado" and rpe <= 4:
            justificativa.append(f"RPE {rpe}/10 baixo para sessão dura — bom estado de forma/frescor")
    if feel is not None and feel < 0:
        justificativa.append(f"sensação subjetiva negativa (feel {feel}) reportada")

    elif familia == "caminhada":
        rotulo = "recuperacao_curto"
        justificativa.append("caminhada (recuperação ativa)")

    return {
        "intencao_inferida": rotulo,
        "justificativa": "; ".join(justificativa) if justificativa else "dados insuficientes para inferir",
        "fracao_alta_intensidade": round(frac_altas, 2),
        "duracao_min": dur,
    }


def carga_do_dia(dados: dict, treino: dict) -> dict:
    """
    Resume a carga total do dia. Prioriza training_load real do Garmin e sRPE de
    Foster (carga interna validada); cai para peso por intenção se ausentes.
    """
    pesos = {
        "duro_intervalado": 9, "moderado_limiar": 6, "longo_aerobio": 6,
        "base_aerobia": 3, "recuperacao_curto": 1, "forca": 5, "indeterminado": 2,
    }
    atividades = treino.get("atividades", [])
    intencoes = []
    peso_total = 0
    training_load_total = 0
    srpe_total = 0
    rpe_valores = []
    feel_valores = []

    for a in atividades:
        inf = inferir_intencao(a)
        a["_intencao"] = inf
        intencoes.append(inf["intencao_inferida"])
        peso_total += pesos.get(inf["intencao_inferida"], 2)
        if a.get("training_load"):
            training_load_total += a["training_load"]
        if a.get("sRPE_foster"):
            srpe_total += a["sRPE_foster"]
        if a.get("rpe_borg") is not None:
            rpe_valores.append(a["rpe_borg"])
        if a.get("feel") is not None:
            feel_valores.append(a["feel"])

    return {
        "intencoes": intencoes,
        "peso_carga_dia": min(peso_total, 10),
        "training_load_total": round(training_load_total) if training_load_total else None,
        "sRPE_foster_total": srpe_total or None,
        "rpe_medio": round(sum(rpe_valores) / len(rpe_valores), 1) if rpe_valores else None,
        "feel_medio": round(sum(feel_valores) / len(feel_valores), 1) if feel_valores else None,
        "n_atividades": len(atividades),
        "calorias_ativas": dados.get("calorias_ativas"),
    }


def modelo_carga_resposta(historico_registros: list, dados_hoje: dict, peso_carga_ontem: float) -> dict:
    """
    Compara a resposta fisiológica de HOJE (após a carga de ontem) com o padrão
    individual: para um dado peso de carga, quanto a Body Battery costuma cair e
    como HRV/FCrep costumam responder no dia seguinte.

    Retorna confiança calibrada pelo N. Sem dados suficientes, diz isso.
    """
    n = len(historico_registros)

    # Coleta pares (peso_carga, resposta_dia_seguinte) do histórico
    amostras = []
    for r in historico_registros:
        pc = (r.get("_carga") or {}).get("peso_carga_dia")
        bb_min = r.get("body_battery_min")
        bb_max = r.get("body_battery_max")
        if pc is not None and bb_min is not None and bb_max is not None:
            amostras.append({"peso": pc, "queda_bb": bb_max - bb_min})

    if n < 14 or len(amostras) < 7:
        return {
            "confianca": "baixa",
            "status": "aprendizado",
            "mensagem": f"Modelo individual ainda em formação ({n} dias coletados). "
                        f"São necessárias ~2-3 semanas para estabelecer seu padrão carga-resposta. "
                        f"Até lá, a interpretação usa referências da literatura, não o seu baseline pessoal.",
            "n_dias": n,
        }

    # Padrão para cargas similares à de ontem (+-2)
    similares = [s["queda_bb"] for s in amostras if abs(s["peso"] - peso_carga_ontem) <= 2]
    if not similares:
        return {"confianca": "media", "status": "sem_referencia_para_esta_carga", "n_dias": n}

    queda_esperada = sum(similares) / len(similares)
    bb_max_hoje = dados_hoje.get("body_battery_max")
    bb_min_hoje = dados_hoje.get("body_battery_min")
    queda_hoje = (bb_max_hoje - bb_min_hoje) if (bb_max_hoje and bb_min_hoje) else None

    anomalia = None
    if queda_hoje is not None and queda_esperada:
        desvio = (queda_hoje - queda_esperada) / queda_esperada * 100
        if desvio > 40:
            anomalia = f"queda de bateria {round(desvio)}% MAIOR que o esperado para esta carga — resposta exagerada, possível fadiga subjacente"
        elif desvio < -40:
            anomalia = f"queda de bateria {round(abs(desvio))}% MENOR que o esperado — boa resiliência/adaptação"

    return {
        "confianca": "media" if n < 30 else "alta",
        "status": "modelo_ativo",
        "queda_bb_esperada_para_carga": round(queda_esperada),
        "queda_bb_observada": round(queda_hoje) if queda_hoje else None,
        "anomalia": anomalia,
        "n_dias": n,
    }
