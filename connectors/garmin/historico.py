"""
HISTÓRICO — Salva e lê dados do repositório GitHub
Cada dia gera um arquivo historico/YYYY-MM-DD.json
"""

import os
import json
from datetime import date, timedelta
from pathlib import Path

HISTORICO_DIR = Path(__file__).parent.parent.parent / "historico"

def salvar(dados: dict):
    """Salva os dados do dia no arquivo JSON do histórico."""
    HISTORICO_DIR.mkdir(exist_ok=True)
    caminho = HISTORICO_DIR / f"{dados['data']}.json"
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=2, ensure_ascii=False)
    print(f"Historico salvo: {caminho}")

def carregar(data_str: str) -> dict | None:
    """Carrega dados de uma data específica (formato YYYY-MM-DD)."""
    caminho = HISTORICO_DIR / f"{data_str}.json"
    if caminho.exists():
        with open(caminho, encoding="utf-8") as f:
            return json.load(f)
    return None

def carregar_periodo(dias: int, hoje: date) -> list[dict]:
    """Carrega todos os registros dos últimos N dias."""
    registros = []
    for i in range(1, dias + 1):
        data = (hoje - timedelta(days=i)).isoformat()
        dado = carregar(data)
        if dado:
            registros.append(dado)
    return registros

def media_metrica(registros: list[dict], campo: str) -> float | None:
    """Calcula a média de uma métrica em uma lista de registros."""
    valores = [r[campo] for r in registros if r.get(campo) is not None]
    if not valores:
        return None
    return round(sum(valores) / len(valores), 1)

def comparar(hoje: dict) -> dict:
    """Gera comparações com 7d, 30d, 180d e 365d anteriores."""
    data_hoje = date.fromisoformat(hoje["data"])
    metricas = ["hrv_rmssd_noturno", "hrv_media_7d", "hrv_desvio_baseline_pct",
                "readiness_score", "stress_medio", "fc_repouso",
                "sono_total_min", "sono_score", "body_battery_max", "acwr", "vo2max"]

    comparacoes = {}
    periodos = {"7d": 7, "30d": 30, "180d": 180, "365d": 365}

    for nome, dias in periodos.items():
        registros = carregar_periodo(dias, data_hoje)
        if not registros:
            comparacoes[nome] = {"n": 0}
            continue

        comp = {"n": len(registros)}
        for metrica in metricas:
            media = media_metrica(registros, metrica)
            atual = hoje.get(metrica)
            comp[metrica] = {
                "media": media,
                "atual": atual,
                "delta": round(atual - media, 1) if (atual is not None and media is not None) else None
            }
        comparacoes[nome] = comp

    return comparacoes
