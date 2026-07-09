"""OpenRouter backend for LLM completions."""

import asyncio
import random
from typing import Any

import httpx

from gcb_runner.backends.common import (
    EXTRACTION_EMPTY_BUT_EXPLAINABLE,
    EXTRACTION_NO_PARSEABLE_OUTPUT,
    EXTRACTION_OK,
    EXTRACTION_PROVIDER_ERROR,
    EXTRACTION_UNSUPPORTED_SHAPE,
    CompletionResult,
)


# Maximum length of the raw-message summary captured for audit on Class B
# extractions. Kept short on purpose — this is for diagnosis, not archival.
_RAW_SUMMARY_MAX = 2000
_TRANSIENT_STATUS_CODES = {408, 409, 429, 500, 502, 503, 504}
_MAX_TRANSIENT_ATTEMPTS = 8
_INITIAL_RETRY_DELAY_SECONDS = 1.0
_MAX_RETRY_DELAY_SECONDS = 30.0
_MAX_COMPLETION_TOKENS = 4096


def _truncate(value: str, limit: int = _RAW_SUMMARY_MAX) -> str:
    if len(value) <= limit:
        return value
    return value[:limit] + f"...[truncated {len(value) - limit} chars]"


def _summarize_message(message: Any) -> str:
    """Produce a short, printable summary of an assistant message for audit."""
    try:
        import json as _json

        return _truncate(_json.dumps(message, default=str))
    except Exception:
        return _truncate(repr(message))


def _retry_after_seconds(response: httpx.Response) -> float | None:
    retry_after = response.headers.get("retry-after")
    if retry_after is None:
        return None
    try:
        value = float(retry_after)
    except ValueError:
        return None
    return max(0.0, min(value, _MAX_RETRY_DELAY_SECONDS))


def _error_code_is_transient(error: Any) -> bool:
    if not isinstance(error, dict):
        return False
    code = error.get("code")
    try:
        numeric_code = int(code)
    except (TypeError, ValueError):
        return False
    return numeric_code in _TRANSIENT_STATUS_CODES


