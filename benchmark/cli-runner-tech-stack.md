# GCB Runner CLI - Tech Stack

This document explains the technology choices for the GCB Runner CLI and the reasoning behind them.

---

## Overview

| Attribute | Value |
|-----------|-------|
| **Package Name** | `gcb-runner` |
| **Language** | Python 3.10+ |
| **Distribution** | PyPI |
| **Target Users** | Community members (non-developers welcome) |
| **Install Size** | Minimal (~5 MB with deps) |
| **Design Philosophy** | Simple, lightweight, zero-friction |

---

## Core Principle: Minimal Dependencies

The GCB Runner is designed for **community members** who may not be Python developers. Every dependency adds:

- Installation time and potential conflicts
- Troubleshooting complexity
- Maintenance burden

We aggressively minimize dependencies, preferring Python's standard library wherever possible.

---

## Technology Choices

### Python (Language)

**Why Python:**

| Factor | Reasoning |
|--------|-----------|
| **Ubiquity** | Most common language for ML/AI tooling; users likely have it |
| **Ecosystem** | Excellent HTTP clients, CLI frameworks, data validation |
| **Readability** | Community contributors can understand and modify |
| **Cross-platform** | Works on Windows, macOS, Linux without changes |

**Version:** Python 3.10+ (for modern type hints and match statements)

---

### Dependencies

```toml
[project]
dependencies = [
    "httpx>=0.24",          # HTTP client for LLM APIs
    "rich>=13.0",           # Beautiful CLI output
    "typer>=0.9",           # CLI framework
    "pydantic>=2.0",        # Data validation
    "sqlalchemy>=2.0",      # Local results storage
    "python-dotenv>=1.0",   # Environment variables
]
```

#### `httpx` - HTTP Client

**Why httpx over requests:**

| Feature | httpx | requests |
|---------|-------|----------|
| Async support | ✓ Native | ✗ Requires extra lib |
| HTTP/2 | ✓ Built-in | ✗ No |
| Modern API | ✓ | Dated |
| Type hints | ✓ Full | Partial |

httpx allows us to make concurrent API calls (test model + judge model) and supports streaming responses for progress indication.

#### `rich` - CLI Output

**Why rich:**

- Beautiful terminal tables, progress bars, and formatting
- Zero configuration needed
- Works on all terminals (degrades gracefully)
- Same author as `typer` (good integration)

**Example output:**
```
┌────┬────────────────────┬───────┬────────┐
│ ID │ Model              │ Score │ Status │
├────┼────────────────────┼───────┼────────┤
│ 3  │ gpt-4o             │ 82.0  │ ✓ Done │
│ 2  │ claude-3.5-sonnet  │ 78.5  │ ✓ Done │
└────┴────────────────────┴───────┴────────┘
```

#### `typer` - CLI Framework

**Why typer over argparse/click:**

| Feature | typer | argparse | click |
|---------|-------|----------|-------|
| Type-hint based | ✓ | ✗ | ✗ |
| Auto-generated help | ✓ Excellent | Basic | Good |
| Shell completion | ✓ Built-in | Manual | Plugin |
| Learning curve | Low | Medium | Medium |

Typer generates CLI commands from Python function signatures with type hints. Less boilerplate, fewer bugs.

```python
@app.command()
def test(
    model: str = typer.Option(..., help="Model to test"),
    backend: str = typer.Option("openrouter", help="LLM backend"),
):
    """Run the benchmark against a model."""
    ...
```

#### `pydantic` - Data Validation

**Why pydantic:**

- Validates API responses from LLM backends
- Serializes/deserializes JSON exports
- Type-safe configuration handling
- Excellent error messages for users

#### `sqlalchemy` - Database

**Why SQLAlchemy with SQLite:**

| Alternative | Why Not |
|-------------|---------|
| Raw SQLite | Too much boilerplate, error-prone |
| PostgreSQL | Requires external server |
| JSON files | No query capability, slow for large result sets |
| TinyDB | Less mature, limited query power |

SQLite + SQLAlchemy gives us:
- Single-file database (portable, no server)
- Full SQL query capability
- ORM for clean Python code
- Battle-tested reliability

#### `python-dotenv` - Environment Variables

Simple loading of `.env` files for API keys. Standard practice, tiny footprint.

---

### Results Viewer (Zero Additional Dependencies)

The results viewer uses **Python's standard library only**:

| Component | Implementation |
|-----------|----------------|
| HTTP Server | `http.server.HTTPServer` |
| Request Handling | Custom `SimpleHTTPRequestHandler` subclass |
| Database Queries | `sqlite3` (stdlib) |
| JSON API | `json` (stdlib) |
| Browser Launch | `webbrowser` (stdlib) |

**Why not Flask/FastAPI:**

| Consideration | Decision |
|---------------|----------|
| Install size | Flask adds ~30 KB, FastAPI adds ~70 KB + uvicorn |
| Dependency conflicts | Possible with user's other Python projects |
| Feature need | We only need ~5 endpoints |
| User friction | Extra `pip install` step |

For a simple dashboard with 5 API endpoints, the stdlib is sufficient. Users get a web viewer without any additional installation.

**Frontend:**

