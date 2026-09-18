# Skill: ARCHITECT

## Metadata

- name: ARCHITECT
- version: 1.0.0
- description: Design system architecture, component boundaries, interfaces, and data flow for a given scope.
- triggers: "design the architecture", "how should this work", system design, interface decisions, refactoring, scaling
- required_personas: Architect, Planner
- max_duration: 30m
- confidence_threshold: 85

## Workflow

| Step | Name | Persona | Input | Output | Description | Quality Gate |
|---|---|---|---|---|---|---|
| 1 | Understand | Architect | Goal, constraints, existing architecture, Knowledge Graph | Context summary, relevant ADRs, existing patterns | Load current architecture from Knowledge Graph. Find related ADRs. Identify patterns already in use. | Existing architecture fully understood |
| 2 | Define boundaries | Architect | Context summary | Component boundaries, responsibility statements | Decide what each component owns. Define separation of concerns. Establish contracts between components. | No overlapping responsibility; each boundary clear |
| 3 | Design interfaces | Architect | Component boundaries | Interface definitions (inputs, outputs, errors) | Define API contracts. Specify data formats, error states, async/sync boundaries. | Interfaces are consistent with existing patterns |
| 4 | Map data flow | Architect | Interfaces | Data flow diagram, state transitions | Trace data through each component. Identify state machines, persistence, caching. | No data loops; every state transition handled |
| 5 | Risk assessment | Architect, Planner | Data flow, Knowledge Graph, Memory Platform | Risk register with mitigations | Identify single points of failure, scaling bottlenecks, security concerns. Cross-reference with Decision Memory. | All risks have mitigations; no high-risk unaddressed |
| 6 | Document | Architect | All above | ADR or Architecture Decision Record | Write concise ADR: context, decision, consequences, alternatives considered. Write to Knowledge Graph. | ADR meets quality standard; stored in Graph + Memory |

## Quality Gates

| Gate | Step | Condition | Failure Action |
|---|---|---|---|
| Context load | 1 | All relevant ADRs and patterns retrieved | Manual search; request user input |
| No overlap | 2 | Component boundaries don't overlap | Redraw boundaries |
| Pattern consistency | 3 | Interfaces match existing conventions | Adjust interfaces to match |
| Data integrity | 4 | No data loss paths; all states handled | Add missing state handlers |
| Risk coverage | 5 | Every risk has a mitigation path | Surface high-risk items to user |
| ADR quality | 6 | ADR includes context, decision, consequences, alternatives | Revise ADR |

## Evidence

| Artifact | From Step | Format | Retention |
|---|---|---|---|
| Context summary | 1 | Markdown | Project lifetime |
| Component map | 2 | JSON/GraphML | Permanent |
| Interface specs | 3 | OpenAPI or JSON schema | Permanent |
| Data flow | 4 | Mermaid diagram | Permanent |
| Risk register | 5 | Markdown table | Project lifetime |
| ADR | 6 | Markdown | Permanent (Decision Memory) |

## Confidence Scoring

- Context completeness: 0-15 (all prior art found)
- Boundary correctness: 0-20 (no overlap, right abstraction level)
- Interface quality: 0-20 (consistent, well-typed, documented)
- Data flow soundness: 0-15 (no cycles, no data loss)
- Risk coverage: 0-15 (all risks addressed)
- ADR quality: 0-15 (clear, justified, stored)

## Rollback

| Step | Undo Action | Conditions |
|---|---|---|
| 1-6 | Discard architecture proposal; revert Knowledge Graph to prior state | User rejects; gate failure |
| 3 (if implemented) | Revert interface implementations to last known good | Breaking change detected |
| 6 | Mark ADR as superseded in Knowledge Graph | New architecture replaces this one |

## Telemetry

| Step | Event | Payload |
|---|---|---|
| 1 | architect.context_loaded | adr_count, pattern_count |
| 2 | architect.boundaries_defined | component_count |
| 3 | architect.interfaces_designed | interface_count, consistency_score |
| 4 | architect.data_flow_mapped | node_count, edge_count |
| 5 | architect.risk_assessed | risk_count, high_risk_count |
| 6 | architect.adr_created | adr_id, decision_summary |
