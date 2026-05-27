# briefing-automatico

> Repo companheiro dos posts do [@jppace__](https://www.instagram.com/jppace__/)
>
> **Briefing diário automático** dos dados do seu relógio (Apple Watch · Coros · Polar · Amazfit · Garmin) cruzados com a sua IA local, todo dia no mesmo horário.

## ⚠️ Aviso de segurança (leia antes de qualquer coisa)

- **Este repo NÃO usa minhas credenciais.** Você conecta com a sua conta. Os dados ficam no SEU computador. Eu não vejo nada.
- **Nunca commite o `.env`.** Use `.env.example` como template e crie seu `.env` localmente (já no `.gitignore`).
- **Scopes mínimos** nas APIs OAuth (Polar, Strava/Coros). O repo pede só leitura de wellness e atividade. Nada de gravação.
- **Privacy by default.** Os dados nunca saem da sua máquina, EXCETO quando você manda pra IA processar. Se for IA local (Claude Code), 100% offline.

### Disclaimer do conector Garmin

O conector Garmin usa a lib comunitária `python-garminconnect` (**não-oficial**). A Garmin pode quebrar a integração a qualquer atualização ou solicitar takedown. Os outros 4 conectores (Apple Health, Coros via Strava, Polar Accesslink, Amazfit via Zepp+Apple Health) usam **APIs ou exports oficiais** e tendem a ser mais estáveis.

---

## A ideia em 30 segundos

Toda manhã, às 9h, um script puxa seus dados do relógio (HRV, sono, readiness, carga, VO2max, peso, previsão de prova) e gera um arquivo `.md` com semáforos 🟢🟡🔴. Aí você abre sua IA (Claude Code, ChatGPT desktop, etc.) e pede um briefing: ela lê o arquivo, cruza com seu contexto (exames, plano da nutri, planilha do treinador, fase da prova) e devolve a **ação do dia**.

**Arquitetura em 2 camadas:**

- **Camada 1 (script determinístico):** calcula os números crus. Sempre o mesmo formato. Zero alucinação.
- **Camada 2 (IA):** lê esses números no seu contexto e devolve uma decisão. Não recalcula nada.

> Código pra não mentir. IA pra ler o todo.

---

## Estrutura do repo

```
briefing-automatico/
├── README.md
├── LICENSE
├── .gitignore
├── .env.example
├── connectors/         ← um por marca de relógio (escolhe o seu)
│   ├── apple-watch/
│   ├── coros/
│   ├── polar/
│   ├── amazfit/
│   └── garmin/
├── briefing/           ← template e gerador da Camada 1
├── scheduler/          ← como rodar todo dia às 9h (Mac/Win/Linux)
└── prompts/            ← prompts da Camada 2 (interpretação por IA)
```

## Quickstart

1. **Escolhe o conector** do seu relógio em `connectors/{sua-marca}/`. Lê o README de lá pra ver os passos.
2. **Copia `.env.example` pra `.env`** e preenche as credenciais (só do seu conector).
3. **Roda o script** uma vez manualmente pra testar.
4. **Agenda** pelo `scheduler/` (launchd no Mac, Task Scheduler no Windows, cron no Linux).
5. **Manda o arquivo `.md`** pra sua IA todo dia + o prompt da Camada 2 (em `prompts/claude-layer2.md`).

> Cada README de conector tem o passo a passo específico. Comece pelo seu relógio.

## Status dos conectores

| Relógio | Caminho | Stack | Status |
|---|---|---|---|
| Apple Watch | Apple Health export (app Health Auto Export → iCloud) | Shell + JSON | 🛠️ em construção |
| Coros | Strava OAuth (atalho) ou API oficial | Python + OAuth | 🛠️ em construção |
| Polar | Accesslink API (oficial) | Python + OAuth | 🛠️ em construção |
| Amazfit | Zepp → Apple Health (caminho indireto) | Shell + JSON | 🛠️ em construção |
| Garmin | python-garminconnect (não-oficial) | Python | 🛠️ em construção |

## Contribuir

Issues e PRs bem-vindos. O repo nasceu pra ser usado e melhorado pela comunidade. Se você implementou seu conector de um jeito diferente, manda.

## Licença

MIT. Use, modifique, distribua. Sem garantia.

---

*Mantenedor: [JP Perpetuo](https://www.instagram.com/jppace__/). Atleta de endurance, founder, não-dev. Construindo isso porque não achei pronto.*
