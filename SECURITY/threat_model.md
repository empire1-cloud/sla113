# Threat Model — SLA-113 Empire

**Status:** Living document  
**Owner:** sla113  
**Last updated:** 2026-05-03

## Trust Boundaries

| Boundary | Description |
|---|---|
| Public internet → Empire-1/Lyrica3 | Cloudflare WAF + rate limiting |
| Lyrica3 frontend → lyrica3-backend | JWT auth, identity firewall middleware |
| lyrica3-backend → SLA113 control plane | Service account + VPC internal only |
| SLA113 → CockroachDB/MongoDB | Private IP, TLS required |
| Operator (sla113.southernlifestyle.org) → U0 | SLA113 admin JWT, separate secret |

## Key Risks

1. **Cross-universe token reuse** — A token issued for U1 must not be accepted by U4. Mitigated by universe-scoped JWT claims.
2. **Middleware bypass** — If middleware.ts is broken, lyrica3.com falls through to Empire-1 homepage. Fix: ADR 0003, commit f4e1f24.
3. **Agent prompt injection** — Lyrica pipeline agents accept user text. Mitigated by AURA input sanitization layer.
4. **Royalty ledger manipulation** — CockroachDB ledger writes must be idempotent and signed. Mitigated by empire_ledger service checksums.
5. **Cultural vault IP leak** — Heritage data (bloodline vocals, jail calls, family assets) must never leave the vault without artist consent smart contract.

## Key Rotation Policy

- JWT secrets: rotate every 90 days, or immediately on suspected compromise
- GCP service account keys: rotate every 60 days
- See `SECURITY/key_rotation/` for rotation runbooks
