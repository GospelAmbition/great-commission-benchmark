#!/usr/bin/env bash
# Start the GCB MCP stdio server from a checkout of gcb-mcp.
#
# ROOT resolution:
#   1. If GCB_MCP_HOME is set (recommended for Cursor), use it.
#   2. Otherwise infer from this script's location (…/gcb-mcp/scripts/ → …/gcb-mcp).
#
# Execution:
#   1. Prefer `uv run` so the venv is created/updated consistently.
#   2. Fall back to .venv/bin/gcb-mcp if uv is unavailable.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [[ -n "${GCB_MCP_HOME:-}" ]]; then
  ROOT="$(cd "$GCB_MCP_HOME" && pwd)"
else
  ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
fi

if [[ ! -f "$ROOT/pyproject.toml" ]]; then
  echo "gcb_mcp_launch.sh: expected pyproject.toml under ROOT=$ROOT" >&2
  exit 1
fi

cd "$ROOT"

if command -v uv >/dev/null 2>&1; then
  exec uv run --directory "$ROOT" gcb-mcp "$@"
fi

VENV_BIN="$ROOT/.venv/bin/gcb-mcp"
if [[ -x "$VENV_BIN" ]]; then
  exec "$VENV_BIN" "$@"
fi

echo "gcb_mcp_launch.sh: install uv (https://docs.astral.sh/uv/) or run: cd \"$ROOT\" && uv sync" >&2
exit 1
