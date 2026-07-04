# Skill: RESEARCH

## Metadata

- name: RESEARCH
- version: 1.0.0
- description: Gather and synthesize information from external sources (trend intel, competitors, community, papers).
- triggers: "research", "look into", "find out about", "what's happening with", competitive analysis, due diligence
- required_personas: Analyst
- max_duration: 20m
- confidence_threshold: 75

## Workflow

| Step | Name | Persona | Input | Output | Description | Quality Gate |
|---|---|---|---|---|---|---|
| 1 | Define scope | Analyst | Research question, context | Research brief with sources, depth, time window | Clarify what exactly to research. Identify 3-5 sources (Reddit, X, HN, GitHub, news, papers). Set time window. | Research question is specific and falsifiable |
| 2 | Gather | Analyst | Research brief, Trend Intelligence | Raw signal collection | Run Last30Days or equivalent. Collect posts, commits, papers, news. Filter by relevance. | At least 5 relevant signals collected |
| 3 | Cluster | Analyst | Raw signals | Themed clusters with signal counts | Group signals by theme. Identify patterns, frequency, sentiment. | Clusters are coherent; no orphan signals |
| 4 | Score | Analyst | Clusters | Confidence per finding | Rate each finding: strong signal, weak signal, conflicting. Cross-reference across sources. | Every finding has a confidence rating |
| 5 | Synthesize | Analyst | Scored findings | Research summary with recommendations | Write concise brief. Include: what changed, why it matters, what to do, confidence level. | Summary is actionable; recommendations ranked |
| 6 | Store | Analyst | Brief, raw signals | Knowledge Graph + Memory Platform update | Write findings to Knowledge Graph (trend nodes, competitor entities). Store full brief in Memory Platform (Episodic). | Graph updated; brief stored |

## Quality Gates

| Gate | Step | Condition | Failure Action |
|---|---|---|---|
| Specific scope | 1 | Question is specific; sources listed | Refine scope with user |
| Signal threshold | 2 | >= 5 relevant signals from >= 2 sources | Extend time window or add sources |
| Cluster quality | 3 | No orphan signals; clusters tell a story | Re-cluster with different grouping |
| Evidence triangulation | 4 | Each finding confirmed by >= 2 sources | Mark as low confidence; flag to user |
| Actionability | 5 | Brief includes what-to-do section | Add recommendations |
| Persistence | 6 | Graph nodes created; brief accessible | Retry storage |

## Evidence

| Artifact | From Step | Format | Retention |
|---|---|---|---|
| Research brief | 1 | Markdown | 30 days |
| Raw signals | 2 | JSON (source, url, snippet, date) | 90 days |
| Clusters | 3 | JSON (theme, signals[], sentiment) | 90 days |
| Confidence ratings | 4 | JSON (finding, score, sources) | Permanent |
| Synthesis | 5 | Markdown | Permanent (Episodic Memory) |
| Graph updates | 6 | Cypher or JSON patch | Permanent |

## Confidence Scoring

- Source diversity: 0-20 (number of independent sources)
- Signal strength: 0-25 (volume, recency, authority)
- Cluster coherence: 0-20 (clear themes, no orphans)
- Confidence triangulation: 0-20 (multi-source confirmation)
- Actionability: 0-15 (clear what-to-do)

## Rollback

| Step | Undo Action | Conditions |
|---|---|---|
| 2-5 | Discard research; mark Knowledge Graph nodes as stale | User says findings are outdated |
| 6 | Remove Knowledge Graph nodes added by this research | Graph integrity issue |

## Telemetry

| Step | Event | Payload |
|---|---|---|
| 1 | research.scope_defined | question, sources, time_window |
| 2 | research.signals_gathered | signal_count, source_count |
| 3 | research.clusters_formed | cluster_count, orphan_count |
| 4 | research.findings_scored | finding_count, avg_confidence |
| 5 | research.synthesis_complete | recommendation_count |
| 6 | research.stored | graph_nodes_added, memory_id |
