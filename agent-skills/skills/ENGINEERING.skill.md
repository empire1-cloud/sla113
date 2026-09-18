# Skill: ENGINEERING

## Metadata

- name: ENGINEERING
- version: 1.0.0
- description: Infrastructure, CI/CD, dependency management, deployment pipelines, system configuration.
- triggers: "set up", "configure", "deploy", "infrastructure", "CI/CD", "Docker", "migration", dependency
- required_personas: Developer, Architect
- max_duration: 45m
- confidence_threshold: 85

## Workflow

| Step | Name | Persona | Input | Output | Description | Quality Gate |
|---|---|---|---|---|---|---|
| 1 | Assess | Architect | Request, current infra, config, Knowledge Graph | Current state summary, constraints, risk level | Load current infrastructure from config and Knowledge Graph. Identify constraints (ports, secrets, regions). Check ADRs for prior infra decisions. | Current state fully understood; constraints documented |
| 2 | Design | Architect | Assessment, requirements | Design document (approach, files to change, dependencies) | Design the infrastructure change. List exact files. Note dependency changes. Estimate rollback complexity. | Design is minimal; rollback path exists |
| 3 | Guardrail check | Developer | File list, Guardrails | Allowed file list | Filter sensitive paths (secrets, env, production config). Log filtered paths. | No forbidden paths; no secrets exposed |
| 4 | Implement | Developer | Design, allowed files | Configuration changes, scripts, migrations | Apply changes. Update config files, CI pipelines, Dockerfiles, migration scripts. Test dry-run if applicable. | Configs valid; dry-run passes; no syntax errors |
| 5 | Validate | Developer, Architect | Changes | Validation results (syntax, security, integration) | Run config validation, security scan, integration test. Check that nothing is broken. | All validations pass |
| 6 | Document | Developer, Architect | Changes, validation | ADR or changelog entry, rollback instructions | Write changelog. Store infra ADR in Knowledge Graph. Write rollback instructions to Memory Platform (Procedural). | Documented; rollback plan clear |

## Quality Gates

| Gate | Step | Condition | Failure Action |
|---|---|---|---|
| Constraints documented | 1 | All constraints listed; no hidden dependencies | Research further; surface unknowns |
| Rollback exists | 2 | Every change has a revert strategy | Re-design to ensure reversible |
| Secrets safe | 3 | No secrets, env files, or prod credentials in changes | Remove secret exposure; flag to user |
| Dry run passes | 4 | Config dry-run exits 0; migrations reversible | Debug failure before deploying |
| Integration clean | 5 | Downstream services not broken by change | Revert or redesign |
| Rollback documented | 6 | Clear step-by-step rollback in Procedural Memory | Add missing rollback steps |

## Evidence

| Artifact | From Step | Format | Retention |
|---|---|---|---|
| Current state | 1 | JSON/Markdown (services, versions, configs) | Project lifetime |
| Design document | 2 | Markdown | Project lifetime |
| Guardrail log | 3 | JSON (filtered_paths) | 90 days |
| Config diffs | 4 | Git diff or patch | Permanent |
| Validation results | 5 | JSON (checks passed/failed) | Permanent |
| Rollback plan | 6 | Markdown | Permanent (Procedural Memory) |

## Confidence Scoring

- Constraint coverage: 0-15 (all constraints identified)
- Design quality: 0-20 (minimal, reversible, tested)
- Security: 0-20 (no secrets, no exposed ports, no weak configs)
- Validation pass rate: 0-20 (all checks green)
- Documentation: 0-15 (changelog, rollback, rationale)
- Rollback clarity: 0-10 (steps specific enough to follow)

## Rollback

| Step | Undo Action | Conditions |
|---|---|---|
| 4 | Revert config changes via git; restore previous versions | No data migration applied |
| 4 | Run reverse migration | Forward migration applied |
| 4 | Restore from backup config | Production outage |

## Telemetry

| Step | Event | Payload |
|---|---|---|
| 1 | engineering.assessed | constraint_count, risk_level |
| 2 | engineering.designed | file_count, dependency_count |
| 3 | engineering.guardrails_checked | allowed_count, filtered_count |
| 4 | engineering.implemented | files_changed, dry_run_result |
| 5 | engineering.validated | checks_passed, checks_failed |
| 6 | engineering.documented | adr_created, rollback_written |
