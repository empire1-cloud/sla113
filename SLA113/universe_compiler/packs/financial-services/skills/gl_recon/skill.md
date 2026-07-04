# Skill: GL Reconciliation

## Metadata
- name: GL_RECON
- version: 1.0.0
- description: General ledger to subledger reconciliation with break detection and reporting
- domain: fund-admin
- triggers: ["gl reconciliation", "recon", "balance sheet recon"]
- required_personas: ["fund_accountant"]
- max_duration: "1h"
- confidence_threshold: 90

## Workflow
- step: 1; name: import; action: "Load GL trial balance and subledger transactions"
- step: 2; name: match; action: "Compare by amount, date, counterparty; classify as matched/break/missing"
- step: 3; name: break_analysis; skill: "break_trace"; action: "Root-cause each break (timing, classification, error)"
- step: 4; name: report; action: "Exception report with break type, age, amount, resolution owner"

## Quality Gates
- Matching rate >99.5% or flag for review
- All breaks have owner and resolution ETA

## Source
Derived from Anthropic financial-services reference: vertical-plugins/fund-admin/skills/gl-recon
