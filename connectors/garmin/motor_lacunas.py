"""
MOTOR 5 — Identificação de lacunas e pedido ativo de dado
Quando o sistema não consegue desempatar hipóteses, identifica QUAL dado
específico fecharia a lacuna e formula um pedido objetivo ao atleta.

Transforma o atleta em coletor ativo dos dados que faltam — sem fricção diária,
só quando há uma ambiguidade real que um dado pontual resolveria.
"""


def identificar_lacunas(exclusoes: list, dados: dict, treino: dict) -> list:
    """
    Varre as análises de exclusão causal e o estado dos dados para achar
    lacunas acionáveis. Cada lacuna vira um pedido específico e justificado.
    """
    lacunas = []

    # Lacuna 1: exclusão causal sobrou com underfueling/hidratação como hipótese
    for ex in exclusoes:
        if not ex.get("aplicavel"):
            continue
        sobreviventes = ex.get("causas_sobreviventes", [])
        if any("underfueling" in s or "hidrata" in s for s in sobreviventes):
            lacunas.append({
                "tipo": "fueling_hidratacao",
                "contexto": ex.get("achado"),
                "dado_que_falta": "peso corporal antes e depois do treino + ingestão de carboidrato/fluidos durante",
                "pedido": "No próximo treino longo, pese-se antes e depois e anote o que ingeriu. "
                          "Perda >2% do peso indica desidratação; isso desempata a causa da deriva cardíaca.",
                "prioridade": "alta" if ex.get("conclusao_provavel") else "media",
            })
        # Multiplas causas sobreviventes ambientais sem dado de clima
        if len(sobreviventes) >= 2 and "calor/ambiente" in sobreviventes and dados.get("temperatura_c") is None:
            lacunas.append({
                "tipo": "clima_ausente",
                "contexto": ex.get("achado"),
                "dado_que_falta": "temperatura/umidade do treino (Garmin às vezes não sincroniza)",
                "pedido": "O dado de clima do treino não veio. Se foi quente, isso explicaria a deriva — registre a condição mentalmente.",
                "prioridade": "baixa",
            })

    # Lacuna 2: RPE não registrado em sessão relevante
    for ativ in treino.get("atividades", []):
        if ativ.get("familia") in ("corrida", "ciclismo", "natacao") and ativ.get("rpe_borg") is None:
            dur = ativ.get("duracao_min") or 0
            if dur >= 30:  # só pede para sessões com substância
                lacunas.append({
                    "tipo": "rpe_ausente",
                    "contexto": f"{ativ.get('nome') or ativ.get('tipo')} ({round(dur)} min) sem RPE registrado",
                    "dado_que_falta": "RPE da sessão (0-10) no relógio após o treino",
                    "pedido": "Registre o RPE no relógio ao terminar o treino (2 toques). "
                              "Ele é o que permite distinguir fadiga de bom condicionamento — o relógio sozinho não vê isso.",
                    "prioridade": "media",
                })
                break  # um pedido de RPE por dia basta

    # Lacuna 3: HRV ausente por falha de uso noturno
    if dados.get("hrv_rmssd_noturno") is None and dados.get("sono_total_min"):
        lacunas.append({
            "tipo": "hrv_ausente",
            "contexto": "houve sono registrado mas sem leitura de HRV noturna",
            "dado_que_falta": "uso do relógio durante a noite com sensor ativo",
            "pedido": "A HRV noturna não foi captada apesar do sono registrado. "
                      "Verifique se o relógio está sendo usado a noite com pulseira firme — é a métrica central de recuperação.",
            "prioridade": "media",
        })

    # Dedup por tipo
    vistos = set()
    unicas = []
    for l in lacunas:
        if l["tipo"] not in vistos:
            vistos.add(l["tipo"])
            unicas.append(l)
    return unicas
