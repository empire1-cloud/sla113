"""Gemma 4 Model Loader — Local Inference Backend

Loads Gemma 4 26B A4B MoE via Ollama or llama.cpp for self-hosted
inference with no external API dependencies.

Supports three modes:
1. ollama — preferred, uses `ollama run gemma4:26b`
2. llama_cpp — direct GGUF loading via llama-cpp-python
3. mock — fallback for dev/test when no model is available
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import subprocess
from dataclasses import dataclass
from typing import Optional, List

logger = logging.getLogger(__name__)


class ModelNotAvailableError(RuntimeError):
    pass


@dataclass
class InferenceResult:
    content: str
    tokens_used: int
    finish_reason: str = "stop"


class GemmaInference:
    MODEL_NAME = "gemma4:26b"
    OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")

    def __init__(self, model_path: Optional[str] = None):
        self.model_path = model_path
        self._backend = self._detect_backend()

    def _detect_backend(self) -> str:
        if self.model_path and os.path.isfile(self.model_path):
            return "llama_cpp"
        try:
            result = subprocess.run(
                ["ollama", "list"],
                capture_output=True, text=True, timeout=10,
            )
            if self.MODEL_NAME in result.stdout:
                return "ollama"
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass
        logger.warning("No Gemma 4 model found — using mock backend for development")
        return "mock"

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> InferenceResult:
        if self._backend == "ollama":
            return await self._generate_ollama(prompt, system_prompt, temperature, max_tokens)
        elif self._backend == "llama_cpp":
            return await self._generate_llamacpp(prompt, system_prompt, temperature, max_tokens)
        else:
            return self._generate_mock(prompt)

    async def _generate_ollama(
        self, prompt: str, system_prompt: Optional[str],
        temperature: float, max_tokens: int,
    ) -> InferenceResult:
        full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
        try:
            proc = await asyncio.create_subprocess_exec(
                "ollama", "run", self.MODEL_NAME,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await proc.communicate(
                input=full_prompt.encode(), timeout=120
            )
            content = stdout.decode().strip()
            return InferenceResult(content=content, tokens_used=len(content) // 4)
        except asyncio.TimeoutError:
            logger.error("Ollama inference timed out")
            return InferenceResult(content="", tokens_used=0, finish_reason="timeout")
        except Exception as e:
            logger.error(f"Ollama inference failed: {e}")
            raise ModelNotAvailableError(f"Gemma 4 inference unavailable: {e}")

    async def _generate_llamacpp(
        self, prompt: str, system_prompt: Optional[str],
        temperature: float, max_tokens: int,
    ) -> InferenceResult:
        try:
            from llama_cpp import Llama
            llm = Llama(model_path=self.model_path, n_ctx=8192, n_gpu_layers=-1)
            full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
            output = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: llm(
                    full_prompt,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    stop=["<|im_end|>", "<end_of_turn>"],
                ),
            )
            content = output["choices"][0]["text"].strip()
            return InferenceResult(
                content=content,
                tokens_used=output["usage"]["total_tokens"],
            )
        except ImportError:
            logger.error("llama-cpp-python not installed")
            return self._generate_mock(prompt)
        except Exception as e:
            logger.error(f"llama.cpp inference failed: {e}")
            raise ModelNotAvailableError(f"Gemma 4 GGUF loading failed: {e}")

    def _generate_mock(self, prompt: str) -> InferenceResult:
        return InferenceResult(
            content=f"[mock-gemma4] Processed: {prompt[:100]}...",
            tokens_used=0,
            finish_reason="mock",
        )

    @property
    def available(self) -> bool:
        return self._backend != "mock"
