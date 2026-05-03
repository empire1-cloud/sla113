# API Versioning Policy

**Status:** Active  
**Owner:** sla113

## Rules

1. All public API endpoints are versioned: `/api/v1/`, `/api/v2/`, etc.
2. Breaking changes require a new version. Old version must be deprecated with minimum 30-day notice.
3. Internal-only endpoints (universe-to-universe) may use `/internal/` prefix and are not versioned.
4. Payload schemas are stored in `CONTRACTS/payload_schemas/` and in `Lyrica3-pro/backend/schemas/`.
5. The `soulfire_payload.json` schema is the canonical output format for all Lyrica agent pipeline runs.

## Soulfire Payload Schema Reference

See `CONTRACTS/payload_schemas/soulfire_payload.json` (mirrored from `sl-universal/schemas/`).

## Change Control

Any breaking API change requires:
1. ADR documenting the reason
2. Updated schema file with version bump
3. Migration guide in `DATA/migrations/`
