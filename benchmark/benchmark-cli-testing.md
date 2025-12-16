---

# GCB Runner CLI

## Purpose

A lightweight Python CLI for **community members** who want to:

1. Run the official Great Commission Benchmark against an AI model
2. View their results locally
3. Export or upload results to the GCB platform

This tool is intentionally simple and focused. It does not include question generation, curation, or version building features—those are in the separate [GCB Version Builder CLI](benchmark-cli-version-builder.md).

---

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

# Export for platform submission
gcb-runner export --output results.json

# Or upload directly
gcb-runner upload
```

---

## Architecture Overview

```mermaid
flowchart LR
    subgraph input [Input]
        QS[Official Question Set]
        Config[API Configuration]
    end
    
    subgraph runner [Test Runner]
        CLI[CLI Interface]
        Runner[Test Executor]
        Judge[LLM Judge]
    end
    
    subgraph backends [Model Backends]
        OR[OpenRouter]
        LMStudio[LM Studio Local]
        Ollama[Ollama Local]
        Direct[Direct API]
    end
    
    subgraph output [Output]
        Local[Local Results DB]
        Export[JSON Export]
        Upload[Platform Upload]
    end
    
    QS --> Runner
    Config --> Runner
    CLI --> Runner
    Runner --> OR
    Runner --> LMStudio
    Runner --> Ollama
    Runner --> Direct
    OR --> Judge
    LMStudio --> Judge
    Ollama --> Judge
    Direct --> Judge
    Judge --> Local
    Local --> Export
    Local --> Upload
```

---

## Project Structure

```
gcb-runner/
├── gcb_runner/
│   ├── __init__.py
│   ├── cli.py              # Single-file CLI with all commands
│   ├── runner.py           # Test execution logic
│   ├── judge.py            # LLM-as-judge evaluation
│   ├── backends/           # LLM backend adapters
│   │   ├── __init__.py
│   │   ├── openrouter.py
│   │   ├── lmstudio.py
│   │   ├── ollama.py
│   │   └── direct.py
│   ├── versions/           # Embedded benchmark versions
│   │   ├── __init__.py     # Version registry
│   │   ├── loader.py       # Secure bundle loading
│   │   ├── v1_0/           # Benchmark V1.0
│   │   │   ├── __init__.py
│   │   │   └── bundle.py   # Compiled questions
│   │   ├── v2_0/           # Benchmark V2.0
│   │   │   └── ...
│   │   └── v3_0/           # Benchmark V3.0 (current)
│   │       └── ...
│   ├── questions.py        # Question set loader (uses versions/)
│   ├── results.py          # Results storage and display
│   └── export.py           # Export and upload
├── data/                   # Local data directory (user data only)
│   └── results.db          # SQLite results database
├── pyproject.toml
└── README.md
```

---

## CLI Commands

### `gcb-runner config`

Configure API keys and preferences:

```
$ gcb-runner config

╔═══════════════════════════════════════════════════════════════╗
║              Great Commission Benchmark - Runner               ║
╚═══════════════════════════════════════════════════════════════╝

? Configure which backend?
  ❯ OpenRouter (cloud - 100+ models)
    LM Studio (local - recommended)
    Ollama (local models)
    OpenAI Direct
    Anthropic Direct

? Enter your OpenRouter API key: ****************************

? Which model should judge responses?
  ❯ gpt-4o (recommended)
    claude-3.5-sonnet
    Custom

✓ Configuration saved to ~/.gcb-runner/config.json
```

---

### `gcb-runner test`

Run the benchmark against a model:

```
$ gcb-runner test --model gpt-4o --backend openrouter

╔═══════════════════════════════════════════════════════════════╗
║              Great Commission Benchmark - Runner               ║
╚═══════════════════════════════════════════════════════════════╝

Benchmark Version: V3.0 (Current)
CLI Version: 1.3.0

Loading questions from embedded bundle...
  ✓ 150 questions loaded (Tier 1: 105, Tier 2: 30, Tier 3: 15)
  ✓ Scoring weights: 70% Task / 20% Doctrine / 10% Worldview
  ✓ Bundle checksum verified

Testing: gpt-4o via OpenRouter
Judge: gpt-4o

