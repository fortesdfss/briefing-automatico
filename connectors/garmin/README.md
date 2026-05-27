# Conector: Garmin

> ⚠️ **AVISO IMPORTANTE:** Este conector usa a lib comunitária `python-garminconnect` (**NÃO-OFICIAL**). A Garmin pode quebrar a integração a qualquer atualização ou solicitar takedown. **Se você tem outro relógio, prefere os caminhos oficiais (Polar, Apple Health, Strava).**

## Por quê esse caminho

A Garmin não tem API pública pra usuários comuns. A Connect IQ é pra device (programar watch faces), não pra leitura de dados. A lib `python-garminconnect` (mantida por [@cyberjunky](https://github.com/cyberjunky/python-garminconnect)) faz scraping autenticado da Garmin Connect com login do usuário e funciona bem **enquanto a Garmin não muda nada**.

Risco real mas baixo. Vale a pena pra quem JÁ tem Garmin (a maioria dos atletas de endurance).

## Setup

1. Garanta Python 3.9+.
2. Instale: `pip install garminconnect`.
3. Bota email e senha do Garmin no `.env` (`GARMIN_EMAIL` e `GARMIN_PASSWORD`).
4. **Se sua conta tem MFA:**
   - **Authenticator app:** consiga o seed key (não o código de 6 dígitos — o seed key, geralmente visível ao configurar 2FA). Bota em `GARMIN_TOTP_SECRET`. A lib usa `pyotp` pra gerar o código a cada login.
   - **SMS:** na primeira execução, login interativo (você digita o código que chega). A lib salva o session token em `~/.garmin-tokens/` e as próximas rodadas não pedem mais. Quando a sessão expirar (~meses), repete o flow.
5. (em construção) Script `pull.py`.

## Dados que dá pra puxar

- HRV diário e baseline (Status HRV)
- Body Battery
- Sleep Score (com fases)
- Training Status (Productive, Maintaining, Recovery, Unproductive, etc.)
- Training Load (acute/chronic ratio - ACWR)
- VO2max
- Race Predictor
- Atividades (com splits, pace, FC)
- Peso (se sincronizado)

## Status

🛠️ Em construção. Funcional na máquina do mantenedor desde maio/2026. Código vem em PR.
