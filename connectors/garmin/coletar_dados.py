"""
CAMADA 1 — Coleta e cálculo determinístico
Métricas reais do Garmin, rotuladas com honestidade. Sem inferência.
"""

import os
import json
import time
import random
from datetime import date, timedelta
from dotenv import load_dotenv
import garminconnect

load_dotenv()

TOKENSTORE = os.path.join(os.path.dirname(__file__), ".garmin_tokens")

def conectar_garmin():
    email = os.getenv("GARMIN_EMAIL")
    senha = os.getenv("GARMIN_PASSWORD")
    time.sleep(random.uniform(1.5, 3.5))
    client = garminconnect.Garmin(email, senha)
    try:
        client.login(TOKENSTORE)
        print("Sessao Garmin restaurada")
    except Exception:
        print("Fazendo login no Garmin...")
        time.sleep(random.uniform(2, 4))
        client.login()
        try:
            client.garth.dump(TOKENSTORE)
            print("Tokens salvos")
        except Exception as e:
            print(f"Nao foi possivel salvar tokens: {e}")
    return client

def calcular_acwr(client, hoje):
    try:
        cargas = []
        for i in range(28):
            dia = (hoje - timedelta(days=i)).isoformat()
            try:
                stats = client.get_stats(dia)
                cargas.append(stats.get("activeKilocalories", 0) or 0)
                time.sleep(0.3)
            except Exception:
                cargas.append(0)
        aguda = sum(cargas[:7]) / 7 if cargas[:7] else 0
        cronica = sum(cargas[:28]) / 28 if cargas[:28] else 0
        acwr = round(aguda / cronica, 2) if cronica > 0 else None
        return acwr, round(aguda, 1), round(cronica, 1)
    except Exception:
        return None, None, None

