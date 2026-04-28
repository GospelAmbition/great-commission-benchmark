"""In-process MCP server mount for the gcb-platform backend.

Reuses the FastMCP instance defined in :mod:`gcb_mcp` (the existing
stdio MCP package). Tool implementations are unchanged; we only add
scope enforcement and per-request RequestContext binding around the
shared instance.
"""
