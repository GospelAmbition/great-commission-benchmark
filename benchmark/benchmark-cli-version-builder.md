---
name: GCB Version Builder CLI
overview: A command-line Python application for building official Great Commission Benchmark versions. Supports AI-assisted question generation, curation, judge prompt development, and publishing versioned question sets.
todos:
  - id: foundation
    content: Create project structure, pyproject.toml, and core database models
    status: pending
  - id: categories
    content: Define all 19 categories from benchmark-vision.md as code constants
    status: pending
  - id: gen-prompts
    content: Create generation prompt templates for each category (Tier 1, 2, 3)
    status: pending
  - id: cli-skeleton
    content: Build CLI entry point with rich menus and basic navigation
    status: pending
  - id: llm-backends
    content: Implement OpenRouter, LM Studio, and Ollama backend adapters for generation
    status: pending
  - id: generator
    content: Build question generator that uses prompts + LLM to draft questions
    status: pending
  - id: judge-design
    content: Design and implement judge prompts for each tier/category
    status: pending
  - id: curation
    content: Build curation workflow with review, approve, retire states
    status: pending
  - id: versioning
    content: Implement question set versioning and locking for publication
    status: pending
  - id: export
    content: Build JSON export utility for question sets (platform publication)
    status: pending
---

# GCB Version Builder CLI

## Purpose

A self-contained Python CLI for **building official benchmark versions**. Version builders use this tool to create, curate, and publish the question sets that make up each release of the Great Commission Benchmark.

**Core workflow:**

1. **Generate** candidate questions using AI assistance
2. **Curate** and review questions for quality and accuracy
3. **Lock** verified good questions to protect from deletion during iteration
4. **Develop** and validate judge prompts for reliable scoring
5. **Build** versioned question sets from locked + approved content
6. **Publish** locked versions for community use

> **Note:** Community members who want to run benchmarks against models should use the separate [GCB Runner CLI](benchmark-cli-testing.md).

---

## Architecture Overview

```mermaid
flowchart TB
    subgraph gen [Question Generation]
        GenPrompts[Generation Prompts]
        GenLLM[LLM Drafting]
        GenReview[Human Review]
    end
    
    subgraph curate [Curation System]
        DB[(Question Bank)]
        Approved[Approved Questions]
        Locked[🔒 Locked Questions]
    end
    
    subgraph judge [Judge Development]
        JudgePrompts[Judge Prompts]
        JudgeTest[Judge Testing]
        Classification[Classification Framework]
    end
    
    subgraph version [Version Building]
        Builder[Version Builder]
        VersionLock[Lock Version]
        Publish[Publish]
    end
    
    subgraph llms [LLM Backends]
        Cloud[OpenRouter/Direct APIs]
        Local[LM Studio/Ollama]
    end
    
    GenPrompts --> GenLLM --> GenReview --> DB
    DB --> Approved --> Locked
    Locked --> Builder
    Approved --> Builder
    DB --> JudgePrompts
    JudgePrompts --> JudgeTest
    JudgeTest --> Classification
    GenLLM --> Cloud
    GenLLM --> Local
    Classification --> Builder
    Builder --> VersionLock --> Publish
    Publish --> Export[JSON Export]
```

---

## Project Structure

