"""
TRANSCRIÇÃO DE WELLBEING — lê o título de uma issue do GitHub no formato
'wellbeing:campo=valor' e grava no wellbeing.json na raiz do repo.

Acumula respostas do MESMO dia (cada botão clicado é uma issue separada),
preservando os campos já preenchidos. Chamado pelo workflow on:issues.
"""

import os
import json
import sys
from pathlib import Path
from datetime import date

WELLBEING_FILE = Path(__file__).parent.parent.parent / "wellbeing.json"

CAMPOS_VALIDOS = {
    "sono_qualidade": (1, 7),
    "fadiga": (1, 7),
    "estresse": (1, 7),
    "dores_musculares": (1, 7),
    "motivacao": (1, 5),
}


def parse_titulo(titulo: str):
    """'wellbeing:fadiga=3' -> ('fadiga', 3). Retorna None se inválido."""
    titulo = titulo.strip()
    if not titulo.lower().startswith("wellbeing:"):
        return None
    corpo = titulo.split(":", 1)[1]
    if "=" not in corpo:
        return None
    campo, valor = corpo.split("=", 1)
    campo = campo.strip()
    valor = valor.strip()
    if campo not in CAMPOS_VALIDOS:
        return None
    try:
        valor_int = int(valor)
    except ValueError:
        return None
    lo, hi = CAMPOS_VALIDOS[campo]
    if not (lo <= valor_int <= hi):
        return None
    return campo, valor_int


def atualizar(campo: str, valor: int):
    """Grava o campo no wellbeing.json. Reinicia se for de outro dia."""
    hoje = date.today().isoformat()
    dados = {}
    if WELLBEING_FILE.exists():
        try:
            with open(WELLBEING_FILE, encoding="utf-8") as f:
                dados = json.load(f)
        except Exception:
            dados = {}

    # Se o registro existente é de outro dia, começa um novo
    if dados.get("data") != hoje:
        dados = {"data": hoje}

    dados[campo] = valor
    dados["data"] = hoje

    with open(WELLBEING_FILE, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=2, ensure_ascii=False)
    print(f"Wellbeing atualizado: {campo}={valor} (data {hoje})")
    return dados


if __name__ == "__main__":
    # Recebe o título da issue via variável de ambiente ISSUE_TITLE
    titulo = os.getenv("ISSUE_TITLE", "")
    if len(sys.argv) > 1:
        titulo = sys.argv[1]

    resultado = parse_titulo(titulo)
    if not resultado:
        print(f"Título não reconhecido como wellbeing válido: '{titulo}'")
        sys.exit(0)  # sai sem erro para não falhar o workflow

    campo, valor = resultado
    atualizar(campo, valor)
