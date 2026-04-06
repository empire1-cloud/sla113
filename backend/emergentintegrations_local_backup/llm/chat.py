"""
LLM Chat - Unified Chat Interface
Supports OpenAI, Anthropic, and Google/Gemini models.

Usage:
    from emergentintegrations.llm.chat import LlmChat, UserMessage
    
    # Create chat instance
    chat = LlmChat(
        api_key="sk-...",
        session_id="my-session",
        system_message="You are a helpful assistant."
    )
    
    # Configure model
    chat = chat.with_model("openai", "gpt-4o")
    
    # Send message
    response = await chat.send_message(UserMessage(text="Hello!"))
    print(response)
"""

import os
import json
import asyncio
import httpx
from typing import Optional, List, Dict, Any, Union
from dataclasses import dataclass, field
from datetime import datetime
import uuid

from .message import Message, UserMessage, SystemMessage, AssistantMessage, Conversation, MessageRole
from .config import LLMConfig, ModelProvider, MODEL_REGISTRY


@dataclass
class ChatResponse:
    """Response from an LLM chat completion."""
    content: str
    model: str
    provider: str
    usage: Dict[str, int] = field(default_factory=dict)
    raw_response: Dict[str, Any] = field(default_factory=dict)
    finish_reason: str = "stop"


class ChatLLM:
    """
    Low-level unified chat interface for direct API calls.
    
    Usage:
        response = await ChatLLM.chat(
            api_key="sk-...",
            model="gpt-4o",
            provider="openai",
            messages=[{"role": "user", "content": "Hello"}]
        )
    """
    
    DEFAULT_TIMEOUT = 120.0
    
    @classmethod
    async def chat(
        cls,
        api_key: str,
        model: str,
        messages: List[Dict[str, str]],
        provider: Optional[str] = None,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        timeout: float = DEFAULT_TIMEOUT,
        **kwargs
    ) -> ChatResponse:
        """
        Send a chat completion request.
        
        Args:
            api_key: API key for the provider
            model: Model name
            messages: List of message dicts
            provider: Provider name (auto-detected if not specified)
            system_prompt: Optional system prompt
            temperature: Sampling temperature
            max_tokens: Max response tokens
            timeout: Request timeout
            
        Returns:
            ChatResponse with content and metadata
        """
        # Resolve provider and model
        if provider:
            prov, model_id = LLMConfig.resolve_model(provider, model)
        else:
            # Auto-detect from model name
            model_lower = model.lower()
            if "gpt" in model_lower or "o1" in model_lower:
                prov = ModelProvider.OPENAI
            elif "claude" in model_lower:
                prov = ModelProvider.ANTHROPIC
            elif "gemini" in model_lower:
                prov = ModelProvider.GOOGLE
            else:
                prov = ModelProvider.OPENAI
            
            config = MODEL_REGISTRY.get(model)
            model_id = config.model_id if config else model
        
        # Route to provider
        if prov == ModelProvider.OPENAI:
            return await cls._openai_chat(api_key, model_id, messages, system_prompt, temperature, max_tokens, timeout)
        elif prov == ModelProvider.ANTHROPIC:
            return await cls._anthropic_chat(api_key, model_id, messages, system_prompt, temperature, max_tokens, timeout)
        elif prov in (ModelProvider.GOOGLE, ModelProvider.GEMINI):
            return await cls._google_chat(api_key, model_id, messages, system_prompt, temperature, max_tokens, timeout)
        else:
            raise ValueError(f"Unsupported provider: {prov}")
    
    @classmethod
    async def _openai_chat(
        cls, api_key: str, model: str, messages: List[Dict], 
        system_prompt: str, temperature: float, max_tokens: int, timeout: float
    ) -> ChatResponse:
        """OpenAI Chat Completion API."""
        
        formatted_messages = []
        if system_prompt:
            formatted_messages.append({"role": "system", "content": system_prompt})
        formatted_messages.extend(messages)
        
        payload = {
            "model": model,
            "messages": formatted_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                json=payload,
                headers=headers
            )
            response.raise_for_status()
            data = response.json()
        
        return ChatResponse(
            content=data["choices"][0]["message"]["content"],
            model=model,
            provider="openai",
            usage=data.get("usage", {}),
            raw_response=data,
            finish_reason=data["choices"][0].get("finish_reason", "stop")
        )
    
    @classmethod
    async def _anthropic_chat(
        cls, api_key: str, model: str, messages: List[Dict],
        system_prompt: str, temperature: float, max_tokens: int, timeout: float
    ) -> ChatResponse:
        """Anthropic Messages API."""
        
        # Filter out system messages from the messages list
        filtered_messages = [m for m in messages if m.get("role") != "system"]
        
        payload = {
            "model": model,
            "messages": filtered_messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        
        if system_prompt:
            payload["system"] = system_prompt
        
        headers = {
            "x-api-key": api_key,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01",
        }
        
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                json=payload,
                headers=headers
            )
            response.raise_for_status()
            data = response.json()
        
        content = ""
        for block in data.get("content", []):
            if block.get("type") == "text":
                content += block.get("text", "")
        
        return ChatResponse(
            content=content,
            model=model,
            provider="anthropic",
            usage=data.get("usage", {}),
            raw_response=data,
            finish_reason=data.get("stop_reason", "stop")
        )
    
    @classmethod
    async def _google_chat(
        cls, api_key: str, model: str, messages: List[Dict],
        system_prompt: str, temperature: float, max_tokens: int, timeout: float
    ) -> ChatResponse:
        """Google Generative AI API."""
        
        contents = []
        for msg in messages:
            if msg.get("role") == "system":
                continue  # Handle separately
            role = "user" if msg["role"] == "user" else "model"
            contents.append({
                "role": role,
                "parts": [{"text": msg["content"]}]
            })
        
        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens,
            }
        }
        
        if system_prompt:
            payload["systemInstruction"] = {
                "parts": [{"text": system_prompt}]
            }
        
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
        
        content = ""
        candidates = data.get("candidates", [])
        if candidates:
            parts = candidates[0].get("content", {}).get("parts", [])
            for part in parts:
                content += part.get("text", "")
        
        return ChatResponse(
            content=content,
            model=model,
            provider="google",
            usage=data.get("usageMetadata", {}),
            raw_response=data,
            finish_reason=candidates[0].get("finishReason", "STOP") if candidates else "STOP"
        )


