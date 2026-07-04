# Skill: Morning Note
## Metadata
- name: MORNING_NOTE
- version: 1.0.0
- description: Post-earnings morning note — key takeaways, rating, price target
- domain: equity-research
- triggers: ["morning note", "earnings note", "research note"]
- required_personas: ["equity_research_analyst"]
- max_duration: "30m"
- confidence_threshold: 85
## Workflow
- step: 1; name: headline; action: "One-line verdict: beat/miss/in-line, rating, PT change"
- step: 2; name: results_table; action: "Key line items vs consensus and prior period"
- step: 3; name: key_takeaways; action: "3-5 bullet points on what changed and why"
- step: 4; name: outlook; action: "Revised estimates, rating, price target, catalysts"
## Source: Anthropic financial-services reference
