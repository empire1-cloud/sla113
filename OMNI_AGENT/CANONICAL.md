# Execution Engine — Canonical Source

This is the **canonical** copy of the SLA113 Execution Engine (formerly Omni-Agent).

## Location

**Full canonical path:** `~/projects/sla113/OMNI_AGENT/`

## Purpose

The Execution Engine orchestrates work across all SLA113-powered products.
It implements:
- State machine (SQLite, 8 states, 7 tables)
- 3 core personas: Analyst → Developer → Evaluator
- 7 markdown persona definitions for the broader ecosystem
- Guardrails system (allowed/forbidden paths)
- Scanner + triage pipeline
- Client reporting, PR previews, ROI tracking
- Cohesion scoring (5 weighted components, threshold 85)

## Other Copies

### Empire-1 (`~/projects/Empire-1/omni_agent/`)
Contains only state files and sales documentation.
The FastAPI service (`omni_service.py`) reads state from the canonical location.

### lyrica-ecosystem (`~/projects/empire1-lyrica-ecosystem/omni_agent/`)
Diverged copy with minor config/LLM client differences.
Should be replaced with a reference to canonical.

## Using the Execution Engine

```python
# Add to PYTHONPATH or install as editable:
# pip install -e ~/projects/sla113/OMNI_AGENT

from omni_agent.orchestrator import Orchestrator, load_config
from omni_agent.scanner import scan_repo
from omni_agent.state_machine import StateMachine
```
