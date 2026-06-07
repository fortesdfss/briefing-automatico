"""
WELLBEING SEMANAL — escala padrão da literatura (Hooper-Mackinnon / McLean)
Preenchido aos domingos. O email de domingo traz um formulário clicável;
cada botão abre um link que registra a resposta (via GitHub issue ou form).

Escala Hooper-Mackinnon (1-7, onde 1=excelente/muito baixo, 7=péssimo/muito alto):
- qualidade de sono, fadiga, estresse, dores musculares (DOMS)
Mais motivação (1-5) e contexto livre.
"""

import json
from pathlib import Path
from datetime import date

WELLBEING_FILE = Path(__file__).parent.parent.parent / "wellbeing.json"


def carregar_wellbeing() -> dict:
    if not WELLBEING_FILE.exists():
        return {
            "disponivel": False, "vencido": True,
            "mensagem": "Sem registro de wellbeing ainda.",
        }
    try:
        with open(WELLBEING_FILE, encoding="utf-8") as f:
            w = json.load(f)
        data_reg = w.get("data")
        dias = (date.today() - date.fromisoformat(data_reg)).days if data_reg else None
        return {
            "disponivel": True,
            "data_registro": data_reg,
            "dias_desde_registro": dias,
            "vencido": (dias is not None and dias > 9),
            # Hooper-Mackinnon (1=melhor, 7=pior)
            "sono_qualidade": w.get("sono_qualidade"),
            "fadiga": w.get("fadiga"),
            "estresse": w.get("estresse"),
            "dores_musculares": w.get("dores_musculares"),
            "motivacao": w.get("motivacao"),  # 1-5
            "dores_especificas": w.get("dores_especificas"),
            "observacoes": w.get("observacoes"),
        }
    except Exception as e:
        return {"disponivel": False, "vencido": True, "erro": str(e)}


def eh_domingo(d: date = None) -> bool:
    return (d or date.today()).weekday() == 6


def formulario_html(repo="fortesdfss/briefing-automatico") -> str:
    """
    Gera o bloco HTML do formulário de wellbeing para o email de domingo.
    Cada opção é um link que abre uma GitHub issue pré-preenchida (cru mas
    funciona sem servidor) — o atleta clica, a issue registra a resposta,
    e um workflow leve transcreve para wellbeing.json.
    Alternativa simples: links mailto que o atleta responde.
    """
    base = f"https://github.com/{repo}/issues/new"

    def escala7(nome, label, descr_baixo, descr_alto):
        botoes = ""
        for v in range(1, 8):
            titulo = f"wellbeing:{nome}={v}"
            url = f"{base}?title={titulo}&labels=wellbeing"
            botoes += (
                f'<a href="{url}" style="display:inline-block;width:34px;height:34px;'
                f'line-height:34px;margin:2px;text-align:center;border:1px solid #ccc;'
                f'border-radius:6px;text-decoration:none;color:#333;font-weight:600;">{v}</a>'
            )
        return (
            f'<div style="margin:14px 0;">'
            f'<div style="font-weight:600;margin-bottom:4px;">{label}</div>'
            f'<div style="font-size:12px;color:#888;margin-bottom:6px;">1 = {descr_baixo} &nbsp;·&nbsp; 7 = {descr_alto}</div>'
            f'{botoes}</div>'
        )

    def escala5(nome, label, descr_baixo, descr_alto):
        botoes = ""
        for v in range(1, 6):
            titulo = f"wellbeing:{nome}={v}"
            url = f"{base}?title={titulo}&labels=wellbeing"
            botoes += (
                f'<a href="{url}" style="display:inline-block;width:34px;height:34px;'
                f'line-height:34px;margin:2px;text-align:center;border:1px solid #ccc;'
                f'border-radius:6px;text-decoration:none;color:#333;font-weight:600;">{v}</a>'
            )
        return (
            f'<div style="margin:14px 0;">'
            f'<div style="font-weight:600;margin-bottom:4px;">{label}</div>'
            f'<div style="font-size:12px;color:#888;margin-bottom:6px;">1 = {descr_baixo} &nbsp;·&nbsp; 5 = {descr_alto}</div>'
            f'{botoes}</div>'
        )

    return (
        '<div style="border:2px solid #222;border-radius:10px;padding:18px;margin-top:24px;font-family:Arial,sans-serif;">'
        '<div style="font-size:16px;font-weight:700;margin-bottom:4px;">CHECK-IN SEMANAL DE WELLBEING</div>'
        '<div style="font-size:13px;color:#666;margin-bottom:12px;">Escala Hooper-Mackinnon. Toque em um número por item — registra automaticamente.</div>'
        + escala7("sono_qualidade", "Qualidade do sono na semana", "excelente", "péssima")
        + escala7("fadiga", "Nível de fadiga geral", "muito baixa", "exausto")
        + escala7("estresse", "Estresse de vida (trabalho/pessoal)", "muito baixo", "muito alto")
        + escala7("dores_musculares", "Dores musculares (DOMS)", "nenhuma", "intensas")
        + escala5("motivacao", "Motivação para treinar", "nenhuma", "altíssima")
        + '<div style="font-size:12px;color:#888;margin-top:10px;">Dores específicas ou observações? Responda este email com o texto.</div>'
        '</div>'
    )


TEMPLATE = {
    "data": "2026-06-08",
    "sono_qualidade": 3, "fadiga": 3, "estresse": 2,
    "dores_musculares": 2, "motivacao": 4,
    "dores_especificas": "leve tensão panturrilha direita",
    "observacoes": "semana de trabalho puxada",
}

if __name__ == "__main__":
    print(json.dumps(carregar_wellbeing(), indent=2, ensure_ascii=False))
    print("\nÉ domingo?", eh_domingo())
