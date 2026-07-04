# Skill: Earnings Analysis

## Metadata
- name: EARNINGS_ANALYSIS
- version: 1.0.0
- description: Post-earnings results analysis — variance vs consensus, model update, note drafting
- domain: equity-research
- triggers: ["earnings", "results analysis", "earnings review"]
- required_personas: ["equity_research_analyst"]
- max_duration: "2h"
- confidence_threshold: 85

## Workflow

- step: 1
  name: ingest_results
  persona: equity_research_analyst
  input: ["transcript", "press_release", "filing"]
  output: ["results_data"]
  description: Extract reported revenue, EPS, segment results, guidance vs consensus.

- step: 2
  name: variance_analysis
  persona: equity_research_analyst
  input: ["results_data", "estimates"]
  output: ["variance_report"]
  description: Variance vs consensus, vs prior period, vs guidance. Flag material beats/misses.

- step: 3
  name: key_metrics
  persona: equity_research_analyst
  input: ["results_data"]
  output: ["metrics_report"]
  description: Revenue growth, margin expansion/contraction, FCF conversion, ROIC, key operating metrics.

- step: 4
  name: model_update
  persona: financial_analyst
  input: ["variance_report", "existing_model"]
  output: ["updated_model"]
  description: Roll forward actuals, update forward estimates reflecting reported results and guidance.

- step: 5
  name: thesis_impact
  persona: equity_research_analyst
  input: ["metrics_report", "guidance"]
  output: ["thesis_assessment"]
  description: Does this change the investment thesis? Rating implication, price target adjustment.

## Source
Derived from Anthropic financial-services reference: vertical-plugins/equity-research/skills/earnings-analysis
