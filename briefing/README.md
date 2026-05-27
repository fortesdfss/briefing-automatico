# Camada 1: O briefing determinístico

Template e gerador do arquivo `.md` que a IA vai ler todo dia.

## Princípio

Tudo aqui é determinístico. **Sem IA. Sem alucinação.** Os números são CALCULADOS a partir dos dados brutos do seu conector, nunca inventados. O formato é sempre o mesmo, o que dá pra IA um ponto de partida confiável pra Camada 2.

## Estrutura do `.md` de saída

```markdown
☀️ Briefing diário — {YYYY-MM-DD} · T-{X} {prova}

🛌 Recuperação {🟢|🟡|🔴} — HRV {valor}ms (média 14d {média}) · Sono {score}/100 · Readiness {n}/100
🏃 Carga {🟢|🟡|🔴} — ACWR {valor} ({status}) · último rodado {km}km @ {pace}/km
💪 Performance {🟢|🟡|🔴} — VO2max {n} · peso {kg}kg
🎯 {prova} {🟢|🟡|🔴} — T-{dias} · projeção {tempo}
🚩 Flags — {qualquer alerta automático}
```

## Lógica dos semáforos

- 🟢 verde: dentro do range esperado
- 🟡 amarelo: atenção (1+ desvio padrão da baseline ou borderline)
- 🔴 vermelho: fora do range (2+ desvios ou flag crítica)

Os ranges são configuráveis em `briefing/thresholds.yaml` (em construção) — cada atleta tem baselines diferentes.

## Flags automáticos

- Readiness baixa por 3 dias seguidos
- HRV abaixo de 80% da média de 14 dias
- ACWR > 1.5 (zona de risco de lesão)
- Sono < 6h por 2 noites seguidas
- Recovery time pendente > 48h

## Status

🛠️ Em construção. Template definido, código `generate.py` vem.