Running benchmark...
  Tier 1 - Use Cases (70%)   ━━━━━━━━━━━━━━━━━━━━ 105/105
  Tier 2 - Theology (20%)    ━━━━━━━━━━━━━━━━━━━━ 30/30
  Tier 3 - Worldview (10%)   ━━━━━━━━━━━━━━━━━━━━ 15/15

═══════════════════════════════════════════════════════════════

                         RESULTS SUMMARY
                         
Model: gpt-4o
Benchmark: V3.0
Completed: 2025-01-15 14:32:01

┌─────────────────────────┬──────────┬──────────┬─────────┬────────┐
│ Tier                    │ Pass     │ Partial  │ Fail    │ Weight │
├─────────────────────────┼──────────┼──────────┼─────────┼────────┤
│ Tier 1: Use Cases       │ 79 (75%) │ 18 (17%) │ 8 (8%)  │  70%   │
│ Tier 2: Theology        │ 25 (83%) │ 3 (10%)  │ 2 (7%)  │  20%   │
│ Tier 3: Worldview       │ 13 (87%) │ 1 (7%)   │ 1 (6%)  │  10%   │
├─────────────────────────┼──────────┼──────────┼─────────┼────────┤
│ OVERALL (weighted)      │ 117 (78%)│ 22 (15%) │ 11 (7%) │  100%  │
└─────────────────────────┴──────────┴──────────┴─────────┴────────┘

Scoring breakdown:
  Tier 1: 75% × 0.70 = 52.5
  Tier 2: 83% × 0.20 = 16.6
  Tier 3: 87% × 0.10 =  8.7
  ─────────────────────────
  GCB Score: 77.8 → 78

Results saved. Run 'gcb-runner export' to submit to the platform.
```

**Options:**

```
gcb-runner test [OPTIONS]

Options:
  --model TEXT              Model identifier (e.g., gpt-4o, claude-3.5-sonnet)
  --backend TEXT            Backend: openrouter, lmstudio, ollama, openai, anthropic
  --benchmark-version TEXT  Benchmark version to run (default: latest)
  --system-prompt TEXT      Optional system prompt to prepend
  --judge-model TEXT        Model to use for judging (default: gpt-4o)
  --output TEXT             Save detailed results to JSON file
  --resume                  Resume an interrupted test run
```

**Examples:**

```bash
# Run latest benchmark version (recommended)
gcb-runner test --model gpt-4o --backend openrouter

# Run specific benchmark version
gcb-runner test --model gpt-4o --benchmark-version 2.0

# List available benchmark versions
gcb-runner versions
```

---

### `gcb-runner results`

View past test results:

```
$ gcb-runner results

Recent Test Runs:
┌────┬────────────────────┬─────────┬─────────────────────┬───────┬────────┐
│ ID │ Model              │ Version │ Date                │ Score │ Status │
├────┼────────────────────┼─────────┼─────────────────────┼───────┼────────┤
│ 3  │ gpt-4o             │ V3.0    │ 2025-01-15 14:32    │ 82.0  │ ✓ Done │
│ 2  │ claude-3.5-sonnet  │ V3.0    │ 2025-01-14 09:15    │ 78.5  │ ✓ Done │
│ 1  │ llama3.2:70b       │ V2.0    │ 2025-01-13 16:45    │ 65.0  │ ✓ Done │
└────┴────────────────────┴─────────┴─────────────────────┴───────┴────────┘

⚠️  Note: Test #1 used an older benchmark version (V2.0).
    Scores from different versions are not directly comparable.

? View details for run: 3

═══════════════════════════════════════════════════════════════

                    Test Run #3 - gpt-4o
                    
? Filter by:
  ❯ Show all responses
    Show failures only
    Show by category
    Show by tier

[Detailed response view with question, response, and verdict]
```

---

### `gcb-runner export`

Export results to JSON for platform submission:

```
$ gcb-runner export --run 3 --output gpt4o-results.json

Exporting test run #3...
  ✓ Exported to gpt4o-results.json

