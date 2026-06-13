/**
 * Vercel Serverless Function — /api/wellbeing
 *
 * GET  /api/wellbeing              → formulário premium com todos os 5 campos
 * POST /api/wellbeing  (JSON body) → registra todos os campos de uma vez
 * GET  /api/wellbeing?campo=X&valor=Y → legacy (mantido para compatibilidade)
 */

const REPO  = "fortesdfss/briefing-automatico";
const LABEL = "wellbeing";

const CAMPOS = [
  { nome: "sono_qualidade",   label: "Qualidade do sono",          max: 7, descBaixo: "excelente", descAlto: "péssima"   },
  { nome: "fadiga",           label: "Fadiga geral",               max: 7, descBaixo: "muito baixa", descAlto: "exausto" },
  { nome: "estresse",         label: "Estresse de vida",           max: 7, descBaixo: "muito baixo", descAlto: "muito alto" },
  { nome: "dores_musculares", label: "Dores musculares (DOMS)",    max: 7, descBaixo: "nenhuma",   descAlto: "intensas"  },
  { nome: "motivacao",        label: "Motivação para treinar",     max: 5, descBaixo: "nenhuma",   descAlto: "altíssima" },
];

const CAMPOS_VALIDOS = Object.fromEntries(CAMPOS.map(c => [c.nome, [1, c.max]]));

// ─── Paleta e tipografia (espelha template_email.py) ──────────────────────────
const COR_TINTA   = "#1a1a1a";
const COR_TEXTO   = "#33312e";
const COR_SUAVE   = "#7a756e";
const COR_LINHA   = "#e4e0d9";
const COR_FUNDO   = "#f4f2ed";
const COR_PAPEL   = "#fffefb";
const COR_VERDE   = "#1f8a4c";
const COR_AMBAR   = "#e0a106";
const COR_VERM    = "#cf3030";

function paginaFormulario() {
  const escalas = CAMPOS.map(c => {
    const botoes = Array.from({ length: c.max }, (_, i) => i + 1).map(v => `
      <button type="button"
        data-campo="${c.nome}" data-valor="${v}"
        onclick="selecionar(this)"
        style="width:44px;height:44px;margin:3px;border:1.5px solid ${COR_LINHA};
               border-radius:5px;background:${COR_PAPEL};color:${COR_TEXTO};
               font-family:'Helvetica Neue',Helvetica,Arial,sans-serif;
               font-size:15px;font-weight:600;cursor:pointer;transition:all .15s;"
        onmouseover="this.style.borderColor='${COR_TINTA}'"
        onmouseout="if(!this.classList.contains('sel'))this.style.borderColor='${COR_LINHA}'"
      >${v}</button>`).join("");

    return `
    <div style="border-top:1px solid ${COR_LINHA};padding:22px 0 6px;">
      <div style="font-family:'Helvetica Neue',Helvetica,Arial,sans-serif;
                  font-size:11px;letter-spacing:1.5px;text-transform:uppercase;
                  color:${COR_TINTA};font-weight:700;margin-bottom:6px;">${c.label}</div>
      <div style="font-size:11px;color:${COR_SUAVE};margin-bottom:10px;
                  font-family:'Helvetica Neue',Helvetica,Arial,sans-serif;">
        1 = ${c.descBaixo} &nbsp;·&nbsp; ${c.max} = ${c.descAlto}
      </div>
      <div id="scale-${c.nome}">${botoes}</div>
    </div>`;
  }).join("");

  return `<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Check-in Semanal</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,600;1,500&display=swap" rel="stylesheet">
  <style>
    * { box-sizing: border-box; }
    body { margin:0; padding:32px 16px; background:${COR_FUNDO};
           font-family:'Iowan Old Style','Palatino Linotype',Palatino,Georgia,serif; }
    .card { background:${COR_PAPEL}; border:1px solid ${COR_LINHA}; border-radius:4px;
            max-width:560px; margin:0 auto; padding:40px 44px 44px; }
    .btn-enviar { width:100%;padding:16px;margin-top:32px;background:${COR_TINTA};
                  color:#f7f5f1;border:none;border-radius:4px;cursor:pointer;
                  font-family:'Helvetica Neue',Helvetica,Arial,sans-serif;
                  font-size:13px;letter-spacing:2px;text-transform:uppercase;font-weight:700; }
    .btn-enviar:disabled { opacity:.45;cursor:not-allowed; }
    .btn-sel { background:${COR_TINTA} !important; color:#f7f5f1 !important;
               border-color:${COR_TINTA} !important; }
    #msg { display:none;text-align:center;padding:40px 0; }
    #msg .emoji { font-size:48px;margin-bottom:16px; }
    #msg .texto { font-family:'Helvetica Neue',Helvetica,Arial,sans-serif;
                  font-size:16px;color:${COR_TEXTO};line-height:1.6; }
    @media(max-width:500px){.card{padding:28px 20px 32px;}}
  </style>
</head>
<body>
<div class="card">
  <div style="border-bottom:2px solid ${COR_TINTA};padding-bottom:22px;margin-bottom:8px;">
    <div style="font-family:'Cormorant Garamond',Garamond,'Times New Roman',serif;
                font-size:24px;font-weight:600;color:${COR_TINTA};letter-spacing:1px;">
      Diego Salgueiro<span style="font-size:15px;color:${COR_SUAVE};font-weight:500;">, PhD</span>
    </div>
    <div style="font-family:'Helvetica Neue',Helvetica,Arial,sans-serif;font-size:11px;
                letter-spacing:2px;text-transform:uppercase;color:${COR_SUAVE};
                margin-top:8px;font-weight:600;">Check-in Semanal de Wellbeing</div>
    <div style="font-family:'Iowan Old Style',Palatino,Georgia,serif;font-size:14px;
                color:${COR_SUAVE};margin-top:8px;line-height:1.5;">
      Escala Hooper-Mackinnon. Selecione um valor por item e envie.
    </div>
  </div>

  <div id="form">
    ${escalas}
    <button class="btn-enviar" id="btnEnviar" onclick="enviar()" disabled>
      Enviar check-in
    </button>
  </div>

  <div id="msg">
    <div class="emoji">✅</div>
    <div class="texto">Check-in registrado com sucesso.<br>Pode fechar esta aba.</div>
  </div>
</div>

<script>
  const selecionados = {};

  function selecionar(btn) {
    const campo = btn.dataset.campo;
    const escala = document.getElementById('scale-' + campo);
    escala.querySelectorAll('button').forEach(b => {
      b.classList.remove('sel','btn-sel');
      b.style.background = '${COR_PAPEL}';
      b.style.color = '${COR_TEXTO}';
      b.style.borderColor = '${COR_LINHA}';
    });
    btn.classList.add('sel','btn-sel');
    btn.style.background = '${COR_TINTA}';
    btn.style.color = '#f7f5f1';
    btn.style.borderColor = '${COR_TINTA}';
    selecionados[campo] = parseInt(btn.dataset.valor);

    const total = ${CAMPOS.length};
    document.getElementById('btnEnviar').disabled = Object.keys(selecionados).length < total;
  }

  async function enviar() {
    const btn = document.getElementById('btnEnviar');
    btn.disabled = true;
    btn.textContent = 'Registrando…';
    try {
      const r = await fetch('/api/wellbeing', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(selecionados),
      });
      if (!r.ok) throw new Error(await r.text());
      document.getElementById('form').style.display = 'none';
      document.getElementById('msg').style.display = 'block';
    } catch(e) {
      btn.disabled = false;
      btn.textContent = 'Enviar check-in';
      alert('Erro ao registrar. Tente novamente.');
    }
  }
</script>
</body>
</html>`;
}

