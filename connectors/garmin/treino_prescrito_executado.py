"""
CAMADA 1b — PRESCRITO vs EXECUTADO, com segmentação por modalidade
Puxa TODAS as atividades do dia (corrida, bike, natação, força...) com
métricas específicas de cada uma, e o workout prescrito quando houver.
Apenas números — sem interpretação.
"""

from datetime import date

# Famílias de modalidade para roteamento de análise
FAMILIA = {
    "running": "corrida", "treadmill_running": "corrida", "trail_running": "corrida",
    "indoor_running": "corrida",
    "cycling": "ciclismo", "indoor_cycling": "ciclismo", "virtual_ride": "ciclismo",
    "road_biking": "ciclismo", "mountain_biking": "ciclismo",
    "lap_swimming": "natacao", "open_water_swimming": "natacao",
    "strength_training": "forca", "indoor_cardio": "cardio", "cardio": "cardio",
    "hiit": "cardio", "walking": "caminhada",
}


def _min(segundos):
    return round(segundos / 60, 1) if segundos else None

def _pace_s_km(speed_m_s):
    return round(1000 / speed_m_s) if speed_m_s else None


def _deriva_cardiaca(splits):
    """Decoupling FC 1a vs 2a metade (para corrida/ciclismo aerobio)."""
    com_fc = [s for s in splits if s.get("fc_media")]
    if len(com_fc) < 4:
        return None
    meio = len(com_fc) // 2
    fc1 = sum(s["fc_media"] for s in com_fc[:meio]) / meio
    fc2 = sum(s["fc_media"] for s in com_fc[meio:]) / (len(com_fc) - meio)
    return {
        "fc_primeira_metade": round(fc1),
        "fc_segunda_metade": round(fc2),
        "deriva_cardiaca_pct": round((fc2 - fc1) / fc1 * 100, 1) if fc1 else None,
    }


def _analisar_atividade(client, ativ):
    """Extrai métricas específicas conforme a modalidade."""
    aid = ativ.get("activityId")
    tipo = ativ.get("activityType", {}).get("typeKey", "desconhecido")
    familia = FAMILIA.get(tipo, "outro")

    base = {
        "id": aid,
        "nome": ativ.get("activityName"),
        "tipo": tipo,
        "familia": familia,
        "duracao_min": _min(ativ.get("duration")),
        "distancia_km": round(ativ.get("distance", 0) / 1000, 2) if ativ.get("distance") else None,
        "fc_media": ativ.get("averageHR"),
        "fc_max": ativ.get("maxHR"),
        "calorias": ativ.get("calories"),
    }

    # Detalhe da atividade: RPE, feel, training load real, impacto na bateria
    try:
        det = client.get_activity(aid) or {}
        rpe_garmin = det.get("workout_rpe")  # escala 0-100 (Borg CR10 x10)
        base["rpe_borg"] = round(rpe_garmin / 10, 1) if rpe_garmin else None  # converte p/ 0-10
        base["feel"] = det.get("workout_feel")  # sensacao subjetiva
        base["training_load"] = det.get("training_load")  # TRIMP real do Garmin
        base["training_effect"] = det.get("training_effect")
        base["training_effect_label"] = det.get("training_effect_label")
        base["body_battery_impact"] = det.get("body_battery_impact")
        # sRPE de Foster = RPE(0-10) x duracao(min) — carga interna validada
        if base["rpe_borg"] and base["duracao_min"]:
            base["sRPE_foster"] = round(base["rpe_borg"] * base["duracao_min"])
        else:
            base["sRPE_foster"] = None
    except Exception:
        base.update({"rpe_borg": None, "feel": None, "training_load": None,
                     "training_effect": None, "training_effect_label": None,
                     "body_battery_impact": None, "sRPE_foster": None})

    # Tempo por zona de FC (todas as modalidades com FC confiável)
    if familia in ("corrida", "ciclismo", "cardio"):
        try:
            zonas = client.get_activity_hr_in_timezones(aid)
            base["tempo_por_zona_s"] = {
                f"Z{z.get('zoneNumber')}": round(z.get("secsInZone", 0)) for z in zonas
            } if zonas else None
        except Exception:
            base["tempo_por_zona_s"] = None

    # Métricas específicas por família
    if familia == "corrida":
        base["pace_medio_s_km"] = _pace_s_km(ativ.get("averageSpeed"))
        base["elevacao_ganho_m"] = ativ.get("elevationGain")
        base["cadencia_media"] = ativ.get("averageRunningCadenceInStepsPerMinute")
        try:
            splits = client.get_activity_splits(aid)
            laps = splits.get("lapDTOs", []) if isinstance(splits, dict) else []
            base["splits"] = [
                {"n": i+1, "dist_m": round(s.get("distance", 0)),
                 "fc_media": s.get("averageHR"), "pace_s_km": _pace_s_km(s.get("averageSpeed"))}
                for i, s in enumerate(laps)
            ] if laps else None
            if base["splits"]:
                base["deriva"] = _deriva_cardiaca(base["splits"])
        except Exception:
            base["splits"] = None

    elif familia == "ciclismo":
        base["potencia_media_w"] = ativ.get("avgPower")
        base["potencia_normalizada_w"] = ativ.get("normPower")
        base["velocidade_media_kmh"] = round(ativ.get("averageSpeed", 0) * 3.6, 1) if ativ.get("averageSpeed") else None
        base["elevacao_ganho_m"] = ativ.get("elevationGain")
        try:
            splits = client.get_activity_splits(aid)
            laps = splits.get("lapDTOs", []) if isinstance(splits, dict) else []
            base["splits"] = [
                {"n": i+1, "fc_media": s.get("averageHR"), "potencia_w": s.get("averagePower")}
                for i, s in enumerate(laps)
            ] if laps else None
            if base["splits"]:
                base["deriva"] = _deriva_cardiaca(base["splits"])
        except Exception:
            base["splits"] = None

    elif familia == "natacao":
        dist = ativ.get("distance")
        dur = ativ.get("duration")
        base["pace_100m_s"] = round(dur / (dist / 100)) if dist and dur else None
        base["swolf_medio"] = ativ.get("averageSwolf")
        base["stroke_rate"] = ativ.get("averageStrokeRate") or ativ.get("averageSwimCadenceInStrokesPerMinute")
        base["braçadas_totais"] = ativ.get("strokes")
        # FC incluida normalmente na natacao
        try:
            zonas = client.get_activity_hr_in_timezones(aid)
            base["tempo_por_zona_s"] = {
                f"Z{z.get('zoneNumber')}": round(z.get("secsInZone", 0)) for z in zonas
            } if zonas else None
        except Exception:
            base["tempo_por_zona_s"] = None

    elif familia == "forca":
        # Sem pace/zona; foco em volume e densidade
        base["repeticoes_totais"] = ativ.get("totalReps")
        base["series_totais"] = ativ.get("totalSets")
        base["pace_medio_s_km"] = None
        try:
            sets = client.get_activity_exercise_sets(aid)
            base["exercicios"] = sets if sets else None
        except Exception:
            base["exercicios"] = None

    return base


