# Data Retention Policy

**Status:** Active  
**Owner:** sla113

## Retention Rules by Data Type

| Data Type | Retention | Storage | Notes |
|---|---|---|---|
| User auth tokens (JWT) | Session only | Memory | Never persisted |
| User profile data | Indefinite | MongoDB/CockroachDB | Artist-controlled deletion |
| Micro-royalty ledger entries | Permanent | CockroachDB | Immutable audit trail |
| Audio renders (DRAFT) | 7 days | GCS | Auto-purged |
| Audio renders (PREVIEW) | 30 days | GCS | Artist can extend |
| Audio renders (FINAL) | Permanent | GCS | Artist-owned |
| Ghost Audio artifacts (jail calls, voicemails) | Permanent | Cultural Vault (GCS encrypted) | Consent contract required |
| Bloodline vocal matrices | Permanent | Cultural Vault | Consent contract required |
| Session agent logs | 90 days | Cloud Logging | PII scrubbed |
| Observability metrics | 13 months | Cloud Monitoring | |

## Cultural Vault Special Rules

All heritage assets (bloodline vocals, Ghost Audio artifacts, family recordings) are:
- Encrypted at rest with artist-specific KMS key
- Never used for model training without explicit consent smart contract
- Never served cross-universe without artist approval
- Deletion honored within 30 days of artist request
