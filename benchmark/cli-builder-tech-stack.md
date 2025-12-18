> **⚠️ DEPRECATED: This document is archived for historical reference.**
>
> **The GCB Builder CLI has been sunset.** Questions are now managed directly through the Platform's web-based CMS. See [feature-question-management.md](./feature-question-management.md) for current Platform architecture.

# GCB Version Builder CLI - Tech Stack

This document explains the technology choices for the GCB Version Builder CLI and the reasoning behind them.

---

## Overview

| Attribute | Value |
|-----------|-------|
| **Package Name** | `gcb-builder` |
| **Language** | Python 3.10+ |
| **Distribution** | PyPI (or private/internal) |
| **Target Users** | Version builders (power users, developers) |
| **Install Size** | Moderate (~15 MB with deps) |
| **Design Philosophy** | Feature-rich, exploratory, production-quality |

---

## Core Principle: Power User Tooling

The Version Builder is used by a small group of trusted contributors who build official benchmark versions. Unlike the Runner CLI (designed for community members), this tool can:

- Have more dependencies (users are developers)
- Include exploratory/power-user features
- Optimize for capability over simplicity

---

## Technology Choices

### Python (Language)

**Why Python:**

| Factor | Reasoning |
|--------|-----------|
| **Consistency** | Same language as Runner CLI (shared patterns) |
| **LLM ecosystem** | Best libraries for prompt engineering, API clients |
| **Data manipulation** | Excellent for question curation workflows |
| **Rapid iteration** | Quick to modify during benchmark development |

**Version:** Python 3.10+ (for modern type hints and match statements)

---

### Dependencies

```toml
[project]
dependencies = [
    "sqlalchemy>=2.0",      # Database ORM
    "rich>=13.0",           # Beautiful CLI output
    "questionary>=2.0",     # Interactive CLI prompts
    "httpx>=0.24",          # HTTP client for LLM APIs
    "pydantic>=2.0",        # Data validation
    "python-dotenv>=1.0",   # Environment variables
    "datasette>=0.64",      # Database explorer for curation
]
```

#### `sqlalchemy` - Database ORM

**Why SQLAlchemy with SQLite:**

The question bank is the core data structure. SQLAlchemy provides:

| Feature | Benefit |
|---------|---------|
| ORM | Clean Python classes for Question, Version, etc. |
| Migrations | Alembic integration for schema changes |
| Query builder | Complex filtering without raw SQL |
| Relationship handling | Question ↔ Version many-to-many |

**Why SQLite over PostgreSQL:**

| Consideration | Decision |
|---------------|----------|
| Portability | SQLite is a single file—easy to backup, share, version |
| Concurrency | Single user tool, no concurrent writes |
| Setup | No database server to install/configure |
| Datasette compatibility | Datasette works beautifully with SQLite |

#### `rich` - CLI Output

Same as Runner CLI. Beautiful tables, progress bars, syntax highlighting for prompt development.

#### `questionary` - Interactive Prompts

**Why questionary over InquirerPy/prompt_toolkit:**

| Feature | questionary | InquirerPy | prompt_toolkit |
|---------|-------------|------------|----------------|
| Simple API | ✓ Excellent | Good | Complex |
| Select menus | ✓ Built-in | ✓ | Manual |
| Checkboxes | ✓ Built-in | ✓ | Manual |
| Autocomplete | ✓ Built-in | ✓ | ✓ |
| Maintenance | Active | Active | Active |

Version building is an interactive workflow:
- "Select category for generation"
- "Choose which questions to approve"
- "Pick models for testing"

Questionary makes these flows elegant with minimal code.

#### `httpx` - HTTP Client

Same as Runner CLI. Async support for concurrent LLM calls during question generation and judge testing.

#### `pydantic` - Data Validation

**Extended use in Version Builder:**

```python
class QuestionCreate(BaseModel):
    content: str
    category_id: str
    tier: Literal[1, 2, 3]
    difficulty: Literal["easy", "medium", "hard"]
    expected_verdict: str
    expected_refusal_type: str | None
    tests_capability: bool
    tests_willingness: bool
    use_case_tags: list[str]
    
    @field_validator("content")
    def content_not_empty(cls, v):
        if len(v.strip()) < 20:
            raise ValueError("Question content too short")
        return v
```

