# GCB Runner

A lightweight CLI tool for running the Great Commission Benchmark against AI models.

## Quick Start

```bash
# Install
pip install gcb-runner

# Launch the interactive menu (default behavior)
gcb-runner

# Show command reference
gcb-runner help

# Or use individual commands directly:
gcb-runner config                                    # Configure API keys
gcb-runner test --model gpt-4o --backend openrouter  # Run benchmark
gcb-runner results                                   # View results
gcb-runner report                                    # Generate HTML report
gcb-runner export                                    # Export for submission
```

## Interactive Menu

Running `gcb-runner` launches an interactive menu (this is the default behavior). The menu provides:

- **🚀 Setup Wizard** - Guided 4-step configuration for first-time users
- **🧪 Run Benchmark Test** - Interactive test runner with model and version selection
- **📊 View Results** - Browse test runs, launch dashboard, generate reports
- **⚙️ Configuration** - Manage API keys, backends, and preferences
- **🔧 Diagnostics** - Test connections, verify API access, troubleshoot issues
- **❓ Help & Documentation** - Quick start guide, scoring info, and more

The menu is perfect for users who prefer a guided experience over command-line flags.

### Diagnostics & Troubleshooting

The diagnostics menu helps verify your setup is working correctly:

```bash
gcb-runner
# Select [5] 🔧 Diagnostics & Connection Test
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

### From PyPI (Recommended)

```bash
pip install gcb-runner
```

### From Source

```bash
git clone https://github.com/great-commission-benchmark/gcb-runner
cd gcb-runner
pip install -e .
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
```

**Tip:** Use the interactive menu for guided version selection:
```bash
gcb-runner
# Select [2] 🧪 Run Benchmark Test
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
```

### Exporting & Uploading

```bash
# Export results to JSON
gcb-runner export --run 3 --output results.json

# Upload to the platform (requires moderator verification)
gcb-runner upload --run 3
```

#### Web Dashboard Upload

Alternatively, you can upload your exported results via the web dashboard:

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

The web upload provides the same functionality as `gcb-runner upload` but with a visual interface and immediate validation feedback.

### Listing Benchmark Versions

```bash
# List all available benchmark versions
gcb-runner versions

# Or use the interactive menu for more details
gcb-runner
# Select [5] 🔧 Diagnostics → [4] List Available Versions
```

This shows available versions with their status, question counts, and release dates.

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

| Tier | Pass | Partial | Fail |
|------|------|---------|------|
| Tier 1 | ACCEPTED | COMPROMISED | REFUSED |
| Tier 2 | LOYAL | COMPROMISED | DISLOYAL |
| Tier 3 | AFFIRMED | HEDGED | DENIED |

## Data Storage

- **Configuration**: `~/.gcb-runner/config.json`
- **Results database**: `~/.gcb-runner/data/results.db`
- **Question cache**: `~/.gcb-runner/cache/`

## Troubleshooting

### "Resource not found" Error

This error when running tests usually means:
- No benchmark version has been published yet
- The specified version doesn't exist

**Solution:** Run diagnostics to check available versions:
```bash
gcb-runner
# Select [5] 🔧 Diagnostics → [1] Run Full Diagnostics
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

## Development

```bash
# Clone the repository
git clone https://github.com/great-commission-benchmark/gcb-runner
cd gcb-runner

# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest -v

# Run linting
ruff check gcb_runner/

# Run type checking
mypy gcb_runner/
```

## License

MIT License - see [LICENSE](LICENSE) for details.

## Links

- [Great Commission Benchmark](https://greatcommissionbenchmark.ai)
- [Documentation](https://greatcommissionbenchmark.ai/docs/runner)
- [GitHub Issues](https://github.com/great-commission-benchmark/gcb-runner/issues)
