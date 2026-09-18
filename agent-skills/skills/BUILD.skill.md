# Skill: BUILD

## Metadata

- name: BUILD
- version: 1.0.0
- description: Implement code changes — feature development, bug fixes, refactoring, with quality gates at every step.
- triggers: "build", "implement", "add", "fix", "change", "refactor", feature request, bug report, /repo --code-paths
- required_personas: Developer, Evaluator
- max_duration: 30m
- confidence_threshold: 85

## Workflow

| Step | Name | Persona | Input | Output | Description | Quality Gate |
|---|---|---|---|---|---|---|
| 1 | Understand spec | Developer | Task, mini-spec, Knowledge Graph, Repository Intelligence | Implementation plan with file list, approach | Load dependency graph. Find files to change. Understand existing patterns. Check git history for prior attempts. | File list complete; approach consistent with existing patterns |
| 2 | Guardrail check | Developer | File list, Guardrails | Allowed file list; filtered paths logged | Filter proposed file paths through Guardrails. Log any filtered paths. | No forbidden paths in final list |
| 3 | Implement | Developer | Allowed file list, spec, approach | Code changes (create/append/replace) | Apply changes file by file. Follow existing code style. Update imports. Add minimal tests. | Each file compiles; tests pass |
| 4 | Test | Developer, Evaluator | Code changes | Test results (unit, lint, regression) | Run pytest, ruff, type check. Measure coverage on changed lines. | All tests pass; lint clean; no regressions |
| 5 | Evaluate | Evaluator | Test results, spec | Cohesion score, quality assessment | Run Evaluation Engine. Score acceptance criteria, test pass rate, regression, code quality, guardrail compliance. | Cohesion >= threshold (85 default) |
| 6 | Write back | Developer | All artifacts | State machine update, evidence stored, report generated | Update task status. Store artifacts. Generate client report. Write to Memory Platform (Procedural). | State consistent; report accessible |

## Quality Gates

| Gate | Step | Condition | Failure Action |
|---|---|---|---|
| Spec clarity | 1 | Every file to change has a clear reason; no ambiguity | Request clarification from Planner/analyst |
| Guardrail pass | 2 | No forbidden paths in proposed changes | Remove forbidden paths; flag to user |
| Compilation | 3 | All changed files pass syntax check | Fix compilation errors |
| Test pass | 4 | pytest exit code 0; ruff no errors | Fix failing tests; or mark as evaluating_failed |
| Regression | 4 | No previously passing tests broken | Revert regression-causing change |
| Cohesion pass | 5 | Score >= configured threshold | Go to evaluating_failed; surface gaps |

## Evidence

| Artifact | From Step | Format | Retention |
|---|---|---|---|
| Implementation plan | 1 | Markdown | Project lifetime |
| Guardrail log | 2 | JSON (filtered_paths, reasons) | 90 days |
| Code patches | 3 | JSON diff or patch format | Permanent |
| Test results | 4 | JSON (exit_code, stdout, failures) | Permanent |
| Cohesion score | 5 | JSON (score, component_scores) | Permanent |
| Client report | 6 | Markdown + JSON | 90 days |
| PR preview | 6 | Markdown | Until merged or closed |

## Confidence Scoring

- Spec alignment: 0-20 (code matches acceptance criteria)
- Test coverage: 0-20 (changed lines covered)
- Test pass rate: 0-20 (all tests green)
- Regression: 0-15 (no previously passing tests broken)
- Code quality: 0-15 (lint, style, patterns)
- Guardrail compliance: 0-10 (no forbidden path attempts)

## Rollback

| Step | Undo Action | Conditions |
|---|---|---|
| 3 | Revert each changed file to previous git state | No subsequent commits depend on changes |
| 3 | Apply inverse patch | Changes merged with other work |
| 5 | Revert to last known good state | Cohesion below threshold; user rejects |

## Telemetry

| Step | Event | Payload |
|---|---|---|
| 1 | build.spec_understood | file_count, approach_summary |
| 2 | build.guardrail_checked | allowed_count, filtered_count |
| 3 | build.changes_applied | files_changed, insertions, deletions |
| 4 | build.tests_run | pass_count, fail_count, coverage_pct |
| 5 | build.evaluated | cohesion_score, component_scores |
| 6 | build.written_back | task_status, report_path |
