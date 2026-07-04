# Skill: PLAN

## Metadata

- name: PLAN
- version: 1.0.0
- description: Decompose ambiguous goals into concrete, ordered tasks with dependencies and acceptance criteria.
- triggers: new goal, ambiguous request, "figure out what to do", multi-step task, incoming from cognitive loop
- required_personas: Planner, Analyst
- max_duration: 15m
- confidence_threshold: 80

## Workflow

| Step | Name | Persona | Input | Output | Description | Quality Gate |
|---|---|---|---|---|---|---|
| 1 | Clarify | Planner | Goal text, context, memory recall | Clarified goal, constraints, stakeholders | Rephrase the goal in concrete terms. Identify what's in scope, what's out of scope. Recall past decisions via Memory Platform. | All ambiguous terms resolved; goal falsifiable |
| 2 | Decompose | Planner | Clarified goal | Task list with dependencies | Break goal into sub-tasks. Order by dependency. Estimate complexity (S/M/L). | Each task is independently completable; dependencies acyclic |
| 3 | Research gaps | Analyst | Task list, Knowledge Graph | Research notes for unknown areas | For any task with uncertainty, hit Trend Intelligence or search Memory/Graph. | Confidence >= threshold for each unknown |
| 4 | Assign skills | Planner | Task list, research notes | Task-skill assignments | Map each task to a skill (BUILD, RESEARCH, MUSIC, etc.). Identify required personas. | Every task has a valid skill; persona available |
| 5 | Sequence | Planner | Task-skill assignments | Execution plan with timeline | Order tasks for parallel/serial execution. Set expected durations. Identify block points. | Plan is executable; no resource conflict |
| 6 | Validate | Planner, Analyst | Execution plan | Validated plan | Run plan through Decision Engine. Score confidence. Check for conflicts in Knowledge Graph. | Confidence score >= threshold |

## Quality Gates

| Gate | Step | Condition | Failure Action |
|---|---|---|---|
| Goal clarity | 1 | All ambiguous terms resolved; goal is falsifiable | Request clarification from user |
| Dependency acyclicity | 2 | No circular dependencies in task graph | Re-decompose to remove cycles |
| Research confidence | 3 | Each uncertain area has confidence >= 0.7 | Mark task as blocked_context; request input |
| Skill validity | 4 | Every task maps to a registered skill | Flag missing skill; request user to define |
| Resource availability | 5 | No persona assigned to >1 task simultaneously | Adjust timeline or add buffer |
| Decision check | 6 | No conflicting ADRs or prior decisions | Surface conflict to user; recommend resolution |

## Evidence

| Artifact | From Step | Format | Retention |
|---|---|---|---|
| Clarified goal | 1 | Markdown | Project lifetime |
| Task decomposition | 2 | JSON (tasks with deps) | Project lifetime |
| Research notes | 3 | Markdown | 90 days |
| Skill assignments | 4 | JSON (task->skill mapping) | Until plan complete |
| Execution plan | 5 | JSON (ordered timeline) | Until plan complete |
| Validation result | 6 | JSON (confidence, conflicts) | Permanent (Decision Memory) |

## Confidence Scoring

- Goal clarity: 0-20 (explicit scope, time, quality)
- Dependency correctness: 0-25 (no cycles, correct ordering)
- Research completeness: 0-20 (all unknowns addressed)
- Skill fit: 0-15 (right skill for each task)
- Resource feasibility: 0-10 (no overcommit)
- Decision compatibility: 0-10 (no conflicts)

## Rollback

| Step | Undo Action | Conditions |
|---|---|---|
| 1-6 | Discard plan; restore previous execution plan from Memory Platform | Any gate failure; user cancels |

## Telemetry

| Step | Event | Payload |
|---|---|---|
| 1 | goal.clarified | original_text, clarified_text, ambiguity_count |
| 2 | task.decomposed | task_count, complexity_distribution |
| 3 | research.completed | unknown_areas, confidence_scores |
| 4 | skills.assigned | skill_counts, persona_assignments |
| 5 | plan.sequenced | timeline_duration, parallel_count |
| 6 | plan.validated | confidence_score, conflict_count |
