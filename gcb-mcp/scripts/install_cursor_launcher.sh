#!/usr/bin/env bash
# Install a stable MCP entrypoint to ~/.local/bin (or INSTALL_DEST).
# Cursor keeps a fixed "command" path; when the repo moves, only GCB_MCP_HOME in mcp.json changes.
#
# Usage:
#   ./scripts/install_cursor_launcher.sh
#   INSTALL_DEST=/opt/bin ./scripts/install_cursor_launcher.sh

set -euo pipefail

DEST="${INSTALL_DEST:-$HOME/.local/bin}"
LAUNCHER="$DEST/gcb-mcp-cursor"

mkdir -p "$DEST"

cat >"$LAUNCHER" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
if [[ -z "${GCB_MCP_HOME:-}" ]]; then
  echo "gcb-mcp-cursor: set GCB_MCP_HOME in Cursor MCP env to your gcb-mcp directory (contains pyproject.toml)." >&2
  exit 1
fi
exec "${GCB_MCP_HOME}/scripts/gcb_mcp_launch.sh" "$@"
EOF

chmod +x "$LAUNCHER"

echo "Installed: $LAUNCHER"
echo ""
echo "Add to ~/.cursor/mcp.json (example):"
echo '{'
echo '  "mcpServers": {'
echo '    "gcb-mcp": {'
echo "      \"command\": \"$LAUNCHER\","
echo '      "args": [],'
echo '      "env": {'
echo '        "GCB_MCP_HOME": "/path/to/great-commission-benchmark/gcb-mcp",'
echo '        "GCB_API_KEY": "gcb_...",'
echo '        "GCB_API_BASE_URL": "https://api.greatcommissionbenchmark.ai",'
echo '        "OPENROUTER_API_KEY": "sk-or-v1-..."'
echo '      }'
echo '    }'
echo '  }'
echo '}'