def extract_openrouter_message(
    choice: dict[str, Any],
) -> CompletionResult:
    """Extract a normalized CompletionResult from an OpenRouter choice object.

    OpenRouter's Chat Completions response can place the model's answer in
    several different fields depending on the upstream provider and model
    features (reasoning/thinking, refusals, tool calls, multipart content).
    This function applies an explicit precedence spec and tags the result
    with an outcome so the runner can separate honest model behavior from
    integration failures.

    Precedence spec (stop at first hit that yields non-empty text):

      1. `message.content` as a non-empty string.
      2. `message.content` as an array of content parts — concatenate every
         part whose `type` is "text" (or that exposes a `text` field).
      3. `message.refusal` — an explicit refusal string the model emitted;
         this is treated as the model's answer channel for our purposes.
      4. `message.reasoning` (plain string) combined with `message.content`
         if content is empty. Visible reasoning counts as an answer only when
         there is nothing else; we still flag this with sources so reviewers
         can see it.
      5. `message.reasoning_details` — only textual, non-encrypted entries
         (`reasoning.text` / `reasoning.summary`) are concatenated. Entries
         of type `reasoning.encrypted` are explicitly IGNORED because we
         cannot verify their content.

    If none of the above yields text:

      - If the provider indicated a clean finish (`finish_reason` in
        {"stop", "end_turn", "length"}) but produced nothing we recognize
        as an answer, this is `EMPTY_BUT_EXPLAINABLE` only when `refusal`
        or `tool_calls` was present (explained empty). Otherwise it is
        `NO_PARSEABLE_ASSISTANT_OUTPUT` — the run should NOT pretend this
        was a normal empty string answer.
      - If the message shape is unrecognized entirely (missing `message`,
        non-dict, etc.), return `UNSUPPORTED_SHAPE`.

    The caller is responsible for recording this outcome in the database
    and excluding Class B results from scoring.
    """

    if not isinstance(choice, dict):
        return CompletionResult(
            text=None,
            outcome=EXTRACTION_UNSUPPORTED_SHAPE,
            sources=[],
            raw_message_summary=_summarize_message(choice),
            provider="openrouter",
        )

    message = choice.get("message")
    finish_reason = choice.get("finish_reason")
    if not isinstance(finish_reason, str):
        finish_reason = None

    if not isinstance(message, dict):
        return CompletionResult(
            text=None,
            outcome=EXTRACTION_UNSUPPORTED_SHAPE,
            sources=[],
            finish_reason=finish_reason,
            raw_message_summary=_summarize_message(choice),
            provider="openrouter",
        )

    sources: list[str] = []
    text_parts: list[str] = []

    content = message.get("content")
    if isinstance(content, str) and content.strip():
        text_parts.append(content)
        sources.append("message.content")
    elif isinstance(content, list):
        for idx, part in enumerate(content):
            if not isinstance(part, dict):
                continue
            ptype = part.get("type")
            part_text = part.get("text")
            if ptype in (None, "text", "output_text") and isinstance(part_text, str) and part_text.strip():
                text_parts.append(part_text)
                sources.append(f"message.content[{idx}].text")

    refusal = message.get("refusal")
    if not text_parts and isinstance(refusal, str) and refusal.strip():
        text_parts.append(refusal)
        sources.append("message.refusal")

    if not text_parts:
        reasoning = message.get("reasoning")
        if isinstance(reasoning, str) and reasoning.strip():
            text_parts.append(reasoning)
            sources.append("message.reasoning")

    if not text_parts:
        details = message.get("reasoning_details")
        if isinstance(details, list):
            for idx, entry in enumerate(details):
                if not isinstance(entry, dict):
                    continue
                etype = entry.get("type")
                if etype == "reasoning.text":
                    etext = entry.get("text")
                    if isinstance(etext, str) and etext.strip():
                        text_parts.append(etext)
                        sources.append(f"message.reasoning_details[{idx}].text")
                elif etype == "reasoning.summary":
                    esum = entry.get("summary")
                    if isinstance(esum, str) and esum.strip():
                        text_parts.append(esum)
                        sources.append(f"message.reasoning_details[{idx}].summary")

    thought_process: str | None = None
    reasoning_field = message.get("reasoning")
    if isinstance(reasoning_field, str) and "message.reasoning" not in sources:
        thought_process = reasoning_field

    if text_parts:
        joined = "\n\n".join(part.strip() for part in text_parts).strip()
        if joined:
            return CompletionResult(
                text=joined,
                thought_process=thought_process,
                outcome=EXTRACTION_OK,
                sources=sources,
                finish_reason=finish_reason,
                provider="openrouter",
            )

    has_tool_calls = bool(message.get("tool_calls"))
    has_refusal_field = isinstance(refusal, str)
    clean_finish = finish_reason in {"stop", "end_turn", "length", "tool_calls"}

    if clean_finish and (has_tool_calls or has_refusal_field):
        return CompletionResult(
            text=None,
            outcome=EXTRACTION_EMPTY_BUT_EXPLAINABLE,
            sources=sources,
            finish_reason=finish_reason,
            raw_message_summary=_summarize_message(message),
            provider="openrouter",
        )

    return CompletionResult(
        text=None,
        outcome=EXTRACTION_NO_PARSEABLE_OUTPUT,
        sources=sources,
        finish_reason=finish_reason,
        raw_message_summary=_summarize_message(message),
        provider="openrouter",
    )


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

        if "/" not in model and not model.startswith("openai/") and not model.startswith("anthropic/"):
            if model.startswith("gpt-") or model.startswith("o1"):
                model = f"openai/{model}"
            elif model.startswith("claude-"):
                model = f"anthropic/{model}"

        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": _MAX_COMPLETION_TOKENS,
        }
        response: httpx.Response | None = None
        response_data: dict[str, Any] | None = None
        for attempt in range(1, _MAX_TRANSIENT_ATTEMPTS + 1):
            response = await client.post("/chat/completions", json=payload)

            should_retry = response.status_code in _TRANSIENT_STATUS_CODES
            response_data = None
            if response.status_code == 200:
                try:
                    parsed = response.json()
                except Exception:
                    parsed = None
                if isinstance(parsed, dict):
                    response_data = parsed
                    should_retry = _error_code_is_transient(parsed.get("error"))

            if not should_retry:
                break
            if attempt == _MAX_TRANSIENT_ATTEMPTS:
                break

            retry_after = _retry_after_seconds(response)
            if retry_after is None:
                retry_after = min(
                    _INITIAL_RETRY_DELAY_SECONDS * (2 ** (attempt - 1)),
                    _MAX_RETRY_DELAY_SECONDS,
                )
                retry_after += random.uniform(0, 0.25)
            await asyncio.sleep(retry_after)

        assert response is not None

        if response.status_code != 200:
            error_msg = response.text
            try:
                error_data = response.json()
                if "error" in error_data:
                    error_msg = error_data["error"].get("message", error_msg)
            except Exception:
                pass

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

        try:
            data: dict[str, Any] = response_data if response_data is not None else response.json()
        except Exception as exc:
            return CompletionResult(
                text=None,
                outcome=EXTRACTION_PROVIDER_ERROR,
                sources=[],
                raw_message_summary=_truncate(f"Invalid JSON from OpenRouter: {exc!r}"),
                provider="openrouter",
            )

        if isinstance(data.get("error"), dict):
            return CompletionResult(
                text=None,
                outcome=EXTRACTION_PROVIDER_ERROR,
                sources=[],
                raw_message_summary=_summarize_message(data),
                provider="openrouter",
            )

        choices = data.get("choices")
        if not isinstance(choices, list) or not choices:
            return CompletionResult(
                text=None,
                outcome=EXTRACTION_UNSUPPORTED_SHAPE,
                sources=[],
                raw_message_summary=_summarize_message(data),
                provider="openrouter",
            )

        return extract_openrouter_message(choices[0])
