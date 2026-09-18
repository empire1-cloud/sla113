# Skill: REVIEW

## Metadata

- name: REVIEW
- version: 1.0.0
- description: Review code, content, or decisions against quality standards, acceptance criteria, and style guides.
- triggers: "review this", "check my work", "code review", PR review, quality gate checkpoint, human-in-loop
- required_personas: Reviewer, Evaluator
- max_duration: 15m
- confidence_threshold: 85

## Workflow

| Step | Name | Persona | Input | Output | Description | Quality Gate |
|---|---|---|---|---|---|---|
| 1 | Load context | Reviewer | PR/task, acceptance criteria, prior reviews | Context summary, relevant ADRs, patterns | Load the work product. Find acceptance criteria from the task. Check Memory Platform for related reviews. | Work product loaded; acceptance criteria retrieved |
| 2 | Check criteria | Reviewer | Work product, criteria | Criteria status (met/partial/missed) with evidence | For each acceptance criterion, check whether the work product satisfies it. Note evidence. | Every criterion assessed |
| 3 | Quality scan | Reviewer | Work product | Quality issues (style, patterns, edge cases) | Check code style, naming, error handling, test coverage, documentation. Compare with existing patterns. | No blocking issues (style, correctness, coverage) |
| 4 | Risk check | Reviewer, Evaluator | Work product, Knowledge Graph, Memory Platform | Risk assessment (breaking changes, security, perf) | Check if changes break anything in Knowledge Graph (what_breaks?). Check security (secrets, injection). Check perf. | No high-risk items unaddressed |
| 5 | Score | Evaluator | All above | Review score (0-100), summary, recommendation | Compute aggregate score. Recommendation: approve, changes-requested, or reject. | Score computed; recommendation clear |
| 6 | Report | Reviewer | Review score, findings | Review report, PR comment, ADR if needed | Write human-readable review. Post to PR/conversation. Store in Memory Platform (Episodic). | Report posted; evidence stored |

## Quality Gates

| Gate | Step | Condition | Failure Action |
|---|---|---|---|
| Criteria loaded | 1 | Acceptance criteria exist and are retrievable | Flag missing criteria; ask user |
| Full coverage | 2 | Every criterion assessed; no skips | Re-assess missed criteria |
| No blockers | 3 | No style violations, no untested code, no edge case gaps | Surface as changes-requested |
| Risk clean | 4 | No breaking changes; no security issues; no perf regressions | Block until risks addressed |
| Score threshold | 5 | Score >= configured threshold | Recommend reject or major changes |
| Report delivered | 6 | Report visible to user; stored in Memory | Retry delivery |

## Evidence

| Artifact | From Step | Format | Retention |
|---|---|---|---|
| Context summary | 1 | Markdown | Project lifetime |
| Criteria assessment | 2 | JSON (criterion, status, evidence) | Permanent |
| Quality issues | 3 | JSON (severity, file, description) | Until resolved |
| Risk register | 4 | JSON (risk, severity, mitigation) | Permanent |
| Review score | 5 | JSON (score, recommendation) | Permanent |
| Review report | 6 | Markdown | Permanent (Episodic Memory) |

## Confidence Scoring

- Criteria coverage: 0-25 (all criteria assessed)
- Quality pass rate: 0-25 (issues / total LOC)
- Risk coverage: 0-20 (all risks identified and addressed)
- Evidence quality: 0-15 (specific, verifiable evidence for each finding)
- Recommendation clarity: 0-15 (clear go/no-go with reasons)

## Rollback

| Step | Undo Action | Conditions |
|---|---|---|
| 6 | Retract or revise review report | User disagrees; new evidence emerges |

## Telemetry

| Step | Event | Payload |
|---|---|---|
| 1 | review.context_loaded | adr_count, criteria_count |
| 2 | review.criteria_assessed | met_count, missed_count |
| 3 | review.quality_scanned | issue_count, blocking_count |
| 4 | review.risk_checked | risk_count, high_risk_count |
| 5 | review.scored | score, recommendation |
| 6 | review.reported | report_length, stored |
