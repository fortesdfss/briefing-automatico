# Conector: Apple Watch

**Caminho:** Apple Health export (JSON) via app Health Auto Export → iCloud Drive → script no Mac.

## Por quê esse caminho

A Apple não tem API web pública pro Health. Mas o Health do iPhone tem TUDO: HRV, sono, VO2max, ritmo. A solução é exportar do iPhone pro iCloud Drive e ler do Mac.

## Setup

1. Instale **Health Auto Export** na App Store (pago, ~R$50, vale).
2. No app, configure exportação diária em **JSON** pra uma pasta no **iCloud Drive** (`HealthExports/`).
3. Selecione os campos: `Heart Rate Variability`, `Sleep Analysis`, `VO2 Max`, `Active Energy`, `Workout`, `Body Mass`, `Resting Heart Rate`.
4. No Mac, garanta que o iCloud Drive tá sincronizando a pasta (deve aparecer em `~/Library/Mobile Documents/com~apple~CloudDocs/HealthExports/`).
5. Preencha `APPLE_HEALTH_EXPORT_PATH` no `.env`.
6. (em construção) Script `pull.py` que lê o JSON mais recente e produz o briefing.

## Limitações

- Depende do iPhone exportar (precisa o app aberto pelo menos 1x por dia).
- VO2max do Apple Watch é estimado de modo diferente do Garmin/Polar, calibração diferente.

## Status

🛠️ Em construção. README pronto, código vem.
