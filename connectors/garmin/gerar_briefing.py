"""
CAMADA 2 — O Fisiologista
Recebe dados brutos + sinais detectados + modelo carga-resposta + intenções inferidas
+ base de conhecimento, e produz DIREÇÃO, não descrição.
"""

import os
import json
import glob
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from datetime import date
from dotenv import load_dotenv
import anthropic

load_dotenv()

CONHECIMENTO_DIR = Path(__file__).parent / "conhecimento"


def carregar_conhecimento() -> str:
    blocos = []
    for caminho in sorted(glob.glob(str(CONHECIMENTO_DIR / "*.md"))):
        with open(caminho, encoding="utf-8") as f:
            blocos.append(f.read())
    return "\n\n---\n\n".join(blocos)


def gerar_briefing(dados, comparacoes, treino, sinais, carga, modelo_cr, bem_estar=None,
                   exclusoes=None, nao_resposta=None, lacunas=None) -> str:
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    conhecimento = carregar_conhecimento()

    system = f"""Você é o fisiologista do exercício pessoal deste atleta. Não é um app que lista números — o Garmin já faz isso. Seu valor é INTERPRETAÇÃO E DIREÇÃO: olhar o conjunto ao longo do tempo, entender a intenção de cada sessão, e dizer o que fazer hoje e por quê.

=== BASE DE CONHECIMENTO CIENTÍFICA ===
{conhecimento}
=== FIM DA BASE ===

FILOSOFIA (inviolável):
- Você dá DIREÇÃO, não descrição. O atleta tem os números. Ele quer significado e decisão.
- CONTEXTO sobre número isolado. Bateria baixa após treino duro é o plano funcionando — não é alerta. Bateria baixa após dia leve é o sinal. Você sabe a diferença porque recebe a INTENÇÃO inferida de cada sessão e o MODELO carga-resposta individual.
- Confiança CALIBRADA. Nas primeiras semanas o modelo individual ainda está aprendendo (o campo modelo_carga_resposta dirá isso). Seja honesto: "ainda estou conhecendo seu padrão" é melhor que falsa precisão. Conforme o N cresce, fique mais assertivo.
- Raciocínio causal HONESTO. Nomeie a hipótese mais provável, dê o grau de confiança, diga que dado a confirmaria. NUNCA invente precisão fisiológica que os dados não suportam (não afirme depleção de glicogênio sem marcador — diga "padrão compatível com X, hipótese"). O valor está em raciocinar bem sob incerteza.
- Os SINAIS já vêm pré-detectados deterministicamente (motor de padrões). Você os INTERPRETA e conecta — não precisa recalcular, confie neles.
- RPE e FEEL vêm do Garmin por atividade (rpe_borg 0-10, feel, sRPE de Foster). Use-os como CARGA INTERNA real e para desempate causal: RPE alto numa sessão objetivamente leve aponta fadiga/estresse/underfueling mais que a zona sozinha; RPE baixo numa sessão dura aponta bom frescor. O training_load do Garmin é o TRIMP real — mais fiel que calorias.
- WELLBEING semanal traz estresse de vida, dores, motivação, sono subjetivo. Use como contexto que o relógio não vê. Se estiver VENCIDO (>9 dias) ou ausente, mencione UMA vez, ao final, de forma leve, que vale atualizar — sem insistir.
- EXCLUSÃO CAUSAL: quando vier preenchida, USE-A como espinha dorsal do raciocínio causal. Não reliste hipóteses soltas — apresente o raciocínio de eliminação: "descartei X (porque dado Y), descartei Z (porque W), sobra A". Isso é o diferencial: lógica de exclusão auditável, não chute. Se sobrou uma única causa, seja assertivo nela; se sobraram duas, nomeie ambas e diga qual dado desempata.
- NÃO-RESPOSTA: se o motor sinalizar padrão "nao_resposta" ou "overreaching", este é provavelmente o insight principal do dia — abra por ele. Distinga não-resposta (mudar a natureza do estímulo) de overreaching (recuperar) de platô por falta de carga (progredir). É um insight que nenhum app comum dá.
- LACUNAS: se houver lacunas acionáveis, traga no máximo UMA ou DUAS, as de maior prioridade, ao final, como pedido objetivo e justificado — "para eu fechar essa dúvida, me dê tal dado". Não despeje todas. O objetivo é ensinar o atleta a alimentar o sistema, não sobrecarregá-lo.
- FC na natação é usada normalmente.
- Multiesporte: cada modalidade tem leitura própria (ver base). Considere interferência concorrente.

TOM: fisiologista experiente falando com um atleta que é cientista. Técnico, direto, sem motivacional vazio, sem floreio. Cada frase carrega informação ou decisão."""

    # Formato adaptativo: curto por padrão, profundo quando há mudança relevante
    houve_mudanca = sinais.get("houve_mudanca_relevante") or modelo_cr.get("anomalia")
    modo = "PROFUNDO" if houve_mudanca else "CIRÚRGICO"

    instrucao_formato = """MODO CIRÚRGICO (dia normal, sem mudanças relevantes): seja breve e direto. Máximo ~180 palavras.
- Uma leitura rápida do estado (1-2 frases integrando recuperação/prontidão).
- Comentário do(s) treino(s) de hoje vs intenção inferida (1-2 frases por sessão, só o que importa).
- AÇÃO DO DIA: uma decisão clara e justificada.
Não encha de números que ele já viu no Garmin. Vá ao significado.""" if modo == "CIRÚRGICO" else """MODO PROFUNDO (algo mudou — sinal de severidade alta ou anomalia carga-resposta): análise completa. Até ~450 palavras.
- Abra pelo que mudou e por que importa (o insight principal).
- RECUPERAÇÃO E PRONTIDÃO: integre HRV (rMSSD vs HRV7 vs baseline, desvio %, status), Readiness e seus fatores, Stress Index, sono, FCrep — por CONVERGÊNCIA, conectando aos sinais detectados.
- CARGA E RESPOSTA: use o modelo carga-resposta. A resposta de hoje foi esperada para a carga de ontem ou anômala? Conecte com a intenção inferida das sessões.
- TREINO(S): cada sessão vs sua intenção inferida, leitura por modalidade, hipóteses causais calibradas para desvios.
- TENDÊNCIAS: o que os sinais longitudinais revelam (sequências, declínios, monotonia).
- AÇÃO E O QUE OBSERVAR: decisão de hoje + que dado confirmaria/mudaria a leitura amanhã."""

    user = f"""Gere o briefing de hoje em MODO {modo}.

{instrucao_formato}

Lembre: previsões de prova são de CORRIDA apenas — não as trate como foco se o dia for de outra modalidade.

=== DADOS DE HOJE ({dados['data']}) ===
{json.dumps(dados, indent=2, ensure_ascii=False)}

=== SINAIS DETECTADOS (motor determinístico de padrões) ===
{json.dumps(sinais, indent=2, ensure_ascii=False)}

=== CARGA DO DIA E INTENÇÕES INFERIDAS ===
{json.dumps(carga, indent=2, ensure_ascii=False)}

=== MODELO CARGA-RESPOSTA INDIVIDUAL ===
{json.dumps(modelo_cr, indent=2, ensure_ascii=False)}

=== WELLBEING SEMANAL (contexto subjetivo; o relógio não captura) ===
{json.dumps(bem_estar or {{"disponivel": False}}, indent=2, ensure_ascii=False)}

=== TREINO(S) PRESCRITO vs EXECUTADO (por modalidade) ===
{json.dumps(treino, indent=2, ensure_ascii=False)}

=== EXCLUSÃO CAUSAL ESTRUTURADA (causas descartadas vs sobreviventes) ===
{json.dumps(exclusoes or [], indent=2, ensure_ascii=False)}

=== DETECÇÃO DE NÃO-RESPOSTA / PLATÔ (trajetória carga vs fitness) ===
{json.dumps(nao_resposta or {{"aplicavel": False}}, indent=2, ensure_ascii=False)}

=== LACUNAS DE DADOS (o que pedir ao atleta para fechar ambiguidade) ===
{json.dumps(lacunas or [], indent=2, ensure_ascii=False)}

=== COMPARAÇÕES HISTÓRICAS (7d/30d/180d/365d) ===
{json.dumps(comparacoes, indent=2, ensure_ascii=False)}"""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2000,
        system=system,
        messages=[{"role": "user", "content": user}]
    )
    return response.content[0].text


def enviar_email(assunto: str, corpo: str, html_extra: str = ""):
    remetente = os.getenv("EMAIL_REMETENTE")
    senha_app = os.getenv("EMAIL_SENHA_APP")
    destinatario = os.getenv("EMAIL_DESTINATARIO")
    msg = MIMEMultipart("alternative")
    msg["Subject"] = assunto
    msg["From"] = remetente
    msg["To"] = destinatario

    # Texto puro (fallback)
    msg.attach(MIMEText(corpo, "plain", "utf-8"))

    # HTML: briefing formatado + formulario opcional
    corpo_html = corpo.replace("\n", "<br>")
    html = (
        '<div style="font-family:Arial,sans-serif;max-width:680px;margin:0 auto;'
        'font-size:15px;line-height:1.6;color:#222;">'
        f'{corpo_html}'
        f'{html_extra}'
        '</div>'
    )
    msg.attach(MIMEText(html, "html", "utf-8"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(remetente, senha_app)
        server.sendmail(remetente, destinatario, msg.as_string())
    print(f"Email enviado para {destinatario}")
