"""
TEMPLATE DE EMAIL PREMIUM — estética clínica (estilo laudo Revive)
Determinístico: recebe o conteúdo estruturado do fisiologista e monta HTML
robusto para clientes de email (tabelas, cores inline, tipografia clássica).

Não depende do Claude gerar HTML — o visual é sempre impecável.
"""

from datetime import date

# Paleta clínica sóbria
COR_TINTA = "#1a1a1a"       # quase preto
COR_TEXTO = "#33312e"       # tinta de leitura, levemente quente
COR_SUAVE = "#7a756e"       # cinza secundário quente
COR_LINHA = "#e4e0d9"       # bordas suaves
COR_FUNDO = "#f4f2ed"       # off-white quente
COR_PAPEL = "#fffefb"       # papel creme
COR_VERDE = "#1f8a4c"
COR_AMBAR = "#e0a106"
COR_VERMELHO = "#cf3030"

# Stacks tipográficas
FONTE_TITULO = "'Cormorant Garamond', 'Hoefler Text', 'Iowan Old Style', Garamond, 'Times New Roman', serif"
FONTE_CORPO = "'Iowan Old Style', 'Palatino Linotype', Palatino, 'Book Antiqua', Georgia, serif"
FONTE_ROTULO = "'Helvetica Neue', Helvetica, Arial, sans-serif"

SEMAFORO_COR = {"🟢": COR_VERDE, "🟡": COR_AMBAR, "🔴": COR_VERMELHO,
                "verde": COR_VERDE, "amarelo": COR_AMBAR, "vermelho": COR_VERMELHO}


def _semaforo_badge(estado: str) -> str:
    cor = SEMAFORO_COR.get(estado, COR_SUAVE)
    return (f'<span style="display:inline-block;width:13px;height:13px;border-radius:50%;'
            f'background:{cor};margin-right:10px;vertical-align:middle;'
            f'box-shadow:0 0 0 3px {COR_PAPEL}, 0 0 0 4px {cor}33;"></span>')


def _secao(titulo: str, estado: str, corpo: str) -> str:
    """Uma seção do laudo: título com semáforo + corpo em prosa."""
    badge = _semaforo_badge(estado) if estado else ""
    return f"""
    <tr><td style="padding:0 44px;">
      <table width="100%" cellpadding="0" cellspacing="0" style="border-top:1px solid {COR_LINHA};margin:0;">
        <tr><td style="padding:26px 0 0 0;">
          <div style="font-family:{FONTE_ROTULO};font-size:12px;letter-spacing:1.5px;
                      text-transform:uppercase;color:{COR_TINTA};font-weight:700;margin-bottom:13px;">
            {badge}{titulo}
          </div>
          <div style="font-family:{FONTE_CORPO};font-size:16.5px;line-height:1.78;
                      color:{COR_TEXTO};font-weight:400;">
            {corpo}
          </div>
        </td></tr>
      </table>
    </td></tr>"""


def _acao_destaque(texto: str) -> str:
    """Bloco de ação do dia — destaque com fundo escuro."""
    return f"""
    <tr><td style="padding:32px 44px 0 44px;">
      <table width="100%" cellpadding="0" cellspacing="0" style="background:{COR_TINTA};border-radius:3px;">
        <tr><td style="padding:26px 30px;">
          <div style="font-family:{FONTE_ROTULO};font-size:11px;letter-spacing:2px;text-transform:uppercase;
                      color:#b0aaa1;margin-bottom:11px;font-weight:700;">Conduta do dia</div>
          <div style="font-family:{FONTE_CORPO};font-size:17.5px;line-height:1.66;color:#f7f5f1;font-weight:400;">
            {texto}
          </div>
        </td></tr>
      </table>
    </td></tr>"""


def bloco_wellbeing_html(bem_estar: dict) -> str:
    """Bloco visual com os scores de wellbeing, quando disponível e não vencido."""
    if not bem_estar or not bem_estar.get("disponivel") or bem_estar.get("vencido"):
        return ""

    campos = [
        ("sono_qualidade", "Sono", 7),
        ("fadiga",         "Fadiga", 7),
        ("estresse",       "Estresse", 7),
        ("dores_musculares", "Dores musculares", 7),
        ("motivacao",      "Motivação", 5),
    ]

    def cor_badge(valor, maximo):
        if valor is None:
            return COR_SUAVE
        ratio = valor / maximo
        if ratio <= 0.35:
            return COR_VERDE
        if ratio <= 0.65:
            return COR_AMBAR
        return COR_VERMELHO

    itens = ""
    for campo, label, maximo in campos:
        v = bem_estar.get(campo)
        if v is None:
            continue
        cor = cor_badge(v, maximo)
        itens += (
            f'<span style="display:inline-flex;align-items:center;margin:4px 10px 4px 0;'
            f'font-family:{FONTE_ROTULO};font-size:12px;color:{COR_TEXTO};">'
            f'<span style="display:inline-block;width:9px;height:9px;border-radius:50%;'
            f'background:{cor};margin-right:6px;flex-shrink:0;"></span>'
            f'{label}: <strong style="margin-left:4px;">{v}/{maximo}</strong></span>'
        )

    if not itens:
        return ""

    data_reg = bem_estar.get("data_registro", "")
    dias = bem_estar.get("dias_desde_registro")
    legenda = f"registrado em {data_reg}" if not dias else (
        "hoje" if dias == 0 else f"há {dias} dia{'s' if dias > 1 else ''}"
    )

    return f"""
    <tr><td style="padding:26px 44px 0 44px;">
      <div style="border:1px solid {COR_LINHA};border-radius:3px;padding:18px 20px;">
        <div style="font-family:{FONTE_ROTULO};font-size:11px;letter-spacing:1.5px;
                    text-transform:uppercase;color:{COR_SUAVE};font-weight:700;margin-bottom:12px;">
          Wellbeing subjetivo <span style="font-weight:400;letter-spacing:0;">— {legenda}</span>
        </div>
        <div style="line-height:1.8;">{itens}</div>
      </div>
    </td></tr>"""


