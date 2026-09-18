# Skill: SHIP

## Metadata

- name: SHIP
- version: 1.0.0
- description: Deliver completed work — test, lint, commit, push, deploy, announce.
- triggers: "ship", "deploy", "release", "publish", "go live", "push", /ship
- required_personas: Developer, Dispatcher
- max_duration: 15m
- confidence_threshold: 90

## Workflow

| Step | Name | Persona | Input | Output | Description | Quality Gate |
|---|---|---|---|---|---|---|
| 1 | Pre-flight | Developer | Task, changes, git status | Pre-flight check results | Check git status, diff, recent commits. Verify nothing is dirty that shouldn't be. Confirm branch is correct. | Working tree clean for intended files; branch correct |
| 2 | Test | Developer | Codebase | Test results (pytest, ruff, type check) | Run full test suite. Run lint. Run type check. All must pass. | All tests pass; lint clean; types check |
| 3 | Review gate | Developer, Reviewer | Changes, test results | Review outcome (auto or human) | If configured, run auto-review. If human-in-loop requested, wait for approval. | Review approved or auto-gate passed |
| 4 | Commit | Developer | Approved changes | Git commit | Stage intended files. Write commit message (conventional commit). Do not commit secrets, config, or unintended files. | Commit created; message follows convention |
| 5 | Push | Developer, Dispatcher | Commit | Remote push, CI trigger | Push to remote. Trigger CI/CD. Monitor first 60s of CI. | Push successful; CI started |
| 6 | Announce | Dispatcher | Commit, CI result | Deploy notification, changelog entry, Memory update | Post to Slack/email. Update Memory Platform (Procedural). Create changelog entry. Update Knowledge Graph if needed. | Notification sent; Memory updated |

## Quality Gates

| Gate | Step | Condition | Failure Action |
|---|---|---|---|
| Branch correct | 1 | Not on main/master unless intentional | Abort; ask user to confirm |
| Tests green | 2 | pytest exit 0; ruff clean; types pass | Fix failures; or override with user approval |
| Review pass | 3 | Auto-review score >= 90; or human approved | Block; request changes |
| Commit clean | 4 | No secrets, no unintended files, no large binaries | Remove unintended files; rebase |
| Push succeeds | 5 | Remote accepted; CI started | Retry; check remote health |
| Announcement sent | 6 | Notification sent; Memory updated | Retry send; log manually |

## Evidence

| Artifact | From Step | Format | Retention |
|---|---|---|---|
| Pre-flight report | 1 | Markdown | Session |
| Test results | 2 | JSON (exit codes, output) | Permanent |
| Review outcome | 3 | JSON (score, approval) | Permanent |
| Commit SHA | 4 | String | Permanent |
| CI status | 5 | String (triggered URL or status) | 30 days |
| Announcement | 6 | Markdown | Permanent (Procedural Memory) |

## Confidence Scoring

- Test pass rate: 0-30 (all tests green; no skips)
- Lint quality: 0-20 (no warnings; no new warnings)
- Commit quality: 0-20 (message convention; no unintended files)
- CI success rate: 0-15 (first 60s green)
- Notification delivery: 0-15 (announcement sent and confirmed)

## Rollback

| Step | Undo Action | Conditions |
|---|---|---|
| 4 | `git reset HEAD~1`; restore files | Not yet pushed |
| 5 | `git revert <sha>`; force push if needed | Already pushed; CI not yet deployed |
| 5 | Rollback deployment (revert tag or re-deploy previous) | Deployed to production |
| 6 | Send correction or revert announcement | Incorrect announcement |

## Telemetry

| Step | Event | Payload |
|---|---|---|
| 1 | ship.preflight_ok | branch, dirty_count |
| 2 | ship.tests_run | pass_count, fail_count, duration_ms |
| 3 | ship.review_gate | score, approved |
| 4 | ship.committed | sha, message, file_count |
| 5 | ship.pushed | remote, ci_triggered |
| 6 | ship.announced | channel, memory_stored |