class LlmChat:
    """
    High-level chat interface with conversation management.
    
    This is the main class used by engines. Provides:
    - Session management
    - Conversation history
    - Model configuration
    - Easy message sending
    
    Usage:
        chat = LlmChat(
            api_key="sk-...",
            session_id="strategy-engine",
            system_message="You are a strategy expert."
        )
        chat = chat.with_model("openai", "gpt-4o")
        
        response = await chat.send_message(UserMessage(text="Create a strategy for..."))
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        session_id: Optional[str] = None,
        system_message: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        timeout: float = 120.0,
    ):
        """
        Initialize chat instance.
        
        Args:
            api_key: API key (uses env var if not provided)
            session_id: Unique session identifier
            system_message: System prompt for AI behavior
            temperature: Sampling temperature
            max_tokens: Max response tokens
            timeout: Request timeout
        """
        self.api_key = api_key
        self.session_id = session_id or str(uuid.uuid4())
        self.system_message = system_message
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout = timeout
        
        # Default provider/model
        self.provider: ModelProvider = ModelProvider.OPENAI
        self.model: str = "gpt-4o"
        
        # Conversation history
        self.conversation = Conversation(system_message=system_message)
        self.history: List[Dict[str, str]] = []
    
    def with_model(self, provider: str, model: str) -> "LlmChat":
        """
        Configure the model to use.
        
        Args:
            provider: "openai", "anthropic", "google", or "gemini"
            model: Model name or identifier
            
        Returns:
            Self for method chaining
        """
        self.provider, self.model = LLMConfig.resolve_model(provider, model)
        return self
    
    def with_temperature(self, temperature: float) -> "LlmChat":
        """Set sampling temperature."""
        self.temperature = temperature
        return self
    
    def with_max_tokens(self, max_tokens: int) -> "LlmChat":
        """Set max response tokens."""
        self.max_tokens = max_tokens
        return self
    
    def with_timeout(self, timeout: float) -> "LlmChat":
        """Set request timeout."""
        self.timeout = timeout
        return self
    
    def _get_api_key(self) -> str:
        """Get API key from instance or environment."""
        if self.api_key:
            return self.api_key
        
        key = LLMConfig.get_api_key(self.provider)
        if not key:
            raise ValueError(
                f"No API key found for {self.provider.value}. "
                f"Set {LLMConfig.ENV_KEYS.get(self.provider, 'API_KEY')} or EMERGENT_LLM_KEY"
            )
        return key
    
    async def send_message(self, message: Union[UserMessage, str]) -> str:
        """
        Send a message and get a response.
        
        Args:
            message: UserMessage object or string
            
        Returns:
            Assistant's response text
        """
        # Convert string to UserMessage
        if isinstance(message, str):
            message = UserMessage(text=message)
        
        # Add to conversation
        self.conversation.add_message(message)
        
        # Prepare messages for API
        messages = []
        for m in self.conversation.messages:
            if m.role != MessageRole.SYSTEM:  # System handled separately
                messages.append(m.to_dict())
        
        # Get API key
        api_key = self._get_api_key()
        
        # Send request
        response = await ChatLLM.chat(
            api_key=api_key,
            model=self.model,
            provider=self.provider.value,
            messages=messages,
            system_prompt=self.system_message,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            timeout=self.timeout,
        )
        
        # Add response to conversation
        assistant_msg = AssistantMessage(text=response.content)
        self.conversation.add_message(assistant_msg)
        
        # Store in history
        self.history.append({
            "role": "user",
            "content": message.content,
            "timestamp": datetime.utcnow().isoformat(),
        })
        self.history.append({
            "role": "assistant", 
            "content": response.content,
            "timestamp": datetime.utcnow().isoformat(),
        })
        
        return response.content
    
    def send_message_sync(self, message: Union[UserMessage, str]) -> str:
        """Synchronous wrapper for send_message."""
        return asyncio.run(self.send_message(message))
    
    async def generate(self, prompt: str) -> str:
        """
        Generate a one-off response without conversation history.
        
        Args:
            prompt: User prompt
            
        Returns:
            Generated response
        """
        api_key = self._get_api_key()
        
        messages = [{"role": "user", "content": prompt}]
        
        response = await ChatLLM.chat(
            api_key=api_key,
            model=self.model,
            provider=self.provider.value,
            messages=messages,
            system_prompt=self.system_message,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            timeout=self.timeout,
        )
        
        return response.content
    
    def generate_sync(self, prompt: str) -> str:
        """Synchronous wrapper for generate."""
        return asyncio.run(self.generate(prompt))
    
    def clear_history(self):
        """Clear conversation history."""
        self.conversation.clear()
        self.history = []
    
    def get_history(self) -> List[Dict[str, str]]:
        """Get conversation history."""
        return self.history.copy()
    
    def __repr__(self) -> str:
        return f"LlmChat(provider={self.provider.value}, model={self.model}, session={self.session_id})"
