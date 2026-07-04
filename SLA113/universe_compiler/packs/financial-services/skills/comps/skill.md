# Skill: Comps Analysis

## Metadata
- name: COMPS
- version: 1.0.0
- description: Comparable company and precedent transaction analysis with quartile statistics
- domain: financial-analysis
- triggers: ["comps", "trading comps", "peer analysis", "comparable companies"]
- required_personas: ["financial_analyst"]
- max_duration: "1h"
- confidence_threshold: 85

## Workflow

- step: 1
  name: select_peers
  persona: financial_analyst
  input: ["target_company", "sector", "business_model"]
  output: ["peer_list"]
  description: Select 5-15 public peers. Match by sector, business model, size, geography. Flag any that are not pure-plays.

- step: 2
  name: pull_financials
  persona: financial_analyst
  input: ["peer_list"]
  output: ["financial_data"]
  description: Pull revenue, EBITDA, EBIT, net income, EPS, BV/share. Use LTM and NTM. Source: CapIQ > Daloopa > filings.

- step: 3
  name: calculate_multiples
  persona: financial_analyst
  input: ["financial_data", "stock_prices"]
  output: ["multiples_table"]
  description: EV/Revenue, EV/EBITDA, EV/EBIT, P/E, P/BV. Use current price: EV = market cap + net debt. Report mean, median, high, low, Q1, Q3.

- step: 4
  name: flag_outliers
  persona: financial_analyst
  input: ["multiples_table"]
  output: ["flagged_peers"]
  description: Flag any peer >2 stdev from mean. Investigate and document reason (one-time item, different growth, different margin).

- step: 5
  name: precedent_transactions
  persona: financial_analyst
  input: ["sector", "timeframe"]
  output: ["precedent_table"]
  description: Select 5-10 relevant precedent M&A transactions. EV/Revenue, EV/EBITDA, EV/EBIT. Control premium if available.

## Quality Gates
| Gate | Step | Condition | Failure Action |
|---|---|---|---|
| Data sourced | 2 | Every metric has provider | Flag unsourced |
| Outliers investigated | 4 | Every outlier has reason | Document before proceeding |

## Source
Derived from Anthropic financial-services reference: vertical-plugins/financial-analysis/skills/comps-analysis
