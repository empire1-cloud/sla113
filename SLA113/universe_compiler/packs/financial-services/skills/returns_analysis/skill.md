# Skill: Returns Analysis
## Metadata
- name: RETURNS_ANALYSIS
- version: 1.0.0
- description: Private equity returns — MOIC, IRR, waterfall, sensitivity analysis
- domain: private-equity
- triggers: ["returns", "irr", "moic", "waterfall", "performance"]
- required_personas: ["private_equity_analyst", "financial_analyst"]
- max_duration: "1h"
- confidence_threshold: 85
## Workflow
- step: 1; name: cash_flows; action: "Build investment and exit cash flows with timing"
- step: 2; name: moic; action: "MOIC = total distributions / total contributions"
- step: 3; name: irr; action: "XIRR calculation with precise dates"
- step: 4; name: waterfall; action: "GP/LP waterfall with preferred return, catch-up, carried interest"
- step: 5; name: sensitivity; action: "Exit multiple x exit year, revenue x margin scenarios"
## Source: Anthropic financial-services reference