File ready for upload at https://gcb.example.com/submit
```

**Export Format:**

```json
{
  "format_version": "1.0",
  "test_run": {
    "id": "local-3",
    "model": "gpt-4o",
    "backend": "openrouter",
    "benchmark_version": "3.0",
    "judge_model": "gpt-4o",
    "completed_at": "2025-01-15T14:32:01Z"
  },
  "summary": {
    "total_questions": 150,
    "score": 78.0,
    "scoring_weights": {
      "tier1": 0.70,
      "tier2": 0.20,
      "tier3": 0.10
    },
    "tier_scores": {
      "tier1": { "raw": 75.0, "weighted": 52.5, "questions": 105 },
      "tier2": { "raw": 83.0, "weighted": 16.6, "questions": 30 },
      "tier3": { "raw": 87.0, "weighted": 8.7, "questions": 15 }
    },
    "verdict_counts": {
      "pass": 117,
      "partial": 22,
      "fail": 11
    }
  },
  "responses": [
    {
      "question_id": 1,
      "tier": 1,
      "response": "...",
      "verdict": "ACCEPTED",
      "judge_reasoning": "..."
    }
  ],
  "metadata": {
    "cli_version": "1.3.0",
    "benchmark_version": "3.0",
    "benchmark_checksum": "sha256:abc123...",
    "timestamp": "2025-01-15T14:35:00Z"
  }
}
```

**Version Fields Explained:**

| Field | Purpose |
|-------|---------|
| `test_run.benchmark_version` | Which benchmark questions were used |
| `metadata.cli_version` | Which CLI release ran the test |
| `metadata.benchmark_checksum` | Verify bundle integrity |

---

### `gcb-runner upload`

Upload results directly to the platform:

```
$ gcb-runner upload --run 3

? You haven't linked your GCB account. Link now? [Y/n]

Opening browser for authentication...
  ✓ Account linked: user@example.com

Uploading test run #3...
  ✓ Uploaded successfully

View your results at: https://gcb.example.com/results/abc123
```

---

## Core Components

### Question Set Loader

Loads embedded benchmark versions from compiled bundles:

```python
# gcb_runner/questions.py

from gcb_runner.versions.loader import VersionLoader

class QuestionSetLoader:
    def load(self, version: str = "latest") -> QuestionSet:
        """Load question set from embedded bundle."""
        return VersionLoader.load(version)
    
    def list_available(self) -> list[dict]:
        """List all available benchmark versions."""
        return VersionLoader.list_versions()
    
    def get_current_version(self) -> str:
        """Get the current (recommended) benchmark version."""
        return VersionLoader.CURRENT_VERSION
```

Questions are embedded in the CLI package itself — no network access required. See [Benchmark Version System](#benchmark-version-system) for implementation details.

---

### Test Runner

Executes questions against the target model:

```python
# gcb_runner/runner.py

class TestRunner:
    def __init__(
        self,
        backend: LLMBackend,
        judge: Judge,
        model: str,
        system_prompt: str | None = None
    ):
        self.backend = backend
        self.judge = judge
        self.model = model
        self.system_prompt = system_prompt
    
    async def run(self, question_set: QuestionSet) -> TestRun:
        """Run all questions and return results."""
        test_run = TestRun(
            model=self.model,
            question_set_version=question_set.version,
            started_at=datetime.now()
        )
        
        for question in question_set.questions:
            # Get model response
            response = await self.backend.complete(
                messages=[{"role": "user", "content": question.content}],
                model=self.model,
                system_prompt=self.system_prompt
            )
            
            # Judge the response
            verdict = await self.judge.evaluate(question, response)
            
            test_run.responses.append(Response(
                question_id=question.id,
                response=response,
                verdict=verdict.verdict,
                judge_reasoning=verdict.reasoning
            ))
        
        test_run.completed_at = datetime.now()
        return test_run
```

---

### LLM Judge

Evaluates responses using official judge prompts:

```python
# gcb_runner/judge.py

class Judge:
    def __init__(self, backend: LLMBackend, model: str):
        self.backend = backend
        self.model = model
    
    async def evaluate(self, question: Question, response: str) -> Verdict:
        """Evaluate a response using the appropriate judge prompt."""
        prompt = self._get_judge_prompt(question.tier)
        
        judge_response = await self.backend.complete(
            messages=[{
                "role": "user",
                "content": prompt.format(
                    question=question.content,
                    response=response
                )
            }],
            model=self.model
        )
        
        return self._parse_verdict(judge_response)
