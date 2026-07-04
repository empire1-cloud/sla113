# Skill: Deal Sourcing
## Metadata
- name: DEAL_SOURCING
- version: 1.0.0
- description: Identify potential PE investment targets using screening criteria and market data
- domain: private-equity
- triggers: ["deal sourcing", "target identification", "company search"]
- required_personas: ["private_equity_analyst"]
- max_duration: "2h"
- confidence_threshold: 70
## Workflow
- step: 1; name: define_criteria; action: "Size, sector, geography, margin profile, growth rate"
- step: 2; name: screen; provider: "pitchbook"; action: "Run screening via PitchBook or CapIQ universe"
- step: 3; name: rank; action: "Score and rank targets against investment criteria"
- step: 4; name: initial_due_diligence; action: "Quick company overview, management, competitive position"
## Source: Anthropic financial-services reference
