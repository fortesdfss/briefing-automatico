"""
CAMADA 2 — Interpretação via Claude API + envio por email
"""

import os
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import date
from dotenv import load_dotenv
import anthropic

load_dotenv()

def gerar_briefing(dados: dict, comparacoes: dict) -> str:
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    prompt = f"""Você é um especialista em fisiologia do exercício e medicina de precisão.

Gere um briefing diário com base nos dados objetivos do Garmin e nas comparações históricas.

ESTRUTURA OBRIGATÓRIA (máximo 300 palavras):

1. RECUPERAÇÃO [semaforo] — HRV + sono + body battery
2. CARGA [semaforo] — ACWR + estresse  
3. PERFORMANCE [semaforo] — VO2max
4. TENDENCIAS — compare hoje vs 7d, 30d, 180d e 365d. Destaque apenas o que mudou de forma relevante (delta > 5%).
5. ACAO DO DIA — uma frase objetiva e específica

SEMAFOROS: 🔴 ruim | 🟡 moderado | 🟢 ótimo

REGRAS:
- Linguagem técnica mas direta
- Se dado ausente (None), ignore silenciosamente
- Nas tendências, use setas: ↑ melhora, ↓ piora, → estável
- Só mencione períodos com dados suficientes (n >= 5)

DADOS DE HOJE ({dados['data']}):
{json.dumps(dados, indent=2, ensure_ascii=False)}

COMPARACOES HISTORICAS:
{json.dumps(comparacoes, indent=2, ensure_ascii=False)}

REFERENCIAS:
- HRV noturno saudável: > 50ms
- Sono ideal: >= 420 min
- Sleep score ideal: >= 80
- Body battery ao acordar: >= 70
- ACWR zona ótima: 0.8-1.3
- VO2max excelente (40-49 anos): > 46 ml/kg/min
"""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=600,
        messages=[{"role": "user", "content": prompt}]
    )

    return response.content[0].text


def enviar_email(assunto: str, corpo: str):
    remetente = os.getenv("EMAIL_REMETENTE")
    senha_app = os.getenv("EMAIL_SENHA_APP")
    destinatario = os.getenv("EMAIL_DESTINATARIO")

    msg = MIMEMultipart("alternative")
    msg["Subject"] = assunto
    msg["From"] = remetente
    msg["To"] = destinatario

    msg.attach(MIMEText(corpo, "plain", "utf-8"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(remetente, senha_app)
        server.sendmail(remetente, destinatario, msg.as_string())

    print(f"Email enviado para {destinatario}")
