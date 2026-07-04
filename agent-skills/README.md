# SLA113 Skills Framework

The Skills Framework is the universal capability registry. Skills define *what* can be done, *how* to do it, *what quality* is expected, and *how to recover* when things go wrong.

## How It Works

```
Execution Engine (Omni-Agent)
         │
         ▼
  Skills Framework
         │
         ├── Look up skill by intent or command
         ├── Load workflow definition
         ├── Execute steps with quality gates
         ├── Collect evidence at each gate
         ├── Score confidence
         └── Log telemetry
```

## Skill Anatomy

Each skill definition contains:

| Section | Purpose |
|---|---|
| **Metadata** | Name, version, description, triggers, personas |
| **Workflow** | Ordered steps with inputs, outputs, and gates |
| **Quality Gates** | Checkpoints that must pass before proceeding |
| **Evidence** | What data to capture — files, test results, scores |
| **Confidence** | How to score the result (0-100) |
| **Telemetry** | What to log for observability |
| **Rollback** | How to undo the skill's effects |

## Skill Registry

| Skill | Triggers | Personas |
|---|---|---|
| [PLAN](skills/PLAN.skill.md) | New goal, ambiguous request, multi-step task | Planner, Analyst |
| [ARCHITECT](skills/ARCHITECT.skill.md) | System design, interface decisions, refactoring | Architect |
| [RESEARCH](skills/RESEARCH.skill.md) | Unknown domain, competitor analysis, trend intel | Analyst |
| [MUSIC](skills/MUSIC.skill.md) | "make a beat", "produce a track", audio creation | Developer (creative) |
| [BUILD](skills/BUILD.skill.md) | Code generation, feature implementation, bug fix | Developer |
| [REVIEW](skills/REVIEW.skill.md) | PR review, quality check, human-in-loop gate | Reviewer, Evaluator |
| [ENGINEERING](skills/ENGINEERING.skill.md) | Infrastructure, CI/CD, dependency management | Developer, Architect |
| [INTELLIGENCE](skills/INTELLIGENCE.skill.md) | Market research, competitive analysis, due diligence | Analyst |
| [SHIP](skills/SHIP.skill.md) | Deploy, release, publish, go live | Developer, Dispatcher |
| [TRIAGE](skills/TRIAGE.skill.md) | Classify incoming, route to correct skill | Dispatcher, Planner |
