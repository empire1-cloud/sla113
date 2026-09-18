# Skill: Audit XLS

## Metadata
- name: AUDIT_XLS
- version: 1.0.0
- description: Excel workbook audit and quality control — conventions, balance checks, formula hygiene
- domain: financial-analysis
- triggers: ["audit", "xls audit", "model audit", "excel qc"]
- required_personas: ["financial_analyst"]
- max_duration: "30m"
- confidence_threshold: 95

## Conventions
- Blue font: hardcoded inputs
- Black font: formulas
- Green font: cross-references to other sheets
- No hardcodes in calculation cells
- Named ranges for key inputs
- Circular reference detection

## Quality Checks
1. Balance sheet: A = L + E (tolerance: 0.01% of total assets)
2. Cash flow: beginning cash + change = ending cash
3. All sheets present: inputs, P&L, B/S, CF, debt, valuation
4. No #REF or #DIV/0 errors
5. Sensitivity tables fully populated

## Source
Derived from Anthropic financial-services reference: vertical-plugins/financial-analysis/skills/audit-xls