| Component | Implementation |
|-----------|----------------|
| HTML/CSS | Embedded in Python string |
| JavaScript | Vanilla JS (no framework) |
| Charts | Chart.js loaded from CDN |

The entire dashboard is a single HTML string embedded in the Python code. No static files, no build step, no bundler.

---

### Embedded Benchmark Versions

Questions are compiled into Python modules rather than fetched from a server:

```python
# Base64 encoded, zlib compressed JSON
_BUNDLE_DATA = """
eJzVWNtu2zgQfV9g/4HwS+ILJUq2nTgI0KJFs0WLLrZAi32gKMoWI4kCScV2
...
"""
```

**Why embedded over server-fetch:**

| Approach | Pros | Cons |
|----------|------|------|
| Server fetch | Always current | Network required, single point of failure |
| Embedded | Offline, fast, reliable | CLI release needed for new versions |

**Why compressed/encoded over plain JSON:**

| Approach | Pros | Cons |
|----------|------|------|
| Plain JSON files | Easy to inspect | Questions trivially visible |
| Encrypted | "Secure" | Key distribution problem, false security |
| Compressed + encoded | Raises friction, honest about limits | Determined users can decode |

We chose honesty: the questions aren't secret, but they shouldn't be trivially browsable in an IDE file tree.

---

## Architecture Decisions

### Single-File CLI vs Multiple Modules

**Decision:** Minimal module structure with clear boundaries

```
gcb_runner/
├── cli.py              # All CLI commands
├── runner.py           # Test execution
├── judge.py            # Evaluation logic
├── backends/           # LLM adapters (one file per backend)
├── versions/           # Embedded benchmark bundles
├── viewer/             # Results viewer (4 small files)
├── results.py          # Storage
└── export.py           # Export/upload
```

**Why:** 
- Easy to navigate (<15 files total)
- Clear responsibility per file
- No deep import hierarchies
- Community contributors can find things

### Async vs Sync

**Decision:** Async for LLM calls, sync for CLI operations

```python
async def run_benchmark(...):
    # Async allows concurrent model + judge calls
    model_response = await backend.complete(...)
    verdict = await judge.evaluate(...)
```

**Why:**
- LLM API calls are I/O bound and benefit from concurrency
- CLI operations (file I/O, user prompts) are fine as sync
- Typer handles the async/sync boundary cleanly

### Configuration Storage

**Decision:** JSON config file at `~/.gcb-runner/config.json`

**Why not environment variables only:**
- Users shouldn't need to edit shell profiles
- Config persists across terminal sessions
- Can store multiple backend configurations

**Why not YAML/TOML:**
- JSON is universally understood
- No additional parsing dependency
- Good enough for simple config

---

## What We Intentionally Avoided

| Technology | Why Avoided |
|------------|-------------|
| **Docker** | Adds complexity for non-developers |
| **Virtual environments** | Users may not understand them |
| **Build tools** (webpack, etc.) | No JavaScript build needed |
| **Type checkers at runtime** | Pydantic handles validation |
| **Logging frameworks** | `print()` and `rich.console` suffice |
| **Configuration libraries** | JSON + python-dotenv is enough |
| **Testing frameworks beyond pytest** | Standard pytest is sufficient |
| **CI/CD complexity** | Simple GitHub Actions workflow |

---

## Trade-offs Acknowledged

### Embedded Questions vs Server Fetch

**Trade-off:** New benchmark versions require a CLI release.

**Mitigation:** 
- We'll release CLI updates when benchmarks update (quarterly at most)
- Users can pin specific CLI versions for reproducibility
- Platform submission validates version compatibility

### Stdlib HTTP Server vs Flask

**Trade-off:** Less elegant code, no middleware, manual routing.

**Mitigation:**
- We only have 5 endpoints
- Handler class is ~100 lines
- Worth it for zero-dependency viewer

### SQLite vs PostgreSQL

**Trade-off:** No concurrent writes, limited scalability.

**Mitigation:**
- Single user tool—no concurrency needed
- Typical user has <100 test runs
- SQLite handles this trivially

---

## Security Considerations

| Concern | Approach |
|---------|----------|
| API keys | Stored in `~/.gcb-runner/config.json` with 600 permissions |
| Question exposure | Compressed/encoded (friction, not security) |
| Results upload | HTTPS to platform API with user authentication |
| Local viewer | Binds to localhost only, no external access |

---

## Future Considerations

### If We Need to Add Features

| Feature | Approach |
|---------|----------|
| More backends | Add file to `backends/` with same interface |
| Richer viewer | Consider optional `flask` install (`pip install gcb-runner[viewer-extended]`) |
| Plugin system | Not planned—keep it simple |

### What Would Trigger a Rewrite

- Need for real-time collaboration → Would need server component
- Complex query requirements → Might add optional Datasette
- GUI requirement → Would build separate Electron/Tauri app

---

## Summary

The GCB Runner CLI is intentionally boring technology:

- **Python** because it's ubiquitous
- **6 dependencies** because that's all we need
- **SQLite** because it's bulletproof
- **Stdlib HTTP server** because zero deps matters
- **Embedded questions** because offline matters

Every choice optimizes for: *a non-developer can `pip install gcb-runner` and run benchmarks in 5 minutes.*
