# GCB Bulk Tester

**Leadership-only tool** for batch-testing all published models against the current benchmark version with automatic result submission.

This tool lives in the project repository and is **not** distributed publicly. It is exclusively for use by the GCB leadership team to periodically retest all models on the benchmark.

## Prerequisites

- Python 3.10+
- GCB Runner configured with API keys (`~/.gcb-runner/config.json`)
- **Admin-level API key** on the GCB platform
- OpenRouter API key (for testing models across all providers)

## Setup

```bash
# From the project root:

# 1. Install gcb-runner as an editable dependency
pip install -e ./gcb-runner

# 2. Install the bulk tester
pip install -e ./gcb-bulk-tester

# 3. Ensure gcb-runner is configured (if not already)
gcb-runner config
```

## Usage

### List available models

```bash
gcb-bulk-test models
```

### Dry run (see what would be tested)

```bash
gcb-bulk-test run --dry-run
```

### Run all models

```bash
gcb-bulk-test run --backend openrouter
```

### Resume (skip already-tested models)

```bash
gcb-bulk-test run --resume
```

### Exclude specific models

```bash
gcb-bulk-test run --exclude "model/to-skip,another/model"
```

### Test only specific models

```bash
gcb-bulk-test run --include "openai/gpt-4o,anthropic/claude-3.5-sonnet"
```

### Run without auto-submission

```bash
gcb-bulk-test run --no-submit
```

## How It Works

1. **Authenticates** via the platform API key and verifies admin access
2. **Fetches** the current benchmark version and all published models
3. **Applies** any include/exclude/resume filters
4. **Tests** each model sequentially using the gcb-runner engine
5. **Submits** results directly via `POST /api/runner/bulk-submit` (bypasses moderation)
6. **Prints** a summary table of all results

Results are published with `trust_tier="automated"` to distinguish them from community submissions.

## Configuration

The bulk tester reuses `~/.gcb-runner/config.json`. No separate configuration is needed.

Required keys in the config:
- **Platform API key**: Must have admin permissions
- **OpenRouter API key**: For testing models (recommended backend for bulk)
- **Judge model**: Defaults to `openai/gpt-oss-20b` (from gcb-runner config)
