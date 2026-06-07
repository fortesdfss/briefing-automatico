# Variabilidade da Frequência Cardíaca (HRV) — Estado da Arte e Monitoramento

## Definição e base fisiológica
A HRV é a variação no intervalo entre batimentos (intervalos R-R/N-N), refletindo a modulação autonômica do nó sinusal. A HRV de repouso é determinada predominantemente pela atividade **parassimpática (vagal)**. É um biomarcador não invasivo do balanço simpático-vagal e do estado de recuperação sistêmica (Task Force ESC/NASPE, Circulation 1996; Laborde et al., Front Psychol 2017 — recomendações metodológicas de referência).

## Métrica de escolha: rMSSD
O consenso atual da literatura de monitoramento de atletas elege o **rMSSD** como métrica de campo, por refletir robustamente o tônus vagal, ser confiável em registros curtos e ultracurtos (~1–5 min), e ser pouco dependente da frequência respiratória comparado a índices espectrais.
- Esco & Fields et al. (Sensors, 2025, narrative review): rMSSD é o índice mais prático e robusto para wearables; recomenda medidas **quase diárias** em vez de isoladas, com **médias semanais** e **coeficiente de variação (CV)** para capturar tanto adaptação crônica quanto perturbações homeostáticas agudas.
- Frequentemente usa-se **Ln rMSSD** (log natural) para normalizar a distribuição.
- Garmin reporta HRV noturna (ms) durante o sono, aproximando-se do rMSSD.

## Monitoramento: linha de base individual, não norma populacional
Princípio central (Plews, Laursen, Buchheit, Sports Med 2013; Lundstrom et al., Int J Sports Med 2023 — review de práticas aplicadas):
- Medidas **isoladas** têm alta variabilidade dia-a-dia e baixo valor decisório.
- O padrão prático é a **média móvel de 7 dias (HRV7)** comparada à linha de base de 30–60 dias **e seu CV/desvio-padrão**.
- O CV (dispersão da HRV) é informativo por si: **CV crescente** sinaliza instabilidade autonômica/estresse mesmo com média preservada.
- Decisão por **desvio da própria linha de base** (smallest worthwhile change ≈ 0,5× desvio-padrão individual), nunca por corte populacional fixo.

## Padrões interpretativos (Buchheit, Front Physiol 2014)
- HRV7 **estável ou em leve elevação** + boa performance → adaptação positiva, tolerar/progredir carga.
- HRV7 **suprimida** além do SWC por 3+ dias → fadiga acumulada/estresse não assimilado → reduzir carga.
- **Parasympathetic saturation**: em atletas muito treinados, HRV anormalmente *alta* com FCrep baixa pode, paradoxalmente, indicar fadiga profunda — interpretar com contexto.
- Reduções de HRV antecedem frequentemente piora de bem-estar e doença (Bellenger et al., Sports Med 2016, meta-análise: a resposta autonômica distingue estados de adaptação vs fadiga, com direção dependente do índice e do estado de treino).

## Treino guiado por HRV (HRV-guided training)
Meta-análises (Granero-Gallegos et al., IJERPH 2020; revisão metodológica com meta-análise, PMC8507742, 2021) mostram que ajustar a carga diária conforme a HRV tende a produzir adaptações **iguais ou ligeiramente superiores** ao treino predefinido em VO2máx e desempenho, com menor proporção de "não-respondedores". Evidência promissora mas ainda **inconclusiva** quanto à superioridade robusta — efeitos pequenos e amostras limitadas.

## Fatores de confusão (verificar antes de concluir fadiga)
Álcool (supressão marcante), refeição/treino tardios, desidratação, baixa disponibilidade energética, infecção subclínica, estresse psicológico, calor, altitude, inconsistência de horário/posição da medida. HRV exige padronização de condição de registro.

