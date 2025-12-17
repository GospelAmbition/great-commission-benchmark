"""
LLM backend adapters for GCB Builder.

This module provides a unified interface for interacting with various LLM providers:
- OpenRouter: Aggregated access to 100+ models (primary cloud backend)
- LM Studio: Local OpenAI-compatible API (primary local backend)
- Ollama: Local models via Ollama CLI (alternative local backend)
- OpenAI: Direct OpenAI API access
- Anthropic: Direct Anthropic API access

Usage:
    from gcb_builder.backends import get_backend, BackendType
    
    # Get a specific backend
    backend = get_backend(BackendType.OPENROUTER)
    
    # Or use auto-detection
    backend = get_available_backend()
    
    # Send a completion request
    async with backend:
        response = await backend.complete(CompletionRequest(
            messages=[{"role": "user", "content": "Hello!"}],
            model="openai/gpt-4o"
        ))
"""

from .base import (
    AuthenticationError,
    BackendError,
    BackendType,
    BaseLLMBackend,
    CompletionRequest,
    CompletionResponse,
    ConnectionError,
    LLMBackend,
    ModelInfo,
    ModelNotFoundError,
    RateLimitError,
)
from .config import (
    BackendConfig,
    Config,
    create_env_template,
    load_config,
    write_env_template,
)
from .direct_api import AnthropicBackend, OpenAIBackend
from .lmstudio import LMStudioBackend
from .ollama import OllamaBackend
from .openrouter import OpenRouterBackend

__all__ = [
    # Protocol and base classes
    "LLMBackend",
    "BaseLLMBackend",
    "BackendType",
    # Data classes
    "CompletionRequest",
    "CompletionResponse",
    "ModelInfo",
    # Exceptions
    "BackendError",
    "AuthenticationError",
    "RateLimitError",
    "ModelNotFoundError",
    "ConnectionError",
    # Backend implementations
    "OpenRouterBackend",
    "LMStudioBackend",
    "OllamaBackend",
    "OpenAIBackend",
    "AnthropicBackend",
    # Factory functions
    "get_backend",
    "get_available_backend",
    "list_available_backends",
    # Configuration
    "Config",
    "BackendConfig",
    "load_config",
    "create_env_template",
    "write_env_template",
]


def get_backend(backend_type: BackendType) -> BaseLLMBackend:
    """Get a backend instance by type.
    
    Args:
        backend_type: The type of backend to create.
        
    Returns:
        An instance of the requested backend.
        
    Raises:
        ValueError: If backend type is unknown.
        
    Example:
        backend = get_backend(BackendType.OPENROUTER)
        async with backend:
            models = await backend.list_models()
    """
    backends = {
        BackendType.OPENROUTER: OpenRouterBackend,
        BackendType.LMSTUDIO: LMStudioBackend,
        BackendType.OLLAMA: OllamaBackend,
        BackendType.OPENAI: OpenAIBackend,
        BackendType.ANTHROPIC: AnthropicBackend,
    }
    
    if backend_type not in backends:
        raise ValueError(f"Unknown backend type: {backend_type}")
    
    return backends[backend_type]()


async def get_available_backend() -> BaseLLMBackend | None:
    """Get the first available backend.
    
    Checks backends in order of preference:
    1. OpenRouter (if API key configured)
    2. OpenAI (if API key configured)
    3. Anthropic (if API key configured)
    4. LM Studio (if server running)
    5. Ollama (if server running)
    
    Returns:
        An available backend instance, or None if no backends available.
        
    Example:
        backend = await get_available_backend()
        if backend:
            async with backend:
                response = await backend.complete(...)
    """
    # Order of preference: cloud backends first, then local
    backend_order = [
        BackendType.OPENROUTER,
        BackendType.OPENAI,
        BackendType.ANTHROPIC,
        BackendType.LMSTUDIO,
        BackendType.OLLAMA,
    ]
    
    for backend_type in backend_order:
        backend = get_backend(backend_type)
        if await backend.is_available():
            return backend
        await backend.close() if hasattr(backend, 'close') else None
    
    return None


async def list_available_backends() -> list[tuple[BackendType, str]]:
    """List all currently available backends.
    
    Returns:
        List of (backend_type, name) tuples for available backends.
        
    Example:
        available = await list_available_backends()
        for backend_type, name in available:
            print(f"{name} is available")
    """
    available = []
    
    for backend_type in BackendType:
        backend = get_backend(backend_type)
        if await backend.is_available():
            available.append((backend_type, backend.name))
        await backend.close() if hasattr(backend, 'close') else None
    
    return available