```

**Classification Framework** (from [platform-testing-methodology.md](platform-testing-methodology.md)):

| Tier | Weight | Pass | Partial | Fail |
|------|--------|------|---------|------|
| Tier 1 (Tasks) | **70%** | ACCEPTED | COMPROMISED | REFUSED |
| Tier 2 (Doctrine) | **20%** | LOYAL | COMPROMISED | DISLOYAL |
| Tier 3 (Worldview) | **10%** | AFFIRMED | HEDGED | DENIED |

**Scoring Formula:** `GCB Score = (Tier1 × 0.70) + (Tier2 × 0.20) + (Tier3 × 0.10)`

See [benchmark-scoring.md](./benchmark-scoring.md) for complete scoring methodology.

---

### LLM Backend Abstraction

```python
# gcb_runner/backends/__init__.py

class LLMBackend(Protocol):
    async def complete(
        self, 
        messages: list[dict],
        model: str,
        system_prompt: str | None = None
    ) -> str: ...

def get_backend(name: str, api_key: str) -> LLMBackend:
    """Factory function to get configured backend."""
    match name:
        case "openrouter":
            return OpenRouterBackend(api_key)
        case "lmstudio":
            return LMStudioBackend()
        case "ollama":
            return OllamaBackend()
        case "openai":
            return OpenAIBackend(api_key)
        case "anthropic":
            return AnthropicBackend(api_key)
        case _:
            raise ValueError(f"Unknown backend: {name}")
```

**Local LLM Options:**

| Backend | Description | API |
|---------|-------------|-----|
| **LM Studio** | Primary local option. User-friendly GUI with OpenAI-compatible API. | `http://localhost:1234/v1` |
| **Ollama** | CLI-focused local runner. Good for automation. | `http://localhost:11434` |

LM Studio is recommended for most users because:
- Easy model discovery and download
- Visual interface for model management
- OpenAI-compatible API (works with existing code)
- Built-in chat interface for testing

---

### Results Storage

Simple SQLite database for local results:

```python
# gcb_runner/results.py

class TestRun(Base):
    id: int
    model: str
    backend: str
    question_set_version: str
    judge_model: str
    system_prompt: str | None
    score: float
    started_at: datetime
    completed_at: datetime

class Response(Base):
    id: int
    test_run_id: int
    question_id: int
    response: str
    verdict: str
    judge_reasoning: str
```

---

## Dependencies

```toml
[project]
name = "gcb-runner"
version = "0.1.0"
description = "Run Great Commission Benchmark tests against AI models"
dependencies = [
    "httpx>=0.24",          # HTTP client for LLM APIs
    "rich>=13.0",           # Beautiful CLI output
    "typer>=0.9",           # CLI framework
    "pydantic>=2.0",        # Data validation
    "sqlalchemy>=2.0",      # Local results storage
    "python-dotenv>=1.0",   # Environment variables
]

[project.scripts]
gcb-runner = "gcb_runner.cli:main"
```

---

## Configuration

Configuration stored in `~/.gcb-runner/config.json`:

```json
{
  "backends": {
    "openrouter": {
      "api_key": "sk-or-..."
    },
    "openai": {
      "api_key": "sk-..."
    }
  },
  "defaults": {
    "backend": "openrouter",
    "judge_model": "gpt-4o"
  },
  "platform": {
    "url": "https://gcb.example.com",
    "token": "..."
  }
}
```

---

## Implementation Phases

### Phase 1: Core Runner

- Project structure and CLI skeleton
- **Version loader for embedded bundles**
- OpenRouter backend
- Basic test runner
- Console output

### Phase 2: Judge & Results

- LLM-as-judge implementation
- Official judge prompts (loaded from bundles)
- SQLite results storage
- Results display commands

### Phase 3: Export & Upload

- JSON export format (with version metadata)
- Platform API integration
- Direct upload command
- Account linking

### Phase 4: Local Models & Polish

- LM Studio backend for local models (primary)
- Ollama backend for local models
- Resume interrupted runs
- Progress persistence
- Better error handling
- **`gcb-runner versions` command**
- Documentation

### Phase 5: Version Management

- **Bundle compilation tooling** (in gcb-builder)
- **Multi-version CLI releases**
- Version selection UX
- Checksum verification

---

## Benchmark Version System

The GCB Runner includes **embedded benchmark versions** — question sets are compiled directly into the tool rather than fetched from a server. This provides:

- **Offline capability** — Run benchmarks without network access
- **Version stability** — Each CLI release has locked, immutable question sets
- **Light obfuscation** — Questions aren't sitting in plain text files
- **Simple UX** — Users just select which version to run

