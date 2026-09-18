# Skill: Model Update
## Metadata
- name: MODEL_UPDATE
- version: 1.0.0
- description: Rolling forward financial models with actual results and revised estimates
- domain: equity-research
- triggers: ["model update", "roll forward", "estimate revision"]
- required_personas: ["financial_analyst", "equity_research_analyst"]
- max_duration: "1h"
- confidence_threshold: 85
## Workflow
- step: 1; name: post_actuals; action: "Insert reported results into historical period"
- step: 2; name: revise_estimates; action: "Update forward estimates reflecting reported results and guidance"
- step: 3; name: check_integration; action: "Balance sheet still balances, cash flows articulate"
- step: 4; name: target_price; action: "Recalculate price target using updated valuation methodology"
## Source: Anthropic financial-services reference
