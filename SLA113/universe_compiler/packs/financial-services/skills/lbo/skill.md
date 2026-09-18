# Skill: LBO

## Metadata
- name: LBO
- version: 1.0.0
- description: Leveraged buyout analysis — sources & uses, debt schedule, returns sensitivity
- domain: financial-analysis
- triggers: ["lbo", "leveraged buyout", "sponsor return", "buyout model"]
- required_personas: ["financial_analyst", "model_builder"]
- max_duration: "1.5h"
- confidence_threshold: 80

## Workflow

- step: 1
  name: set_assumptions
  persona: financial_analyst
  input: ["target_price", "debt_metrics", "sponsor_parameters"]
  output: ["lbo_assumptions"]
  description: Entry valuation, financing structure (revolver, Term A, Term B, senior notes), management roll, sponsor equity, fees.

- step: 2
  name: sources_and_uses
  persona: model_builder
  input: ["lbo_assumptions"]
  output: ["sources_uses"]
  description: Sources = debt tranches + equity + rollover. Uses = purchase price + fees + refinanced debt. Must balance.

- step: 3
  name: debt_schedule
  persona: model_builder
  input: ["sources_uses", "projections"]
  output: ["debt_schedule", "interest_expense"]
  description: Mandatory repayments, cash sweep, PIK toggle. Calculate interest by tranche with LIBOR/SOFR floor.

- step: 4
  name: project_returns
  persona: financial_analyst
  input: ["debt_schedule", "fcf_forecast", "exit_assumptions"]
  output: ["returns_summary"]
  description: Entry/exit year, exit multiple, net debt paydown. Calculate MOIC, IRR, cash-on-cash. Returns sensitivity on exit year x exit multiple.

## Quality Gates
| Gate | Step | Condition | Failure Action |
|---|---|---|---|
| S&U balanced | 2 | Sources = Uses | Halt, trace discrepancy |
| Debt sized | 2 | Tranches sum to total debt | Adjust tranche allocations |
| Returns computed | 4 | MOIC, IRR, CoC all populated | Check exit assumptions |

## Source
Derived from Anthropic financial-services reference: vertical-plugins/financial-analysis/skills/lbo-model
