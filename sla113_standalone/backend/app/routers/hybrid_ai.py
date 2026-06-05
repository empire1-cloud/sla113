"""HYBRID AI Router — Local Gemma 4 Inference API

Replaces the external emergentintegrations dependency with self-hosted
Gemma 4 26B A4B MoE inference for all SLA113 engines.
"""
from fastapi import APIRouter, HTTPException
import logging
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
from HYBRID_AI.orchestrator import LlmChat, UserMessage, ChatLLM
from HYBRID_AI.canon_enforcer import CanonEnforcer
from HYBRID_AI.gemma_loader import GemmaInference, ModelNotAvailableError

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/hybrid-ai", tags=["hybrid-ai"])

_inference = GemmaInference()
_canon = CanonEnforcer()


@router.get("/status")
async def hybrid_ai_status():
    return {
        "engine": "hybrid_ai",
        "model": "gemma-4-26b-a4b",
        "backend": _inference._backend,
        "available": _inference.available,
        "canon_enabled": True,
    }


@router.post("/chat")
async def hybrid_ai_chat(prompt: str, system_prompt: str = None, temperature: float = 0.7, max_tokens: int = 4096):
    try:
        chat = LlmChat(system_message=system_prompt, temperature=temperature, max_tokens=max_tokens)
        response = await chat.send_message(UserMessage(text=prompt))
        return {"response": response, "model": "gemma-4-26b-a4b", "provider": "local"}
    except ModelNotAvailableError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inference failed: {e}")


@router.post("/generate")
async def hybrid_ai_generate(prompt: str, system_prompt: str = None, temperature: float = 0.7, max_tokens: int = 4096):
    try:
        result = await _inference.generate(
            prompt=prompt, system_prompt=system_prompt,
            temperature=temperature, max_tokens=max_tokens,
        )
        content = _canon.enforce(result.content)
        return {
            "response": content,
            "model": "gemma-4-26b-a4b",
            "tokens_used": result.tokens_used,
            "finish_reason": result.finish_reason,
        }
    except ModelNotAvailableError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation failed: {e}")


@router.get("/canon/status")
async def canon_status():
    return {
        "cultural_firewall": True,
        "epd_enabled": True,
        "sovereign_minting": True,
    }


@router.post("/canon/validate")
async def canon_validate(content: str):
    issue = _canon.validate_output(content)
    return {
        "valid": issue is None,
        "issue": issue,
        "epd_score": _canon.score_epd(content),
    }
