# GCB Builder

CLI tool for building official Great Commission Benchmark versions.

## Overview

The GCB Builder is a command-line application for creating, curating, and publishing benchmark question sets. It's used by version builders to:

1. **Generate** candidate questions using AI assistance
2. **Curate** and review questions for quality and accuracy
3. **Lock** verified good questions to protect from deletion
4. **Develop** and validate judge prompts for reliable scoring
5. **Build** versioned question sets from locked + approved content
6. **Publish** locked versions for community use

## Installation

```bash
# From the gcb-builder directory
pip install -e .

# Or with development dependencies
pip install -e ".[dev]"
```

## Quick Start

```bash
# Initialize the database
gcb-builder init

# Start the interactive menu
gcb-builder

# Or use subcommands directly
gcb-builder categories  # List all 19 benchmark categories
gcb-builder status      # Show question bank status
```

## Project Structure

```
gcb-builder/
├── gcb_builder/           # Python package
│   ├── cli/               # CLI commands
│   ├── core/              # Categories, models, database
│   ├── generation/        # Question generation
│   ├── judging/           # Judge prompt development
│   ├── backends/          # LLM adapters
│   ├── versioning/        # Version building
│   └── export/            # Export utilities
├── prompts/               # Generation prompt templates
├── judge_prompts/         # Judge prompt templates
├── data/                  # Local database
└── tests/                 # Test suite
```

## Categories

The benchmark tests **19 categories** across three tiers:

| Tier | Focus | Categories | Weight |
|------|-------|------------|--------|
| **Tier 1** | Task Capability | 3.1-3.7 | 70% |
| **Tier 2** | Doctrinal Fidelity | 4.1-4.6 | 20% |
| **Tier 3** | Worldview Confession | 5.1-5.6 | 10% |

Run `gcb-builder categories` to see the full list.

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Type checking
mypy gcb_builder

# Linting
ruff check gcb_builder
```

## Configuration

Set environment variables or create a `.env` file:

```bash
# Optional: Custom database location
GCB_BUILDER_DB=/path/to/custom/database.db

# LLM API keys (when generation is implemented)
OPENROUTER_API_KEY=your-key-here
OPENAI_API_KEY=your-key-here
ANTHROPIC_API_KEY=your-key-here
```

## Related Documents

- [cli-builder-specifications.md](../benchmark/cli-builder-specifications.md) - Full specification
- [cli-builder-tech-stack.md](../benchmark/cli-builder-tech-stack.md) - Technology choices
- [benchmark-categories.md](../benchmark/benchmark-categories.md) - Category definitions
- [spec-export-schema-validation.md](../benchmark/spec-export-schema-validation.md) - Export format

## License

MIT