Pydantic validates:
- LLM-generated questions (catch malformed output)
- User-edited questions (enforce constraints)
- Export format (ensure schema compliance)

#### `python-dotenv` - Environment Variables

API keys for multiple backends (OpenRouter, OpenAI, Anthropic).

#### `datasette` - Database Explorer

**Why Datasette:**

| Feature | Benefit for Version Building |
|---------|------------------------------|
| **SQL interface** | Run arbitrary queries against question bank |
| **Faceted browsing** | Filter by tier, category, status, locked |
| **Export** | CSV/JSON export for analysis |
| **Saved queries** | Store common curation queries |
| **Zero code** | Works immediately with any SQLite database |

**Why not build our own explorer:**

Building a web-based database explorer is significant work. Datasette is:
- Battle-tested (used by data journalists, researchers)
- Feature-rich (facets, plugins, JSON API)
- Actively maintained
- Perfect for SQLite

**How it's used:**

```bash
gcb-builder explore
# Opens http://localhost:8001 with full database access
```

Workflow: Use Datasette to *find* questions → Use CLI to *act* on them

---

### LLM Backend Architecture

```python
class LLMBackend(Protocol):
    async def complete(
        self, 
        messages: list[dict],
        model: str,
        system_prompt: str | None = None
    ) -> str: ...
    
    def list_models(self) -> list[str]: ...
```

**Supported Backends:**

| Backend | Use Case | API |
|---------|----------|-----|
| **OpenRouter** | Primary cloud option, 100+ models | Standard |
| **LM Studio** | Primary local option, GUI-based | OpenAI-compatible |
| **Ollama** | Alternative local, CLI-focused | Custom |
| **Direct API** | OpenAI, Anthropic direct | Native SDKs |

**Why multiple backends:**

Question generation and judge testing benefit from trying different models:
- Generate with GPT-4o, test judge with Claude
- Compare local model outputs to cloud models
- Use cheap models for bulk generation, expensive for quality passes

**Why LM Studio as primary local:**

| Feature | LM Studio | Ollama |
|---------|-----------|--------|
| GUI | ✓ Excellent | ✗ CLI only |
| Model browser | ✓ Built-in | Manual download |
| API | OpenAI-compatible | Custom |
| Resource monitoring | ✓ Visual | CLI |

Version builders spend hours interacting with models. LM Studio's GUI makes this pleasant.

---

## Architecture Decisions

### Module Structure

```
gcb_builder/
├── cli/                    # CLI commands (one file per menu section)
│   ├── main.py             # Entry point, main menu
│   ├── generate.py         # Question generation
│   ├── curate.py           # Curation workflow
│   ├── judge.py            # Judge prompt development
│   ├── version.py          # Version building
│   └── explore.py          # Datasette launcher
├── core/                   # Shared business logic
│   ├── models.py           # SQLAlchemy models
│   ├── database.py         # DB session management
│   ├── schemas.py          # Pydantic schemas
│   └── categories.py       # Category definitions
├── generation/             # Question generation
│   ├── prompts/            # Category-specific prompts
│   └── generator.py        # LLM orchestration
├── judging/                # Judge development
│   ├── prompts.py          # Judge prompt templates
│   └── tester.py           # Accuracy testing
├── backends/               # LLM adapters
├── versioning/             # Version assembly & export
└── export/                 # Export utilities
```

**Why this structure:**

| Principle | Implementation |
|-----------|----------------|
| **Separation of concerns** | CLI, business logic, infrastructure separated |
| **Feature-based organization** | `generation/`, `judging/`, `versioning/` |
| **Shared code in `core/`** | Models, schemas used everywhere |
| **One file per CLI section** | Easy to find command implementations |

### Database Schema

