# Prompts da Camada 2 (a IA interpretando)

A Camada 2 é onde a IA pega o briefing determinístico (`.md` gerado pela Camada 1) e cruza com o **contexto pessoal** pra devolver a **ação do dia**.

## Princípio

A IA **não recalcula nada**. Os números vêm da Camada 1 (script). A IA só **lê e decide** considerando:

- O briefing daquele dia
- Seu histórico (memória da conversa ou arquivo de histórico que você passe)
- Seus exames de sangue
- O plano da nutri
- A planilha do treinador
- A fase da prova (taper, base, peak, etc.)

## Arquivos

- `claude-layer2.md` — (em construção) prompt principal pra Claude / ChatGPT desktop
- `claude-cli-systemprompt.md` — (em construção) system prompt pra Claude Code (caso você use a CLI)

## Como usar

1. Roda o conector de manhã (automatizado via `scheduler/`).
2. Abre sua IA (Claude Code, ChatGPT desktop, etc.).
3. Cola o conteúdo de `prompts/claude-layer2.md` (ou anexa) + o `.md` gerado pela Camada 1.
4. Pede: **"briefing de hoje"**.
5. A IA devolve a ação do dia, considerando o contexto.

## Status

🛠️ Em construção.
