"""Common types for LLM backends."""

from dataclasses import dataclass, field


# Extraction outcome enum values.
#
# A backend MUST set exactly one of these on every CompletionResult so the
# runner can distinguish an honest model answer from a capture/integration
# failure. The runner treats OK / EMPTY_BUT_EXPLAINABLE as Class A (judgeable
# model behavior) and everything else as Class B (test-harness failure that
# must NOT be scored as a normal verdict).
EXTRACTION_OK = "OK"
EXTRACTION_EMPTY_BUT_EXPLAINABLE = "EMPTY_BUT_EXPLAINABLE"
EXTRACTION_NO_PARSEABLE_OUTPUT = "NO_PARSEABLE_ASSISTANT_OUTPUT"
EXTRACTION_UNSUPPORTED_SHAPE = "UNSUPPORTED_SHAPE"
EXTRACTION_PROVIDER_ERROR = "PROVIDER_ERROR"

EXTRACTION_CLASS_A = frozenset({EXTRACTION_OK, EXTRACTION_EMPTY_BUT_EXPLAINABLE})
EXTRACTION_CLASS_B = frozenset({
    EXTRACTION_NO_PARSEABLE_OUTPUT,
    EXTRACTION_UNSUPPORTED_SHAPE,
    EXTRACTION_PROVIDER_ERROR,
})


@dataclass
class CompletionResult:
    """Result from an LLM completion call.

    `text` is the normalized assistant answer sent to the judge when the
    outcome is Class A (OK / EMPTY_BUT_EXPLAINABLE). For Class B outcomes,
    `text` is None and the runner must not treat the result as a normal
    model response.

    `outcome` identifies which channel/path produced the result so reviewers
    can distinguish "model answered" from "test failed to capture an answer".

    `sources` records exactly which response fields were concatenated into
    `text`, e.g. ["message.content"], ["message.content[0].text",
    "message.content[1].text"], or ["message.refusal"]. Useful for audit.

    `raw_message_summary` is a short (truncated, redacted) dump of the raw
    assistant message or provider error, preserved only so operators can
    diagnose Class B outcomes without re-running the request.
    """

    text: str | None
    thought_process: str | None = None
    outcome: str = EXTRACTION_OK
    sources: list[str] = field(default_factory=list)
    finish_reason: str | None = None
    raw_message_summary: str | None = None
    provider: str | None = None

    @property
    def is_class_a(self) -> bool:
        """True if this result represents a trusted model answer."""
        return self.outcome in EXTRACTION_CLASS_A

    @property
    def is_class_b(self) -> bool:
        """True if this result represents a capture/integration failure."""
        return self.outcome in EXTRACTION_CLASS_B