## Referências-chave
- Task Force ESC/NASPE. HRV: standards of measurement. Circulation. 1996.
- Plews DJ, Laursen PB, Stanley J, Kilding AE, Buchheit M. Training adaptation and HRV in elite endurance athletes. Sports Med. 2013.
- Bellenger CR et al. Monitoring athletic training status through autonomic HR regulation: systematic review and meta-analysis. Sports Med. 2016.
- Buchheit M. Monitoring training status with HR measures. Front Physiol. 2014.
- Laborde S, Mosley E, Thayer JF. HRV and cardiac vagal tone — recommendations. Front Psychol. 2017.
- Lundstrom CJ, Foreman NA, Biltz G. Practices and applications of HRV monitoring in endurance athletes. Int J Sports Med. 2023.
- Esco MR et al. Monitoring training adaptation and recovery via HRV using mobile devices: narrative review. Sensors. 2025.
- Granero-Gallegos A et al. HRV-based training for improving VO2max: systematic review with meta-analysis. IJERPH. 2020.
- Kaufmann S, Gronwald T, et al. HRV-derived thresholds for exercise intensity prescription: systematic review. Sports Med Open. 2023.

## Operacionalização das métricas neste sistema (rotulagem honesta)
O que o Garmin fornece e como a literatura mais atual orienta interpretar:

### rMSSD noturno (lastNightAvg)
Média do rMSSD durante o sono. É a leitura individual do dia. **Não decidir por ela isolada** — alta variabilidade dia-a-dia (Plews 2013; Esco 2025). Serve como ponto, não como tendência.

### Média de 7 dias (weeklyAvg) = HRV7
A métrica de tendência. Reflete o estado autonômico crônico/adaptativo. É a base para julgar fadiga acumulada. Comparar HRV7 atual com HRV7 de 30/180/365 dias revela a direção da adaptação.

### Desvio do baseline (%)
Garmin fornece a faixa de baseline individual (balancedLow–balancedUpper) e um marker central. O **desvio percentual do rMSSD noturno vs o centro do baseline** operacionaliza o conceito de smallest worthwhile change de forma individual:
- Dentro da faixa balanced → estado autonômico típico do indivíduo.
- Abaixo do balancedLow de forma sustentada → supressão vagal → fadiga/estresse não assimilado.
- Acima do balancedUpper de forma anômala em atleta muito treinado → possível parasympathetic saturation (fadiga profunda) — ler com contexto, não como "ótimo".

### Status HRV do Garmin (BALANCED / UNBALANCED / LOW)
Classificação categórica que o Garmin deriva da relação rMSSD vs baseline. BALANCED = dentro da faixa esperada; UNBALANCED = fora (alto ou baixo); LOW = cronicamente abaixo. Usar como triagem, confirmar com HRV7 e convergência.

### Dispersão noturna (desvio-padrão das leituras de 5 min)
NÃO é SDNN (que exige R-R batimento-a-batimento, indisponível). É a dispersão das leituras de rMSSD de 5 min ao longo da noite — uma medida de **estabilidade autonômica noturna**. Rotular sempre como "dispersão noturna", nunca como SDNN. Dispersão crescente pode indicar sono fragmentado ou instabilidade autonômica.

### Training Readiness (score 0–100 + fatores)
Índice composto proprietário do Garmin que integra sono, HRV, tempo de recuperação, carga aguda e estresse recente. Os fatores contribuintes (sleepScoreFactor, hrvFactor, recoveryTimeFactor, acuteLoadFactor) permitem ver **o que está puxando o score para baixo**. Usar como triagem de prontidão e, principalmente, ler os fatores para diagnóstico — ex.: readiness baixo puxado pelo fator HRV ≠ readiness baixo puxado por carga aguda alta.

### Stress Index do Garmin (0–100 + distribuição)
Leitura de balanço autonômico ao longo do dia derivada da HRV (não é fadiga de treino no sentido de Banister). A distribuição (% repouso/baixo/médio/alto) mostra a qualidade da recuperação diurna. Stress de repouso alto + HRV7 baixa = convergência para sobrecarga autonômica.

## Classificação prática de fadiga/prontidão (síntese para o relatório)
Combinar, nunca isolar:
- **Prontidão alta**: Readiness ≥ 75 · HRV7 ≥ baseline · desvio ≥ 0% · Stress repouso predominante · sono ≥ 7h score ≥ 80 · FCrep normal.
- **Prontidão moderada / cautela**: Readiness 40–74 · HRV7 levemente abaixo · desvio −5 a −10% · sono subótimo.
- **Fadiga / baixa prontidão**: Readiness < 40 · HRV7 abaixo do baseline sustentado · desvio < −10% · Stress médio/alto predominante · FCrep ↑ · sono ruim. Convergência de 3+ sinais = reduzir carga.
