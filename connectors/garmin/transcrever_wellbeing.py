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

# Aliases para nomes alternativos usados no email
ALIASES = {
    "sono": "sono_qualidade",
    "dor_muscular": "dores_musculares",
    "dor": "dores_musculares",
}


def parse_titulo(titulo: str):
    """Aceita um ou múltiplos pares campo=valor separados por vírgula.
    Retorna dict com os campos válidos, ou None se nenhum for reconhecido."""
    titulo = titulo.strip()
    if not titulo.lower().startswith("wellbeing:"):
        return None
    corpo = titulo.split(":", 1)[1]
    resultado = {}
    for par in corpo.split(","):
        par = par.strip()
        if "=" not in par:
            continue
        campo, valor = par.split("=", 1)
        campo = campo.strip().lower()
        valor = valor.strip()
        campo = ALIASES.get(campo, campo)
        if campo not in CAMPOS_VALIDOS:
            continue
        try:
            valor_int = int(valor)
        except ValueError:
            continue
        lo, hi = CAMPOS_VALIDOS[campo]
        if not (lo <= valor_int <= hi):
            continue
        resultado[campo] = valor_int
    return resultado if resultado else None


def atualizar(campos: dict):
    """Grava os campos no wellbeing.json. Reinicia se for de outro dia."""
    hoje = date.today().isoformat()
    dados = {}
    if WELLBEING_FILE.exists():
        try:
            with open(WELLBEING_FILE, encoding="utf-8") as f:
                dados = json.load(f)
        except Exception:
            dados = {}

    if dados.get("data") != hoje:
        dados = {"data": hoje}

    dados.update(campos)
    dados["data"] = hoje

    with open(WELLBEING_FILE, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=2, ensure_ascii=False)
    print(f"Wellbeing atualizado: {campos} (data {hoje})")
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

    atualizar(resultado)
