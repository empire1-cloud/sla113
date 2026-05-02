"""
Message Classes for LLM Chat
Defines message types for conversation handling.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from enum import Enum
from datetime import datetime
import uuid


class MessageRole(Enum):
    """Message roles in a conversation."""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    FUNCTION = "function"
    TOOL = "tool"


@dataclass
class Message:
    """
    Base message class for LLM conversations.
    
    Attributes:
        role: The role of the message sender
        content: The text content of the message
        name: Optional name identifier
        metadata: Additional metadata
        id: Unique message identifier
        timestamp: When the message was created
    """
    role: MessageRole
    content: str
    name: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API calls."""
        d = {
            "role": self.role.value,
            "content": self.content,
        }
        if self.name:
            d["name"] = self.name
        return d
    
    def to_openai(self) -> Dict[str, str]:
        """Format for OpenAI API."""
        return self.to_dict()
    
    def to_anthropic(self) -> Dict[str, str]:
        """Format for Anthropic API."""
        return {
            "role": self.role.value,
            "content": self.content,
        }
    
    def to_google(self) -> Dict[str, Any]:
        """Format for Google API."""
        role = "user" if self.role == MessageRole.USER else "model"
        return {
            "role": role,
            "parts": [{"text": self.content}]
        }


@dataclass
class SystemMessage(Message):
    """
    System message for setting AI behavior.
    
    Usage:
        system = SystemMessage(text="You are a helpful assistant.")
    """
    text: str = ""
    role: MessageRole = field(default=MessageRole.SYSTEM)
    content: str = ""
    
    def __post_init__(self):
        self.role = MessageRole.SYSTEM
        if self.text and not self.content:
            self.content = self.text
        elif self.content and not self.text:
            self.text = self.content


@dataclass  
class UserMessage(Message):
    """
    User message in a conversation.
    
    Usage:
        msg = UserMessage(text="Hello, how are you?")
    """
    text: str = ""
    role: MessageRole = field(default=MessageRole.USER)
    content: str = ""
    
    def __post_init__(self):
        self.role = MessageRole.USER
        if self.text and not self.content:
            self.content = self.text
        elif self.content and not self.text:
            self.text = self.content


@dataclass
class AssistantMessage(Message):
    """
    Assistant/AI response message.
    
    Usage:
        msg = AssistantMessage(text="I'm doing well, thank you!")
    """
    text: str = ""
    role: MessageRole = field(default=MessageRole.ASSISTANT)
    content: str = ""
    
    def __post_init__(self):
        self.role = MessageRole.ASSISTANT
        if self.text and not self.content:
            self.content = self.text
        elif self.content and not self.text:
            self.text = self.content


@dataclass
class FunctionMessage(Message):
    """Function/tool call result message."""
    function_name: str = ""
    
    def __post_init__(self):
        self.role = MessageRole.FUNCTION
        if self.function_name:
            self.name = self.function_name


class Conversation:
    """
    Manages a conversation history.
    
    Usage:
        conv = Conversation(system_message="You are helpful.")
        conv.add_user_message("Hello")
        conv.add_assistant_message("Hi there!")
        messages = conv.to_messages()
    """
    
    def __init__(self, system_message: Optional[str] = None):
        self.messages: List[Message] = []
        self.system_message = system_message
        
        if system_message:
            self.messages.append(SystemMessage(text=system_message))
    
    def add_message(self, message: Message):
        """Add a message to the conversation."""
        self.messages.append(message)
    
    def add_user_message(self, text: str):
        """Add a user message."""
        self.messages.append(UserMessage(text=text))
    
    def add_assistant_message(self, text: str):
        """Add an assistant message."""
        self.messages.append(AssistantMessage(text=text))
    
    def to_messages(self) -> List[Dict[str, str]]:
        """Convert to list of message dicts for API calls."""
        return [m.to_dict() for m in self.messages]
    
    def to_openai(self) -> List[Dict[str, str]]:
        """Format for OpenAI API."""
        return [m.to_openai() for m in self.messages]
    
    def to_anthropic(self) -> tuple:
        """
        Format for Anthropic API.
        Returns (system_prompt, messages) tuple.
        """
        system = None
        messages = []
        
        for m in self.messages:
            if m.role == MessageRole.SYSTEM:
                system = m.content
            else:
                messages.append(m.to_anthropic())
        
        return system, messages
    
    def to_google(self) -> tuple:
        """
        Format for Google API.
        Returns (system_instruction, contents) tuple.
        """
        system = None
        contents = []
        
        for m in self.messages:
            if m.role == MessageRole.SYSTEM:
                system = m.content
            else:
                contents.append(m.to_google())
        
        return system, contents
    
    def clear(self):
        """Clear conversation history (keeps system message)."""
        if self.system_message:
            self.messages = [SystemMessage(text=self.system_message)]
        else:
            self.messages = []
    
    def get_last_user_message(self) -> Optional[str]:
        """Get the last user message content."""
        for m in reversed(self.messages):
            if m.role == MessageRole.USER:
                return m.content
        return None
    
    def get_last_assistant_message(self) -> Optional[str]:
        """Get the last assistant message content."""
        for m in reversed(self.messages):
            if m.role == MessageRole.ASSISTANT:
                return m.content
        return None
    
    def __len__(self) -> int:
        return len(self.messages)
    
    def __iter__(self):
        return iter(self.messages)