```python
class Question(Base):
    __tablename__ = "questions"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    content: Mapped[str]
    category_id: Mapped[str]
    tier: Mapped[int]
    difficulty: Mapped[str]
    status: Mapped[str]  # draft, review, approved, retired
    
    # Locking
    locked: Mapped[bool] = mapped_column(default=False)
    locked_at: Mapped[datetime | None]
    locked_by: Mapped[str | None]
    
    # Verdicts and classification
    expected_verdict: Mapped[str]
    expected_refusal_type: Mapped[str | None]
    
    # Capability vs willingness
    tests_capability: Mapped[bool]
    tests_willingness: Mapped[bool]
    
    # Metadata for filtering
    use_case_tags: Mapped[list[str]]
    audience_context: Mapped[str | None]
    ministry_type: Mapped[str | None]
    
    # Curation
    curator_notes: Mapped[str | None]
    created_at: Mapped[datetime]
    updated_at: Mapped[datetime]
```

**Key design decisions:**

| Decision | Reasoning |
|----------|-----------|
| **Soft delete via `status=retired`** | Preserve history, allow recovery |
| **Explicit `locked` flag** | Protected questions survive bulk operations |
| **Rich metadata** | Enables actionable filtering (Principle 7) |
| **`tests_capability` + `tests_willingness`** | Distinguish what each question measures (Principle 3) |

### Question Locking

**Why locking matters:**

During iterative development:
1. Generate 50 questions
2. Review → find 10 good ones
3. Regenerate 40 more (want to delete old drafts)
4. **Don't want to lose the 10 good ones!**

Locked questions:
- Cannot be deleted
- Survive bulk delete operations
- Are prioritized for version inclusion
- Represent "verified good" content

### Prompt Template System

Generation prompts are stored as Markdown files:

```
prompts/
├── tier1_use_cases/
│   ├── 3.1_missiological_research.md
│   ├── 3.2_evangelistic_material.md
│   └── ...
├── tier2_theological/
│   ├── 4.1_trinity.md
│   └── ...
└── tier3_worldview/
    ├── 5.1_nature_of_god.md
    └── ...
```

**Why Markdown files over database:**

| Approach | Pros | Cons |
|----------|------|------|
| Database | Queryable, version-controlled in DB | Hard to edit, no syntax highlighting |
| Markdown files | Easy to edit, git-versioned, IDE support | Not queryable |

Prompts are edited frequently during development. Markdown files with IDE syntax highlighting wins.

### Judge Prompt Development

