"""OpenAI backend for LLM completions."""

from typing import Any

import httpx

from gcb_runner.backends.common import CompletionResult


class OpenAIBackend:
    """Backend for OpenAI API."""
    
    BASE_URL = "https://api.openai.com/v1"
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self._client: httpx.AsyncClient | None = None
    
    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create the HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.BASE_URL,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                },
                timeout=120.0,
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
        
        response = await client.post(
            "/chat/completions",
            json={
                "model": model,
                "messages": messages,
            },
        )
        
        if response.status_code != 200:
            error_msg = response.text
            try:
                error_data = response.json()
                if "error" in error_data:
                    error_msg = error_data["error"].get("message", error_msg)
            except Exception:
                pass
            raise RuntimeError(f"OpenAI API error ({response.status_code}): {error_msg}")
        
        data: dict[str, Any] = response.json()
        response_text = data["choices"][0]["message"]["content"]
        
        # Check for reasoning traces (o1 models may include this in the response structure)
        # Currently OpenAI doesn't expose reasoning separately, so we return None
        # Future: if OpenAI adds reasoning traces to the API, extract them here
        thought_process = None
        
        return CompletionResult(text=response_text, thought_process=thought_process)
