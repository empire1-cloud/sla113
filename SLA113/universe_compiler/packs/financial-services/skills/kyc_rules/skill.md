# Skill: KYC Rules Engine

## Metadata
- name: KYC_RULES
- version: 1.0.0
- description: Evaluate extracted KYC data against AML sanctions and compliance rules
- domain: operations
- triggers: ["kyc rules", "aml screening", "sanctions check"]
- required_personas: ["compliance_officer"]
- max_duration: "10m"
- confidence_threshold: 95

## Rules Categories
- Sanctions screening (OFAC, UN, EU, UK)
- PEP detection
- Adverse media
- Jurisdiction risk scoring
- Entity type restrictions
- Beneficial ownership threshold checks

## Source
Derived from Anthropic financial-services reference: plugins/vertical-plugins/operations/skills/kyc-rules
