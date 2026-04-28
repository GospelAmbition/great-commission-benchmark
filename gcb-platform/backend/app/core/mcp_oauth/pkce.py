"""RFC 7636 PKCE S256 helpers.

Plain code-challenge method is intentionally rejected — MCP 2025-06-18
requires S256 for all clients, including confidential ones.
"""
from __future__ import annotations

import base64
import hashlib
import hmac

S256 = "S256"


class PKCEError(ValueError):
    """Raised when PKCE parameters fail validation."""


def assert_supported_method(method: str | None) -> None:
    """Reject ``plain`` / missing methods early at the authorize step."""
    if method != S256:
        raise PKCEError(
            "Only the S256 code_challenge_method is supported "
            "(received %r)" % method
        )


def verify_s256(code_verifier: str, code_challenge: str) -> bool:
    """Constant-time check that ``BASE64URL(SHA256(verifier)) == challenge``.

    Returns False on any malformed input rather than raising — the
    caller folds this into a generic invalid_grant response.
    """
    if not code_verifier or not code_challenge:
        return False
    # RFC 7636 §4.1: verifier is 43..128 chars from the unreserved set.
    if not (43 <= len(code_verifier) <= 128):
        return False

    digest = hashlib.sha256(code_verifier.encode("ascii")).digest()
    expected = base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")
    return hmac.compare_digest(expected, code_challenge)
