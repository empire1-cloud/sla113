# Skill: TRIAGE

## Metadata

- name: TRIAGE
- version: 1.0.0
- description: Classify incoming requests, extract metadata, determine priority, route to correct skill and persona.
- triggers: incoming message, new issue, new PR, new email, new Slack message, voice note, any unclassified input
- required_personas: Dispatcher, Planner
- max_duration: 2m
- confidence_threshold: 80

## Workflow

| Step | Name | Persona | Input | Output | Description | Quality Gate |
|---|---|---|---|---|---|---|
| 1 | Parse | Dispatcher | Raw input (text, issue, email, voice) | Parsed intent, entities, metadata | Extract: what type of request? what domain? what entities mentioned? what urgency? Use keyword + LLM hybrid. | Intent extracted; entities identified |
| 2 | Classify | Dispatcher | Parsed intent | Task type, skill assignment, persona hint | Map intent to skill: MUSIC? BUILD? RESEARCH? SHIP? INTELLIGENCE? Also detect: is this a question, a request, a report, a command? | Skill exists for intent; confidence >= threshold |
| 3 | Prioritize | Dispatcher | Task type, entities, source | Priority (P0-P4), urgency, source weight | Score priority based on: source (Slack DM > email > issue), keywords (urgent, blocked, p0), entities mentioned (executive, customer). | Priority assigned; rationale logged |
| 4 | Context check | Dispatcher, Planner | Task, priority, Knowledge Graph, Memory Platform | Context enrichment (related tasks, prior decisions, people) | Check Knowledge Graph for related entities. Check Memory Platform for prior work on this topic. Note: who asked, what's related, what's blocked. | Enriched context attached to task |
| 5 | Route | Dispatcher | Classified + prioritized + enriched task | Task in Execution Engine queue; assigned skill | Create task in state machine (not_started). Assign to skill. Record source, priority, context. | Task created in DB; visible in queue |
| 6 | Notify | Dispatcher | Task info, route decision | Brief acknowledgement to user | Send quick ACK to user: "Got it. Triaged as [skill] at priority [P0-P4]." If blocked, explain why. | User acknowledged within 2s |

## Quality Gates

| Gate | Step | Condition | Failure Action |
|---|---|---|---|
| Intent extracted | 1 | Clear intent category; confidence >= 0.7 | Ask clarifying question |
| Skill exists | 2 | Mapped to a registered skill | Route to default (PLAN); flag missing skill |
| Priority justified | 3 | Priority matches source + content signals | Default to P2; surface for user correction |
| Context attached | 4 | Related tasks and people linked | Create orphan task; note "no context found" |
| Task stored | 5 | Task visible in state machine query | Retry; surface persistence error |
| User acknowledged | 6 | ACK sent within 2s | Skip ACK; log latency |

## Evidence

| Artifact | From Step | Format | Retention |
|---|---|---|---|
| Raw input | 0 | Text | 90 days |
| Parsed intent | 1 | JSON (intent, entities, confidence) | Permanent |
| Classification | 2 | JSON (task_type, skill, persona) | Permanent |
| Priority | 3 | JSON (priority, urgency, source_weight) | Permanent |
| Context enrichment | 4 | JSON (related_tasks, related_people, prior_work) | 90 days |
| Created task | 5 | JSON (task_id, skill, status) | Permanent |

## Confidence Scoring

- Intent accuracy: 0-25 (correct intent category)
- Skill assignment: 0-20 (right skill for the request)
- Priority correctness: 0-20 (appropriate priority level)
- Context depth: 0-20 (relevant related work found)
- Response latency: 0-15 (ACK within 2s)

## Rollback

| Step | Undo Action | Conditions |
|---|---|---|
| 5 | Delete or reassign task in state machine | Mistriage; user corrects |
| 6 | Send correction to user | Wrong ACK sent |

## Telemetry

| Step | Event | Payload |
|---|---|---|
| 1 | triage.parsed | intent, entities, confidence |
| 2 | triage.classified | task_type, skill, persona |
| 3 | triage.prioritized | priority, urgency_score |
| 4 | triage.context_checked | related_task_count, person_count |
| 5 | triage.routed | task_id, skill_assigned |
| 6 | triage.acknowledged | latency_ms, response_text |
