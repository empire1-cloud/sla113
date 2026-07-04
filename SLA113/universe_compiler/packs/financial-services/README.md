# Financial Services Capability Pack

> A pluggable financial intelligence capability pack for the SLA113 Execution Engine.
> Mapped from Anthropic's financial-services reference architecture.

## Architecture

```
financial-services/
├── agents/       → 10 workflow agents (pitch, research, modeling, compliance, ops)
├── skills/       → 50+ domain skills (DCF, LBO, comps, KYC, reporting)
├── providers/    → 14 MCP data provider configs
├── workflows/    → 10 cross-agent orchestration flows
├── connectors/   → MCP server connection specs
├── templates/    → Reference materials, slide templates, report templates
├── pipelines/    → CI/CD deployment pipelines
└── config/      → Plugin manifests, marketplace registries
```

## Consumption by ArchiSynapse

```
SLA113
└── Products
    └── ArchiSynapse
        ├── Agent Registry   → financial-services/agents/
        ├── Skills Registry  → financial-services/skills/
        ├── Tool Registry    → financial-services/providers/ + connectors/
        ├── Workflow Engine  → financial-services/workflows/
        └── Templates        → financial-services/templates/
```

## White-Label Architecture

White-labeling lives at the **product layer**, not the SLA113 core.
Each universe (ArchiSynapse, Empire-1, Southern Lifestyle) decides
how much branding, UI, workflows, and features are customizable
for partners. The capability pack remains domain-pure.
