"""LM Studio backend for local LLM completions."""

from typing import Any

import httpx

from gcb_runner.backends.common import (
    EXTRACTION_NO_PARSEABLE_OUTPUT,
    EXTRACTION_OK,
    EXTRACTION_UNSUPPORTED_SHAPE,
    CompletionResult,
)


class LMStudioBackend:
    """Backend for LM Studio (OpenAI-compatible local server)."""
    
    def __init__(self, base_url: str = "http://localhost:1234/v1"):
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
                "/chat/completions",
                json={
                    "model": model,
                    "messages": messages,
                },
            )
        except httpx.ConnectError as e:
            raise RuntimeError(
                f"Could not connect to LM Studio at {self.base_url}. "
                "Make sure LM Studio is running and the server is started."
            ) from e
        
        if response.status_code != 200:
            error_msg = response.text
            try:
                error_data = response.json()
                if "error" in error_data:
                    error_msg = error_data["error"].get("message", error_msg)
            except Exception:
                pass
            raise RuntimeError(f"LM Studio API error ({response.status_code}): {error_msg}")
        
        data: dict[str, Any] = response.json()

        choices = data.get("choices")
        if not isinstance(choices, list) or not choices:
            return CompletionResult(
                text=None,
                outcome=EXTRACTION_UNSUPPORTED_SHAPE,
                sources=[],
                raw_message_summary=repr(data)[:2000],
                provider="lmstudio",
            )

        choice = choices[0] if isinstance(choices[0], dict) else {}
        message = choice.get("message") if isinstance(choice.get("message"), dict) else {}
        finish_reason = choice.get("finish_reason") if isinstance(choice.get("finish_reason"), str) else None
        response_text = message.get("content") if isinstance(message, dict) else None

        if isinstance(response_text, str) and response_text.strip():
            return CompletionResult(
                text=response_text,
                thought_process=None,
                outcome=EXTRACTION_OK,
                sources=["message.content"],
                finish_reason=finish_reason,
                provider="lmstudio",
            )

        return CompletionResult(
            text=None,
            thought_process=None,
            outcome=EXTRACTION_NO_PARSEABLE_OUTPUT,
            sources=[],
            finish_reason=finish_reason,
            raw_message_summary=repr(message)[:2000],
            provider="lmstudio",
        )
