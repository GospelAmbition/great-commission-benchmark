"""LLM backend adapters."""

from typing import Protocol, runtime_checkable

from gcb_runner.backends.anthropic import AnthropicBackend
from gcb_runner.backends.common import CompletionResult
from gcb_runner.backends.lmstudio import LMStudioBackend
from gcb_runner.backends.ollama import OllamaBackend
from gcb_runner.backends.openai import OpenAIBackend
from gcb_runner.backends.openrouter import OpenRouterBackend


@runtime_checkable
class LLMBackend(Protocol):
    """Protocol for LLM backends."""
    
    async def complete(
        self,
        messages: list[dict[str, str]],
        model: str,
    ) -> CompletionResult:
        """Complete a chat conversation and return the response text and thought process."""
        ...
    
    async def close(self) -> None:
        """Close any open connections."""
        ...


def get_backend(name: str, api_key: str | None = None, base_url: str | None = None) -> LLMBackend:
    """Factory function to get a configured backend."""
    match name:
        case "openrouter":
            if not api_key or not api_key.strip():
                raise ValueError(
                    "OpenRouter requires an API key. "
                    "Please configure it using 'gcb-runner config' or 'gcb-runner menu' → Configure Backend."
                )
            return OpenRouterBackend(api_key.strip())
        case "openai":
            if not api_key or not api_key.strip():
                raise ValueError(
                    "OpenAI requires an API key. "
                    "Please configure it using 'gcb-runner config' or 'gcb-runner menu' → Configure Backend."
                )
            return OpenAIBackend(api_key.strip())
        case "anthropic":
            if not api_key or not api_key.strip():
                raise ValueError(
                    "Anthropic requires an API key. "
                    "Please configure it using 'gcb-runner config' or 'gcb-runner menu' → Configure Backend."
                )
            return AnthropicBackend(api_key.strip())
        case "lmstudio":
            return LMStudioBackend(base_url or "http://localhost:1234/v1")
        case "ollama":
            return OllamaBackend(base_url or "http://localhost:11434")
        case _:
            raise ValueError(f"Unknown backend: {name}")


__all__ = [
    "LLMBackend",
    "CompletionResult",
    "get_backend",
    "OpenRouterBackend",
    "OpenAIBackend",
    "AnthropicBackend",
    "LMStudioBackend",
    "OllamaBackend",
]
