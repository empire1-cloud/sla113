# Skill: Portfolio Monitoring
## Metadata
- name: PORTFOLIO_MONITORING
- version: 1.0.0
- description: Private equity portfolio company tracking — KPIs, performance, value creation
- domain: private-equity
- triggers: ["portfolio monitoring", "portfolio tracking", "kpi dashboard"]
- required_personas: ["private_equity_analyst"]
- max_duration: "1h"
- confidence_threshold: 80
## Workflow
- step: 1; name: company_snapshots; action: "Revenue, EBITDA, debt, cash for each portfolio company"
- step: 2; name: kpi_tracking; action: "Same-store revenue growth, margin evolution, debt paydown"
- step: 3; name: value_creation; action: "Track value creation bridges: multiple expansion, EBITDA growth, debt paydown"
- step: 4; name: risk_flags; action: "Covenant headroom, maturity wall, management changes"
## Source: Anthropic financial-services reference
