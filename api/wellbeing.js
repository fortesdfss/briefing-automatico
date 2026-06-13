/**
 * Vercel Serverless Function — POST/GET /api/wellbeing
 *
 * Recebe campo=X&valor=Y, cria uma GitHub Issue via API,
 * e retorna uma página HTML de confirmação.
 * O workflow transcrever_wellbeing.yml processa a issue normalmente.
 */

const REPO  = "fortesdfss/briefing-automatico";
const LABEL = "wellbeing";

const CAMPOS_VALIDOS = {
  sono_qualidade:   [1, 7],
  fadiga:           [1, 7],
  estresse:         [1, 7],
  dores_musculares: [1, 7],
  motivacao:        [1, 5],
};

const LABELS = {
  sono_qualidade:   "Qualidade do sono",
  fadiga:           "Fadiga",
  estresse:         "Estresse",
  dores_musculares: "Dores musculares",
  motivacao:        "Motivação",
};

function paginaConfirmacao(campo, valor, erro) {
  const label = LABELS[campo] || campo;
  const [ok, mensagem, emoji] = erro
    ? [false, erro, "⚠️"]
    : [true, `<strong>${label}</strong>: ${valor} registrado com sucesso.`, "✅"];

  return `<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>${emoji} Wellbeing</title>
  <style>
    body { font-family: -apple-system, Arial, sans-serif; display: flex;
           justify-content: center; align-items: center; min-height: 100vh;
           margin: 0; background: #f4f2ed; }
    .card { background: #fffefb; border: 1px solid #e4e0d9; border-radius: 8px;
            padding: 40px 48px; max-width: 400px; text-align: center; }
    .emoji { font-size: 48px; margin-bottom: 16px; }
    .msg { font-size: 17px; color: #33312e; line-height: 1.6; }
    .fechar { margin-top: 28px; font-size: 13px; color: #7a756e; }
  </style>
</head>
<body>
  <div class="card">
    <div class="emoji">${emoji}</div>
    <div class="msg">${mensagem}</div>
    <div class="fechar">Pode fechar esta aba.</div>
  </div>
</body>
</html>`;
}

export default async function handler(req, res) {
  const { campo, valor } = req.method === "POST"
    ? req.body
    : req.query;

  // Validação
  if (!campo || !CAMPOS_VALIDOS[campo]) {
    res.setHeader("Content-Type", "text/html; charset=utf-8");
    return res.status(400).send(paginaConfirmacao(campo, valor, "Campo inválido."));
  }

  const v = parseInt(valor, 10);
  const [lo, hi] = CAMPOS_VALIDOS[campo];
  if (isNaN(v) || v < lo || v > hi) {
    res.setHeader("Content-Type", "text/html; charset=utf-8");
    return res.status(400).send(paginaConfirmacao(campo, valor, `Valor inválido para ${campo} (esperado ${lo}–${hi}).`));
  }

  const token = process.env.GITHUB_TOKEN;
  if (!token) {
    res.setHeader("Content-Type", "text/html; charset=utf-8");
    return res.status(500).send(paginaConfirmacao(campo, valor, "Configuração ausente no servidor."));
  }

  // Cria a issue no GitHub
  const titulo = `wellbeing:${campo}=${v}`;
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
    console.error("GitHub API error:", resp.status, txt);
    res.setHeader("Content-Type", "text/html; charset=utf-8");
    return res.status(502).send(paginaConfirmacao(campo, valor, "Erro ao registrar. Tente novamente."));
  }

  res.setHeader("Content-Type", "text/html; charset=utf-8");
  return res.status(200).send(paginaConfirmacao(campo, valor, null));
}
