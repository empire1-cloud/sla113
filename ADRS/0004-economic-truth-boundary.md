# Economic Truth Boundary

## Decision

SLA113 owns the universal economic-action envelope. Domain systems such as Lyrica and Archisynapse provide policies, adapters, and evidence; they do not create incompatible truth formats.

An external economic effect is governed only when it flows through this state machine:

`PROPOSED -> AUTHORIZED -> EXECUTED|REFUSED -> RECEIPTED -> VERIFIED`

Reversals are new evidence-bearing transitions. Existing records are never deleted or rewritten.

## Non-negotiable invariants

1. Charter, policy, actor, organization, target, value, and idempotency key are mandatory.
2. Illegal state skips fail closed.
3. Execution and refusal require evidence.
4. Receipts are canonicalized, hashed, signed, and chained.
5. Signing keys come from managed key custody; the runtime contains no fallback key.
6. A workflow is not counted as covered merely because it has an audit log.
7. The public claim “Every Economic Action. Proven.” is enabled only when every registered economic surface reports governed coverage.

## Migration sequence

1. Stripe checkout, subscription, invoice, refund, and payout effects.
2. Archisynapse ledger postings, reversals, settlements, and application fees.
3. Lyrica royalty accruals, payout approvals/refusals, licenses, and ownership changes.
4. CRM offers, discounts, renewal messages, and contract changes.
5. Remaining customer, money, rights, and revenue connectors.

Until a surface is migrated, the coverage registry must report it as uncovered. Silence is not coverage.
