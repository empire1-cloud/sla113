# ADR 0002 — SLA113 as Control Plane

**Status:** Accepted  
**Date:** 2026-05-03  
**Owner:** sla113

## Context

All universes need a single root authority for routing, identity firewall rules, operator access, and billing control. Without a control plane, universes diverge and can't be governed or monetized uniformly.

## Decision

SLA113 (U0) is the sovereign control plane. It:
- Owns the universe registry (`SHARED/universe_registry.yaml`)
- Runs the identity firewall (`SLA113/identity_firewall/`)
- Owns the universe compiler (`SLA113/universe_compiler/`)
- Controls the operator OS via OMNI_AGENT (U5)
- Holds all billing, API key, and team management
- Is the only universe that may modify routing rules

All other universes are downstream of U0. U0 has no upstream dependencies.

## Consequences

- `sla113.southernlifestyle.org` is the operator entry point
- SLA113 backend must be the first service deployed in any environment
- Any new universe must register with U0 before going live
- SLA113 keys and secrets are classified above all other universe secrets
