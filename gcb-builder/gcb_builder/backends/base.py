"""
Base protocol and types for LLM backend adapters.

All backends (OpenRouter, LM Studio, Ollama, Direct APIs) implement the LLMBackend protocol
to provide a unified interface for question generation and judge evaluation.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Protocol, runtime_checkable


class BackendType(str, Enum):
    """Supported LLM backend types."""
    
    OPENROUTER = "openrouter"
    LMSTUDIO = "lmstudio"
    OLLAMA = "ollama"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"


@dataclass
class ModelInfo:
    """Information about an available model."""
    
    id: str
    name: str
    backend: BackendType
    context_length: int | None = None
    description: str | None = None
    pricing: dict[str, float] | None = None  # e.g., {"prompt": 0.001, "completion": 0.002}
    
    def __str__(self) -> str:
        return f"{self.name} ({self.id})"


@dataclass
class CompletionRequest:
    """Request for LLM completion."""
    
    messages: list[dict[str, str]]
    model: str
    system_prompt: str | None = None
    temperature: float = 0.7
    max_tokens: int | None = None
    stop: list[str] | None = None
    
    def to_openai_format(self) -> dict[str, Any]:
        """Convert to OpenAI API format."""
        formatted_messages = []
        
        if self.system_prompt:
            formatted_messages.append({
                "role": "system",
                "content": self.system_prompt
            })
        
        formatted_messages.extend(self.messages)
        
        request = {
            "model": self.model,
            "messages": formatted_messages,
            "temperature": self.temperature,
        }
        
        if self.max_tokens:
            request["max_tokens"] = self.max_tokens
        if self.stop:
            request["stop"] = self.stop
            
        return request


@dataclass
class CompletionResponse:
    """Response from LLM completion."""
    
    content: str
    model: str
    usage: dict[str, int] | None = None  # {"prompt_tokens": X, "completion_tokens": Y}
    finish_reason: str | None = None
    raw_response: dict[str, Any] | None = field(default=None, repr=False)
    
    @property
    def total_tokens(self) -> int | None:
        """Total tokens used in the request."""
        if self.usage:
            return self.usage.get("prompt_tokens", 0) + self.usage.get("completion_tokens", 0)
        return None


class BackendError(Exception):
    """Base exception for backend errors."""
    
    def __init__(self, message: str, backend: BackendType | None = None):
        self.backend = backend
        super().__init__(message)


class AuthenticationError(BackendError):
    """Raised when API key is invalid or missing."""
    pass


class RateLimitError(BackendError):
    """Raised when rate limit is exceeded."""
    
    def __init__(self, message: str, retry_after: float | None = None, backend: BackendType | None = None):
        self.retry_after = retry_after
        super().__init__(message, backend)


class ModelNotFoundError(BackendError):
    """Raised when requested model is not available."""
    pass


class ConnectionError(BackendError):
    """Raised when connection to backend fails."""
    pass


@runtime_checkable
class LLMBackend(Protocol):
    """Protocol for LLM backend adapters.
    
    All backends must implement:
    - complete(): Send a completion request and get a response
    - list_models(): List available models on this backend
    - is_available(): Check if the backend is configured and accessible
    """
    
    @property
    def backend_type(self) -> BackendType:
        """Return the type of this backend."""
        ...
    
    @property
    def name(self) -> str:
        """Human-readable name for this backend."""
        ...
    
    async def complete(self, request: CompletionRequest) -> CompletionResponse:
        """Send a completion request.
        
        Args:
            request: The completion request with messages, model, etc.
            
        Returns:
            CompletionResponse with the model's response.
            
        Raises:
            AuthenticationError: If API key is invalid or missing.
            RateLimitError: If rate limit is exceeded.
            ModelNotFoundError: If requested model is not available.
            ConnectionError: If connection to backend fails.
            BackendError: For other backend-specific errors.
        """
        ...
    
    async def list_models(self) -> list[ModelInfo]:
        """List available models on this backend.
        
        Returns:
            List of ModelInfo objects describing available models.
        """
        ...
    
    async def is_available(self) -> bool:
        """Check if the backend is configured and accessible.
        
        Returns:
            True if the backend can accept requests, False otherwise.
        """
        ...


class BaseLLMBackend(ABC):
    """Abstract base class for LLM backends.
    
    Provides common functionality and enforces the LLMBackend protocol.
    Backends can inherit from this class for shared implementation details.
    """
    
    def __init__(self, api_key: str | None = None, base_url: str | None = None):
        self._api_key = api_key
        self._base_url = base_url
    
    @property
    @abstractmethod
    def backend_type(self) -> BackendType:
        """Return the type of this backend."""
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable name for this backend."""
        pass
    
    @abstractmethod
    async def complete(self, request: CompletionRequest) -> CompletionResponse:
        """Send a completion request."""
        pass
    
    @abstractmethod
    async def list_models(self) -> list[ModelInfo]:
        """List available models on this backend."""
        pass
    
    @abstractmethod
    async def is_available(self) -> bool:
        """Check if the backend is configured and accessible."""
        pass
    
    def _validate_api_key(self) -> None:
        """Validate that an API key is configured."""
        if not self._api_key:
            raise AuthenticationError(
                f"API key not configured for {self.name}",
                backend=self.backend_type
            )
