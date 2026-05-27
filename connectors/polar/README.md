# Conector: Polar

**Caminho:** Polar Accesslink API (OFICIAL — a mais developer-friendly entre relógios esportivos).

## Por quê

Polar tem a API mais completa e amigável: free tier, OAuth, HRV, sono, treino, recovery — tudo no padrão. Sem dependência de terceiros, sem hack.

## Setup

1. Crie um app em https://www.polar.com/accesslink-api/ (free, instantâneo).
2. Pegue `Client ID` e `Client Secret`.
3. Faça o OAuth flow e salve o `Access Token`:
   - Callback URL no painel Polar: `http://localhost:8000/callback`
   - (em construção) Script `auth.py` que abre o browser, recebe o callback e salva o token.
4. Bota tudo no `.env`.
5. (em construção) Script `pull.py` que puxa diariamente: HRV Nightly Recharge, sono, treino, Cardio Load.

## Endpoints úteis (Accesslink v3)

- `/v3/users/continuous-heart-rate/{date}` — HRV detalhado
- `/v3/users/sleep` — análise de sono
- `/v3/users/nightly-recharge` — recovery score
- `/v3/users/exercise-transactions` — treinos
- `/v3/users/activity-transactions` — atividade diária

## Status

🛠️ Em construção. Pretendo deixar esse conector como referência (caminho mais limpo).