### Version Architecture

```
gcb-runner/
├── gcb_runner/
│   ├── versions/                    # Embedded benchmark versions
│   │   ├── __init__.py              # Version registry
│   │   ├── loader.py                # Secure loading logic
│   │   ├── v1_0/                    # Benchmark V1.0
│   │   │   ├── __init__.py
│   │   │   └── bundle.py            # Compiled question bundle
│   │   ├── v2_0/                    # Benchmark V2.0
│   │   │   ├── __init__.py
│   │   │   └── bundle.py
│   │   └── v3_0/                    # Benchmark V3.0 (latest)
│   │       ├── __init__.py
│   │       └── bundle.py
│   └── ...
```

### Version Selection UX

```
$ gcb-runner test --model gpt-4o

╔═══════════════════════════════════════════════════════════════╗
║              Great Commission Benchmark - Runner               ║
╚═══════════════════════════════════════════════════════════════╝

? Select benchmark version:
  ❯ V3.0 (Current - recommended)      150 questions
    V2.0 (Archived)                    150 questions
    V1.0 (Archived)                    120 questions

Using benchmark V3.0...
```

Or specify directly:

```bash
# Use latest (default)
gcb-runner test --model gpt-4o

# Use specific version
gcb-runner test --model gpt-4o --benchmark-version 2.0

# List available versions
gcb-runner versions
```

### Version Listing Command

```
$ gcb-runner versions

╔═══════════════════════════════════════════════════════════════╗
║           Available Benchmark Versions                         ║
╚═══════════════════════════════════════════════════════════════╝

┌─────────┬────────────┬────────────┬────────────────────────────┐
│ Version │ Status     │ Questions  │ Released                   │
├─────────┼────────────┼────────────┼────────────────────────────┤
│ V3.0    │ ⭐ Current │ 150        │ December 2025              │
│ V2.0    │ Archived   │ 150        │ June 2025                  │
│ V1.0    │ Archived   │ 120        │ January 2025               │
└─────────┴────────────┴────────────┴────────────────────────────┘

Question distribution follows 70/20/10 weighting:
  • Tier 1 (Task Capability): 70% - e.g., 105 questions in V3.0
  • Tier 2 (Doctrinal Fidelity): 20% - e.g., 30 questions in V3.0
  • Tier 3 (Worldview Confession): 10% - e.g., 15 questions in V3.0

Use --benchmark-version to select a specific version.
```

---

## Question Bundle Format

### Compiled Bundle Structure

Questions are compiled into Python modules with light obfuscation:

```python
# gcb_runner/versions/v3_0/bundle.py

"""
GCB Benchmark V3.0 - Question Bundle
Generated: 2025-12-01T00:00:00Z
Checksum: sha256:abc123...

DO NOT MODIFY - This file is auto-generated by gcb-builder.
"""

import base64
import zlib
from typing import Any

# Metadata (visible)
VERSION = "3.0"
RELEASE_DATE = "2025-12-01"
QUESTION_COUNT = 150
TIER_DISTRIBUTION = {"tier1": 105, "tier2": 30, "tier3": 15}
CHECKSUM = "sha256:abc123def456..."

# Question data (compressed + encoded)
# This isn't security - determined users can decode it.
# It's just friction to prevent casual browsing.
_BUNDLE_DATA = """
eJzVWNtu2zgQfV9g/4HwS+ILJUq2nTgI0KJFs0WLLrZAi32gKMoWI4kCScV2
... (base64 encoded, zlib compressed JSON) ...
"""

def _decode_bundle() -> dict[str, Any]:
    """Decode the question bundle. Internal use only."""
    compressed = base64.b64decode(_BUNDLE_DATA)
    json_bytes = zlib.decompress(compressed)
    return json.loads(json_bytes)

# Judge prompts (also embedded)
_JUDGE_PROMPTS = """
eJzVWNtu2zgQfV9g/4HwS+ILJUq2nTgI0KJFs0WLLrZAi32gKMoWI4kCScV2
... (base64 encoded judge prompts) ...
"""
```

### Why This Approach?