```
gcb-builder/
├── gcb_builder/
│   ├── __init__.py
│   ├── cli/                    # CLI interface
│   │   ├── __init__.py
│   │   ├── main.py             # Entry point with rich menus
│   │   ├── generate.py         # Question generation commands
│   │   ├── curate.py           # Curation commands
│   │   ├── judge.py            # Judge prompt development
│   │   └── version.py          # Version building commands
│   ├── core/                   # Shared business logic
│   │   ├── __init__.py
│   │   ├── models.py           # SQLAlchemy models
│   │   ├── database.py         # DB connection/session
│   │   ├── schemas.py          # Pydantic schemas
│   │   └── categories.py       # Category definitions from vision
│   ├── generation/             # Question generation
│   │   ├── __init__.py
│   │   ├── prompts/            # Category-specific generation prompts
│   │   └── generator.py        # LLM-based generator
│   ├── judging/                # Judge development
│   │   ├── __init__.py
│   │   ├── prompts.py          # Judge prompts for each tier
│   │   └── tester.py           # Test judge accuracy
│   ├── backends/               # LLM backend adapters
│   │   ├── __init__.py
│   │   ├── openrouter.py
│   │   ├── lmstudio.py
│   │   ├── ollama.py
│   │   └── direct_api.py
│   ├── versioning/             # Version building
│   │   ├── __init__.py
│   │   ├── builder.py          # Assemble questions into versions
│   │   ├── validator.py        # Pre-publish validation
│   │   └── publisher.py        # Lock and export
│   └── export/                 # Export utilities
│       ├── __init__.py
│       └── question_export.py  # Export for platform publication
├── prompts/                    # Generation prompt templates
│   ├── tier1_use_cases/
│   ├── tier2_theological/
│   └── tier3_worldview/
├── judge_prompts/              # Judge prompt templates
│   ├── tier1_task.md
│   ├── tier2_doctrine.md
│   └── tier3_worldview.md
├── data/                       # Local data directory
│   └── gcb_builder.db          # SQLite database
├── tests/
├── pyproject.toml
└── README.md
```

---

## Component 1: Question Generation System

### Category Definitions (from [benchmark-vision.md](benchmark-vision.md))

The system has built-in category definitions matching the vision document:

**Tier 1 - Use Case Categories (70% of questions, 70% of score weight):**

- 3.1 Missiological Research
- 3.2 Evangelistic Material Creation
- 3.3 Apologetic Purposes
- 3.4 Conversational AI Tools
- 3.5 Intercessory Prayer Purposes
- 3.6 Scripture Processing (vocabulary + passages)

**Tier 2 - Theological Minimums (20% of questions, 20% of score weight):**

- 4.1-4.6 (Exclusivity, Sin, Judgment, Lordship, Repentance, Discipleship)

**Tier 3 - Worldview Confession (10% of questions, 10% of score weight):**

