# Skill: Roll Forward
## Metadata
- name: ROLL_FORWARD
- version: 1.0.0
- description: Balance sheet roll-forward schedules for month-end and quarter-end close
- domain: fund-admin
- triggers: ["roll forward", "balance sheet roll", "account roll"]
- required_personas: ["fund_accountant"]
- max_duration: "30m"
- confidence_threshold: 95
## Workflow
- step: 1; name: beginning_balance; action: "Load prior period ending balance"
- step: 2; name: additions; action: "Additions, accruals, reclasses for the period"
- step: 3; name: reductions; action: "Payments, amortization, settlements"
- step: 4; name: ending_balance; action: "Beginning + additions - reductions = ending (must balance)"
- step: 5; name: validate; action: "Ending balance ties to trial balance and general ledger"
## Quality Gates
- Beginning + additions - reductions = ending (tolerance: $0.01)
- Ending balance ties to subledger
## Source: Anthropic financial-services reference
