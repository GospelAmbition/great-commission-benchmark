"""
Ollama backend adapter.

Ollama provides a local API for running models through its CLI-focused interface.
Alternative local backend for users who prefer Ollama over LM Studio.

API Documentation: https://github.com/ollama/ollama/blob/main/docs/api.md
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


class OllamaBackend(BaseLLMBackend):
    """Ollama local API backend.
    
    Ollama runs models locally with its own API format.
    No API key required - just have Ollama running.
    
    Environment variables:
        OLLAMA_BASE_URL: Override base URL (default: http://localhost:11434)
        
    Example:
        backend = OllamaBackend()
        
        # Check if Ollama is running
        if await backend.is_available():
            models = await backend.list_models()
            response = await backend.complete(CompletionRequest(
                messages=[{"role": "user", "content": "Hello!"}],
                model="llama3.2"
            ))
    """
    
    DEFAULT_BASE_URL = "http://localhost:11434"
    
    def __init__(
        self,
        base_url: str | None = None,
        timeout: float = 300.0,  # Local models can be slow
    ):
        """Initialize Ollama backend.
        
        Args:
            base_url: Override base URL. Falls back to OLLAMA_BASE_URL env var.
            timeout: Request timeout in seconds (default 300s for slow local models).
        """
        super().__init__(
            api_key=None,  # Ollama doesn't require API key
            base_url=base_url or os.getenv("OLLAMA_BASE_URL", self.DEFAULT_BASE_URL)
        )
        self._timeout = timeout
        self._client: httpx.AsyncClient | None = None
    
    @property
    def backend_type(self) -> BackendType:
        return BackendType.OLLAMA
    
    @property
    def name(self) -> str:
        return "Ollama"
    
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
        """Send completion request to Ollama.
        
        Ollama has its own API format, which we convert from OpenAI format.
        
        Args:
            request: Completion request with messages and model.
            
        Returns:
            CompletionResponse with model's response.
        """
        client = await self._get_client()
        
        # Convert to Ollama chat format
        messages = []
        if request.system_prompt:
            messages.append({
                "role": "system",
                "content": request.system_prompt
            })
        messages.extend(request.messages)
        
        payload = {
            "model": request.model,
            "messages": messages,
            "stream": False,  # Don't stream for simplicity
            "options": {
                "temperature": request.temperature,
            }
        }
        
        if request.max_tokens:
            payload["options"]["num_predict"] = request.max_tokens
        
        try:
            response = await client.post("/api/chat", json=payload)
            
            if response.status_code == 404:
                raise ModelNotFoundError(
                    f"Model '{request.model}' not found. Run 'ollama pull {request.model}' first.",
                    backend=self.backend_type
                )
            
            if response.status_code >= 400:
                error_msg = response.text
                try:
                    error_data = response.json()
                    error_msg = error_data.get("error", response.text)
                except Exception:
                    pass
                raise BackendError(
                    f"Ollama API error ({response.status_code}): {error_msg}",
                    backend=self.backend_type
                )
            
            data = response.json()
            
            # Ollama returns response in "message" field
            message = data.get("message", {})
            content = message.get("content", "")
            
            # Ollama provides token counts differently
            usage = None
            if "prompt_eval_count" in data or "eval_count" in data:
                usage = {
                    "prompt_tokens": data.get("prompt_eval_count", 0),
                    "completion_tokens": data.get("eval_count", 0),
                }
            
            return CompletionResponse(
                content=content,
                model=data.get("model", request.model),
                usage=usage,
                finish_reason=data.get("done_reason"),
                raw_response=data,
            )
            
        except httpx.ConnectError as e:
            raise ConnectionError(
                f"Failed to connect to Ollama. Is it running? Try 'ollama serve'. ({e})",
                backend=self.backend_type
            ) from e
        except httpx.TimeoutException as e:
            raise ConnectionError(
                f"Ollama request timed out. The model may be loading or generating slowly. ({e})",
                backend=self.backend_type
            ) from e
    
    async def list_models(self) -> list[ModelInfo]:
        """List models available in Ollama.
        
        Returns:
            List of models that have been pulled to this Ollama instance.
        """
        client = await self._get_client()
        
        try:
            response = await client.get("/api/tags")
            
            if response.status_code != 200:
                raise BackendError(
                    f"Failed to list Ollama models: {response.status_code}",
                    backend=self.backend_type
                )
            
            data = response.json()
            models = []
            
            for model_data in data.get("models", []):
                # Parse model details
                details = model_data.get("details", {})
                
                models.append(ModelInfo(
                    id=model_data["name"],
                    name=model_data["name"],
                    backend=self.backend_type,
                    context_length=details.get("context_length"),
                    description=f"Family: {details.get('family', 'unknown')}, "
                               f"Parameters: {details.get('parameter_size', 'unknown')}",
                ))
            
            return models
            
        except httpx.ConnectError as e:
            raise ConnectionError(
                f"Failed to connect to Ollama. Is it running? Try 'ollama serve'. ({e})",
                backend=self.backend_type
            ) from e
    
    async def is_available(self) -> bool:
        """Check if Ollama is running and accessible.
        
        Returns:
            True if Ollama server is running and responding.
        """
        try:
            client = await self._get_client()
            # Ollama has a simple endpoint to check if it's running
            response = await client.get("/api/tags")
            return response.status_code == 200
        except Exception:
            return False
    
    async def pull_model(self, model_name: str) -> bool:
        """Pull a model from the Ollama library.
        
        Note: This can take a long time for large models.
        
        Args:
            model_name: Name of model to pull (e.g., "llama3.2", "mistral")
            
        Returns:
            True if pull was successful.
        """
        client = await self._get_client()
        
        try:
            # Use a much longer timeout for pulling models
            response = await client.post(
                "/api/pull",
                json={"name": model_name, "stream": False},
                timeout=3600.0,  # 1 hour for large models
            )
            return response.status_code == 200
        except Exception:
            return False
    
    async def __aenter__(self) -> "OllamaBackend":
        """Context manager entry."""
        return self
    
    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit - close client."""
        await self.close()
