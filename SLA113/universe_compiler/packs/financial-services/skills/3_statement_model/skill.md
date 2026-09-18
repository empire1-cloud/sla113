# Skill: 3-Statement Model

## Metadata
- name: THREE_STATEMENT
- version: 1.0.0
- description: Integrated 3-statement financial model with balance sheet, P&L, and cash flow
- domain: financial-analysis
- triggers: ["3 statement", "integrated model", "financial model", "three statement"]
- required_personas: ["financial_analyst", "model_builder"]
- max_duration: "3h"
- confidence_threshold: 85

## Workflow
- step: 1; name: historical_inputs; output: ["historical_data"]
- step: 2; name: revenue_drivers; output: ["revenue_schedule"]
- step: 3; name: operating_costs; output: ["cost_schedule"]
- step: 4; name: working_capital; output: ["wc_schedule"]
- step: 5; name: capex_depreciation; output: ["ppne_schedule"]
- step: 6; name: debt_and_interest; output: ["debt_schedule"]
- step: 7; name: equity; output: ["equity_schedule"]
- step: 8; name: integrate; quality_gate: "A = L + E"

## Source
Derived from Anthropic financial-services reference: vertical-plugins/financial-analysis/skills/3-statement-model
