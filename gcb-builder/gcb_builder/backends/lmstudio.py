"""
LM Studio backend adapter.

LM Studio provides a local OpenAI-compatible API for running models locally.
This is the primary local backend for GCB Builder due to its excellent GUI.

API Documentation: https://lmstudio.ai/docs/local-server
"""

import os
from typing import Any

import httpx

from .base import (
    BackendError,
    BackendType,
    BaseLLMBackend,
    CompletionRequest,
    CompletionResponse,
    ConnectionError,
    ModelInfo,
    ModelNotFoundError,
)


class LMStudioBackend(BaseLLMBackend):
    """LM Studio local API backend.
    
    LM Studio runs models locally with an OpenAI-compatible API.
    No API key required - just start the local server in LM Studio.
    
    Environment variables:
        LMSTUDIO_BASE_URL: Override base URL (default: http://localhost:1234/v1)
        
    Example:
        backend = LMStudioBackend()
        
        # Check if LM Studio server is running
        if await backend.is_available():
            models = await backend.list_models()
            response = await backend.complete(CompletionRequest(
                messages=[{"role": "user", "content": "Hello!"}],
                model=models[0].id
            ))
    """
    
    DEFAULT_BASE_URL = "http://localhost:1234/v1"
    
    def __init__(
        self,
        base_url: str | None = None,
        timeout: float = 300.0,  # Local models can be slow
    ):
        """Initialize LM Studio backend.
        
        Args:
            base_url: Override base URL. Falls back to LMSTUDIO_BASE_URL env var.
            timeout: Request timeout in seconds (default 300s for slow local models).
        """
        super().__init__(
            api_key=None,  # LM Studio doesn't require API key
            base_url=base_url or os.getenv("LMSTUDIO_BASE_URL", self.DEFAULT_BASE_URL)
        )
        self._timeout = timeout
        self._client: httpx.AsyncClient | None = None
    
    @property
    def backend_type(self) -> BackendType:
        return BackendType.LMSTUDIO
    
    @property
    def name(self) -> str:
        return "LM Studio"
    
    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self._base_url,
                timeout=self._timeout,
                headers={"Content-Type": "application/json"},
            )
        return self._client
    
    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None
    
    async def complete(self, request: CompletionRequest) -> CompletionResponse:
        """Send completion request to LM Studio.
        
        Args:
            request: Completion request with messages and model.
            
        Returns:
            CompletionResponse with model's response.
        """
        client = await self._get_client()
        
        payload = request.to_openai_format()
        
        try:
            response = await client.post("/chat/completions", json=payload)
            
            if response.status_code == 404:
                raise ModelNotFoundError(
                    f"Model '{request.model}' not loaded in LM Studio",
                    backend=self.backend_type
                )
            
            if response.status_code >= 400:
                error_msg = response.text
                try:
                    error_data = response.json()
                    error_msg = error_data.get("error", {}).get("message", response.text)
                except Exception:
                    pass
                raise BackendError(
                    f"LM Studio API error ({response.status_code}): {error_msg}",
                    backend=self.backend_type
                )
            
            data = response.json()
            
            # Extract content from response
            choices = data.get("choices", [])
            if not choices:
                raise BackendError(
                    "No choices in LM Studio response",
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
                f"Failed to connect to LM Studio. Is the server running? ({e})",
                backend=self.backend_type
            ) from e
        except httpx.TimeoutException as e:
            raise ConnectionError(
                f"LM Studio request timed out. The model may be loading or generating slowly. ({e})",
                backend=self.backend_type
            ) from e
    
    async def list_models(self) -> list[ModelInfo]:
        """List models currently loaded in LM Studio.
        
        Returns:
            List of currently loaded models.
        """
        client = await self._get_client()
        
        try:
            response = await client.get("/models")
            
            if response.status_code != 200:
                raise BackendError(
                    f"Failed to list LM Studio models: {response.status_code}",
                    backend=self.backend_type
                )
            
            data = response.json()
            models = []
            
            for model_data in data.get("data", []):
                models.append(ModelInfo(
                    id=model_data["id"],
                    name=model_data.get("id", "Unknown"),  # LM Studio uses id as name
                    backend=self.backend_type,
                    context_length=model_data.get("context_length"),
                    description="Local model loaded in LM Studio",
                ))
            
            return models
            
        except httpx.ConnectError as e:
            raise ConnectionError(
                f"Failed to connect to LM Studio. Is the server running? ({e})",
                backend=self.backend_type
            ) from e
    
    async def is_available(self) -> bool:
        """Check if LM Studio server is running and accessible.
        
        Returns:
            True if server is running and responding.
        """
        try:
            client = await self._get_client()
            response = await client.get("/models")
            return response.status_code == 200
        except Exception:
            return False
    
    async def __aenter__(self) -> "LMStudioBackend":
        """Context manager entry."""
        return self
    
    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit - close client."""
        await self.close()