def coletar_treino(client, hoje: date) -> dict:
    hoje_str = hoje.isoformat()
    resultado = {"prescrito": None, "atividades": [], "erros": []}

    # ---- PRESCRITO ----
    try:
        agendados = client.get_scheduled_workouts(hoje_str, hoje_str)
        if agendados:
            w = agendados[0]
            wid = w.get("workoutId") or w.get("workout", {}).get("workoutId")
            detalhe = client.get_workout_by_id(wid) if wid else {}
            steps = []
            for seg in detalhe.get("workoutSegments", []):
                for step in seg.get("workoutSteps", []):
                    steps.append({
                        "tipo": step.get("stepType", {}).get("stepTypeKey"),
                        "zona_alvo": step.get("zoneNumber"),
                        "alvo_min": step.get("targetValueOne"),
                        "alvo_max": step.get("targetValueTwo"),
                        "duracao_tipo": (step.get("endCondition") or {}).get("conditionTypeKey"),
                        "duracao_valor": step.get("endConditionValue"),
                    })
            resultado["prescrito"] = {
                "nome": detalhe.get("workoutName") or w.get("workoutName"),
                "esporte": detalhe.get("sportType", {}).get("sportTypeKey"),
                "steps": steps,
            }
    except Exception as e:
        resultado["erros"].append(f"Prescrito: {e}")

    # ---- EXECUTADO: TODAS as atividades do dia ----
    try:
        ativ_dia = client.get_activities_fordate(hoje_str)
        lista = []
        if isinstance(ativ_dia, dict):
            payload = ativ_dia.get("ActivitiesForDay", {})
            lista = (payload.get("payload") if isinstance(payload, dict) else payload) or []
        elif isinstance(ativ_dia, list):
            lista = ativ_dia

        for ativ in lista:
            try:
                resultado["atividades"].append(_analisar_atividade(client, ativ))
            except Exception as e:
                resultado["erros"].append(f"Atividade {ativ.get('activityId')}: {e}")
    except Exception as e:
        resultado["erros"].append(f"Executado: {e}")

    resultado["n_atividades"] = len(resultado["atividades"])
    resultado["modalidades_do_dia"] = sorted(set(a["familia"] for a in resultado["atividades"]))

    return resultado
