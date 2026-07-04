# AGENTS.md — SLA113 OS

This repo is part of the Empire1 ecosystem. See `~/projects/AGENTS.md` for full ecosystem context.

## Agent Skills (Engineering Workflow)

This project follows disciplined development workflows defined in `~/projects/agent-skills/skills/`. Key skills for this repo:

- `spec-driven-development` — PRD before code for all engine work
- `test-driven-development` — Red-Green-Refactor for game engines
- `incremental-implementation` — Thin vertical slices
- `security-and-hardening` — OWASP for all compliance/regulatory routes
- `performance-optimization` — Measure-first for game engine perf
- `api-and-interface-design` — Contract-first for all SLA113 endpoints

## Key Paths

| Resource | Path |
|----------|------|
| Ecosystem source of truth | `~/projects/AGENTS.md` |
| Skills (23 engineering workflows) | `~/projects/agent-skills/skills/` |
| Skill agents/personas | `~/projects/agent-skills/agents/` |
| Agent memory (MCP) | `mempalace` — installed via `uv tool install mempalace` |
| Market research | `/last30days <topic>` — requires `npx skills add mvanhorn/last30days-skill -g` |
