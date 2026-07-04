# Skill: NAV Tie-Out
## Metadata
- name: NAV_TIEOUT
- version: 1.0.0
- description: LP statement NAV reconciliation — LP-level NAV to fund-level NAV
- domain: fund-admin
- triggers: ["nav tieout", "nav reconciliation", "lp nav"]
- required_personas: ["fund_accountant"]
- max_duration: "30m"
- confidence_threshold: 95
## Workflow
- step: 1; name: lps; action: "Sum all LP-level NAVs from individual statements"
- step: 2; name: fund; action: "Extract fund-level NAV from fund accounting system"
- step: 3; name: tie; action: "Compare: sum of LP NAVs must equal fund NAV (net of GP stake)"
- step: 4; name: flag; action: "Flag differences >0.1% for investigation"
## Source: Anthropic financial-services reference
