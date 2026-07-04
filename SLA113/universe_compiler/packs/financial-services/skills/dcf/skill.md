# Skill: DCF

## Metadata
- name: DCF
- version: 1.0.0
- description: Discounted cash flow valuation methodology — projections, FCF, WACC, terminal value, sensitivity
- domain: financial-analysis
- triggers: ["dcf", "valuation", "discounted cash flow", "DCF model"]
- required_personas: ["financial_analyst", "model_builder"]
- max_duration: "2h"
- confidence_threshold: 85

## Workflow

- step: 1
  name: pull_data
  persona: financial_analyst
  input: ["ticker", "reporting_currency"]
  output: ["historical_financials", "segment_data", "guidance"]
  description: Fetch historical financials from MCP (Daloopa > CapIQ > SEC). Load 5 years of P&L, balance sheet, cash flow, segment breakdowns. Use latest 10-K/10-Q.

- step: 2
  name: historical_analysis
  persona: financial_analyst
  input: ["historical_financials"]
  output: ["normalized_historicals", "revenue_drivers", "margin_drivers"]
  description: Normalize non-recurring items. Identify core revenue and margin drivers. Calculate historical growth rates, margins, capex/revenue.

- step: 3
  name: project_revenue
  persona: model_builder
  input: ["revenue_drivers", "guidance"]
  output: ["revenue_forecast", "key_assumptions"]
  description: Build revenue build-up by product/segment. Justify each assumption with historical trend, management guidance, or industry growth.

- step: 4
  name: project_costs
  persona: model_builder
  input: ["margin_drivers", "revenue_forecast"]
  output: ["full_pnl_forecast", "cogs", "opex"]
  description: Model COGS, gross margin, operating expenses. Reflect fixed/variable cost structure. Add D&A detail.

- step: 5
  name: calculate_fcf
  persona: model_builder
  input: ["pnl_forecast", "balance_sheet_drivers"]
  output: ["ufcf_forecast", "working_capital", "capex"]
  description: Unlevered FCF = EBIT(1-t) + D&A - CapEx - delta WC. Model each component explicitly.

- step: 6
  name: calculate_wacc
  persona: financial_analyst
  input: ["cap_structure", "risk_free_rate", "beta", "equity_risk_premium", "cost_of_debt"]
  output: ["wacc"]
  description: WACC = E/(D+E) * Ke + D/(D+E) * Kd * (1-t). Source risk-free rate, ERP, beta from CapIQ. Validate with sensitivity.

- step: 7
  name: terminal_value
  persona: model_builder
  input: ["fcf_forecast", "wacc", "terminal_growth_rate"]
  output: ["tv"]
  description: Perpetuity method: TV = FCF_n * (1+g) / (WACC - g). Exit multiple method as cross-check.

- step: 8
  name: bridge_to_equity
  persona: model_builder
  input: ["ev", "net_debt", "minority", "preferred"]
  output: ["equity_value", "implied_price"]
  description: Equity Value = EV - Net Debt - Minority - Preferred. Implied price = Equity Value / Diluted Shares.

- step: 9
  name: sensitivity
  persona: financial_analyst
  input: ["equity_value", "wacc", "growth_rate"]
  output: ["sensitivity_table"]
  description: 3-table sensitivity: (WACC x terminal growth), (WACC x EBITDA multiple), (revenue growth x margin). Each table 5x5.

- step: 10
  name: validate
  persona: financial_analyst
  input: ["model"]
  output: ["validation_report"]
  description: Check balance, no hardcodes in calc cells, formulas use named ranges, all assumptions sourced.

## Quality Gates
| Gate | Step | Condition | Failure Action |
|---|---|---|---|
| Data sourced | 1 | Every input has provider citation | Flag [UNSOURCED], proceed with estimate |
| Model balances | 10 | A = L + E | Halt, trace break |
| Sensitivity valid | 9 | All cells populated, no #REF | Rerun with valid grid |
| Assumptions sourced | 3-5 | Every hardcode has explanatory comment | Add comment before proceeding |

## Evidence
| Artifact | From Step | Format | Retention |
|---|---|---|---|
| Historical financials | 1 | .xlsx raw data tab | 90d |
| Assumptions sheet | 3-5 | .xlsx assumptions tab | 90d |
| Valuation output | 8-9 | .xlsx valuation tab | 90d |
| Validation report | 10 | .md or .txt | 90d |

## Confidence Scoring
- criteria:
  - { name: "data_completeness", weight: 20, measurement: "% of inputs sourced from MCP provider" }
  - { name: "balance_check", weight: 20, measurement: "A=L+E within 0.01% of total assets" }
  - { name: "sensitivity_complete", weight: 15, measurement: "All 75 cells populated" }
  - { name: "assumptions_documented", weight: 15, measurement: "Every assumption has comment" }
  - { name: "formula_consistency", weight: 15, measurement: "No hardcodes in calc cells" }
  - { name: "convergence", weight: 15, measurement: "Circular refs resolved, model stable" }

## Source
Derived from Anthropic financial-services reference: vertical-plugins/financial-analysis/skills/dcf-model
