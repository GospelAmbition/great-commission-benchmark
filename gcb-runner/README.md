# GCB Runner

A lightweight CLI tool for running the Great Commission Benchmark against AI models.

## Quick Start

```bash
# Install
pip install gcb-runner

# Configure your API keys
gcb-runner config

# Run the benchmark against a model
gcb-runner test --model gpt-4o --backend openrouter

# View results
gcb-runner results

# Generate an HTML report
gcb-runner report

# Export for platform submission
gcb-runner export
```

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
gcb-runner test --model gpt-4o --benchmark-version 2.0

# Add a custom system prompt
gcb-runner test --model gpt-4o --system-prompt "You are a helpful Christian assistant."

# Resume an interrupted test
gcb-runner test --model gpt-4o --resume
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

### Listing Benchmark Versions

```bash
gcb-runner versions
```

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
