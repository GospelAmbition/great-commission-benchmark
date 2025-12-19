"""LLM backend adapters."""

from typing import Protocol, runtime_checkable

from gcb_runner.backends.openrouter import OpenRouterBackend
from gcb_runner.backends.openai import OpenAIBackend
from gcb_runner.backends.anthropic import AnthropicBackend
from gcb_runner.backends.lmstudio import LMStudioBackend
from gcb_runner.backends.ollama import OllamaBackend


@runtime_checkable
class LLMBackend(Protocol):
    """Protocol for LLM backends."""
    
    async def complete(
        self,
        messages: list[dict[str, str]],
        model: str,
        system_prompt: str | None = None,
    ) -> str:
        """Complete a chat conversation and return the response text."""
        ...
    
    async def close(self) -> None:
        """Close any open connections."""
        ...


def get_backend(name: str, api_key: str | None = None, base_url: str | None = None) -> LLMBackend:
    """Factory function to get a configured backend."""
    match name:
        case "openrouter":
            if not api_key:
                raise ValueError("OpenRouter requires an API key")
            return OpenRouterBackend(api_key)
        case "openai":
            if not api_key:
                raise ValueError("OpenAI requires an API key")
            return OpenAIBackend(api_key)
        case "anthropic":
            if not api_key:
                raise ValueError("Anthropic requires an API key")
            return AnthropicBackend(api_key)
        case "lmstudio":
            return LMStudioBackend(base_url or "http://localhost:1234/v1")
        case "ollama":
            return OllamaBackend(base_url or "http://localhost:11434")
        case _:
            raise ValueError(f"Unknown backend: {name}")


__all__ = [
    "LLMBackend",
    "get_backend",
    "OpenRouterBackend",
    "OpenAIBackend",
    "AnthropicBackend",
    "LMStudioBackend",
    "OllamaBackend",
]