| Approach | Pros | Cons |
|----------|------|------|
| **Plain JSON files** | Easy to inspect/debug | Trivially readable |
| **Encrypted bundles** | "Secure" | Key distribution problem; false security |
| **Compiled + compressed** | Raises friction; honest about limits | Determined users can still decode |
| **Server fetch only** | Central control | Requires network; single point of failure |

We chose **compiled + compressed** because:

1. **Honest security model** — We're not claiming the questions are secret, just not trivially browsable
2. **Works offline** — No network dependency for running benchmarks
3. **Version stability** — Once released, a CLI version always has the same questions
4. **Simple distribution** — Single `pip install` includes everything

### What This Protects Against

✅ **Casual browsing** — `cat bundle.py` doesn't show questions  
✅ **Accidental exposure** — Questions won't appear in IDE file trees  
✅ **Simple extraction** — Requires writing code to decode  

### What This Does NOT Protect Against

❌ **Determined reverse engineering** — Anyone who wants to can decode it  
❌ **Memory inspection** — Questions exist in memory during runs  
❌ **Response logging** — Users can log the prompts sent to LLMs  

**This is intentional.** The goal isn't DRM — it's preventing the questions from being obviously visible while maintaining an honest, open-source approach.

---

## Version Loader Implementation

```python
# gcb_runner/versions/loader.py

from importlib import import_module
from typing import Protocol
import hashlib

class QuestionSet(Protocol):
    version: str
    questions: list[dict]
    judge_prompts: dict[str, str]
    scoring_config: dict

class VersionLoader:
    """Load embedded benchmark versions."""
    
    AVAILABLE_VERSIONS = {
        "1.0": "gcb_runner.versions.v1_0",
        "2.0": "gcb_runner.versions.v2_0",
        "3.0": "gcb_runner.versions.v3_0",
    }
    
    CURRENT_VERSION = "3.0"
    
    @classmethod
    def list_versions(cls) -> list[dict]:
        """List all available benchmark versions."""
        versions = []
        for version_id, module_path in cls.AVAILABLE_VERSIONS.items():
            module = import_module(f"{module_path}.bundle")
            versions.append({
                "version": version_id,
                "release_date": module.RELEASE_DATE,
                "question_count": module.QUESTION_COUNT,
                "tier_distribution": module.TIER_DISTRIBUTION,
                "is_current": version_id == cls.CURRENT_VERSION,
            })
        return sorted(versions, key=lambda v: v["version"], reverse=True)
    
    @classmethod
    def load(cls, version: str = "latest") -> QuestionSet:
        """Load a benchmark version."""
        if version == "latest":
            version = cls.CURRENT_VERSION
        
        if version not in cls.AVAILABLE_VERSIONS:
            available = ", ".join(cls.AVAILABLE_VERSIONS.keys())
            raise ValueError(f"Unknown version: {version}. Available: {available}")
        
        module_path = cls.AVAILABLE_VERSIONS[version]
        bundle = import_module(f"{module_path}.bundle")
        
        # Decode and verify
        data = bundle._decode_bundle()
        
        # Verify checksum
        computed = hashlib.sha256(
            json.dumps(data, sort_keys=True).encode()
        ).hexdigest()
        
        if f"sha256:{computed}" != bundle.CHECKSUM:
            raise RuntimeError("Bundle checksum mismatch - data may be corrupted")
        
        return QuestionSet(
            version=version,
            questions=data["questions"],
            judge_prompts=data["judge_prompts"],
            scoring_config=data["scoring"]
        )
```

---

## CLI Release Workflow

### How Versions Get Into the CLI

```
┌─────────────────────────────────────────────────────────────────┐
│                    VERSION RELEASE WORKFLOW                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. VERSION BUILDER                                              │
│     └─ gcb-builder exports locked version → gcb-v3.0.json       │
│                                                                  │
│  2. COMPILE BUNDLE                                               │
│     └─ gcb-compile-bundle gcb-v3.0.json → v3_0/bundle.py        │
│        (Compresses, encodes, generates checksums)                │
│                                                                  │
│  3. ADD TO RUNNER                                                │
│     └─ Add v3_0/ to gcb_runner/versions/                        │
│     └─ Update AVAILABLE_VERSIONS registry                        │
│     └─ Set CURRENT_VERSION = "3.0"                              │
│                                                                  │
│  4. RELEASE CLI                                                  │
│     └─ Bump gcb-runner version (e.g., 1.3.0)                    │
│     └─ Publish to PyPI                                          │
│                                                                  │
│  5. USERS UPDATE                                                 │
│     └─ pip install --upgrade gcb-runner                         │
│     └─ New benchmark versions now available                      │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Bundle Compilation Tool

A helper script (can be in gcb-builder or separate) compiles JSON exports:

```bash
# In the gcb-builder project, after publishing a version:
gcb-compile-bundle gcb-v3.0.json --output ../gcb-runner/gcb_runner/versions/v3_0/

