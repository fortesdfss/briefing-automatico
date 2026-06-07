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

    instrucao_formato = """MODO CIRÚRGICO (dia normal): breve e direto. Abertura curta opcional. 2-3 seções no máximo, corpo de 1-2 frases cada. Vá ao significado, não aos números que ele já viu.""" if modo == "CIRÚRGICO" else """MODO PROFUNDO (algo mudou): análise completa. Abra pelo insight principal. Seções: Recuperação e Prontidão, Carga e Resposta, Treino(s), Tendências. Corpo denso mas claro."""

    formato_saida = """
FORMATO DE SAÍDA — responda APENAS com um objeto JSON válido, sem markdown, sem cercas de código, nesta estrutura exata:
{
  "abertura": "1-2 frases de abertura com o insight principal do dia, ou null se dia trivial",
  "secoes": [
    {"titulo": "Recuperação e Prontidão", "estado": "🟢|🟡|🔴", "corpo": "prosa interpretativa"},
    {"titulo": "...", "estado": "...", "corpo": "..."}
  ],
  "acao_do_dia": "uma recomendação específica e fisiologicamente justificada",
  "observacao_final": "observação leve (ex: wellbeing vencido) ou null"
}
Use os semáforos 🟢🟡🔴 no campo estado. O corpo de cada seção é prosa em português, tom de fisiologista. NÃO inclua nada fora do JSON."""

    user = f"""Gere o briefing de hoje em MODO {modo}.

{instrucao_formato}

{formato_saida}

Lembre: previsões de prova são de CORRIDA apenas. Exclusão causal como espinha dorsal do raciocínio. Não-resposta abre o dia se relevante. Lacunas no máximo 1-2 ao final.

=== DADOS DE HOJE ({dados['data']}) ===
{json.dumps(dados, indent=2, ensure_ascii=False)}

=== SINAIS DETECTADOS ===
{json.dumps(sinais, indent=2, ensure_ascii=False)}

=== CARGA E INTENÇÕES ===
{json.dumps(carga, indent=2, ensure_ascii=False)}

=== MODELO CARGA-RESPOSTA ===
{json.dumps(modelo_cr, indent=2, ensure_ascii=False)}

=== WELLBEING SEMANAL ===
{json.dumps(bem_estar or {{"disponivel": False}}, indent=2, ensure_ascii=False)}

=== TREINO(S) ===
{json.dumps(treino, indent=2, ensure_ascii=False)}

=== EXCLUSÃO CAUSAL ===
{json.dumps(exclusoes or [], indent=2, ensure_ascii=False)}

=== NÃO-RESPOSTA / PLATÔ ===
{json.dumps(nao_resposta or {{"aplicavel": False}}, indent=2, ensure_ascii=False)}

=== LACUNAS ===
{json.dumps(lacunas or [], indent=2, ensure_ascii=False)}

=== COMPARAÇÕES HISTÓRICAS ===
{json.dumps(comparacoes, indent=2, ensure_ascii=False)}"""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2000,
        system=system,
        messages=[{"role": "user", "content": user}]
    )
    texto = response.content[0].text.strip()

    # Parsing robusto do JSON
    estruturado = _parse_json_briefing(texto, dados)
    estruturado["modo"] = modo
    estruturado.setdefault("data", _data_br(dados["data"]))
    return estruturado


def _data_br(iso: str) -> str:
    try:
        from datetime import date as _d
        d = _d.fromisoformat(iso)
        return d.strftime("%d/%m/%Y")
    except Exception:
        return iso


def _parse_json_briefing(texto: str, dados: dict) -> dict:
    """Extrai o JSON do briefing, tolerante a cercas de código."""
    import re
    limpo = texto.strip()
    limpo = re.sub(r'^```(?:json)?', '', limpo).strip()
    limpo = re.sub(r'```$', '', limpo).strip()
    try:
        return json.loads(limpo)
    except Exception:
        # Fallback: tenta achar o primeiro { ... } balanceado
        ini = limpo.find('{')
        fim = limpo.rfind('}')
        if ini >= 0 and fim > ini:
            try:
                return json.loads(limpo[ini:fim+1])
            except Exception:
                pass
        # Último recurso: devolve o texto cru como uma seção única
        return {
            "abertura": None,
            "secoes": [{"titulo": "Briefing", "estado": "", "corpo": texto.replace(chr(10), "<br>")}],
            "acao_do_dia": "",
            "observacao_final": None,
        }


def _texto_puro(estruturado: dict) -> str:
    """Versão texto puro do briefing estruturado (fallback do email)."""
    linhas = []
    if estruturado.get("abertura"):
        linhas.append(estruturado["abertura"])
        linhas.append("")
    for s in estruturado.get("secoes", []):
        linhas.append(f"{s.get('estado','')} {s.get('titulo','').upper()}")
        # remove tags HTML simples do corpo
        import re
        corpo = re.sub(r'<[^>]+>', '', s.get("corpo", ""))
        linhas.append(corpo)
        linhas.append("")
    if estruturado.get("acao_do_dia"):
        linhas.append(f"AÇÃO DO DIA: {estruturado['acao_do_dia']}")
    if estruturado.get("observacao_final"):
        linhas.append("")
        linhas.append(estruturado["observacao_final"])
    return "\n".join(linhas)


def enviar_email(assunto: str, briefing_estruturado: dict, formulario_html: str = ""):
    from template_email import montar_email
    remetente = os.getenv("EMAIL_REMETENTE")
    senha_app = os.getenv("EMAIL_SENHA_APP")
    destinatario = os.getenv("EMAIL_DESTINATARIO")

    msg = MIMEMultipart("alternative")
    msg["Subject"] = assunto
    msg["From"] = remetente
    msg["To"] = destinatario

    # Fallback texto puro + HTML premium
    msg.attach(MIMEText(_texto_puro(briefing_estruturado), "plain", "utf-8"))
    html = montar_email(briefing_estruturado, formulario_html)
    msg.attach(MIMEText(html, "html", "utf-8"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(remetente, senha_app)
        server.sendmail(remetente, destinatario, msg.as_string())
    print(f"Email enviado para {destinatario}")
