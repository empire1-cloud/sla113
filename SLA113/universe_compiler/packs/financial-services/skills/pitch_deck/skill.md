# Skill: Pitch Deck

## Metadata
- name: PITCH_DECK
- version: 1.0.0
- description: Generate branded investment banking pitch deck on PowerPoint template
- domain: investment-banking
- triggers: ["pitch deck", "presentation", "deck", "pitchbook"]
- required_personas: ["investment_banker"]
- max_duration: "2h"
- confidence_threshold: 85

## Workflow
- step: 1; name: load_template; action: "Load bank's PowerPoint template with branded slide master"
- step: 2; name: title_slide; action: "Target name, situation, bank branding, date"
- step: 3; name: situation_overview; action: "Strategic rationale narrative with transaction summary"
- step: 4; name: company_snapshot; action: "Business overview, key financials, stock chart"
- step: 5; name: valuation_summary; action: "Football field: comps, precedents, DCF, LBO ranges"
- step: 6; name: comps_detail; action: "Trading comps page with quartile statistics"
- step: 7; name: precedents_detail; action: "Precedent transactions with premium analysis"
- step: 8; name: illustrative_process; action: "Indicative timeline and process overview"

## Quality Gates
- Every number on a slide traces to named range in workbook
- Consistent date format across all slides

## References
- Calculation standards
- Formatting standards
- Slide templates
- XML reference for python-pptx

## Source
Derived from Anthropic financial-services reference: vertical-plugins/investment-banking/skills/pitch-deck
