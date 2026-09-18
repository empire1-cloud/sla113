"""Claude Runtime Adapter — Anthropic Claude API."""

from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

from base import (
    AgentHandle,
    AgentSpec,
    Event,
    RuntimeAdapter,
    Signal,
    ToolResult,
)


class ClaudeAdapter(RuntimeAdapter):
    name = "claude"
    supports_tools = True
    supports_agents = False
    supports_memory = False

    def __init__(self, api_key: Optional[str] = None, model: str = "claude-sonnet-4-20250514"):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY", "")
        self.model = model
        self._client = None

    async def _ensure_client(self):
        if self._client is None:
            try:
                import anthropic
                self._client = anthropic.AsyncAnthropic(api_key=self.api_key)
            except ImportError:
                raise RuntimeError("anthropic package not installed. Run: pip install anthropic")

    async def execute(self, tool: str, args: Dict[str, Any]) -> ToolResult:
        await self._ensure_client()
        try:
            if tool == "chat":
                messages = args.get("messages", [])
                system = args.get("system", "")
                resp = await self._client.messages.create(
                    model=self.model,
                    max_tokens=args.get("max_tokens", 4096),
                    system=system,
                    messages=messages,
                )
                return ToolResult(
                    success=True,
                    output=resp.content[0].text if resp.content else "",
                    data={"model": self.model, "usage": dict(resp.usage) if resp.usage else {}},
                )
            elif tool == "analyze_code":
                code = args.get("code", "")
                prompt = args.get("prompt", "Analyze this code")
                resp = await self._client.messages.create(
                    model=self.model,
                    max_tokens=4096,
                    messages=[
                        {"role": "user", "content": f"{prompt}\n\n```\n{code[:8000]}\n```"},
                    ],
                )
                return ToolResult(
                    success=True,
                    output=resp.content[0].text if resp.content else "",
                )
            elif tool == "generate_text":
                resp = await self._client.messages.create(
                    model=self.model,
                    max_tokens=args.get("max_tokens", 4096),
                    messages=[{"role": "user", "content": args.get("prompt", "")}],
                )
                return ToolResult(
                    success=True,
                    output=resp.content[0].text if resp.content else "",
                )
            else:
                return ToolResult(success=False, error=f"Unknown tool: {tool}")
        except Exception as e:
            return ToolResult(success=False, error=str(e))

    async def health(self) -> Dict[str, Any]:
        if not self.api_key:
            return {"status": "degraded", "error": "ANTHROPIC_API_KEY not set"}
        return {"status": "online", "model": self.model, "provider": "anthropic"}


class OpenAIAdapter(RuntimeAdapter):
    name = "openai"
    supports_tools = True
    supports_agents = True
    supports_memory = False

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY", "")
        self.model = model
        self._client = None

    async def _ensure_client(self):
        if self._client is None:
            try:
                from openai import AsyncOpenAI
                self._client = AsyncOpenAI(api_key=self.api_key)
            except ImportError:
                raise RuntimeError("openai package not installed. Run: pip install openai")

    async def execute(self, tool: str, args: Dict[str, Any]) -> ToolResult:
        await self._ensure_client()
        try:
            if tool == "chat":
                resp = await self._client.chat.completions.create(
                    model=self.model,
                    messages=args.get("messages", []),
                    max_tokens=args.get("max_tokens", 4096),
                )
                return ToolResult(
                    success=True,
                    output=resp.choices[0].message.content or "",
                    data={"model": self.model, "usage": dict(resp.usage) if resp.usage else {}},
                )
            elif tool == "generate_text":
                resp = await self._client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": args.get("prompt", "")}],
                    max_tokens=args.get("max_tokens", 4096),
                )
                return ToolResult(
                    success=True,
                    output=resp.choices[0].message.content or "",
                )
            elif tool == "generate_image":
                resp = await self._client.images.generate(
                    prompt=args.get("prompt", ""),
                    n=args.get("n", 1),
                    size=args.get("size", "1024x1024"),
                )
                return ToolResult(
                    success=True,
                    data={"urls": [img.url for img in resp.data]},
                )
            else:
                return ToolResult(success=False, error=f"Unknown tool: {tool}")
        except Exception as e:
            return ToolResult(success=False, error=str(e))

    async def spawn_agent(self, spec: AgentSpec) -> AgentHandle:
        await self._ensure_client()
        import uuid
        agent_id = f"openai_agent_{uuid.uuid4().hex[:8]}"
        # OpenAI Assistants API or simple agent loop
        return AgentHandle(agent_id=agent_id, status="running")

    async def health(self) -> Dict[str, Any]:
        if not self.api_key:
            return {"status": "degraded", "error": "OPENAI_API_KEY not set"}
        return {"status": "online", "model": self.model, "provider": "openai"}
