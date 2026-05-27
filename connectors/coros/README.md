# Conector: Coros

**Caminho recomendado:** Strava OAuth (sincronização auto entre Coros e Strava + API pública da Strava).
**Caminho técnico:** API oficial Coros em `apply.coros.com` (acesso de developer).

## Por quê esse caminho

Coros não tem app pra desktop e a API oficial exige developer access (leva dias). Mas o Coros sincroniza automaticamente com Strava, e Strava tem API pública estável (OAuth). 5 minutos de setup.

## Setup via Strava (recomendado)

1. No app Coros, ative `Auto-sync to Strava` (Configurações → Apps → Strava).
2. Crie um app em https://www.strava.com/settings/api:
   - Application Name: `Briefing Automatico` (ou qualquer)
   - Category: `Data Importer`
   - Authorization Callback Domain: `localhost`
3. Pegue `Client ID` e `Client Secret`.
4. Faça o OAuth flow uma vez pra pegar o `Refresh Token` (script de auth `auth.py` em construção).
5. Bota tudo no `.env`.
6. (em construção) Script `pull.py` que puxa atividades + wellness via API Strava.

## Setup via API oficial Coros (caminho técnico)

1. Solicite acesso em https://apply.coros.com (leva dias pra aprovar).
2. Crie OAuth app no painel.
3. Mesmo fluxo de Client ID / Secret no `.env`.
4. (em construção) Script `pull_coros_official.py`.

## Limitações

- HRV diário do Coros sincroniza com Strava? Verificar (a Strava nem sempre carrega todos os campos de wellness).
- Se faltar algum dado via Strava, o caminho oficial é mais completo.

## Status

🛠️ Em construção.
