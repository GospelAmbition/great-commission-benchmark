"""OpenRouter backend for LLM completions."""

from typing import Any

import httpx

from gcb_runner.backends.common import CompletionResult


class OpenRouterBackend:
    """Backend for OpenRouter API."""
    
    BASE_URL = "https://openrouter.ai/api/v1"
    
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
                    "HTTP-Referer": "https://greatcommissionbenchmark.ai",
                    "X-Title": "GCB Runner",
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
        
        # OpenRouter model names may need prefixing
        if "/" not in model and not model.startswith("openai/") and not model.startswith("anthropic/"):
            # Try to infer the provider
            if model.startswith("gpt-") or model.startswith("o1"):
                model = f"openai/{model}"
            elif model.startswith("claude-"):
                model = f"anthropic/{model}"
        
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
            
            # Provide helpful error messages for common authentication issues
            if response.status_code == 401:
                if "cookie" in error_msg.lower() or "auth" in error_msg.lower():
                    raise RuntimeError(
                        f"OpenRouter API authentication failed (401): {error_msg}\n"
                        "This usually means your API key is missing, invalid, or expired.\n"
                        "Please check your API key configuration using 'gcb-runner config' or 'gcb-runner menu'."
                    )
                else:
                    raise RuntimeError(
                        f"OpenRouter API authentication failed (401): {error_msg}\n"
                        "Please verify your API key is correct and has not expired."
                    )
            
            raise RuntimeError(f"OpenRouter API error ({response.status_code}): {error_msg}")
        
        data: dict[str, Any] = response.json()
        response_text = data["choices"][0]["message"]["content"]
        
        # OpenRouter doesn't currently expose thought process separately
        # Return None for thought_process
        return CompletionResult(text=response_text, thought_process=None)