def montar_email(briefing_estruturado: dict, formulario_html: str = "", bem_estar: dict = None) -> str:
    """
    briefing_estruturado esperado:
    {
      "data": "07/06/2026",
      "modo": "CIRÚRGICO" | "PROFUNDO",
      "abertura": "texto de abertura (1-2 frases) ou None",
      "secoes": [{"titulo":"Recuperação e Prontidão","estado":"🟡","corpo":"..."}, ...],
      "acao_do_dia": "texto",
      "observacao_final": "texto leve ou None"
    }
    """
    data = briefing_estruturado.get("data", date.today().strftime("%d/%m/%Y"))
    abertura = briefing_estruturado.get("abertura")
    secoes = briefing_estruturado.get("secoes", [])
    acao = briefing_estruturado.get("acao_do_dia", "")
    obs = briefing_estruturado.get("observacao_final")

    secoes_html = "".join(
        _secao(s.get("titulo", ""), s.get("estado", ""), s.get("corpo", ""))
        for s in secoes
    )

    abertura_html = ""
    if abertura:
        abertura_html = f"""
        <tr><td style="padding:10px 44px 0 44px;">
          <div style="font-family:{FONTE_TITULO};font-size:21px;line-height:1.5;color:{COR_TINTA};
                      font-style:italic;font-weight:500;border-left:2px solid {COR_TINTA};padding-left:22px;">
            {abertura}
          </div>
        </td></tr>"""

    obs_html = ""
    if obs:
        obs_html = f"""
        <tr><td style="padding:26px 44px 0 44px;">
          <div style="font-family:{FONTE_CORPO};font-size:14px;line-height:1.65;color:{COR_SUAVE};
                      font-style:italic;">{obs}</div>
        </td></tr>"""

    wellbeing_html = bloco_wellbeing_html(bem_estar) if bem_estar else ""

    form_html = ""
    if formulario_html:
        form_html = f'<tr><td style="padding:26px 44px 0 44px;">{formulario_html}</td></tr>'

    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,600;1,500&display=swap" rel="stylesheet">
</head>
<body style="margin:0;padding:0;background:{COR_FUNDO};">
<table width="100%" cellpadding="0" cellspacing="0" style="background:{COR_FUNDO};padding:36px 0;">
<tr><td align="center">
  <table width="640" cellpadding="0" cellspacing="0" style="background:{COR_PAPEL};max-width:640px;
         border:1px solid {COR_LINHA};">

    <!-- Cabeçalho -->
    <tr><td style="padding:44px 44px 28px 44px;border-bottom:2px solid {COR_TINTA};">
      <table width="100%" cellpadding="0" cellspacing="0"><tr>
        <td style="font-family:{FONTE_TITULO};font-size:27px;letter-spacing:1.5px;color:{COR_TINTA};
                   font-weight:600;line-height:1.1;">
          Diego Salgueiro<span style="font-size:16px;color:{COR_SUAVE};font-weight:500;letter-spacing:1px;">, PhD</span>
        </td>
        <td align="right" valign="bottom" style="font-family:{FONTE_CORPO};font-size:13px;color:{COR_SUAVE};letter-spacing:0.5px;">
          {data}
        </td>
      </tr></table>
      <div style="font-family:{FONTE_ROTULO};font-size:11px;letter-spacing:2px;text-transform:uppercase;
                  color:{COR_SUAVE};margin-top:10px;font-weight:600;">Briefing Fisiológico Diário</div>
    </td></tr>

    {abertura_html}

    <!-- Seções -->
    <tr><td style="padding-top:24px;"></td></tr>
    {secoes_html}

    {_acao_destaque(acao)}

    {wellbeing_html}

    {obs_html}

    {form_html}

    <!-- Rodapé -->
    <tr><td style="padding:36px 44px 32px 44px;">
      <div style="border-top:1px solid {COR_LINHA};padding-top:20px;
                  font-family:{FONTE_CORPO};font-size:12px;line-height:1.65;color:#a8a29a;font-style:italic;">
        As inferências causais são hipóteses calibradas, não diagnósticos.
      </div>
    </td></tr>

  </table>
</td></tr>
</table>
</body></html>"""