- 5.1-5.6 (God's existence, Historical Jesus, Crucifixion, Resurrection, Sinfulness, Salvation)

**Why This Distribution?** Tier 1 dominates because it directly answers the user's primary question: *"Can I use this LLM for my ministry work?"* See [benchmark-scoring.md](./benchmark-scoring.md) for detailed rationale.

### Generation Prompts

For each category, we create specialized prompts that:

1. Explain the category and its purpose
2. Provide examples of good questions
3. Specify difficulty levels and expected failure modes
4. Guide the LLM to generate realistic test scenarios

Example prompt structure for Tier 1 Category 3.2 (Evangelistic Material Creation):

```markdown
# Evangelistic Material Creation - Question Generation

## Category Definition
Creating content intended to communicate, connect with, and persuade 
non-Christians of the truth of Christianity.

## Question Types to Generate
- Gospel presentation requests for specific audiences
- Evangelistic tract drafting
- Conversion testimony crafting
- Outreach material for cultural contexts

## Difficulty Levels
- EASY: General gospel explanation requests
- MEDIUM: Persuasive content with specific claims
- HARD: Direct calls to conversion, exclusivist claims

## Generate 5 questions at each difficulty level...
```

---

## Component 2: Database Schema

Using SQLite for local version building:

```python
# gcb_builder/core/models.py

class Question(Base):
    id: int
    content: str                    # The actual question/prompt
    category: str                   # e.g., "3.2_evangelistic"
    tier: int                       # 1, 2, or 3
    difficulty: str                 # easy, medium, hard
    expected_verdict: str           # What we expect good LLMs to do
    notes: str                      # Curator notes
    status: str                     # draft, review, approved, retired
    locked: bool                    # Protected from deletion/modification
    locked_at: datetime | None      # When it was locked
    locked_by: str | None           # Who locked it
    created_at: datetime
    updated_at: datetime

class BenchmarkVersion(Base):
    """A complete, publishable benchmark version."""
    id: int
    version: str                    # e.g., "1.0.0"
    name: str
    description: str
    status: str                     # building, validating, locked, published
    created_at: datetime
    locked_at: datetime | None
    published_at: datetime | None

class VersionQuestion(Base):
    """Links questions to a specific version."""
    version_id: int
    question_id: int
    order: int                      # Order within the version

class JudgeTestCase(Base):
    """Known-answer test cases for validating judge prompts."""
    id: int
    question_id: int
    sample_response: str            # Example LLM response
    expected_verdict: str           # What verdict judge should give
    verdict_reasoning: str          # Why this is the correct verdict
```

### Question Locking

Questions go through many iterations during development—generated, reviewed, edited, deleted, regenerated. Once a question is verified as good, it should be **locked** to prevent accidental loss.

**Question lifecycle with locking:**

```
┌─────────────────────────────────────────────────────────────────┐
│                    QUESTION LIFECYCLE                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   DRAFT ──────► REVIEW ──────► APPROVED ──────► LOCKED 🔒       │
│     │             │               │                              │
│     ▼             ▼               ▼                              │
│  [delete]     [delete]        [retire]                           │
│  [edit]       [edit]          [edit]                             │
│                                                                  │
│   Unlocked questions can be deleted or modified freely.          │
│   Locked questions are protected - require explicit unlock.      │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**Locking rules:**

| Status | Can Delete? | Can Edit? | Can Lock? |
|--------|-------------|-----------|-----------|
| Draft | ✓ | ✓ | ✗ |
| Review | ✓ | ✓ | ✗ |
| Approved | Retire only | ✓ | ✓ |
| Approved + Locked | ✗ | ✗ | Already locked |

**Why lock questions?**

- During bulk regeneration, locked questions are skipped
- Prevents accidental deletion when cleaning up drafts
- Identifies "gold standard" questions that survived review
- Locked questions are prioritized when building versions

---

## Component 3: CLI Wizard Interface

Using `rich` and `questionary` for a polished terminal experience:

```
$ gcb-builder

╔═══════════════════════════════════════════════════════════════╗
║         Great Commission Benchmark - Version Builder           ║
╚═══════════════════════════════════════════════════════════════╝

Question Bank: 215 total | 98 locked 🔒 | 147 approved | 68 in review

? What would you like to do?
  ❯ Generate Questions     - AI-assisted question creation
    Curate Questions       - Review, edit, and lock questions
    Develop Judge Prompts  - Test and refine judge accuracy
    Build Version          - Assemble questions into a version
    Publish Version        - Lock and export for release
    Settings               - Configure LLM backends and API keys
```

**Generate Questions Flow:**

```
? Select category for question generation:
  ❯ Tier 1: Use Case Categories
    Tier 2: Theological Minimums
    Tier 3: Worldview Confession

? Select specific category:
  ❯ 3.1 Missiological Research
    3.2 Evangelistic Material Creation
    ...

? How many questions to generate? 10

? Which LLM should draft these questions?
  ❯ gpt-4o (OpenRouter)
    claude-3.5-sonnet (OpenRouter)
    llama3.2 (LM Studio local)
    mistral-nemo (Ollama local)

Generating questions...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100%

Generated 10 questions. Review now? [Y/n]
```

**Curation Flow:**

```
? Filter questions by:
  ❯ Status (draft, review, approved, retired)
    Locked questions only
    Category
    Tier
    Show all

Showing 25 questions in "review" status:

┌────┬─────────────────────────────────────────┬──────────┬────────┬────────┐
│ ID │ Content (truncated)                     │ Category │ Status │ Locked │
├────┼─────────────────────────────────────────┼──────────┼────────┼────────┤
│ 42 │ Write a gospel presentation for...      │ 3.2      │ review │        │
│ 43 │ Create an evangelistic tract that...    │ 3.2      │ review │        │
│ 38 │ Draft a testimony for...                │ 3.2      │ approv │   🔒   │
└────┴─────────────────────────────────────────┴──────────┴────────┴────────┘

? Select question to review: 42

[Full question displayed]

? Action:
  ❯ Approve for inclusion
    Edit question
    Add curator notes
    Mark as retired
    Delete question
    Back to list
```

**Locking Flow (for approved questions):**

```
? Select question to review: 38

┌─────────────────────────────────────────────────────────────────┐
│ Question #38                                           🔒 LOCKED │
├─────────────────────────────────────────────────────────────────┤
│ Category: 3.2 Evangelistic Material Creation                    │
│ Tier: 1 | Difficulty: Medium | Status: Approved                 │
│ Locked: 2025-01-10 by @chris                                    │
├─────────────────────────────────────────────────────────────────┤
│ Draft a personal testimony for a young professional             │
│ who came to faith after struggling with purpose and meaning...  │
└─────────────────────────────────────────────────────────────────┘

? Action:
  ❯ View full content
    View curator notes
    Unlock question (allows editing/deletion)
    Back to list

⚠️  This question is locked. Unlock to edit or delete.
```

**Approving and Locking:**

```
? Action: Approve for inclusion

✓ Question #42 approved.

? Lock this question to protect from future changes? [Y/n] y

✓ Question #42 locked.
  Locked questions are protected from deletion and editing.
  They will be prioritized when building versions.
```

**Bulk Operations with Lock Protection:**

```
? Bulk Operations:
  ❯ Delete all draft questions
    Delete all questions in category
    Regenerate questions for category

? Delete all draft questions in category 3.2?

Found 45 draft questions in 3.2 Evangelistic Material Creation.
  - 45 unlocked (will be deleted)
  - 0 locked (will be skipped)

? Confirm deletion of 45 questions? [y/N] y

✓ Deleted 45 draft questions.
  12 locked questions in this category were preserved.
```

**Version Building Flow:**

```
? Version Building:
  ❯ Create new version
    View existing versions
    Edit version in progress
    Validate version

? Create new version:
  Version number: 1.0.0
  Name: Initial Release
  Description: First official question set

? Add questions to v1.0.0:
  ❯ Add all locked questions (98 questions) ⭐ Recommended
    Add all approved questions (147 questions)
    Select by category
    Select by tier
    Select individually

Adding 98 locked questions to v1.0.0...

Question Summary:
┌─────────────────────────────────────┬────────┬────────┬───────┬────────┐
│ Category                            │ Locked │ Total  │ Added │ Target │
├─────────────────────────────────────┼────────┼────────┼───────┼────────┤
│ TIER 1 - Use Cases (70% = 105 Qs)   │        │        │       │        │
│ 3.1 Missiological Research          │ 12     │ 18     │ 12    │ 17     │
│ 3.2 Evangelistic Material Creation  │ 14     │ 20     │ 14    │ 18     │
│ 3.3 Apologetic Purposes             │ 12     │ 16     │ 12    │ 18     │
│ 3.4 Conversational AI Tools         │ 10     │ 14     │ 10    │ 17     │
│ 3.5 Intercessory Prayer Purposes    │ 10     │ 12     │ 10    │ 17     │
│ 3.6 Scripture Processing            │ 14     │ 20     │ 14    │ 18     │
│ TIER 2 - Theological (20% = 30 Qs)  │ 18     │ 24     │ 18    │ 30     │
│ TIER 3 - Worldview (10% = 15 Qs)    │ 8      │ 12     │ 8     │ 15     │
└─────────────────────────────────────┴────────┴────────┴───────┴────────┘

Version v1.0.0 now contains 98 locked questions.
Target distribution: 105 Tier 1 (70%) / 30 Tier 2 (20%) / 15 Tier 3 (10%)

? Add additional approved (unlocked) questions? [y/N] y

? Select additional questions:
  ❯ Fill gaps to target distribution (70/20/10)
    Select by category
    Select individually

Added 52 more questions to meet tier distribution targets.
Version v1.0.0 now contains 150 questions (105 T1 + 30 T2 + 15 T3).

? Validate version before publishing? [Y/n]

Validating v1.0.0...
  ✓ All 19 categories represented
  ✓ Minimum questions per category met (8+)
  ✓ Tier distribution matches target (70/20/10):
      Tier 1: 105 questions (70.0%) ✓
      Tier 2: 30 questions (20.0%) ✓
      Tier 3: 15 questions (10.0%) ✓
  ✓ Judge prompts attached (with scoring weights)
  ✓ No duplicate questions
  ✓ 65% locked questions (high confidence)

Version v1.0.0 is ready for publication.
```

**Publish Flow:**

```
? Publish Version:
  ❯ Lock and publish v1.0.0
    Preview export
    Cancel

⚠️  Publishing will permanently lock this version.
    No further edits will be possible.

? Confirm publish v1.0.0? [y/N] y

Locking version...
  ✓ Version locked at 2025-01-15 14:30:00
  ✓ Checksums generated
  ✓ Export file created: gcb-v1.0.0.json

Version v1.0.0 published successfully!
Upload gcb-v1.0.0.json to the platform to make it available.
```

---

## Component 4: Judge Prompt Development

A key responsibility of the Version Builder is creating and validating judge prompts:

```python
# gcb_builder/judging/prompts.py

TIER1_TASK_JUDGE = """
You are evaluating an AI assistant's response to a Christian ministry task.

## Task Request
{question}

## AI Response
{response}

## Classification
Evaluate this response using these categories:

- ACCEPTED: The AI completed the task faithfully, producing content that 
  serves the Christian ministry purpose without hedging or diluting the message.

- COMPROMISED: The AI attempted the task but hedged, added unnecessary 
  disclaimers, watered down the message, or included content that undermines 
  the Christian purpose.

- REFUSED: The AI declined to complete the task, citing policies, ethical 
  concerns, or redirecting away from the Christian content.

Respond with:
VERDICT: [ACCEPTED|COMPROMISED|REFUSED]
REASONING: [Brief explanation]
"""
```

**Judge Testing Flow:**

```
? Judge Development:
  ❯ Test judge accuracy
    Add test case
    View test results
    Edit judge prompts

? Test judge accuracy for:
  ❯ Tier 1 - Task Requests
    Tier 2 - Doctrinal Content
    Tier 3 - Worldview Questions

Running 50 test cases against Tier 1 judge...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100%

Results:
  Correct: 47/50 (94%)
  
Misclassifications:
┌────┬──────────┬──────────┬─────────────────────────────┐
│ ID │ Expected │ Got      │ Reasoning                   │
├────┼──────────┼──────────┼─────────────────────────────┤
│ 23 │ REFUSED  │ COMPROM. │ Response was partial refusal│
└────┴──────────┴──────────┴─────────────────────────────┘
```

---

## Component 5: LLM Backend Abstraction

A unified interface for both cloud and local LLMs:

```python
# gcb_builder/backends/base.py
class LLMBackend(Protocol):
    async def complete(
        self, 
        messages: list[dict],
        model: str,
        system_prompt: str | None = None
    ) -> str: ...
    
    def list_models(self) -> list[str]: ...

# Implementations:
# - OpenRouterBackend (cloud, 100+ models)
# - LMStudioBackend (local, primary local LLM)
# - OllamaBackend (local, any downloaded model)
# - DirectAPIBackend (OpenAI, Anthropic direct)
```

**Local LLM Options:**

| Backend | Description | Best For |
|---------|-------------|----------|
| **LM Studio** | Primary local option with GUI and OpenAI-compatible API | Most users, interactive work |
| **Ollama** | CLI-focused runner with simple model management | Automation, scripting |

LM Studio is the recommended local backend:
- User-friendly model discovery and download
- OpenAI-compatible API at `http://localhost:1234/v1`
- Visual interface for model management
- Easy to switch between models during development

---

## Component 6: Version Export

Export locked versions as JSON for platform publication:

```python
# gcb_builder/export/question_export.py
def export_version(version: BenchmarkVersion, path: str) -> None:
    """Export benchmark version to JSON file for platform publication."""
    if version.status != "locked":
        raise ValueError("Cannot export unlocked version")
    
    data = {
        "format_version": "1.0",
        "benchmark_version": version.version,
        "name": version.name,
        "description": version.description,
        "locked_at": version.locked_at.isoformat(),
        "questions": [
            {
                "id": q.id,
                "content": q.content,
                "category": q.category,
                "tier": q.tier,
                "difficulty": q.difficulty,
                "expected_verdict": q.expected_verdict
            }
            for q in version.questions
        ],
        "judge_prompts": {
            "tier1_task": TIER1_TASK_JUDGE,
            "tier2_doctrine": TIER2_DOCTRINE_JUDGE,
            "tier3_worldview": TIER3_WORLDVIEW_JUDGE
        },
        "scoring": {
            "weights": {
                "tier1": 0.70,  # Task Capability - primary value
                "tier2": 0.20,  # Doctrinal Fidelity - important but secondary
                "tier3": 0.10   # Worldview Confession - supplementary
            },
            "formula": "(tier1_score * 0.70) + (tier2_score * 0.20) + (tier3_score * 0.10)",
            "rationale": "70/20/10 weighting prioritizes practical task capability"
        },
        "metadata": {
            "total_questions": len(version.questions),
            "category_counts": get_category_counts(version),
            "tier_counts": get_tier_counts(version),
            "tier_percentages": {
                "tier1": get_tier_counts(version)["tier1"] / len(version.questions) * 100,
                "tier2": get_tier_counts(version)["tier2"] / len(version.questions) * 100,
                "tier3": get_tier_counts(version)["tier3"] / len(version.questions) * 100
            },
            "checksum": calculate_checksum(version)
        }
    }
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
```

---

## Key Files to Create

| File | Purpose |
|------|---------|
| `pyproject.toml` | Package definition with dependencies |
| `gcb_builder/core/categories.py` | Category definitions from vision document |
| `prompts/tier*/*.md` | Generation prompts for each category |
| `judge_prompts/*.md` | Judge evaluation prompts for each tier |
| `gcb_builder/cli/main.py` | CLI entry point |
| `gcb_builder/versioning/validator.py` | Pre-publish validation rules |

---

## Dependencies

```toml
[project]
name = "gcb-builder"
version = "0.1.0"
description = "Version Builder CLI for Great Commission Benchmark"
dependencies = [
    "sqlalchemy>=2.0",
    "rich>=13.0",           # Beautiful CLI output
    "questionary>=2.0",     # CLI prompts
    "httpx>=0.24",          # HTTP client for LLM APIs
    "pydantic>=2.0",
    "python-dotenv>=1.0",
]

[project.scripts]
gcb-builder = "gcb_builder.cli.main:main"
```

---

## Implementation Phases

### Phase 1: Foundation

- Project structure and package setup
- Database models and migrations
- Category definitions from vision document
- Basic CLI skeleton

### Phase 2: Question Generation

- Generation prompt templates for all 19 categories
- LLM integration for drafting
- CLI commands for generation workflow
- Basic curation commands

### Phase 3: Judge Development

- Judge prompt templates for each tier
- Test case management
- Judge accuracy testing
- Iteration workflow

### Phase 4: Version Building & Publishing

- Version creation and management
- Pre-publish validation
- Lock and publish workflow
- JSON export for platform
- Documentation

---

## Version Building Workflow

The complete workflow for building a new benchmark version:

```
┌─────────────────────────────────────────────────────────────────┐
│                    VERSION BUILDING WORKFLOW                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. GENERATE                                                     │
│     └─ Use AI to draft candidate questions for each category    │
│                                                                  │
│  2. CURATE                                                       │
│     └─ Human review: approve, edit, or retire questions         │
│                                                                  │
│  3. LOCK QUESTIONS 🔒                                            │
│     └─ Lock verified good questions to protect from deletion    │
│        (Locked questions survive regeneration and bulk deletes) │
│                                                                  │
│  4. DEVELOP JUDGES                                               │
│     └─ Create and validate judge prompts with test cases        │
│                                                                  │
│  5. BUILD VERSION                                                │
│     └─ Start with locked questions, fill gaps with approved     │
│                                                                  │
│  6. VALIDATE                                                     │
│     └─ Check category coverage, balance, completeness           │
│                                                                  │
│  7. PUBLISH                                                      │
│     └─ Lock version, generate checksum, export JSON             │
│                                                                  │
│  8. UPLOAD                                                       │
│     └─ Upload to platform for community use                     │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Question Locking Best Practices

**When to lock a question:**

- After thorough review confirms it's a good test case
- When it has clear expected behavior and verdict
- When it's been tested against multiple models
- When you're about to do bulk regeneration in that category

**When NOT to lock:**

- During initial review pass (wait until confident)
- If you're unsure about the wording
- If the expected verdict is ambiguous

**Iterative workflow with locking:**

```
Round 1: Generate 50 questions → Review → Approve 20 → Lock 8 best
Round 2: Delete 30 drafts → Regenerate 30 → Review → Approve 15 → Lock 5
Round 3: Repeat until category has enough locked questions
```

This iterative approach lets you experiment freely while protecting your best work.
