# Skill: KYC Document Parse

## Metadata
- name: KYC_DOC_PARSE
- version: 1.0.0
- description: Parse KYC onboarding documents and extract structured fields
- domain: operations
- triggers: ["kyc parse", "document parsing", "onboarding extract"]
- required_personas: ["compliance_officer"]
- max_duration: "15m"
- confidence_threshold: 90

## Fields to Extract
- Entity name, jurisdiction, entity type
- Beneficial owners (name, % ownership, DOB, nationality)
- Directors and officers
- Business description and industry
- Source of funds
- Geographic exposure

## Source
Derived from Anthropic financial-services reference: plugins/vertical-plugins/operations/skills/kyc-doc-parse
