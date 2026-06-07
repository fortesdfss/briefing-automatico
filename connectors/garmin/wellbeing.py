"""
WELLBEING SEMANAL — contexto subjetivo que o relógio não captura
Lê um arquivo wellbeing.json (atualizado ~1x/semana pelo atleta) com:
estresse de vida, dores/desconfortos, motivação, sono subjetivo, nutrição.

O relatório usa esse contexto e AVISA quando está vencido (>9 dias),
sem criar fricção diária.
"""

import json
from pathlib import Path
from datetime import date, datetime

WELLBEING_FILE = Path(__file__).parent.parent.parent / "wellbeing.json"


def carregar_wellbeing() -> dict:
    """Lê o wellbeing mais recente e calcula há quantos dias foi atualizado."""
    if not WELLBEING_FILE.exists():
        return {
            "disponivel": False,
            "vencido": True,
            "mensagem": "Sem registro de wellbeing ainda. Considere preencher wellbeing.json "
                        "(estresse de vida, dores, motivação, sono subjetivo) ~1x/semana — "
                        "é o contexto que o relógio não captura.",
        }
    try:
        with open(WELLBEING_FILE, encoding="utf-8") as f:
            w = json.load(f)
        data_reg = w.get("data")
        dias = None
        if data_reg:
            dias = (date.today() - date.fromisoformat(data_reg)).days
        return {
            "disponivel": True,
            "data_registro": data_reg,
            "dias_desde_registro": dias,
            "vencido": (dias is not None and dias > 9),
            "estresse_vida": w.get("estresse_vida"),          # 1-5
            "dores_desconfortos": w.get("dores_desconfortos"), # texto/lista
            "motivacao": w.get("motivacao"),                   # 1-5
            "sono_subjetivo": w.get("sono_subjetivo"),         # 1-5
            "nutricao": w.get("nutricao"),                     # texto livre
            "observacoes": w.get("observacoes"),
        }
    except Exception as e:
        return {"disponivel": False, "vencido": True, "erro": str(e)}


# Template de referencia (para o atleta saber o formato)
TEMPLATE = {
    "data": "2026-06-07",
    "estresse_vida": 2,
    "dores_desconfortos": "leve tensão panturrilha direita",
    "motivacao": 4,
    "sono_subjetivo": 3,
    "nutricao": "comendo bem, hidratação ok",
    "observacoes": "semana de trabalho puxada",
}

if __name__ == "__main__":
    print(json.dumps(carregar_wellbeing(), indent=2, ensure_ascii=False))
