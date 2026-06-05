"""LLM client wrapper with hybrid fallback support."""
from __future__ import annotations

import asyncio
import json
import logging
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv


logger = logging.getLogger("omni_agent.llm")


class LLMUnavailable(Exception):
    """Raised when LLM cannot be used (no key, error, timeout, rate limit)."""


@dataclass
class LLMResult:
    text: str
    model: str
    mode_used: str  # "llm" or "rule"


def _load_env_files(repo_root: Path, env_files):
    for ef in env_files or []:
        p = repo_root / ef
        if p.exists():
            load_dotenv(p, override=False)


class LLMClient:
    def __init__(self, config: dict, repo_root: Path):
        self.repo_root = Path(repo_root)
        llm_cfg = (config or {}).get("llm", {}) or {}
        self.provider = llm_cfg.get("provider", "google")
        self.model = llm_cfg.get("model", "gemini-2.0-flash")
        self.timeout = int(llm_cfg.get("timeout_seconds", 30))
        self.api_key_env = llm_cfg.get("api_key_env", "GOOGLE_API_KEY")
        _load_env_files(self.repo_root, llm_cfg.get("env_files"))
        self.api_key = os.environ.get(self.api_key_env)

    def available(self) -> bool:
        if not self.api_key:
            return False
        try:
            from google import genai  # noqa: F401
            return True
        except Exception:
            return False

    async def _call_async(self, system_message: str, user_text: str, session_id: str) -> str:
        from google import genai
        from google.genai import types
        client = genai.Client(api_key=self.api_key)
        try:
            response = await asyncio.wait_for(
                asyncio.to_thread(
                    client.models.generate_content,
                    model=self.model,
                    contents=user_text,
                    config=types.GenerateContentConfig(
                        system_instruction=system_message,
                    ),
                ),
                timeout=self.timeout,
            )
            return response.text or ""
        except asyncio.TimeoutError as e:
            raise LLMUnavailable(f"timeout after {self.timeout}s") from e

    def call(self, system_message: str, user_text: str, session_id: str) -> LLMResult:
        if not self.available():
            raise LLMUnavailable("LLM not available (missing key or library)")
        try:
            text = asyncio.run(self._call_async(system_message, user_text, session_id))
            return LLMResult(text=text or "", model=self.model, mode_used="llm")
        except LLMUnavailable:
            raise
        except Exception as e:
            msg = str(e).lower()
            if "rate" in msg or "quota" in msg or "429" in msg:
                raise LLMUnavailable(f"rate limit: {e}") from e
            raise LLMUnavailable(f"llm error: {e}") from e

    @staticmethod
    def extract_json(text: str) -> Optional[dict]:
        """Best-effort JSON extraction from LLM response."""
        if not text:
            return None
        # try fenced code block first
        m = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
        candidate = m.group(1) if m else None
        if not candidate:
            # find first { ... } balanced-ish
            start = text.find("{")
            end = text.rfind("}")
            if start != -1 and end > start:
                candidate = text[start : end + 1]
        if not candidate:
            return None
        try:
            return json.loads(candidate)
        except Exception:
            return None
