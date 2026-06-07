# Análise por Modalidade — Multiesporte (Força, Natação, Ciclismo, Corrida)

## Princípio: cada modalidade tem métricas e leituras próprias
Não se analisa natação com deriva cardíaca de corrida, nem força com pace. O sistema deve **identificar o tipo de atividade** (campo typeKey do Garmin) e aplicar a leitura correta. Tipos comuns: running, treadmill_running, trail_running, cycling, indoor_cycling, virtual_ride, lap_swimming, open_water_swimming, strength_training, walking, cardio, hiit.

## CORRIDA (running / trail / treadmill)
Métricas: pace, FC por zona, cadência, oscilação vertical, deriva cardíaca, GAP (grade-adjusted pace em trilha).
- Z2: avaliar % tempo < LT1 e decoupling < 5%.
- Trilha: usar elevação para contextualizar oscilações de FC; preferir GAP a pace bruto.
- Cadência baixa + oscilação vertical alta = ineficiência mecânica.

## CICLISMO (cycling / indoor / virtual)
Métrica de ouro: **potência (W)**, superior à FC por responder instantaneamente.
- **FTP** (functional threshold power) ≈ potência sustentável ~1 h; proxy prático = 95% da melhor potência média de 20 min.
- **Normalized Power (NP)**, **Intensity Factor (IF = NP/FTP)** e **TSS** (Training Stress Score = (s × NP × IF)/(FTP × 3600) × 100) — Coggan/Allen, *Training and Racing with a Power Meter*. TSS é o equivalente em potência ao TRIMP.
- **Variability Index (VI = NP/potência média)**: ~1,0 em contrarrelógio/indoor estável; alto = pedalada intervalada/irregular.
- Decoupling Pw:Hr > 5% em ride longo Z2 = mesma leitura de durabilidade/fueling da corrida.
- Indoor sem potência: usar FC, mas lembrar que FC tem inércia (subestima esforços curtos).

## NATAÇÃO (lap_swimming / open_water)
FC subaquática é pouco confiável (contato do sensor, imersão). Métricas centrais:
- **Pace por 100 m**, **SWOLF** (tempo de 25/50 m + nº de braçadas: menor = mais eficiente), **stroke rate** e **distance per stroke (DPS)**.
- **CSS (Critical Swim Speed)** — proxy de limiar: velocidade entre testes de 400 m e 200 m; base para zonas de natação.
- Analisar **eficiência técnica** (SWOLF, DPS) e aderência ao alvo de pace, não FC.
- Conjuntos (sets) e intervalos: avaliar consistência de pace entre repetições e queda no fim (fadiga técnica).

## FORÇA (strength_training)
Não tem pace nem zona aeróbia significativa. FC reflete densidade/pausas, não intensidade da carga.
- Métricas úteis: duração, volume (séries × reps × carga = tonnage), densidade (trabalho/tempo), distribuição de grupos musculares.
- Princípios de prescrição (ACSM position stand, Med Sci Sports Exerc 2009; Schoenfeld et al. — meta-análises de volume/hipertrofia e força):
  - Força máxima: ~≥ 85% 1RM, baixas reps, pausas longas.
  - Hipertrofia: volume semanal por grupo é o principal driver (≈10+ séries/semana), proximidade da falha relevante.
  - Potência: cargas moderadas, alta velocidade intencional.
- Monitorar **carga semanal por grupo muscular**, proximidade da falha (RIR/RPE) e gestão de fadiga concorrente com endurance.

## INTERFERÊNCIA CONCORRENTE (concurrent training)
Atleta multiesporte: força + endurance no mesmo ciclo podem interferir. Meta-análises (Wilson et al., J Strength Cond Res 2012; reviews recentes de concurrent training) indicam:
- O **efeito de interferência** afeta mais ganhos de força/potência que de endurance.
- Mitigação: separar sessões (≥ 6 h), priorizar a qualidade-alvo do dia, evitar endurance intenso imediatamente antes de força máxima, gerir fadiga global.
- Implicação para o briefing: ler a carga do dia no **contexto da semana inteira e das modalidades combinadas**, não sessão isolada.

## Carga comum entre modalidades
Para comparar/ somar cargas de modalidades diferentes num ACWR/strain coerente, usar uma moeda única: **sRPE (sessão RPE × duração)** ou **TRIMP por zonas**. Potência (TSS) na bike e CSS-based na natação podem ser convertidos a sRPE para integração. Manter o método constante.

## Referências-chave
- Allen H, Coggan A, McGregor S. Training and Racing with a Power Meter. 3rd ed. 2019.
- ACSM Position Stand. Progression models in resistance training. Med Sci Sports Exerc. 2009.
- Schoenfeld BJ et al. Dose-response of resistance training volume on hypertrophy: meta-analysis. J Sports Sci / Med Sci Sports Exerc. 2017.
- Wilson JM et al. Concurrent training: meta-analysis of interference. J Strength Cond Res. 2012.
- Ginn E. The Critical Swim Speed concept; Wakayoshi K et al. CSS validation. 1992.
