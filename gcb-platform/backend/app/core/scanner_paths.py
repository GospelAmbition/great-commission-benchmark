"""Fast-reject paths used by vulnerability scanners and exploit kits.

These probes never match a real GCB route. Returning 404 here avoids
checking out DB/Redis connections or running application code.
"""
from __future__ import annotations

import re

_PREFIXES = (
    "/.env",
    "/.git",
    "/.aws",
    "/actuator",
    "/wp-admin",
    "/wp-login",
    "/wp-content",
    "/wp-includes",
    "/wp-config",
    "/wordpress",
    "/phpmyadmin",
    "/phpinfo",
)

_EXACT = {
    "/env",
    "/.htaccess",
    "/xmlrpc.php",
    "/web.config",
    "/config.php",
    "/phpinfo.php",
    "/info.php",
}

_PHP_OR_ENV_SUFFIX = (".php", ".env")
_MULTI_SLASH = re.compile(r"/{2,}")


def is_scanner_path(path: str) -> bool:
    """Return True when ``path`` is a well-known scanner/exploit probe."""
    if not path:
        return False
    normalized = _MULTI_SLASH.sub("/", path.lower())
    if normalized in _EXACT:
        return True
    if "phpinfo" in normalized:
        return True
    if "/.git" in normalized or normalized.startswith("/.git"):
        return True
    if "/wp-" in normalized or normalized.startswith("/wp-"):
        return True
    if normalized.startswith("/.env"):
        return True
    for prefix in _PREFIXES:
        if normalized == prefix or normalized.startswith(prefix + "/"):
            return True
    return normalized.endswith(_PHP_OR_ENV_SUFFIX)