# Creates:
#   v3_0/__init__.py
#   v3_0/bundle.py (compiled question bundle)
```

```python
# compile_bundle.py (standalone script or part of gcb-builder)

import json
import zlib
import base64
import hashlib
from pathlib import Path
from datetime import datetime

def compile_bundle(input_path: str, output_dir: str) -> None:
    """Compile a JSON question set export into a Python bundle."""
    
    with open(input_path) as f:
        data = json.load(f)
    
    version = data["benchmark_version"]
    version_slug = f"v{version.replace('.', '_')}"
    
    # Compute checksum
    checksum = hashlib.sha256(
        json.dumps(data, sort_keys=True).encode()
    ).hexdigest()
    
    # Compress and encode
    json_bytes = json.dumps(data).encode()
    compressed = zlib.compress(json_bytes, level=9)
    encoded = base64.b64encode(compressed).decode()
    
    # Generate bundle.py
    bundle_code = f'''"""
GCB Benchmark V{version} - Question Bundle
Generated: {datetime.utcnow().isoformat()}Z
Checksum: sha256:{checksum}

DO NOT MODIFY - This file is auto-generated by gcb-compile-bundle.
"""

import base64
import zlib
import json
from typing import Any

VERSION = "{version}"
RELEASE_DATE = "{data.get('locked_at', '')[:10]}"
QUESTION_COUNT = {len(data['questions'])}
TIER_DISTRIBUTION = {data['metadata']['tier_counts']}
CHECKSUM = "sha256:{checksum}"

_BUNDLE_DATA = """
{encoded}
"""

def _decode_bundle() -> dict[str, Any]:
    """Decode the question bundle. Internal use only."""
    compressed = base64.b64decode(_BUNDLE_DATA.strip())
    json_bytes = zlib.decompress(compressed)
    return json.loads(json_bytes)
'''
    
    # Write files
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    (output_path / "__init__.py").write_text(
        f'"""GCB Benchmark V{version}"""\n'
    )
    (output_path / "bundle.py").write_text(bundle_code)
    
    print(f"✓ Compiled V{version} to {output_path}")
    print(f"  Questions: {len(data['questions'])}")
    print(f"  Checksum: sha256:{checksum[:16]}...")
```

---

## Version Compatibility

### CLI Version vs Benchmark Version

| Concept | Example | What It Means |
|---------|---------|---------------|
| **CLI Version** | `gcb-runner 1.3.0` | The software release |
| **Benchmark Version** | `V3.0` | The question set being tested |

A single CLI release may include multiple benchmark versions:

```
gcb-runner 1.3.0
├── Benchmark V1.0 (archived)
├── Benchmark V2.0 (archived)
└── Benchmark V3.0 (current)
```

### Backward Compatibility

- New CLI versions **add** benchmark versions, never remove them
- Users can always run older benchmark versions for comparison
- Results always record both CLI version and benchmark version used

### Results Export Format

```json
{
  "format_version": "1.0",
  "test_run": {
    "id": "local-3",
    "model": "gpt-4o",
    "backend": "openrouter",
    "benchmark_version": "3.0",        // ← Benchmark version
    "cli_version": "1.3.0",            // ← CLI version
    "judge_model": "gpt-4o",
    "completed_at": "2025-01-15T14:32:01Z"
  },
  // ... rest of results
}
```

---

## Differences from Version Builder CLI

| Feature | GCB Runner | GCB Version Builder |
|---------|------------|---------------------|
| Question Generation | ❌ | ✓ |
| Question Curation | ❌ | ✓ |
| Judge Development | ❌ | ✓ |
| Version Building | ❌ | ✓ |
| Run Benchmarks | ✓ | Limited testing only |
| Platform Upload | ✓ | ❌ |
| Target Users | Community | Version Builders |
| Complexity | Simple | Full-featured |
