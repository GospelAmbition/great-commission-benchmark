"""
OpenRouter backend adapter.

OpenRouter provides access to 100+ models through a unified API.
This is the primary cloud backend for GCB Builder.

API Documentation: https://openrouter.ai/docs
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


class OpenRouterBackend(BaseLLMBackend):
    """OpenRouter API backend.
    
    OpenRouter aggregates multiple LLM providers (OpenAI, Anthropic, Google, etc.)
    through a single API endpoint with unified billing.
    
    Environment variables:
        OPENROUTER_API_KEY: Your OpenRouter API key
        
    Example:
        backend = OpenRouterBackend()
        response = await backend.complete(CompletionRequest(
            messages=[{"role": "user", "content": "Hello!"}],
            model="openai/gpt-4o"
        ))
    """
    
    DEFAULT_BASE_URL = "https://openrouter.ai/api/v1"
    
    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        app_name: str = "GCB Builder",
        timeout: float = 120.0,
    ):
        """Initialize OpenRouter backend.
        
        Args:
            api_key: OpenRouter API key. Falls back to OPENROUTER_API_KEY env var.
            base_url: Override base URL (for testing).
            app_name: App name sent in X-Title header for OpenRouter analytics.
            timeout: Request timeout in seconds.
        """
        super().__init__(
            api_key=api_key or os.getenv("OPENROUTER_API_KEY"),
            base_url=base_url or self.DEFAULT_BASE_URL
        )
        self._app_name = app_name
        self._timeout = timeout
        self._client: httpx.AsyncClient | None = None
    
    @property
    def backend_type(self) -> BackendType:
        return BackendType.OPENROUTER
    
    @property
    def name(self) -> str:
        return "OpenRouter"
    
    def _get_headers(self) -> dict[str, str]:
        """Get headers for API requests."""
        self._validate_api_key()
        return {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
            "X-Title": self._app_name,
            "HTTP-Referer": "https://github.com/great-commission-benchmark",
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
        """Send completion request to OpenRouter.
        
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
                    "Invalid OpenRouter API key",
                    backend=self.backend_type
                )
            
            if response.status_code == 429:
                retry_after = response.headers.get("Retry-After")
                raise RateLimitError(
                    "OpenRouter rate limit exceeded",
                    retry_after=float(retry_after) if retry_after else None,
                    backend=self.backend_type
                )
            
            if response.status_code == 404:
                raise ModelNotFoundError(
                    f"Model '{request.model}' not found on OpenRouter",
                    backend=self.backend_type
                )
            
            if response.status_code >= 400:
                error_data = response.json() if response.content else {}
                error_msg = error_data.get("error", {}).get("message", response.text)
                raise BackendError(
                    f"OpenRouter API error ({response.status_code}): {error_msg}",
                    backend=self.backend_type
                )
            
            data = response.json()
            
            # Extract content from response
            choices = data.get("choices", [])
            if not choices:
                raise BackendError(
                    "No choices in OpenRouter response",
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
                f"Failed to connect to OpenRouter: {e}",
                backend=self.backend_type
            ) from e
        except httpx.TimeoutException as e:
            raise ConnectionError(
                f"OpenRouter request timed out: {e}",
                backend=self.backend_type
            ) from e
    
    async def list_models(self) -> list[ModelInfo]:
        """List available models on OpenRouter.
        
        Returns:
            List of available models with pricing and context info.
        """
        client = await self._get_client()
        
        try:
            response = await client.get("/models")
            
            if response.status_code != 200:
                raise BackendError(
                    f"Failed to list OpenRouter models: {response.status_code}",
                    backend=self.backend_type
                )
            
            data = response.json()
            models = []
            
            for model_data in data.get("data", []):
                pricing = None
                if "pricing" in model_data:
                    pricing = {
                        "prompt": float(model_data["pricing"].get("prompt", 0)),
                        "completion": float(model_data["pricing"].get("completion", 0)),
                    }
                
                models.append(ModelInfo(
                    id=model_data["id"],
                    name=model_data.get("name", model_data["id"]),
                    backend=self.backend_type,
                    context_length=model_data.get("context_length"),
                    description=model_data.get("description"),
                    pricing=pricing,
                ))
            
            return models
            
        except httpx.ConnectError as e:
            raise ConnectionError(
                f"Failed to connect to OpenRouter: {e}",
                backend=self.backend_type
            ) from e
    
    async def is_available(self) -> bool:
        """Check if OpenRouter is available and configured.
        
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
    
    async def __aenter__(self) -> "OpenRouterBackend":
        """Context manager entry."""
        return self
    
    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit - close client."""
        await self.close()
