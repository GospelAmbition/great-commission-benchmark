"""MCP server for the Great Commission Benchmark platform API.

Importing :mod:`gcb_mcp` exposes a fully-configured ``FastMCP`` instance
(``gcb_mcp.mcp``) with all GCB tools registered, so external hosts (e.g.
the gcb-platform FastAPI backend) can mount the same tool surface over
HTTP without re-declaring tool signatures.

Stdio CLI entrypoint remains :func:`gcb_mcp.server.main`.
"""

from __future__ import annotations

from gcb_mcp.context import RequestContext, behalf_headers, bind, current, reset, scope
from gcb_mcp.server import main, mcp

__all__ = [
    "RequestContext",
    "behalf_headers",
    "bind",
    "current",
    "main",
    "mcp",
    "reset",
    "scope",
]
