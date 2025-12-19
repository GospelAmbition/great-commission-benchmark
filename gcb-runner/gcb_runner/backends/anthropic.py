"""Anthropic backend for LLM completions."""

import httpx


class AnthropicBackend:
    """Backend for Anthropic API."""
    
    BASE_URL = "https://api.anthropic.com"
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self._client: httpx.AsyncClient | None = None
    
    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create the HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.BASE_URL,
                headers={
                    "x-api-key": self.api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
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
        system_prompt: str | None = None,
    ) -> str:
        """Complete a chat conversation."""
        client = await self._get_client()
        
        # Anthropic uses a different format
        # Convert messages and extract system prompt
        anthropic_messages = []
        for msg in messages:
            anthropic_messages.append({
                "role": msg["role"],
                "content": msg["content"],
            })
        
        payload: dict = {
            "model": model,
            "messages": anthropic_messages,
            "max_tokens": 4096,
        }
        
        if system_prompt:
            payload["system"] = system_prompt
        
        response = await client.post("/v1/messages", json=payload)
        
        if response.status_code != 200:
            error_msg = response.text
            try:
                error_data = response.json()
                if "error" in error_data:
                    error_msg = error_data["error"].get("message", error_msg)
            except Exception:
                pass
            raise RuntimeError(f"Anthropic API error ({response.status_code}): {error_msg}")
        
        data = response.json()
        
        # Anthropic returns content as a list of blocks
        content_blocks = data.get("content", [])
        text_parts = []
        for block in content_blocks:
            if block.get("type") == "text":
                text_parts.append(block.get("text", ""))
        
        return "".join(text_parts)
