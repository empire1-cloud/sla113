"""Emergent Integrations → HYBRID_AI compatibility shim.

Routes all LLM calls to local Gemma 4 inference.
No external API keys required.
"""
import sys, os
_sla113_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if _sla113_root not in sys.path:
    sys.path.insert(0, _sla113_root)
