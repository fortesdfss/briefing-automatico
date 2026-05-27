# Conector: Amazfit / Zepp

**Caminho:** indireto, via Apple Health.

## Por quê esse caminho

Zepp Health (app oficial do Amazfit) **não tem API pública**. Mas ele sincroniza com Apple Health, e dali a gente lê (mesmo fluxo do conector `apple-watch/`).

## Setup

1. No app **Zepp**, vá em Configurações → Integrações → ative **`Connect to Apple Health`**.
2. Selecione os campos pra sincronizar:
   - ✅ HRV (Heart Rate Variability)
   - ✅ Sleep Analysis
   - ✅ Active Energy
   - ✅ Workout
   - ✅ Resting Heart Rate
   - ✅ Body Mass
   - ⚠️ PAI e Body Composition (Zepp-only, não sincronizam pro Health)
3. Siga o setup do conector `apple-watch/` (Health Auto Export → iCloud).
4. (em construção) Script de filtragem pra normalizar os campos vindos do Zepp (mapear nomes / unidades).

## Limitações

- **PAI Score** e dados de **composição corporal** não viajam pro Apple Health. Pra HRV, sono e treino, funciona bem.
- Watch faces e métricas proprietárias do Zepp ficam de fora.
- Latência: Zepp → Health (alguns minutos) + Health Auto Export (1 vez por dia).

## Caminho alternativo (avançado, por sua conta e risco)

Existem parsers comunitários no GitHub que fazem reverse engineering da API privada do Zepp. **Não recomendo** pra produção. Risco de quebrar + tos.

## Status

🛠️ Em construção.
