"""
MOTOR 4 — Detecção de não-resposta / platô adaptativo
Correlaciona a trajetória da CARGA CRÔNICA com a trajetória de marcadores de
FITNESS (VO2máx, FCrep, eficiência FC-a-ritmo) ao longo de janelas de semanas.

Assinatura de não-resposta (literatura de responders/non-responders, Bouchard;
variabilidade de resposta ao treino): carga crônica subindo de forma consistente
SEM melhora dos marcadores de fitness por 4+ semanas. Distingue isso de:
- falta de carga (carga não subiu -> platô esperado)
- fadiga (fitness caiu junto com sobrecarga -> overreaching, não não-resposta)

Puramente observacional. Não infere causa biológica — apenas sinaliza o padrão.
"""

from statistics import mean


def _slope(valores: list) -> float:
    """Inclinação linear simples (variação por amostra)."""
    n = len(valores)
    if n < 3:
        return 0.0
    xs = list(range(n))
    mx, my = mean(xs), mean(valores)
    denom = sum((x - mx) ** 2 for x in xs)
    if denom == 0:
        return 0.0
    return sum((xs[i] - mx) * (valores[i] - my) for i in range(n)) / denom


def _serie_semanal(registros: list, campo: str, semanas: int = 6) -> list:
    """Agrega um campo em médias semanais (mais antigo -> recente)."""
    ordenados = sorted(registros, key=lambda x: x.get("data", ""))
    if not ordenados:
        return []
    # Agrupa em blocos de 7 dias a partir do mais recente
    blocos = []
    bloco_atual = []
    from datetime import date
    datas = [date.fromisoformat(r["data"]) for r in ordenados if r.get("data")]
    if not datas:
        return []
    fim = max(datas)
    for s in range(semanas):
        ini_janela = fim.toordinal() - (s + 1) * 7 + 1
        fim_janela = fim.toordinal() - s * 7
        vals = [r[campo] for r in ordenados
                if r.get("data") and r.get(campo) is not None
                and ini_janela <= date.fromisoformat(r["data"]).toordinal() <= fim_janela]
        if vals:
            blocos.append(mean(vals))
    blocos.reverse()  # antigo -> recente
    return blocos


def detectar_nao_resposta(registros: list) -> dict:
    """
    Precisa de pelo menos ~4 semanas de dados para ter sentido.
    Retorna status calibrado pelo histórico disponível.
    """
    n = len(registros)
    if n < 28:
        return {
            "aplicavel": False,
            "status": "dados_insuficientes",
            "mensagem": f"Detecção de não-resposta requer ~4+ semanas ({n} dias disponíveis). "
                        f"Esta análise ativa conforme o histórico cresce.",
        }

    # Trajetórias semanais
    carga = _serie_semanal(registros, "carga_cronica_28d", 6)
    if not carga:
        carga = _serie_semanal(registros, "calorias_ativas", 6)
    vo2 = _serie_semanal(registros, "vo2max", 6)
    fcrep = _serie_semanal(registros, "fc_repouso", 6)

    if len(carga) < 4:
        return {"aplicavel": False, "status": "series_curtas", "n_dias": n}

    slope_carga = _slope(carga)
    carga_media = mean(carga) if carga else 0
    carga_subindo = slope_carga > 0 and carga_media > 0 and (slope_carga * len(carga) / carga_media) > 0.05

    # Fitness melhorando? VO2 subindo OU FCrep descendo
    vo2_melhora = _slope(vo2) > 0 if len(vo2) >= 4 else None
    fcrep_melhora = _slope(fcrep) < 0 if len(fcrep) >= 4 else None

    sinais_fitness = [s for s in [vo2_melhora, fcrep_melhora] if s is not None]
    fitness_estagnado = sinais_fitness and not any(sinais_fitness)
    fitness_caindo = (len(vo2) >= 4 and _slope(vo2) < 0) and (len(fcrep) >= 4 and _slope(fcrep) > 0)

    # Classificação do padrão
    if not carga_subindo:
        padrao = "carga_estavel"
        interpretacao = "Carga crônica estável/baixa — eventual platô é esperado por ausência de estímulo progressivo, não por não-resposta."
    elif carga_subindo and fitness_caindo:
        padrao = "overreaching"
        interpretacao = "Carga subindo E fitness caindo — assinatura de sobrecarga/overreaching, não de não-resposta. Priorizar recuperação."
    elif carga_subindo and fitness_estagnado:
        padrao = "nao_resposta"
        interpretacao = ("Carga crônica em ascensão consistente nas últimas semanas SEM melhora dos marcadores de fitness "
                         "(VO2máx/FCrep estagnados). Padrão compatível com não-resposta ao estímulo atual — "
                         "considerar MUDAR a natureza do estímulo (distribuição de intensidade, modalidade, recuperação) "
                         "em vez de apenas aumentar volume. Hipótese observacional, não diagnóstico.")
    elif carga_subindo and (vo2_melhora or fcrep_melhora):
        padrao = "resposta_positiva"
        interpretacao = "Carga subindo e fitness acompanhando — adaptação positiva em curso."
    else:
        padrao = "indeterminado"
        interpretacao = "Padrão sem assinatura clara; seguir monitorando."

    return {
        "aplicavel": True,
        "status": "ativo",
        "padrao": padrao,
        "interpretacao": interpretacao,
        "trajetoria_carga": [round(c) for c in carga],
        "trajetoria_vo2": [round(v, 1) for v in vo2] if vo2 else None,
        "trajetoria_fcrep": [round(f) for f in fcrep] if fcrep else None,
        "n_semanas_analisadas": len(carga),
        "relevante": padrao in ("nao_resposta", "overreaching"),
    }
