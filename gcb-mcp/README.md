# GCB MCP server

## Stable Codex entrypoint (recommended)

Codex is the preferred agent for running GCB tools. Register the MCP server in
`~/.codex/config.toml` so tools such as `run_gcb_test`,
`check_ready_for_testing`, `start_gcb_test`, `get_job_status`, and
`upload_result` are exposed directly in Codex sessions.

Use the repo launcher directly:

```toml
[mcp_servers.gcb-mcp]
command = "/ABS/PATH/TO/great-commission-benchmark/gcb-mcp/scripts/gcb_mcp_launch.sh"
args = []
startup_timeout_sec = 120

[mcp_servers.gcb-mcp.env]
GCB_MCP_HOME = "/ABS/PATH/TO/great-commission-benchmark/gcb-mcp"
GCB_API_BASE_URL = "https://api.greatcommissionbenchmark.ai"
```

Secrets do not need to be duplicated in `~/.codex/config.toml` if
`~/.gcb-runner/config.json` already contains `platform.api_key` and the
OpenRouter backend key. The MCP server reads that same config automatically.

After updating Codex config, start a fresh Codex session and run:

```bash
codex mcp list
```

You should see `gcb-mcp` enabled. Existing sessions usually do not gain newly
configured MCP tools until restarted.

## Stable Cursor entrypoint (optional)

Hard‑coding `…/gcb-mcp/.venv/bin/gcb-mcp` in `mcp.json` breaks whenever the repo
moves or the venv is recreated. Cursor can use a fixed launcher on `PATH` and
put volatility in `GCB_MCP_HOME`.

### One‑time install

From this directory:

```bash
./scripts/install_cursor_launcher.sh
```

This installs `~/.local/bin/gcb-mcp-cursor` (override with
`INSTALL_DEST=/other/bin`).

Ensure `~/.local/bin` is on your `PATH` for GUI apps if needed (macOS: some
Cursor builds inherit a minimal PATH).

### `~/.cursor/mcp.json`

Use a **constant** `command` and only change `GCB_MCP_HOME` when the checkout moves:

```json
{
  "mcpServers": {
    "gcb-mcp": {
      "command": "/Users/YOU/.local/bin/gcb-mcp-cursor",
      "args": [],
      "env": {
        "GCB_MCP_HOME": "/ABS/PATH/TO/great-commission-benchmark/gcb-mcp",
        "GCB_API_KEY": "gcb_your_dashboard_key_here",
        "GCB_API_BASE_URL": "https://api.greatcommissionbenchmark.ai",
        "OPENROUTER_API_KEY": "sk-or-v1-..."
      }
    }
  }
}
```

The launcher runs `scripts/gcb_mcp_launch.sh`, which:

1. Uses **`uv run --directory "$ROOT" gcb-mcp`** when `uv` is available (keeps deps aligned with `pyproject.toml`).
2. Otherwise runs **`$ROOT/.venv/bin/gcb-mcp`**.

You can also call `./scripts/gcb_mcp_launch.sh` directly while developing (no `GCB_MCP_HOME` required).

### Alternative without launcher

If you prefer not to install the stub:

```json
"command": "uv",
"args": ["run", "--directory", "/ABS/PATH/TO/gcb-mcp", "gcb-mcp"],
"env": { "GCB_API_KEY": "…" }
```

When the repo moves, update the **single** path in `args`.

---

## GCB platform API key (required for most tools)

Many tools call the GCB **runner HTTP API** (`X-API-Key`): active models, blog CRUD, image upload, bulk submit, remote exports, etc. That is the same **dashboard API key** you use elsewhere—not an OpenRouter key.

### Option A — Cursor MCP `env` (recommended for agents)

Set **`GCB_API_KEY`** in the MCP `env` block (see examples above).

### Option B — Reuse `gcb-runner` config (no duplicate secret)

If you already ran **`gcb-runner config`** and saved **`platform.api_key`** in `~/.gcb-runner/config.json`, the MCP server will pick that up automatically when **`GCB_API_KEY` is unset**.

If both are set, **`GCB_API_KEY` wins** (useful for overriding per machine).

### Where to get the key

Dashboard → Settings → API key, with **admin** or **benchmark editor** access for runner endpoints.

### Verify

Use the MCP tool **`check_ready_for_testing`** (or `list_active_models`). If the key is missing or invalid, the response will say so explicitly.
