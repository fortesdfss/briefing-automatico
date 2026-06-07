"""
CAMADA 1 — Coleta e cálculo determinístico
Baixa dados do Garmin Connect e retorna um dicionário com números brutos.
Nenhuma inferência ou interpretação aqui — só fatos.
"""

import os
import json
from datetime import date, timedelta
from dotenv import load_dotenv
import garminconnect

load_dotenv()

def conectar_garmin():
    email = os.getenv("GARMIN_EMAIL")
    senha = os.getenv("GARMIN_PASSWORD")
    client = garminconnect.Garmin(email, senha)
    client.login()
    return client

def calcular_acwr(client, hoje):
    """
    ACWR = carga aguda (7 dias) / carga crônica (28 dias)
    Usa Training Load (se disponível) ou calorias como proxy.
    """
    try:
        cargas = []
        for i in range(28):
            dia = (hoje - timedelta(days=i)).isoformat()
            try:
                stats = client.get_stats(dia)
                carga = stats.get("activeKilocalories", 0) or 0
                cargas.append(carga)
            except Exception:
                cargas.append(0)

        aguda = sum(cargas[:7]) / 7 if cargas[:7] else 0
        cronica = sum(cargas[:28]) / 28 if cargas[:28] else 0
        acwr = round(aguda / cronica, 2) if cronica > 0 else None
        return acwr, round(aguda, 1), round(cronica, 1)
    except Exception:
        return None, None, None

def coletar(hoje=None):
    if hoje is None:
        hoje = date.today()

    hoje_str = hoje.isoformat()
    ontem_str = (hoje - timedelta(days=1)).isoformat()

    client = conectar_garmin()
    dados = {"data": hoje_str, "erros": []}

    # HRV
    try:
        hrv = client.get_hrv_data(hoje_str)
        dados["hrv_semanal"] = hrv.get("hrvSummary", {}).get("weeklyAvg")
        dados["hrv_noturno"] = hrv.get("hrvSummary", {}).get("lastNight")
        dados["hrv_status"] = hrv.get("hrvSummary", {}).get("status")
    except Exception as e:
        dados["erros"].append(f"HRV: {e}")
        dados["hrv_semanal"] = None
        dados["hrv_noturno"] = None
        dados["hrv_status"] = None

    # Sono
    try:
        sono = client.get_sleep_data(ontem_str)
        resumo = sono.get("dailySleepDTO", {})
        dados["sono_total_min"] = resumo.get("sleepTimeSeconds", 0) // 60
        dados["sono_profundo_min"] = resumo.get("deepSleepSeconds", 0) // 60
        dados["sono_score"] = resumo.get("sleepScores", {}).get("overall", {}).get("value")
    except Exception as e:
        dados["erros"].append(f"Sono: {e}")
        dados["sono_total_min"] = None
        dados["sono_profundo_min"] = None
        dados["sono_score"] = None

    # Body Battery / Readiness
    try:
        bb = client.get_body_battery(hoje_str, hoje_str)
        if bb and len(bb) > 0:
            valores = [v[1] for v in bb[0].get("bodyBatteryValuesArray", []) if v[1] is not None]
            dados["body_battery_max"] = max(valores) if valores else None
            dados["body_battery_atual"] = valores[-1] if valores else None
        else:
            dados["body_battery_max"] = None
            dados["body_battery_atual"] = None
    except Exception as e:
        dados["erros"].append(f"Body Battery: {e}")
        dados["body_battery_max"] = None
        dados["body_battery_atual"] = None

    # VO2máx
    try:
        stats = client.get_stats(hoje_str)
        dados["vo2max"] = stats.get("maxMetValue")
        dados["stress_medio"] = stats.get("averageStressLevel")
        dados["passos"] = stats.get("totalSteps")
        dados["calorias_ativas"] = stats.get("activeKilocalories")
    except Exception as e:
        dados["erros"].append(f"Stats: {e}")
        dados["vo2max"] = None
        dados["stress_medio"] = None
        dados["passos"] = None
        dados["calorias_ativas"] = None

    # Peso
    try:
        peso_data = client.get_weigh_ins(hoje_str, hoje_str)
        registros = peso_data.get("dailyWeightSummaries", [])
        if registros:
            peso_g = registros[0].get("summaryList", [{}])[0].get("weight")
            dados["peso_kg"] = round(peso_g / 1000, 1) if peso_g else None
        else:
            dados["peso_kg"] = None
    except Exception as e:
        dados["erros"].append(f"Peso: {e}")
        dados["peso_kg"] = None

    # Previsão de prova
    try:
        previsao = client.get_race_predictions()
        dados["previsao_5k"] = previsao.get("time5K")
        dados["previsao_10k"] = previsao.get("time10K")
        dados["previsao_meia"] = previsao.get("timeHalfMarathon")
        dados["previsao_maratona"] = previsao.get("timeMarathon")
    except Exception as e:
        dados["erros"].append(f"Previsão de prova: {e}")
        dados["previsao_5k"] = None
        dados["previsao_10k"] = None
        dados["previsao_meia"] = None
        dados["previsao_maratona"] = None

    # ACWR
    acwr, aguda, cronica = calcular_acwr(client, hoje)
    dados["acwr"] = acwr
    dados["carga_aguda_7d"] = aguda
    dados["carga_cronica_28d"] = cronica

    return dados


if __name__ == "__main__":
    resultado = coletar()
    print(json.dumps(resultado, indent=2, ensure_ascii=False))
