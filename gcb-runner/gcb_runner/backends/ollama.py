"""Ollama backend for local LLM completions."""

from typing import Any

import httpx

from gcb_runner.backends.common import CompletionResult


class OllamaBackend:
    """Backend for Ollama local server."""
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url.rstrip("/")
        self._client: httpx.AsyncClient | None = None
    
    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create the HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=300.0,  # Longer timeout for local models
            )
        return self._client
    
    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None
    
    async def complete(
        self,
        messages: list[dict[str, str]],
        model: str,
    ) -> CompletionResult:
        """Complete a chat conversation."""
        client = await self._get_client()
        
        try:
            response = await client.post(
                "/api/chat",
                json={
                    "model": model,
                    "messages": messages,
                    "stream": False,
                },
            )
        except httpx.ConnectError as e:
            raise RuntimeError(
                f"Could not connect to Ollama at {self.base_url}. "
                "Make sure Ollama is running (run 'ollama serve')."
            ) from e
        
        if response.status_code != 200:
            error_msg = response.text
            try:
                error_data = response.json()
                if "error" in error_data:
                    error_msg = error_data.get("error", error_msg)
            except Exception:
                pass
            raise RuntimeError(f"Ollama API error ({response.status_code}): {error_msg}")
        
        data: dict[str, Any] = response.json()
        response_text = data["message"]["content"]
        
        # Ollama doesn't currently expose thought process separately
        # Return None for thought_process
        return CompletionResult(text=response_text, thought_process=None)
