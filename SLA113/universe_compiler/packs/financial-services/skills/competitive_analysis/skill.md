# Skill: Competitive Analysis

## Metadata
- name: COMPETITIVE_ANALYSIS
- version: 1.0.0
- description: Competitive landscape mapping — positioning, market share, moats, peer benchmarking
- domain: financial-analysis
- triggers: ["competitive analysis", "landscape", "market map", "positioning"]
- required_personas: ["equity_research_analyst", "financial_analyst"]
- max_duration: "1.5h"
- confidence_threshold: 80

## Workflow
- step: 1; name: define_universe; action: "Identify direct and indirect competitors, adjacencies"
- step: 2; name: market_share; action: "Revenue share, unit share, geographic presence"
- step: 3; name: positioning_map; action: "Price vs quality, features, TAM focus"
- step: 4; name: moat_assessment; action: "Network effects, switching costs, IP, scale advantages"
- step: 5; name: peer_benchmarks; action: "Revenue growth, margins, ROIC, valuation multiples"

## Frameworks
- Porter's Five Forces
- SWOT analysis
- BCG matrix
- McKinsey 7S

## References
Each framework includes structured prompts for systematic application.

## Source
Derived from Anthropic financial-services reference: vertical-plugins/financial-analysis/skills/competitive-analysis
