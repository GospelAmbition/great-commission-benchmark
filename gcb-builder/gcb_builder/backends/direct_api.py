"""
Direct API backends for OpenAI and Anthropic.

These backends connect directly to the provider APIs without going through
an aggregator like OpenRouter. Useful when you need:
- Lower latency (no proxy hop)
- Specific provider features
- Separate billing from OpenRouter

API Documentation:
- OpenAI: https://platform.openai.com/docs/api-reference
- Anthropic: https://docs.anthropic.com/en/api
"""

import os
from typing import Any

import httpx

from .base import (
    AuthenticationError,
    BackendError,
    BackendType,
    BaseLLMBackend,
    CompletionRequest,
    CompletionResponse,
    ConnectionError,
    ModelInfo,
    ModelNotFoundError,
    RateLimitError,
)


class OpenAIBackend(BaseLLMBackend):
    """Direct OpenAI API backend.
    
    Connects directly to OpenAI's API for GPT models.
    
    Environment variables:
        OPENAI_API_KEY: Your OpenAI API key
        OPENAI_BASE_URL: Override base URL (optional, for Azure etc.)
        
    Example:
        backend = OpenAIBackend()
        response = await backend.complete(CompletionRequest(
            messages=[{"role": "user", "content": "Hello!"}],
            model="gpt-4o"
        ))
    """
    
    DEFAULT_BASE_URL = "https://api.openai.com/v1"
    
    # Common OpenAI models - not exhaustive, just for reference
    KNOWN_MODELS = [
        ("gpt-4o", "GPT-4o - Flagship multimodal model", 128000),
        ("gpt-4o-mini", "GPT-4o Mini - Fast and affordable", 128000),
        ("gpt-4-turbo", "GPT-4 Turbo - High capability", 128000),
        ("gpt-4", "GPT-4 - Original GPT-4", 8192),
        ("gpt-3.5-turbo", "GPT-3.5 Turbo - Fast and cheap", 16385),
        ("o1-preview", "o1 Preview - Advanced reasoning", 128000),
        ("o1-mini", "o1 Mini - Cost-effective reasoning", 128000),
    ]
    
    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        timeout: float = 120.0,
    ):
        """Initialize OpenAI backend.
        
        Args:
            api_key: OpenAI API key. Falls back to OPENAI_API_KEY env var.
            base_url: Override base URL. Falls back to OPENAI_BASE_URL env var.
            timeout: Request timeout in seconds.
        """
        super().__init__(
            api_key=api_key or os.getenv("OPENAI_API_KEY"),
            base_url=base_url or os.getenv("OPENAI_BASE_URL", self.DEFAULT_BASE_URL)
        )
        self._timeout = timeout
        self._client: httpx.AsyncClient | None = None
    
    @property
    def backend_type(self) -> BackendType:
        return BackendType.OPENAI
    
    @property
    def name(self) -> str:
        return "OpenAI"
    
    def _get_headers(self) -> dict[str, str]:
        """Get headers for API requests."""
        self._validate_api_key()
        return {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }
    
    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self._base_url,
                headers=self._get_headers(),
                timeout=self._timeout,
            )
        return self._client
    
    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None
    
    async def complete(self, request: CompletionRequest) -> CompletionResponse:
        """Send completion request to OpenAI.
        
        Args:
            request: Completion request with messages and model.
            
        Returns:
            CompletionResponse with model's response.
        """
        client = await self._get_client()
        
        payload = request.to_openai_format()
        
        try:
            response = await client.post("/chat/completions", json=payload)
            
            if response.status_code == 401:
                raise AuthenticationError(
                    "Invalid OpenAI API key",
                    backend=self.backend_type
                )
            
            if response.status_code == 429:
                retry_after = response.headers.get("Retry-After")
                raise RateLimitError(
                    "OpenAI rate limit exceeded",
                    retry_after=float(retry_after) if retry_after else None,
                    backend=self.backend_type
                )
            
            if response.status_code == 404:
                raise ModelNotFoundError(
                    f"Model '{request.model}' not found on OpenAI",
                    backend=self.backend_type
                )
            
            if response.status_code >= 400:
                error_data = response.json() if response.content else {}
                error_msg = error_data.get("error", {}).get("message", response.text)
                raise BackendError(
                    f"OpenAI API error ({response.status_code}): {error_msg}",
                    backend=self.backend_type
                )
            
            data = response.json()
            
            choices = data.get("choices", [])
            if not choices:
                raise BackendError(
                    "No choices in OpenAI response",
                    backend=self.backend_type
                )
            
            content = choices[0].get("message", {}).get("content", "")
            finish_reason = choices[0].get("finish_reason")
            usage = data.get("usage")
            
            return CompletionResponse(
                content=content,
                model=data.get("model", request.model),
                usage=usage,
                finish_reason=finish_reason,
                raw_response=data,
            )
            
        except httpx.ConnectError as e:
            raise ConnectionError(
                f"Failed to connect to OpenAI: {e}",
                backend=self.backend_type
            ) from e
        except httpx.TimeoutException as e:
            raise ConnectionError(
                f"OpenAI request timed out: {e}",
                backend=self.backend_type
            ) from e
    
    async def list_models(self) -> list[ModelInfo]:
        """List available OpenAI models.
        
        Returns a curated list of commonly used models.
        """
        # Return known models - OpenAI's /models endpoint returns many fine-tunes
        return [
            ModelInfo(
                id=model_id,
                name=name,
                backend=self.backend_type,
                context_length=context,
            )
            for model_id, name, context in self.KNOWN_MODELS
        ]
    
    async def is_available(self) -> bool:
        """Check if OpenAI is available and configured.
        
        Returns:
            True if API key is set and API is reachable.
        """
        if not self._api_key:
            return False
        
        try:
            client = await self._get_client()
            response = await client.get("/models")
            return response.status_code == 200
        except Exception:
            return False
    
    async def __aenter__(self) -> "OpenAIBackend":
        """Context manager entry."""
        return self
    
    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit - close client."""
        await self.close()


class AnthropicBackend(BaseLLMBackend):
    """Direct Anthropic API backend.
    
    Connects directly to Anthropic's API for Claude models.
    
    Environment variables:
        ANTHROPIC_API_KEY: Your Anthropic API key
        
    Example:
        backend = AnthropicBackend()
        response = await backend.complete(CompletionRequest(
            messages=[{"role": "user", "content": "Hello!"}],
            model="claude-sonnet-4-20250514"
        ))
    """
    
    DEFAULT_BASE_URL = "https://api.anthropic.com"
    API_VERSION = "2023-06-01"
    
    # Common Anthropic models
    KNOWN_MODELS = [
        ("claude-sonnet-4-20250514", "Claude Sonnet 4 - Latest Sonnet", 200000),
        ("claude-opus-4-20250514", "Claude Opus 4 - Most capable", 200000),
        ("claude-3-5-sonnet-20241022", "Claude 3.5 Sonnet - Balanced", 200000),
        ("claude-3-5-haiku-20241022", "Claude 3.5 Haiku - Fast", 200000),
        ("claude-3-opus-20240229", "Claude 3 Opus - Previous flagship", 200000),
    ]
    
    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        timeout: float = 120.0,
    ):
        """Initialize Anthropic backend.
        
        Args:
            api_key: Anthropic API key. Falls back to ANTHROPIC_API_KEY env var.
            base_url: Override base URL (optional).
            timeout: Request timeout in seconds.
        """
        super().__init__(
            api_key=api_key or os.getenv("ANTHROPIC_API_KEY"),
            base_url=base_url or self.DEFAULT_BASE_URL
        )
        self._timeout = timeout
        self._client: httpx.AsyncClient | None = None
    
    @property
    def backend_type(self) -> BackendType:
        return BackendType.ANTHROPIC
    
    @property
    def name(self) -> str:
        return "Anthropic"
    
    def _get_headers(self) -> dict[str, str]:
        """Get headers for API requests."""
        self._validate_api_key()
        return {
            "x-api-key": self._api_key,
            "anthropic-version": self.API_VERSION,
            "Content-Type": "application/json",
        }
    
    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self._base_url,
                headers=self._get_headers(),
                timeout=self._timeout,
            )
        return self._client
    
    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None
    
    async def complete(self, request: CompletionRequest) -> CompletionResponse:
        """Send completion request to Anthropic.
        
        Note: Anthropic's API format differs from OpenAI's. We convert here.
        
        Args:
            request: Completion request with messages and model.
            
        Returns:
            CompletionResponse with model's response.
        """
        client = await self._get_client()
        
        # Convert to Anthropic format
        # Anthropic uses "system" as a separate field, not in messages
        system = request.system_prompt
        messages = []
        
        for msg in request.messages:
            # Handle system messages that might be in the messages list
            if msg.get("role") == "system":
                if not system:
                    system = msg.get("content", "")
                continue
            messages.append(msg)
        
        payload = {
            "model": request.model,
            "messages": messages,
            "max_tokens": request.max_tokens or 4096,  # Anthropic requires max_tokens
        }
        
        if system:
            payload["system"] = system
        
        if request.temperature is not None:
            payload["temperature"] = request.temperature
        
        if request.stop:
            payload["stop_sequences"] = request.stop
        
        try:
            response = await client.post("/v1/messages", json=payload)
            
            if response.status_code == 401:
                raise AuthenticationError(
                    "Invalid Anthropic API key",
                    backend=self.backend_type
                )
            
            if response.status_code == 429:
                retry_after = response.headers.get("Retry-After")
                raise RateLimitError(
                    "Anthropic rate limit exceeded",
                    retry_after=float(retry_after) if retry_after else None,
                    backend=self.backend_type
                )
            
            if response.status_code == 404:
                raise ModelNotFoundError(
                    f"Model '{request.model}' not found on Anthropic",
                    backend=self.backend_type
                )
            
            if response.status_code >= 400:
                error_data = response.json() if response.content else {}
                error_msg = error_data.get("error", {}).get("message", response.text)
                raise BackendError(
                    f"Anthropic API error ({response.status_code}): {error_msg}",
                    backend=self.backend_type
                )
            
            data = response.json()
            
            # Anthropic returns content as array of content blocks
            content_blocks = data.get("content", [])
            content = ""
            for block in content_blocks:
                if block.get("type") == "text":
                    content += block.get("text", "")
            
            # Convert Anthropic usage format
            usage = None
            if "usage" in data:
                usage = {
                    "prompt_tokens": data["usage"].get("input_tokens", 0),
                    "completion_tokens": data["usage"].get("output_tokens", 0),
                }
            
            return CompletionResponse(
                content=content,
                model=data.get("model", request.model),
                usage=usage,
                finish_reason=data.get("stop_reason"),
                raw_response=data,
            )
            
        except httpx.ConnectError as e:
            raise ConnectionError(
                f"Failed to connect to Anthropic: {e}",
                backend=self.backend_type
            ) from e
        except httpx.TimeoutException as e:
            raise ConnectionError(
                f"Anthropic request timed out: {e}",
                backend=self.backend_type
            ) from e
    
    async def list_models(self) -> list[ModelInfo]:
        """List available Anthropic models.
        
        Returns a curated list of Claude models.
        """
        return [
            ModelInfo(
                id=model_id,
                name=name,
                backend=self.backend_type,
                context_length=context,
            )
            for model_id, name, context in self.KNOWN_MODELS
        ]
    
    async def is_available(self) -> bool:
        """Check if Anthropic is available and configured.
        
        Returns:
            True if API key is set. (Anthropic doesn't have a simple health check)
        """
        return bool(self._api_key)
    
    async def __aenter__(self) -> "AnthropicBackend":
        """Context manager entry."""
        return self
    
    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit - close client."""
        await self.close()