def coletar(hoje=None, client=None):
    if hoje is None:
        hoje = date.today()
    hoje_str = hoje.isoformat()
    ontem_str = (hoje - timedelta(days=1)).isoformat()
    if client is None:
        client = conectar_garmin()
    dados = {"data": hoje_str, "erros": []}

    # HRV completo (rMSSD noturno, media 7d, baseline, status, desvio %)
    try:
        hrv = client.get_hrv_data(hoje_str)
        resumo = (hrv or {}).get("hrvSummary") or {}
        rmssd_noturno = resumo.get("lastNightAvg")
        media_7d = resumo.get("weeklyAvg")
        baseline = resumo.get("baseline") or {}
        bl_baixo = baseline.get("lowUpper") or baseline.get("balancedLow")
        bl_alto = baseline.get("balancedUpper") or baseline.get("markerValue")
        bl_marker = baseline.get("markerValue")  # ponto central da baseline

        dados["hrv_rmssd_noturno"] = rmssd_noturno
        dados["hrv_media_7d"] = media_7d
        dados["hrv_status"] = resumo.get("status")  # BALANCED / UNBALANCED / LOW
        dados["hrv_baseline_baixo"] = bl_baixo
        dados["hrv_baseline_alto"] = bl_alto
        dados["hrv_baseline_marker"] = bl_marker

        # Desvio % do rMSSD noturno em relacao ao centro da baseline
        ref = bl_marker or media_7d
        if rmssd_noturno is not None and ref:
            dados["hrv_desvio_baseline_pct"] = round((rmssd_noturno - ref) / ref * 100, 1)
        else:
            dados["hrv_desvio_baseline_pct"] = None

        # Dispersao das leituras noturnas de 5 min (variabilidade global da noite)
        try:
            hrv_ts = client.get_hrv_data(hoje_str, return_timeseries=True)
            leituras = [r.get("hrvValue") for r in (hrv_ts or {}).get("hrvReadings", []) if r.get("hrvValue")]
            if len(leituras) >= 5:
                m = sum(leituras) / len(leituras)
                dp = (sum((x - m) ** 2 for x in leituras) / len(leituras)) ** 0.5
                dados["hrv_dispersao_noturna_ms"] = round(dp, 1)
                dados["hrv_cv_noturno_pct"] = round(dp / m * 100, 1) if m else None
            else:
                dados["hrv_dispersao_noturna_ms"] = None
                dados["hrv_cv_noturno_pct"] = None
        except Exception:
            dados["hrv_dispersao_noturna_ms"] = None
            dados["hrv_cv_noturno_pct"] = None
    except Exception as e:
        dados["erros"].append(f"HRV: {e}")
        for k in ["hrv_rmssd_noturno","hrv_media_7d","hrv_status","hrv_baseline_baixo",
                  "hrv_baseline_alto","hrv_baseline_marker","hrv_desvio_baseline_pct",
                  "hrv_dispersao_noturna_ms","hrv_cv_noturno_pct"]:
            dados[k] = None

    # Training Readiness (score composto + fatores)
    try:
        tr = client.get_training_readiness(hoje_str)
        if isinstance(tr, list) and tr:
            tr = tr[0]
        tr = tr or {}
        dados["readiness_score"] = tr.get("score")
        dados["readiness_nivel"] = tr.get("level")  # LOW/MODERATE/HIGH/MAXIMUM
        dados["readiness_sono_fator"] = tr.get("sleepScoreFactorPercent")
        dados["readiness_recuperacao_fator"] = tr.get("recoveryTimeFactorPercent")
        dados["readiness_hrv_fator"] = tr.get("hrvFactorPercent")
        dados["readiness_carga_aguda_fator"] = tr.get("acuteLoadFactorPercent")
    except Exception as e:
        dados["erros"].append(f"Readiness: {e}")
        for k in ["readiness_score","readiness_nivel","readiness_sono_fator",
                  "readiness_recuperacao_fator","readiness_hrv_fator","readiness_carga_aguda_fator"]:
            dados[k] = None

    # Stress Index do Garmin (balanco autonomico diario)
    try:
        stats = client.get_stats(hoje_str)
        dados["stress_medio"] = stats.get("averageStressLevel")
        dados["stress_max"] = stats.get("maxStressLevel")
        dados["stress_repouso_pct"] = stats.get("restStressPercentage")
        dados["stress_baixo_pct"] = stats.get("lowStressPercentage")
        dados["stress_medio_pct"] = stats.get("mediumStressPercentage")
        dados["stress_alto_pct"] = stats.get("highStressPercentage")
        dados["vo2max"] = stats.get("maxMetValue")
        dados["passos"] = stats.get("totalSteps")
        dados["calorias_ativas"] = stats.get("activeKilocalories")
        dados["fc_repouso"] = stats.get("restingHeartRate")
    except Exception as e:
        dados["erros"].append(f"Stats: {e}")
        for k in ["stress_medio","stress_max","stress_repouso_pct","stress_baixo_pct",
                  "stress_medio_pct","stress_alto_pct","vo2max","passos","calorias_ativas","fc_repouso"]:
            dados[k] = None

    # Sono (arquitetura + score)
    try:
        sono = client.get_sleep_data(hoje_str)
        resumo = (sono or {}).get("dailySleepDTO") or {}
        dados["sono_total_min"] = (resumo.get("sleepTimeSeconds") or 0) // 60
        dados["sono_profundo_min"] = (resumo.get("deepSleepSeconds") or 0) // 60
        dados["sono_leve_min"] = (resumo.get("lightSleepSeconds") or 0) // 60
        dados["sono_rem_min"] = (resumo.get("remSleepSeconds") or 0) // 60
        dados["sono_acordado_min"] = (resumo.get("awakeSleepSeconds") or 0) // 60
        scores = resumo.get("sleepScores") or {}
        dados["sono_score"] = (scores.get("overall") or {}).get("value")
    except Exception as e:
        dados["erros"].append(f"Sono: {e}")
        for k in ["sono_total_min","sono_profundo_min","sono_leve_min","sono_rem_min",
                  "sono_acordado_min","sono_score"]:
            dados[k] = None

    # Body Battery
    try:
        bb = client.get_body_battery(hoje_str, hoje_str)
        if bb and len(bb) > 0:
            valores = [v[1] for v in bb[0].get("bodyBatteryValuesArray", []) if v[1] is not None]
            dados["body_battery_max"] = max(valores) if valores else None
            dados["body_battery_min"] = min(valores) if valores else None
            dados["body_battery_atual"] = valores[-1] if valores else None
        else:
            dados["body_battery_max"] = dados["body_battery_min"] = dados["body_battery_atual"] = None
    except Exception as e:
        dados["erros"].append(f"Body Battery: {e}")
        dados["body_battery_max"] = dados["body_battery_min"] = dados["body_battery_atual"] = None

    # Peso
    try:
        peso_data = client.get_weigh_ins(hoje_str, hoje_str)
        registros = (peso_data or {}).get("dailyWeightSummaries") or []
        if registros:
            sl = registros[0].get("summaryList") or [{}]
            peso_g = sl[0].get("weight")
            dados["peso_kg"] = round(peso_g / 1000, 1) if peso_g else None
        else:
            dados["peso_kg"] = None
    except Exception as e:
        dados["erros"].append(f"Peso: {e}")
        dados["peso_kg"] = None

    # Previsao de prova (CORRIDA)
    try:
        previsao = client.get_race_predictions()
        if isinstance(previsao, list) and previsao:
            previsao = previsao[0]
        previsao = previsao or {}
        dados["previsao_corrida_5k"] = previsao.get("time5K")
        dados["previsao_corrida_10k"] = previsao.get("time10K")
        dados["previsao_corrida_meia"] = previsao.get("timeHalfMarathon")
        dados["previsao_corrida_maratona"] = previsao.get("timeMarathon")
    except Exception as e:
        dados["erros"].append(f"Previsao corrida: {e}")
        for k in ["previsao_corrida_5k","previsao_corrida_10k","previsao_corrida_meia","previsao_corrida_maratona"]:
            dados[k] = None

    # ACWR
    acwr, aguda, cronica = calcular_acwr(client, hoje)
    dados["acwr"] = acwr
    dados["carga_aguda_7d"] = aguda
    dados["carga_cronica_28d"] = cronica

    return dados


if __name__ == "__main__":
    print(json.dumps(coletar(), indent=2, ensure_ascii=False))
