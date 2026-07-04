# Skill: INTELLIGENCE

## Metadata

- name: INTELLIGENCE
- version: 1.0.0
- description: Market and competitive intelligence gathering — structured research with source triangulation and scoring.
- triggers: "competitive analysis", "market research", "who are the competitors", "what's trending", /intelligence
- required_personas: Analyst
- max_duration: 25m
- confidence_threshold: 75

## Workflow

| Step | Name | Persona | Input | Output | Description | Quality Gate |
|---|---|---|---|---|---|---|
| 1 | Define intelligence goal | Analyst | Question, context, Business domain from Knowledge Graph | Intelligence brief (target domain, competitors, time window, sources) | Identify the specific competitive or market question. Load existing business entities from Knowledge Graph. Select 3-5 sources. | Brief is specific; sources are relevant |
| 2 | Collect signals | Analyst | Intelligence brief | Raw signals (news, posts, commits, filings, papers) | Run Trend Intelligence (Last30Days). Search GitHub for competitive repos. Check HN/Reddit/X. Collect jobs, funding, product launches. | >= 8 signals from >= 3 source types |
| 3 | Analyze | Analyst | Raw signals | Competitive landscape map, trend analysis, signal clustering | Cluster signals by competitor, trend, or theme. Identify each competitor's position: leader, challenger, niche, new entrant. Rate momentum. | Every competitor positioned; trends identified |
| 4 | Score | Analyst | Analysis | Confidence-weighted findings | Rate each finding: confirmed (2+ sources), indicated (1 source + strong signal), speculative (1 source). | Every finding has confidence level |
| 5 | Recommend | Analyst | Scored findings | Strategic recommendations with rationale | What to do: build, partner, wait, ignore. Each with confidence, cost estimate, timeline. | Recommendations ranked by confidence * impact |
| 6 | Store | Analyst | Full intelligence package | Knowledge Graph update + Memory Platform (Episodic) + optional report | Update Business domain in Knowledge Graph. Store full report in Memory Platform. Generate standalone brief if requested. | All entities updated; report stored |

## Quality Gates

| Gate | Step | Condition | Failure Action |
|---|---|---|---|
| Scope clarity | 1 | Target domain and competitors named | Narrow scope with user |
| Signal volume | 2 | >= 8 signals from >= 3 source types | Extend time window or add sources |
| Positioning | 3 | Every competitor has a position and momentum | Add unknown; mark as low confidence |
| Evidence triangulation | 4 | Confirmed findings have >= 2 sources | Downgrade to indicated/speculative |
| Recommendation ranked | 5 | Each recommendation has confidence * impact score | Add missing scores |
| Persistence | 6 | Knowledge Graph has new/modified business entities | Retry storage; flag if persistent |

## Evidence

| Artifact | From Step | Format | Retention |
|---|---|---|---|
| Intelligence brief | 1 | Markdown | 30 days |
| Signal collection | 2 | JSON (source, url, snippet, date, type) | 90 days |
| Competitive landscape | 3 | JSON (competitors, positions, momentum) | Permanent |
| Confidence ratings | 4 | JSON (finding, score, sources) | Permanent |
| Recommendations | 5 | Markdown | Permanent |
| Stored entities | 6 | Cypher/JSON (graph entities added) | Permanent |

## Confidence Scoring

- Source diversity: 0-20 (types and count of sources)
- Signal volume: 0-20 (total signals collected)
- Analysis depth: 0-20 (competitors positioned, trends identified)
- Evidence quality: 0-20 (triangulation rate)
- Recommendation quality: 0-20 (specific, ranked, actionable)

## Rollback

| Step | Undo Action | Conditions |
|---|---|---|
| 2-5 | Discard intelligence package | User says findings are stale |
| 6 | Remove or deprecate Knowledge Graph entities added | Mistaken entity creation |

## Telemetry

| Step | Event | Payload |
|---|---|---|
| 1 | intelligence.goal_defined | domain, competitors, sources |
| 2 | intelligence.signals_collected | signal_count, source_types |
| 3 | intelligence.analyzed | competitor_count, trend_count |
| 4 | intelligence.scored | finding_count, avg_confidence |
| 5 | intelligence.recommended | recommendation_count, top_recommendation |
| 6 | intelligence.stored | entities_added, report_path |