Judge prompts evaluate AI responses and classify them into verdict categories. See [cli-builder-specifications.md](./cli-builder-specifications.md#judge-prompts) for complete judge prompt definitions including:

- `TIER1_TASK_JUDGE` — Evaluates task completion (ACCEPTED / COMPROMISED / REFUSED)
- `TIER2_DOCTRINE_JUDGE` — Evaluates doctrinal fidelity (LOYAL / COMPROMISED / DISLOYAL)
- `TIER3_WORLDVIEW_JUDGE` — Evaluates worldview confession (AFFIRMED / HEDGED / DENIED)

**Judge testing workflow:**

1. Create test cases (question + known-good response + expected verdict)
2. Run judge prompt against test cases
3. Measure accuracy (does judge classify correctly?)
4. Iterate on prompt wording until accuracy is high
5. Lock judge prompt for version

---

## Export & Bundle Compilation

### JSON Export Format

```json
{
  "format_version": "2.0",
  "benchmark_version": "3.0",
  "locked_at": "2025-01-15T14:30:00Z",
  "questions": [
    {
      "id": 1,
      "content": "...",
      "tier": 1,
      "category": "3.2",
      "expected_verdict": "ACCEPTED",
      "expected_refusal_type": null,
      "tests_capability": true,
      "tests_willingness": true,
      "use_case_tags": ["chatbot", "content_generation"],
      "audience_context": "secular_western",
      "ministry_type": "evangelism"
    }
  ],
  "judge_prompts": {
    "tier1": "...",
    "tier2": "...",
    "tier3": "..."
  },
  "scoring": {
    "tier1_weight": 0.70,
    "tier2_weight": 0.20,
    "tier3_weight": 0.10
  }
}
```

### Bundle Compilation

For CLI distribution, JSON is compiled into Python modules:

```python
# Compress and encode
json_bytes = json.dumps(data).encode()
compressed = zlib.compress(json_bytes, level=9)
encoded = base64.b64encode(compressed).decode()

# Generate bundle.py
bundle_code = f'''
_BUNDLE_DATA = """
{encoded}
"""

def _decode_bundle():
    compressed = base64.b64decode(_BUNDLE_DATA.strip())
    json_bytes = zlib.decompress(compressed)
    return json.loads(json_bytes)
'''
```

**Why this approach:**

| Goal | How Achieved |
|------|--------------|
| Offline capability | Questions embedded in CLI package |
| Version stability | Once compiled, bundle is immutable |
| Light obfuscation | Not trivially readable (honest about limits) |
| Simple distribution | Single `pip install` includes everything |

---

## Differences from Runner CLI

| Aspect | Runner CLI | Version Builder CLI |
|--------|------------|---------------------|
| **Users** | Community (non-devs) | Power users (devs) |
| **Dependencies** | Minimal (6) | More allowed (7) |
| **Datasette** | ✗ | ✓ |
| **Interactive prompts** | Basic (typer) | Rich (questionary) |
| **Database complexity** | Simple (2 tables) | Complex (5+ tables) |
| **Prompt templates** | Embedded in bundles | Editable Markdown files |
| **Primary purpose** | Run tests | Build tests |

---

## What We Intentionally Avoided

| Technology | Why Avoided |
|------------|-------------|
| **Django** | Overkill for CLI; no web framework needed |
| **FastAPI** | No REST API to serve |
| **Celery** | No background job queue needed |
| **Redis** | No caching layer needed |
| **Docker** | Single-user tool, runs locally |
| **Cloud database** | Portability matters more than scale |

---

## Trade-offs Acknowledged

### SQLite vs PostgreSQL

**Trade-off:** No concurrent access, limited to single user.

**Why acceptable:**
- Version building is inherently single-user
- Portability (single file) outweighs concurrency needs
- Datasette works best with SQLite anyway

### Datasette Dependency

**Trade-off:** Adds ~10 transitive dependencies.

**Why acceptable:**
- Target users are developers (can handle deps)
- Massive productivity boost for curation
- Alternative would be building our own explorer

### Markdown Prompts vs Database

**Trade-off:** Prompts not queryable, separate from questions.

**Why acceptable:**
- Prompts change slowly, questions change constantly
- IDE editing experience far superior
- Git versioning for prompts is valuable

---

## Security Considerations

| Concern | Approach |
|---------|----------|
| API keys | Stored in environment variables or `.env` |
| Question bank | Local SQLite file, user controls access |
| Published versions | Checksums for integrity verification |
| Datasette | Binds to localhost only |

---

## Future Considerations

### If We Need Team Collaboration

Currently single-user. If multiple version builders need to collaborate:

| Option | Complexity | Benefit |
|--------|------------|---------|
| Git sync of SQLite | Low | Version control for question bank |
| Shared PostgreSQL | Medium | Real-time collaboration |
| Web-based builder | High | Full multi-user support |

We'd likely start with Git sync before building a web tool.

### If Question Volume Grows Significantly

Current design handles ~1000s of questions easily. At 10,000+:
- Consider PostgreSQL for query performance
- Add indexing on frequently-filtered columns
- Potentially split into category-specific databases

### Potential Plugin System

For custom generation prompts or backends:
```python
# Future: plugin discovery
gcb-builder plugins install my-custom-backend
```

Not planned currently—keep it simple until needed.

---

## Summary

The GCB Version Builder CLI is **power-user tooling**:

- **Python** for consistency with Runner CLI and LLM ecosystem
- **SQLAlchemy + SQLite** for portable, queryable question bank
- **Questionary** for rich interactive workflows
- **Datasette** for SQL exploration (the killer feature)
- **Markdown prompts** for easy editing with IDE support
- **Bundle compilation** to feed the Runner CLI

Every choice optimizes for: *a version builder can efficiently create, curate, and publish benchmark versions through an iterative workflow.*
