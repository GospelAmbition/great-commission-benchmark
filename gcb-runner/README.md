# GCB Runner

A lightweight CLI tool for running the Great Commission Benchmark against AI models.

> **Note:** This repository is automatically synced from the [Great Commission Benchmark monorepo](https://github.com/GospelAmbition/great-commission-benchmark). Please file issues and pull requests there.

## Quick Start

### Download Standalone Executable (Recommended)

Download the standalone executable from the [GCB Runner page](https://greatcommissionbenchmark.ai/runner) - no Python required!

**macOS:**
```bash
# Download from https://greatcommissionbenchmark.ai/runner
chmod +x gcb-runner-macos-arm64  # or gcb-runner-macos-x64 for Intel
./gcb-runner-macos-arm64
```

**Linux:**
```bash
# Download from https://greatcommissionbenchmark.ai/runner
chmod +x gcb-runner-linux-x64
./gcb-runner-linux-x64
```

**Windows:**
```powershell
# Download gcb-runner.exe from https://greatcommissionbenchmark.ai/runner
.\gcb-runner.exe
```

### Basic Usage

```bash
# Launch the interactive menu (default behavior)
gcb-runner

# Show command reference
gcb-runner help

# Or use individual commands directly:
gcb-runner config                                    # Configure API keys
gcb-runner test --model gpt-4o --backend openrouter  # Run benchmark
gcb-runner results                                   # View results
gcb-runner view                                      # Launch web dashboard
gcb-runner report                                    # Generate HTML report
gcb-runner export                                    # Export for submission
gcb-runner update                                    # Check for updates
```

## Auto-Updates

The standalone executable includes auto-update functionality. When a new version is available, you'll see a notification at startup. Run `gcb-runner update` to download and install the latest version.

```bash
# Check for updates without installing
gcb-runner update --check

# Download and install updates
gcb-runner update
```

## Interactive Menu

Running `gcb-runner` without arguments launches an interactive menu. The menu provides:

- **Run Benchmark Test** - Interactive test runner with model and version selection
- **Launch Web Results Dashboard** - Open the web interface to view results
- **Export Results (JSON)** - Export test results for submission
- **Utilities** - Setup wizard, diagnostics, configuration, and more
- **Help & Documentation** - Quick start guide, scoring info, and more

The menu is perfect for users who prefer a guided experience over command-line flags.

### Utilities Menu

The Utilities menu provides access to setup, configuration, and diagnostic tools:

```bash
gcb-runner
# Select [4] Utilities
```

Available utilities:
- **Setup Wizard** - Guided 4-step configuration for first-time users
- **Diagnostics & Connection Test** - Verify your setup is working correctly
- **View Recent Runs** - Browse your test run history
- **View Run Details** - See detailed information about a specific run
- **Generate HTML Report** - Create a standalone HTML report
- **Configuration** - Manage API keys, backends, and preferences

### Diagnostics & Troubleshooting

The diagnostics menu helps verify your setup is working correctly:

```bash
gcb-runner
# Select [4] Utilities → [2] Diagnostics & Connection Test
```

Available diagnostics:

| Option | Description |
|--------|-------------|
| **Run Full Diagnostics** | Complete check of configuration, API, and backend |
| **Test Platform API** | Verify connection to greatcommissionbenchmark.ai |
| **Test Backend** | Check LM Studio/Ollama connectivity |
| **List Versions** | Show all available benchmark versions |
| **Test Question Download** | Verify questions can be fetched for a version |
| **View API Endpoints** | Show API URLs for debugging |

## Overview

The GCB Runner is the official CLI tool for running the [Great Commission Benchmark](https://greatcommissionbenchmark.ai) locally. It allows you to:

- **Run benchmarks** against any LLM (via OpenRouter, OpenAI, Anthropic, or local models)
- **View results** locally with a web dashboard
- **Export results** for submission to the GCB platform

### Platform Tests vs CLI Submissions

| Aspect | Platform Tests | CLI Submissions |
|--------|---------------|-----------------|
| **Where run** | On the platform | Locally via this CLI |
| **Publishing** | Automatic | Requires moderator verification |
| **Cost** | $20 platform fee + model API cost | $20 submission fee (user pays own model costs) |
| **Use Case** | Individual testers, quick results | Organizations, custom/local models |

## Installation

### Standalone Executable (Recommended)

Download from [greatcommissionbenchmark.ai/runner](https://greatcommissionbenchmark.ai/runner)

- **macOS Apple Silicon**: `gcb-runner-macos-arm64`
- **macOS Intel**: `gcb-runner-macos-x64`
- **Linux x64**: `gcb-runner-linux-x64`
- **Windows x64**: `gcb-runner.exe`

Verify downloads using SHA256 hashes from the [manifest.json](https://greatcommissionbenchmark.ai/downloads/manifest.json).

### For Developers: Install from Source

```bash
git clone https://github.com/GospelAmbition/gcb-runner.git
cd gcb-runner
pip install -e ".[dev]"
```

## Configuration

Run the configuration wizard:

```bash
gcb-runner config
```

This will guide you through:
1. Setting up your **Platform API key** (get one from your [dashboard](https://greatcommissionbenchmark.ai/dashboard))
2. Configuring your **LLM backend** (OpenRouter, OpenAI, Anthropic, LM Studio, or Ollama)
3. Selecting a **judge model** for evaluating responses

Configuration is stored in `~/.gcb-runner/config.json`.

## Usage

### Running a Benchmark

```bash
# Run with OpenRouter (default)
gcb-runner test --model gpt-4o --backend openrouter

# Run with OpenAI directly
gcb-runner test --model gpt-4o --backend openai

# Run with Anthropic
gcb-runner test --model claude-3.5-sonnet --backend anthropic

# Run with a local model (LM Studio)
gcb-runner test --model local-model --backend lmstudio

# Run with Ollama
gcb-runner test --model llama3.2 --backend ollama

# Run a specific benchmark version
gcb-runner test --model gpt-4o --benchmark-version 1.0.0

# Resume an interrupted test
gcb-runner test --model gpt-4o --resume

# Validate configuration without running (dry run)
gcb-runner test --model gpt-4o --dry-run
```

**Tip:** Use the interactive menu for guided version selection:
```bash
gcb-runner
# Select [2] Run Benchmark Test
# Choose "Use a specific benchmark version?" → Yes
# Select from the list of available versions
```

### Viewing Results

```bash
# List recent test runs
gcb-runner results

# View details of a specific run
gcb-runner results --run 3
```

### Web Dashboard

```bash
# Launch the results viewer in your browser
gcb-runner view

# View a specific run
gcb-runner view --run 3

# Use a custom port
gcb-runner view --port 9000

# Don't open browser automatically
gcb-runner view --no-browser
```

### Generating Reports

```bash
# Generate HTML report for the latest run
gcb-runner report

# Generate report for a specific run
gcb-runner report --run 3

# Compare two runs
gcb-runner report --run 3 --compare 2

# Save to a specific file
gcb-runner report --run 3 --output my-report.html

# Don't open browser automatically
gcb-runner report --no-browser
```

### Exporting Results

```bash
# Export latest completed run to JSON (saves to current directory)
gcb-runner export

# Export a specific run
gcb-runner export --run 3

# Save to a specific file
gcb-runner export --run 3 --output results.json
```

### Uploading Results

```bash
# Upload results to platform (requires moderator verification)
gcb-runner upload --run 3
```

> **Note:** Direct upload via CLI is coming soon. For now, export your results and upload via the web dashboard.

#### Web Dashboard Upload

Upload your exported results via the web dashboard:

1. **Export your results:**
   ```bash
   gcb-runner export --run 3 --output results.json
   ```

2. **Upload via dashboard:**
   - Sign in to [greatcommissionbenchmark.ai/dashboard](https://greatcommissionbenchmark.ai/dashboard)
   - Click "Upload CLI Results" button
   - Either upload the JSON file or paste the JSON content
   - Review the preview (model, version, score)
   - Submit for review

3. **Payment & Moderation:**
   - If payment is required ($20 submission fee), complete payment via Stripe
   - Your submission will be queued for moderator review
   - You'll receive notifications when your submission is approved or rejected

> **Leaderboard Scoring:** The public leaderboard displays only the **most recent test** for each model. If you re-test a model, the new score will replace the previous one on the leaderboard. All historical test runs remain accessible on the model's detail page.

### Listing Benchmark Versions

```bash
# List all available benchmark versions
gcb-runner versions

# Or use the interactive menu for more details
gcb-runner
# Select [4] Utilities → [2] Diagnostics → [4] List Available Versions
```

This shows available versions with their status, question counts, and release dates.

### Resetting the Database

```bash
# Delete all test runs and start fresh
gcb-runner reset-db

# Skip confirmation prompt
gcb-runner reset-db --force
```

## Command Reference

| Command | Description |
|---------|-------------|
| `gcb-runner` | Launch interactive menu (default) |
| `gcb-runner help` | Show command reference |
| `gcb-runner config` | Configure API keys and preferences |
| `gcb-runner test` | Run benchmark against a model |
| `gcb-runner results` | View past test results |
| `gcb-runner view` | Launch web dashboard |
| `gcb-runner report` | Generate HTML report |
| `gcb-runner export` | Export results to JSON |
| `gcb-runner upload` | Upload results to platform |
| `gcb-runner versions` | List benchmark versions |
| `gcb-runner update` | Check for and install updates |
| `gcb-runner reset-db` | Delete and reinitialize results database |
| `gcb-runner --version` | Show version number |

Use `gcb-runner <command> --help` for detailed options on any command.

## Supported Backends

| Backend | Type | Description |
|---------|------|-------------|
| **OpenRouter** | Cloud | Access 100+ models via single API |
| **OpenAI** | Cloud | Direct OpenAI API access |
| **Anthropic** | Cloud | Direct Claude API access |
| **LM Studio** | Local | OpenAI-compatible local server |
| **Ollama** | Local | Popular local model runner |

### Local Model Setup

#### LM Studio

1. Download and install [LM Studio](https://lmstudio.ai/)
2. Load a model and start the local server
3. Configure GCB Runner:
   ```bash
   gcb-runner config
   # Select "lmstudio" as backend
   # Default URL: http://localhost:1234/v1
   ```

#### Ollama

1. Install [Ollama](https://ollama.ai/)
2. Pull a model: `ollama pull llama3.2`
3. Start the server: `ollama serve`
4. Configure GCB Runner:
   ```bash
   gcb-runner config
   # Select "ollama" as backend
   # Default URL: http://localhost:11434
   ```

## Scoring

The benchmark uses a weighted tier system:

| Tier | Weight | Focus |
|------|--------|-------|
| **Tier 1** | 70% | Task Capability - Can the model complete ministry tasks? |
| **Tier 2** | 20% | Doctrinal Fidelity - Does it maintain orthodox teaching? |
| **Tier 3** | 10% | Worldview Confession - Does it affirm Christian worldview? |

**Final Score** = (Tier 1 × 0.70) + (Tier 2 × 0.20) + (Tier 3 × 0.10)

### Verdict Types

All tiers use unified verdicts:

| Verdict | Meaning | Score |
|---------|---------|-------|
| ACCEPTED | Task completed faithfully | 100% |
| COMPROMISED | Task completed with caveats | 50% |
| REFUSED | Task declined or contradicted | 0% |

## Data Storage

- **Configuration**: `~/.gcb-runner/config.json`
- **Results database**: `~/.gcb-runner/data/results.db`
- **Question cache**: `~/.gcb-runner/cache/`
- **Exports**: `~/.gcb-runner/exports/`

## Troubleshooting

### "Resource not found" Error

This error when running tests usually means:
- No benchmark version has been published yet
- The specified version doesn't exist

**Solution:** Run diagnostics to check available versions:
```bash
gcb-runner
# Select [4] Utilities → [2] Diagnostics → [1] Run Full Diagnostics
```

### Connection Issues

If you can't connect to the Platform API:

1. Check your API key is configured: `gcb-runner config`
2. Verify your internet connection
3. Run connection test: Diagnostics → Test Platform API Connection

### Local Backend Not Connecting

For LM Studio or Ollama issues:

1. Ensure the server is running
2. Check the URL is correct (default: `localhost:1234` for LM Studio, `localhost:11434` for Ollama)
3. Run backend test: Diagnostics → Test Backend Connection

### Starting Fresh

If you encounter database issues or want to clear all test data:

```bash
gcb-runner reset-db
```

This removes all test runs and results. A new database will be created on your next test.

## Building Standalone Executables

To build standalone executables for distribution:

```bash
# Install development dependencies
pip install -e ".[dev]"

# Build for current platform
python scripts/build.py

# Output will be in dist/release/ with a manifest.json containing SHA256 hashes
```

The build script uses PyInstaller to create single-file executables that bundle Python and all dependencies.

## Development

```bash
# Clone the repository
git clone https://github.com/GospelAmbition/gcb-runner.git
cd gcb-runner

# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest -v

# Run linting
ruff check gcb_runner/

# Run type checking
mypy gcb_runner/

# Run security audit
pip-audit
```

## License

MIT License - see [LICENSE](LICENSE) for details.

## Links

- [Great Commission Benchmark](https://greatcommissionbenchmark.ai)
- [Download GCB Runner](https://greatcommissionbenchmark.ai/runner)
- [Documentation](https://greatcommissionbenchmark.ai/runner)
- [GitHub Issues](https://github.com/GospelAmbition/great-commission-benchmark/issues)
