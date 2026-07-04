# Skill: Client Report
## Metadata
- name: CLIENT_REPORT
- version: 1.0.0
- description: Wealth management client reporting — performance, holdings, market commentary
- domain: wealth-management
- triggers: ["client report", "performance report", "portfolio report"]
- required_personas: ["wealth_manager"]
- max_duration: "1h"
- confidence_threshold: 85
## Workflow
- step: 1; name: portfolio_snapshot; action: "Total value, asset allocation, cash position"
- step: 2; name: performance; action: "MTD, QTD, YTD, ITD returns vs benchmark"
- step: 3; name: holdings_detail; action: "Top holdings, gainers/losers, concentration"
- step: 4; name: commentary; action: "Market narrative, portfolio changes, forward outlook"
## Source: Anthropic financial-services reference
