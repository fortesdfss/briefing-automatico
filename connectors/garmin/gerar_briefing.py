"""
CAMADA 2 — Interpretação via Claude API + envio por email
Recebe os números brutos da Camada 1 e gera o briefing com semáforos.
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

def formatar_tempo(segundos):
    if not segundos:
        return "—"
    m, s = divmod(int(segundos), 60)
    h, m = divmod(m, 60)
    if h:
        return f"{h}h{m:02d}min"
    return f"{m}min{s:02d}s"

def gerar_briefing(dados: dict) -> str:
    """Envia os dados para o Claude e retorna o briefing interpretado."""

    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    prompt = f"""Você é um assistente especialista em fisiologia do exercício e medicina de precisão.

Receberá dados objetivos do Garmin de hoje e deve gerar um briefing diário curto, direto e prático.

REGRAS:
- Use semáforos: 🔴 (ruim/atenção), 🟡 (moderado/cautela), 🟢 (ótimo)
- Máximo 200 palavras no total
- Estrutura obrigatória:
  1. RECUPERAÇÃO 🔴🟡🟢 — HRV + sono + body battery (1-2 linhas)
  2. CARGA 🔴🟡🟢 — ACWR + estresse (1-2 linhas)  
  3. PERFORMANCE 🔴🟡🟢 — VO2máx + previsão de prova (1-2 linhas)
  4. AÇÃO DO DIA — uma frase objetiva com a recomendação principal
- Linguagem técnica mas leve, sem rodeios
- Se um dado estiver ausente (None), ignore-o silenciosamente

DADOS DE HOJE ({dados['data']}):
{json.dumps(dados, indent=2, ensure_ascii=False)}

REFERÊNCIAS:
- HRV noturno saudável adulto ativo: > 50ms
- Sono total ideal: ≥ 420 min (7h)
- Sleep score ideal: ≥ 80
- Body battery ideal ao acordar: ≥ 70
- ACWR zona ótima: 0.8 – 1.3 (< 0.8 = subtreino, > 1.5 = risco)
- VO2máx excelente homem 40-49 anos: > 46 ml/kg/min
"""

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}]
    )

    return response.content[0].text


def enviar_email(assunto: str, corpo: str):
    """Envia o briefing por email via Gmail."""
    remetente = os.getenv("EMAIL_REMETENTE")
    senha_app = os.getenv("EMAIL_SENHA_APP")
    destinatario = os.getenv("EMAIL_DESTINATARIO")

    msg = MIMEMultipart("alternative")
    msg["Subject"] = assunto
    msg["From"] = remetente
    msg["To"] = destinatario

    # Versão texto puro
    parte_texto = MIMEText(corpo, "plain", "utf-8")
    msg.attach(parte_texto)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(remetente, senha_app)
        server.sendmail(remetente, destinatario, msg.as_string())

    print(f"✅ Email enviado para {destinatario}")


if __name__ == "__main__":
    from coletar_dados import coletar

    print("📡 Coletando dados do Garmin...")
    dados = coletar()

    if dados.get("erros"):
        print(f"⚠️  Avisos: {dados['erros']}")

    print("🧠 Gerando interpretação...")
    briefing = gerar_briefing(dados)

    print("\n" + "="*50)
    print(briefing)
    print("="*50 + "\n")

    hoje = date.today().strftime("%d/%m/%Y")
    assunto = f"🏃 Briefing Garmin — {hoje}"

    print("📧 Enviando email...")
    enviar_email(assunto, briefing)