async function criarIssue(token, campo, valor) {
  const titulo = `wellbeing:${campo}=${valor}`;
  const resp = await fetch(`https://api.github.com/repos/${REPO}/issues`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      Accept: "application/vnd.github+json",
      "X-GitHub-Api-Version": "2022-11-28",
      "Content-Type": "application/json",
      "User-Agent": "briefing-automatico-wellbeing",
    },
    body: JSON.stringify({ title: titulo, labels: [LABEL] }),
  });
  if (!resp.ok) {
    const txt = await resp.text();
    throw new Error(`GitHub API ${resp.status}: ${txt}`);
  }
}

export default async function handler(req, res) {
  // GET sem parâmetros → formulário
  if (req.method === "GET" && !req.query.campo) {
    res.setHeader("Content-Type", "text/html; charset=utf-8");
    return res.status(200).send(paginaFormulario());
  }

  // GET com campo+valor → legacy single-field
  if (req.method === "GET" && req.query.campo) {
    const { campo, valor } = req.query;
    if (!CAMPOS_VALIDOS[campo]) {
      res.setHeader("Content-Type", "application/json");
      return res.status(400).json({ erro: "Campo inválido." });
    }
    const v = parseInt(valor, 10);
    const [lo, hi] = CAMPOS_VALIDOS[campo];
    if (isNaN(v) || v < lo || v > hi) {
      res.setHeader("Content-Type", "application/json");
      return res.status(400).json({ erro: `Valor inválido para ${campo}.` });
    }
    const token = process.env.GITHUB_TOKEN;
    if (!token) return res.status(500).json({ erro: "Configuração ausente." });
    await criarIssue(token, campo, v);
    res.setHeader("Content-Type", "application/json");
    return res.status(200).json({ ok: true, campo, valor: v });
  }

  // POST com body JSON → registra todos os campos
  if (req.method === "POST") {
    const token = process.env.GITHUB_TOKEN;
    if (!token) return res.status(500).json({ erro: "Configuração ausente." });

    const body = req.body || {};
    const erros = [];
    const validos = [];

    for (const [campo, valor] of Object.entries(body)) {
      if (!CAMPOS_VALIDOS[campo]) { erros.push(`campo inválido: ${campo}`); continue; }
      const v = parseInt(valor, 10);
      const [lo, hi] = CAMPOS_VALIDOS[campo];
      if (isNaN(v) || v < lo || v > hi) { erros.push(`valor inválido: ${campo}=${valor}`); continue; }
      validos.push({ campo, valor: v });
    }

    if (validos.length === 0) {
      return res.status(400).json({ erro: "Nenhum campo válido.", detalhes: erros });
    }

    await Promise.all(validos.map(({ campo, valor }) => criarIssue(token, campo, valor)));

    res.setHeader("Content-Type", "application/json");
    return res.status(200).json({ ok: true, registrados: validos.length, erros });
  }

  return res.status(405).json({ erro: "Método não permitido." });
}
