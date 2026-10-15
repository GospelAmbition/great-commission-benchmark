"""Recover abbreviated OpenRouter descriptions during metadata synchronization only."""
import asyncio
import json
import re
from html.parser import HTMLParser
from typing import Optional
from urllib.parse import quote, unquote, urlsplit

import httpx

MAX_PAGE_BYTES = 8 * 1024 * 1024
MAX_DESCRIPTION_BYTES = 128 * 1024
PAGE_TIMEOUT_SECONDS = 5


def valid_model_id(model_id: str) -> bool:
    return bool(re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._:+-]*/[A-Za-z0-9][A-Za-z0-9._:+-]*", model_id))


def _matches_model_url(value, model_id: str) -> bool:
    if not isinstance(value, str):
        return False
    try:
        parsed = urlsplit(value)
        return (parsed.scheme == "https" and parsed.netloc == "openrouter.ai"
                and not parsed.query and not parsed.fragment
                and unquote(parsed.path).rstrip("/") == f"/{model_id}")
    except ValueError:
        return False


def abbreviated_prefix(description: Optional[str]) -> Optional[str]:
    text = (description or "").strip()
    for suffix in ("...", "…"):
        if text.endswith(suffix):
            return text[:-len(suffix)].rstrip() or None
    return None


def is_abbreviated(description: Optional[str]) -> bool:
    return abbreviated_prefix(description) is not None


class _StructuredDataParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.documents = []
        self._parts = None

    def handle_starttag(self, tag, attrs):
        if tag == "script" and dict(attrs).get("type", "").lower() == "application/ld+json":
            self._parts = []

    def handle_data(self, data):
        if self._parts is not None:
            self._parts.append(data)

    def handle_endtag(self, tag):
        if tag == "script" and self._parts is not None:
            try:
                self.documents.append(json.loads("".join(self._parts)))
            except (ValueError, TypeError):
                pass
            self._parts = None


def _entities(value):
    if isinstance(value, list):
        for item in value:
            yield from _entities(item)
    elif isinstance(value, dict):
        yield value
        yield from _entities(value.get("@graph"))


def extract_full_description(html: str, model_id: str, abbreviated: str) -> Optional[str]:
    prefix = abbreviated_prefix(abbreviated)
    if not prefix or not valid_model_id(model_id):
        return None
    parser = _StructuredDataParser()
    parser.feed(html)
    for document in parser.documents:
        for entity in _entities(document):
            types = entity.get("@type")
            if not (types == "SoftwareApplication" or isinstance(types, list) and "SoftwareApplication" in types) or not _matches_model_url(entity.get("url"), model_id):
                continue
            description = entity.get("description")
            if (isinstance(description, str) and description.startswith(prefix)
                    and len(description) > len(prefix) and not is_abbreviated(description)
                    and len(description.encode("utf-8")) <= MAX_DESCRIPTION_BYTES):
                return description
    return None


async def fetch_full_description(model_id: str, abbreviated: str) -> Optional[str]:
    if not valid_model_id(model_id) or not is_abbreviated(abbreviated):
        return None
    # A separate public client never receives the authenticated API client's headers.
    url = f"https://openrouter.ai/{quote(model_id, safe='/:')}"
    try:
        async with asyncio.timeout(PAGE_TIMEOUT_SECONDS):
            async with httpx.AsyncClient(timeout=PAGE_TIMEOUT_SECONDS, follow_redirects=False) as client:
                async with client.stream("GET", url) as response:
                    response.raise_for_status()
                    if response.status_code != 200:
                        return None
                    body = bytearray()
                    async for chunk in response.aiter_bytes():
                        body.extend(chunk)
                        if len(body) > MAX_PAGE_BYTES:
                            return None
                    return extract_full_description(body.decode("utf-8", errors="replace"), model_id, abbreviated)
    except (httpx.HTTPError, TimeoutError, ValueError):
        return None
