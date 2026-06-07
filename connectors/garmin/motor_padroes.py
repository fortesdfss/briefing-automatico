"""
MOTOR 2 — Detecção de padrões longitudinais e tendências com significância
Determinístico. Transforma séries de métricas em SINAIS interpretáveis:
- sequências (ex: 3 dias seguidos de HRV abaixo do baseline)
- tendências direcionais com magnitude
- monotonia de carga (Foster)
- detecção de anomalias vs a própria variabilidade do atleta

Não interpreta clinicamente — só identifica os padrões que merecem atenção.
A interpretação fica com a camada do fisiologista (Claude).
"""

from datetime import date, timedelta
from statistics import mean, pstdev


def _serie(registros: list, campo: str) -> list:
    """Extrai série temporal (mais antigo->recente) de um campo, ignorando None."""
    vals = []
    for r in sorted(registros, key=lambda x: x.get("data", "")):
        v = r.get(campo)
        if v is not None:
            vals.append((r.get("data"), v))
    return vals


def _sequencia_abaixo(serie_valores: list, limite: float) -> int:
    """Conta quantos dos valores mais recentes consecutivos estão abaixo do limite."""
    cont = 0
    for v in reversed(serie_valores):
        if v < limite:
            cont += 1
        else:
            break
    return cont


def _tendencia(valores: list) -> dict:
    """Tendência linear simples (slope por dia) e magnitude relativa."""
    n = len(valores)
    if n < 4:
        return {"direcao": "indefinida", "n": n}
    xs = list(range(n))
    mx, my = mean(xs), mean(valores)
    denom = sum((x - mx) ** 2 for x in xs)
    if denom == 0:
        return {"direcao": "estavel", "n": n}
    slope = sum((xs[i] - mx) * (valores[i] - my) for i in range(n)) / denom
    variacao_total_pct = round(slope * (n - 1) / my * 100, 1) if my else None
    if abs(variacao_total_pct or 0) < 3:
        direcao = "estavel"
    elif slope > 0:
        direcao = "subindo"
    else:
        direcao = "descendo"
    return {"direcao": direcao, "variacao_pct_periodo": variacao_total_pct, "n": n}


def detectar_sinais(registros_historico: list, dados_hoje: dict) -> dict:
    """
    Roda a bateria de detecções e retorna apenas os sinais que merecem atenção.
    registros_historico: lista de dias anteriores (não inclui hoje).
    """
    todos = registros_historico + [dados_hoje]
    sinais = []
    n_dias = len(todos)

    # --- HRV: sequência abaixo do baseline + tendência da HRV7 ---
    hrv_desvios = _serie(todos, "hrv_desvio_baseline_pct")
    if hrv_desvios:
        vals = [v for _, v in hrv_desvios]
        seq_neg = _sequencia_abaixo(vals, -5)  # abaixo de -5% do baseline
        if seq_neg >= 3:
            sinais.append({
                "tipo": "hrv_supressao_sustentada",
                "severidade": "alta" if seq_neg >= 5 else "media",
                "detalhe": f"HRV abaixo do baseline (-5%) por {seq_neg} dias consecutivos",
                "acao_sugerida": "padrão de fadiga acumulada; priorizar recuperação se persistir",
            })
    hrv7 = _serie(todos, "hrv_media_7d")
    if len(hrv7) >= 7:
        t = _tendencia([v for _, v in hrv7[-14:]])
        if t["direcao"] == "descendo" and abs(t.get("variacao_pct_periodo") or 0) >= 8:
            sinais.append({
                "tipo": "hrv7_declinio",
                "severidade": "media",
                "detalhe": f"HRV7 em declínio: {t['variacao_pct_periodo']}% no período",
                "acao_sugerida": "monitorar; pode indicar carga acima do limiar de assimilação",
            })

    # --- FC repouso: elevação sustentada ---
    fcrep = _serie(todos, "fc_repouso")
    if len(fcrep) >= 7:
        vals = [v for _, v in fcrep]
        base = mean(vals[:-3]) if len(vals) > 3 else mean(vals)
        recentes = vals[-3:]
        if all(v >= base + 5 for v in recentes):
            sinais.append({
                "tipo": "fcrep_elevada",
                "severidade": "media",
                "detalhe": f"FC de repouso ~{round(mean(recentes))} bpm, ≥5 acima do baseline (~{round(base)})",
                "acao_sugerida": "sinal de recuperação incompleta, estresse ou início de doença",
            })

    # --- Sono: débito acumulado ---
    sono = _serie(todos, "sono_total_min")
    if len(sono) >= 5:
        ultimos = [v for _, v in sono[-5:]]
        media_min = mean(ultimos)
        if media_min < 420:
            sinais.append({
                "tipo": "debito_sono",
                "severidade": "alta" if media_min < 360 else "media",
                "detalhe": f"média de sono dos últimos {len(ultimos)} dias: {round(media_min)} min ({round(media_min/60,1)}h)",
                "acao_sugerida": "débito de sono compromete adaptação e imunidade",
            })

    # --- Carga: monotonia (Foster) na última semana ---
    cargas = _serie(todos, "calorias_ativas")
    if len(cargas) >= 7:
        ult7 = [v for _, v in cargas[-7:]]
        if mean(ult7) > 0 and pstdev(ult7) > 0:
            monotonia = mean(ult7) / pstdev(ult7)
            if monotonia > 2.0:
                sinais.append({
                    "tipo": "monotonia_alta",
                    "severidade": "media",
                    "detalhe": f"monotonia de carga {round(monotonia,1)} (>2.0): treino uniforme demais na semana",
                    "acao_sugerida": "introduzir contraste (dias mais fáceis e mais duros) reduz risco de doença/estagnação",
                })

    # --- Readiness: queda persistente ---
    readiness = _serie(todos, "readiness_score")
    if len(readiness) >= 4:
        vals = [v for _, v in readiness]
        if _sequencia_abaixo(vals, 40) >= 3:
            sinais.append({
                "tipo": "readiness_baixo_sustentado",
                "severidade": "alta",
                "detalhe": "Training Readiness < 40 por 3+ dias",
                "acao_sugerida": "prontidão cronicamente baixa; reavaliar volume/intensidade da microciclo",
            })

    return {
        "n_dias_historico": n_dias,
        "sinais": sinais,
        "n_sinais": len(sinais),
        "houve_mudanca_relevante": any(s["severidade"] == "alta" for s in sinais),
    }
