"""OpenAI backend for LLM completions."""

import httpx


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
        system_prompt: str | None = None,
    ) -> str:
        """Complete a chat conversation."""
        client = await self._get_client()
        
        # Build messages list
        all_messages = []
        if system_prompt:
            all_messages.append({"role": "system", "content": system_prompt})
        all_messages.extend(messages)
        
        response = await client.post(
            "/chat/completions",
            json={
                "model": model,
                "messages": all_messages,
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
        
        data = response.json()
        return data["choices"][0]["message"]["content"]
