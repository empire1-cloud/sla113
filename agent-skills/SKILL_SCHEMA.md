# Skill Definition Schema

Every skill is a markdown file under `skills/` following this schema.

```
# Skill: <NAME>

## Metadata

- name: <string>                    # Unique skill identifier (UPPERCASE)
- version: <semver>                 # e.g., 1.0.0
- description: <string>            # What this skill does (one sentence)
- triggers: <list[string]>         # Intent keywords or commands that invoke this skill
- required_personas: <list[string]> # Which Execution Engine personas are needed
- max_duration: <duration>          # Expected max wall-clock time (e.g., "30m", "2h")
- confidence_threshold: <int>      # Minimum score to consider success (0-100)

## Workflow

Ordered steps. Each step has:

- step: <int>                       # Step number
- name: <string>                    # Short name (imperative verb)
- persona: <string>                 # Which persona executes this step
- input: <list[string]>             # What information this step needs
- output: <list[string]>            # What this step produces
- description: <string>             # What to do (natural language)
- quality_gate: <string>            # Condition that must be true to proceed

## Quality Gates

Checkpoints that must pass before the next step or before the skill is considered done.

| Gate | Step | Condition | Failure Action |
|---|---|---|---|

## Evidence

What data to capture for scoring, telemetry, and audit.

| Artifact | From Step | Format | Retention |
|---|---|---|---|

## Confidence Scoring

How to compute a 0-100 score for the skill's output.

- criteria: <list[rule]>           # Each criterion with weight and measurement

## Rollback

How to undo each step's effects.

| Step | Undo Action | Conditions |
|---|---|---|

## Telemetry

What to log at each step.

| Step | Event | Payload |
|---|---|---|
