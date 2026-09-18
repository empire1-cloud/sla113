"""Local Runtime Adapter — runs models via Ollama or direct inference.

Provides offline/lightweight execution for environments without
cloud API access.
"""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional

from base import (
    AgentHandle,
    AgentSpec,
    Event,
    RuntimeAdapter,
    Signal,
    ToolResult,
)


class LocalAdapter(RuntimeAdapter):
    name = "local"
    supports_tools = True
    supports_agents = False
    supports_memory = False

    def __init__(self, model: str = "llama3", ollama_host: str = "http://localhost:11434"):
        self.model = model
        self.ollama_host = ollama_host
        self._mode = self._detect_mode()

    def _detect_mode(self) -> str:
        """Detect available local inference engine."""
        if self._check_ollama():
            return "ollama"
        return "none"

    def _check_ollama(self) -> bool:
        try:
            r = subprocess.run(
                ["ollama", "list"],
                capture_output=True, text=True, timeout=10,
            )
            return r.returncode == 0
        except Exception:
            return False

    async def _ollama_execute(self, prompt: str, system: str = "") -> str:
        try:
            r = subprocess.run(
                ["ollama", "run", self.model],
                input=f"{system}\n\n{prompt}" if system else prompt,
                capture_output=True, text=True, timeout=120,
            )
            if r.returncode == 0:
                return r.stdout.strip()
            return f"Error: {r.stderr[:500]}"
        except subprocess.TimeoutExpired:
            return "Error: Model inference timed out"
        except Exception as e:
            return f"Error: {e}"

    async def execute(self, tool: str, args: Dict[str, Any]) -> ToolResult:
        if self._mode == "none":
            return ToolResult(success=False, error="No local inference engine available. Install Ollama.")

        try:
            if tool == "chat":
                messages = args.get("messages", [])
                prompt = messages[-1].get("content", "") if messages else ""
                system = args.get("system", "")
                output = await self._ollama_execute(prompt, system)
                return ToolResult(success=True, output=output)
            elif tool == "generate_text":
                output = await self._ollama_execute(args.get("prompt", ""))
                return ToolResult(success=True, output=output)
            elif tool == "analyze_code":
                code = args.get("code", "")
                prompt = args.get("prompt", "Analyze this code")
                output = await self._ollama_execute(f"{prompt}\n\n```\n{code[:4000]}\n```")
                return ToolResult(success=True, output=output)
            else:
                return ToolResult(success=False, error=f"Unknown tool: {tool}")
        except Exception as e:
            return ToolResult(success=False, error=str(e))

    async def health(self) -> Dict[str, Any]:
        if self._mode == "none":
            return {"status": "offline", "error": "No local model engine detected"}
        return {
            "status": "online",
            "mode": self._mode,
            "model": self.model,
            "supports_offline": True,
        }


class EnterpriseAdapter(RuntimeAdapter):
    name = "enterprise"
    supports_tools = True
    supports_agents = True
    supports_memory = True

    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        model: str = "enterprise-llm",
    ):
        self.base_url = base_url or os.getenv("ENTERPRISE_LLM_URL", "")
        self.api_key = api_key or os.getenv("ENTERPRISE_API_KEY", "")
        self.model = model
        self._mode = "api" if self.base_url else "config"

    async def execute(self, tool: str, args: Dict[str, Any]) -> ToolResult:
        if not self.base_url:
            return ToolResult(success=False, error="Enterprise LLM URL not configured")

        import httpx
        try:
            headers = {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}
            async with httpx.AsyncClient(timeout=120) as client:
                resp = await client.post(
                    f"{self.base_url}/v1/chat/completions",
                    headers=headers,
                    json={
                        "model": self.model,
                        "messages": args.get("messages", [{"role": "user", "content": args.get("prompt", "")}]),
                        "max_tokens": args.get("max_tokens", 4096),
                    },
                )
                if resp.status_code == 200:
                    data = resp.json()
                    return ToolResult(
                        success=True,
                        output=data.get("choices", [{}])[0].get("message", {}).get("content", ""),
                    )
                return ToolResult(
                    success=False,
                    error=f"Enterprise API error {resp.status_code}: {resp.text[:500]}",
                )
        except Exception as e:
            return ToolResult(success=False, error=str(e))

    async def health(self) -> Dict[str, Any]:
        if not self.base_url:
            return {"status": "degraded", "error": "ENTERPRISE_LLM_URL not set"}
        return {
            "status": "online",
            "model": self.model,
            "provider": "enterprise",
            "endpoint": self.base_url,
        }
