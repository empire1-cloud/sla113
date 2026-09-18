# Capability Pack Interface

Every pack follows the same layout so the Universe Loader loads them identically.
No pack is a special case.

## Directory Structure

```
packs/<pack-name>/
├── pack.json           → Manifest (schema v1.0+)
├── agents/             → Agent definitions (one per agent)
├── skills/             → Domain skills (SLA113 SKILL_SCHEMA.md format)
├── providers/          → Data sources (MCP, API, etc.)
├── workflows/          → Cross-agent orchestration flows
├── connectors/         → Connection specs
├── templates/          → White-labelable assets
├── pipelines/          → CI/CD
└── README.md           → Pack documentation
```

## Unified Boot Sequence

On startup, the **Universe Loader** runs this sequence:

```
1. READ pack-registry.json
2. For each registered pack:
   a. VALIDATE pack.json against pack-schema.json
   b. CHECK lifecycle state (skip if not 'active')
   c. RESOLVE dependencies against loaded capabilities
   d. REGISTER agents with the Agent Registry
   e. REGISTER skills with the Skills Registry
   f. REGISTER providers with the Tool Registry
   g. MOUNT capabilities into the Knowledge Graph
3. EXPOSE unified capability registry via /api/packs/
```

## Manifest Fields (pack.json)

| Field | Required | Description |
|---|---|---|
| `name` | yes | Unique pack identifier |
| `pack_version` | yes | Semantic version (e.g. "1.2.0") |
| `schema_version` | yes | Pack schema version (e.g. "1.0") |
| `engine_version` | yes | Required SLA113 engine version (e.g. ">=0.5.0") |
| `lifecycle` | yes | scaffold / development / testing / active / deprecated |
| `capabilities` | yes | Array of capabilities this pack provides |
| `dependencies` | no | Optional shared capability dependencies |
| `revenue_model` | yes | Primary + white-label revenue streams |

## Lifecycle States

| State | Engine Loads? | Use |
|---|---|---|
| `scaffold` | No | Placeholder for future packs |
| `development` | No (opt-in) | Active development |
| `testing` | No (opt-in) | Staging validation |
| `active` | Yes | Production — loaded at boot |
| `deprecated` | No | Replaced by newer version |

## Capability-Based Routing

The Execution Engine routes by **capability name**, not pack name.

```
Engine query: "which pack provides 'financial_modeling'?"
Registry:     "financial-services pack"
Engine:       "dispatch to financial-services/model_builder agent"
```

This keeps routing generic — the Engine never needs to know a pack's name.

## Version Compatibility

- `schema_version` — version of the pack interface (bumped only when the contract changes)
- `engine_version` — engine constraint (e.g., `>=0.5.0` allows packs to require minimum engine features)
- `pack_version` — pack's own version (bumped on content changes)

## Revenue Model

Every pack declares its revenue model:

- `revenue_model.primary` — Revenue the universe earns directly
- `revenue_model.white_label` — Revenue from white-label licensing

SLA113 collects platform fees. The universe keeps the rest.
