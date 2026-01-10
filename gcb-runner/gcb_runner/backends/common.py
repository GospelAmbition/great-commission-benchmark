"""Common types for LLM backends."""

from dataclasses import dataclass


@dataclass
class CompletionResult:
    """Result from an LLM completion call."""
    text: str
    thought_process: str | None = None
