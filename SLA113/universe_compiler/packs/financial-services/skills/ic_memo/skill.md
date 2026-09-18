# Skill: IC Memo

## Metadata
- name: IC_MEMO
- version: 1.0.0
- description: Investment committee memo — executive summary, financial analysis, returns, risk factors
- domain: private-equity
- triggers: ["ic memo", "investment committee", "investment memo"]
- required_personas: ["private_equity_analyst"]
- max_duration: "3h"
- confidence_threshold: 80

## Workflow

- step: 1
  name: executive_summary
  persona: private_equity_analyst
  input: ["target", "deal_parameters"]
  output: ["executive_summary"]
  description: Company name, sector, transaction summary, investment rationale, key metrics.

- step: 2
  name: company_overview
  persona: private_equity_analyst
  input: ["executive_summary"]
  output: ["company_section"]
  description: Business description, products/services, customers, competitive position, management team.

- step: 3
  name: industry_analysis
  persona: private_equity_analyst
  input: ["company_section"]
  output: ["industry_section"]
  description: Market size, growth, trends, competitive landscape, regulatory environment.

- step: 4
  name: financial_analysis
  persona: financial_analyst
  input: ["company_section", "industry_section"]
  output: ["financial_section"]
  description: Historical financials, projections, key value drivers, unit economics.

- step: 5
  name: investment_thesis
  persona: private_equity_analyst
  input: ["all_sections"]
  output: ["thesis_section"]
  description: Clear thesis with 3-5 key value creation levers.

- step: 6
  name: returns_analysis
  persona: financial_analyst
  input: ["financial_section", "deal_parameters"]
  output: ["returns_section"]
  description: Base/base/upside cases. MOIC, IRR, exit multiples. Sensitivity analysis.

- step: 7
  name: risk_factors
  persona: private_equity_analyst
  input: ["all_sections"]
  output: ["risk_section"]
  description: Top 5-7 risks with mitigation strategies.

- step: 8
  name: recommendation
  persona: private_equity_analyst
  input: ["all_sections"]
  output: ["recommendation"]
  description: Clear vote recommendation with deal structure terms.

## Source
Derived from Anthropic financial-services reference: vertical-plugins/private-equity/skills/ic-memo
