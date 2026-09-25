"""SLA113 Genesis Engine — deterministic game generation pipeline.

Ported from hybrid-intelligence-core PR #16 (branch fix/engine-route-contract-tests),
where it was built in the wrong repo. SLA113 is the game studio, so it lives here.

Additive only: the existing LLM-backed Vision / Logic / Composer engines in
backend/sla113/ are untouched. Genesis is the no-LLM path whose numbers are
computed, not generated.
"""
from .pipeline import GenesisPipeline

__all__ = ["GenesisPipeline"]
