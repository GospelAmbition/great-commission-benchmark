"""Minimal HTML consent page rendered between the Google bounce and
the issuance of an authorization code.

Kept inline (no Jinja file) to avoid adding a templates layer to the
backend just for this. The page is plain HTML5 with inline styles so it
renders correctly in the iPhone in-app browser.
"""
from __future__ import annotations

import html
from typing import Iterable

_SCOPE_DESCRIPTIONS = {
    "mcp:read": "Read benchmark data, jobs, and published results",
    "mcp:write": "Run new tests and upload benchmark results",
    "mcp:blog": "Create and edit blog posts",
    "mcp:newsletter": "Compose and preview newsletter drafts",
    "mcp:admin": "Send newsletters and perform admin operations",
}


def render_consent_html(
    *,
    client_name: str,
    granted_scopes: Iterable[str],
    user_email: str,
    pending_session_id: str,
    csrf_token: str,
) -> str:
    rows = "".join(
        f'<li><strong>{html.escape(s)}</strong> — '
        f"{html.escape(_SCOPE_DESCRIPTIONS.get(s, 'GCB tools'))}</li>"
        for s in granted_scopes
    )
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Authorize {html.escape(client_name)}</title>
<style>
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI',
          Roboto, sans-serif; max-width: 480px; margin: 2rem auto;
          padding: 0 1rem; color: #111; }}
  h1 {{ font-size: 1.4rem; }}
  ul {{ padding-left: 1.2rem; }}
  li {{ margin: .35rem 0; }}
  .muted {{ color: #555; font-size: .9rem; }}
  form {{ margin-top: 1.5rem; display: flex; gap: .75rem; }}
  button {{ padding: .6rem 1.2rem; font-size: 1rem; border-radius: 8px;
            border: 1px solid #d0d0d0; cursor: pointer; }}
  button.primary {{ background: #2256ff; color: white; border-color: #2256ff; }}
  button.secondary {{ background: white; }}
</style>
</head>
<body>
<h1>Authorize {html.escape(client_name)}</h1>
<p class="muted">Signed in as {html.escape(user_email)}.</p>
<p>This client is requesting permission to:</p>
<ul>{rows}</ul>
<p class="muted">If you have not been granted a permission flag for a
requested scope, only public benchmark data will be accessible until an
admin updates your permissions.</p>
<form method="POST" action="/oauth/authorize/consent">
  <input type="hidden" name="session_id" value="{html.escape(pending_session_id)}">
  <input type="hidden" name="csrf_token" value="{html.escape(csrf_token)}">
  <button class="primary" name="action" value="approve" type="submit">Approve</button>
  <button class="secondary" name="action" value="deny" type="submit">Cancel</button>
</form>
</body>
</html>"""
