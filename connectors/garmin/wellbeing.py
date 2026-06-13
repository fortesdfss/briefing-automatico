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


def formulario_html(endpoint="https://briefing-automatico.vercel.app/api/wellbeing") -> str:
    """
    Gera o bloco HTML do formulário de wellbeing para o email de domingo.
    Um único botão que abre a página de check-in completa no Vercel.
    """
    return (
        f'<div style="border:1px solid #e4e0d9;border-radius:4px;padding:26px 28px;margin-top:8px;">'
        f'<div style="font-family:\'Helvetica Neue\',Helvetica,Arial,sans-serif;font-size:11px;'
        f'letter-spacing:1.5px;text-transform:uppercase;color:#7a756e;font-weight:700;margin-bottom:10px;">'
        f'Check-in Semanal de Wellbeing</div>'
        f'<div style="font-family:\'Iowan Old Style\',Palatino,Georgia,serif;font-size:15px;'
        f'color:#33312e;line-height:1.6;margin-bottom:18px;">'
        f'Preencha o check-in semanal da escala Hooper-Mackinnon. Leva menos de 1 minuto.</div>'
        f'<a href="{endpoint}" '
        f'style="display:inline-block;background:#1a1a1a;color:#f7f5f1;padding:13px 28px;'
        f'text-decoration:none;border-radius:4px;'
        f'font-family:\'Helvetica Neue\',Helvetica,Arial,sans-serif;'
        f'font-size:12px;letter-spacing:1.5px;text-transform:uppercase;font-weight:700;">'
        f'Preencher check-in &rarr;</a>'
        f'</div>'
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
