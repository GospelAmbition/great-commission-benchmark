# Pre-Build Checklist: GCB Builder System

**Generated:** December 2025  
**Purpose:** Identify all remaining tasks, decisions, and specifications needed before beginning implementation of the gcb-builder system in the `gcb-builder/` folder.

---

## Executive Summary

Based on review of all specifications and the REVIEW-GAPS-AND-DECISIONS.md document, the following items need to be completed or finalized before building the gcb-builder system:

### Status Overview

| Category | Total Items | Remaining | Status |
|----------|-------------|-----------|--------|
| **Foundation & Setup** | 5 | 5 | ⚠️ **BLOCKING** |
| **Question Generation Prompts** | 19 | 19 | ⚠️ **BLOCKING** |
| **Judge Prompts** | 3 | 3 | ⚠️ **BLOCKING** |
| **LLM Backend Adapters** | 4 | 4 | ⚠️ **BLOCKING** |
| **Core Implementation** | 15+ | 15+ | ⚠️ **BLOCKING** |
| **Documentation** | 6 | 6 | ⚠️ **NON-BLOCKING** (can be done in parallel) |

**Critical Path:** Foundation → Prompts → Core Implementation → Testing

---

## 1. CRITICAL: Foundation & Project Setup

### 1.1 Project Structure Creation
- [ ] **Create `gcb-builder/` folder** at project root
- [ ] **Create `pyproject.toml`** with all dependencies:
  - sqlalchemy>=2.0
  - rich>=13.0
  - questionary>=2.0
  - httpx>=0.24
  - pydantic>=2.0
  - python-dotenv>=1.0
  - datasette>=0.64
- [ ] **Set up directory structure** per cli-builder-specifications.md:
  ```
  gcb-builder/
  ├── gcb_builder/              # Python package (code only)
  │   ├── cli/
  │   ├── core/
  │   ├── generation/
  │   │   └── prompts/          # Code to load prompts (not the prompt files themselves)
  │   ├── judging/
  │   ├── backends/
  │   ├── versioning/
  │   └── export/
  ├── prompts/                   # Actual markdown prompt template files (data)
  ├── judge_prompts/            # Judge prompt template files (data)
  ├── data/                      # Database and local data files
  └── tests/                     # Test files
  ```

### 1.2 Category Definitions
- [ ] **Create `gcb_builder/core/categories.py`** with all 19 categories:
  - Tier 1 (7 categories): 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7
  - Tier 2 (6 categories): 4.1, 4.2, 4.3, 4.4, 4.5, 4.6
  - Tier 3 (6 categories): 5.1, 5.2, 5.3, 5.4, 5.5, 5.6
- [ ] **Reference:** benchmark-categories.md for canonical definitions
- [ ] **Include:** Category IDs, names, tier assignments, weights

### 1.3 Database Models
- [ ] **Create `gcb_builder/core/models.py`** with SQLAlchemy models:
  - `Question` (with all fields from spec)
  - `BenchmarkVersion`
  - `VersionQuestion`
  - `JudgeTestCase`
- [ ] **Set up Alembic** for migrations
- [ ] **Create initial migration** for schema

### 1.4 Database Connection
- [ ] **Create `gcb_builder/core/database.py`** for SQLite connection
- [ ] **Set up session management**
- [ ] **Configure database path** (`data/gcb_builder.db`)

---

## 2. CRITICAL: Question Generation Prompts

**Status:** All 19 prompts need to be written before generation can begin.

### 2.1 Tier 1: Use Case Categories (7 prompts)

- [ ] **3.1 Missiological Research** (`prompts/tier1_use_cases/3.1_missiological_research.md`)
  - Include capability vs willingness guidance
  - Include metadata requirements (use_case_tags, audience_context, ministry_type)
  - Specify difficulty levels (easy, medium, hard)
  
- [ ] **3.2 Evangelistic Material Creation** (`prompts/tier1_use_cases/3.2_evangelistic_material.md`)
  - Draft exists in cli-builder-specifications.md (lines 236-277)
  - Needs to be finalized and saved as markdown file
  
- [ ] **3.3 Apologetic Purposes** (`prompts/tier1_use_cases/3.3_apologetic_purposes.md`)
  
- [ ] **3.4 Conversational AI Tools** (`prompts/tier1_use_cases/3.4_conversational_ai.md`)
  
- [ ] **3.5 Intercessory Prayer Purposes** (`prompts/tier1_use_cases/3.5_intercessory_prayer.md`)
  
- [ ] **3.6 Problematic Vocabulary** (`prompts/tier1_use_cases/3.6_problematic_vocabulary.md`)
  - Draft exists in cli-builder-specifications.md (lines 279-322)
  - Needs to be finalized and saved as markdown file
  
- [ ] **3.7 Difficult Passages** (`prompts/tier1_use_cases/3.7_difficult_passages.md`)
  - Draft exists in cli-builder-specifications.md (lines 326-380)
  - Needs to be finalized and saved as markdown file

### 2.2 Tier 2: Theological Minimums (6 prompts)

- [ ] **4.1 Exclusivity of Jesus Christ** (`prompts/tier2_theological/4.1_exclusivity.md`)
  
- [ ] **4.2 Universality of Sin** (`prompts/tier2_theological/4.2_sin.md`)
  
- [ ] **4.3 Reality of Judgment** (`prompts/tier2_theological/4.3_judgment.md`)
  
- [ ] **4.4 Lordship of Jesus** (`prompts/tier2_theological/4.4_lordship.md`)
  
- [ ] **4.5 Call to Repentance and Faith** (`prompts/tier2_theological/4.5_repentance_faith.md`)
  
- [ ] **4.6 Burden to Make Disciples** (`prompts/tier2_theological/4.6_discipleship.md`)

### 2.3 Tier 3: Worldview Confessions (6 prompts)

- [ ] **5.1 Existence of God** (`prompts/tier3_worldview/5.1_god_exists.md`)
  
- [ ] **5.2 Historical Reality of Jesus** (`prompts/tier3_worldview/5.2_historical_jesus.md`)
  
- [ ] **5.3 The Crucifixion** (`prompts/tier3_worldview/5.3_crucifixion.md`)
  
- [ ] **5.4 The Resurrection** (`prompts/tier3_worldview/5.4_resurrection.md`)
  
- [ ] **5.5 Human Sinfulness** (`prompts/tier3_worldview/5.5_sinfulness.md`)
  
- [ ] **5.6 Salvation Through Faith** (`prompts/tier3_worldview/5.6_salvation.md`)

### 2.4 Prompt Template Requirements

**Note:** All prompt files should be saved in the root `prompts/` directory (not inside the `gcb_builder/` package). The package code in `gcb_builder/generation/prompts/` will load these files.

Each prompt must include:
- [ ] Category definition and purpose
- [ ] Examples of good questions
- [ ] Difficulty level guidance (easy, medium, hard)
- [ ] Capability vs willingness distinction
- [ ] Metadata requirements (use_case_tags, audience_context, ministry_type)
- [ ] Expected failure modes
- [ ] Question count targets per difficulty

**Reference:** cli-builder-specifications.md lines 179-358 for examples

---

## 3. CRITICAL: Judge Prompt Development

**Status:** Drafts exist in cli-builder-specifications.md but need to be finalized.

### 3.1 Judge Prompt Files

- [ ] **Tier 1 Task Judge** (`judge_prompts/tier1_task.md`)
  - Draft exists in cli-builder-specifications.md (lines 975-1017)
  - Verdicts: ACCEPTED, COMPROMISED, REFUSED
  - Refusal types: CAPABILITY, SAFETY, IDEOLOGICAL, UNCLEAR
  - Needs finalization and testing
  
- [ ] **Tier 2 Doctrine Judge** (`judge_prompts/tier2_doctrine.md`)
  - Draft exists in cli-builder-specifications.md (lines 1019-1056)
  - Verdicts: LOYAL, COMPROMISED, DISLOYAL
  - Refusal types: CAPABILITY, SAFETY, IDEOLOGICAL, UNCLEAR
  - Needs finalization and testing
  
- [ ] **Tier 3 Worldview Judge** (`judge_prompts/tier3_worldview.md`)
  - Draft exists in cli-builder-specifications.md (lines 1058-1096)
  - Verdicts: AFFIRMED, HEDGED, DENIED
  - Refusal types: CAPABILITY, SAFETY, IDEOLOGICAL, UNCLEAR
  - Needs finalization and testing

### 3.2 Judge Testing Framework

- [ ] **Create test case management system** (`gcb_builder/judging/tester.py`)
- [ ] **Implement accuracy measurement** (target: ≥90% per Technical-Decisions.md)
- [ ] **Create test case database** (JudgeTestCase model)
- [ ] **Build validation workflow** for judge prompts

**Reference:** spec-inter-rater-reliability.md for methodology

---

## 4. CRITICAL: LLM Backend Implementation

### 4.1 Backend Adapters

- [ ] **OpenRouter Backend** (`gcb_builder/backends/openrouter.py`)
  - API integration
  - Model listing
  - Async completion support
  
- [ ] **LM Studio Backend** (`gcb_builder/backends/lmstudio.py`)
  - Local OpenAI-compatible API
  - Model discovery
  - Async completion support
  
- [ ] **Ollama Backend** (`gcb_builder/backends/ollama.py`)
  - Local Ollama API
  - Model listing
  - Async completion support
  
- [ ] **Direct API Backends** (`gcb_builder/backends/direct_api.py`)
  - OpenAI direct
  - Anthropic direct
  - Unified interface

### 4.2 Backend Abstraction

- [ ] **Create Protocol/Interface** (`gcb_builder/backends/base.py`)
  - `LLMBackend` protocol
  - `complete()` method signature
  - `list_models()` method signature

### 4.3 Configuration

- [ ] **Environment variable management** (`.env` support)
- [ ] **API key storage** (secure, not in code)
- [ ] **Backend selection** in CLI

**Reference:** cli-builder-tech-stack.md for backend details

---

## 5. CRITICAL: Core Implementation

### 5.1 CLI Interface

- [ ] **Main entry point** (`gcb_builder/cli/main.py`)
  - Rich menu system
  - Navigation between sections
  - Status display (question counts, locked questions, etc.)
  
- [ ] **Generate commands** (`gcb_builder/cli/generate.py`)
  - Category selection
  - Question count input
  - LLM model selection
  - Generation workflow
  
- [ ] **Curate commands** (`gcb_builder/cli/curate.py`)
  - Question listing/filtering
  - Review workflow
  - Approve/lock/retire actions
  - Bulk operations
  
- [ ] **Judge commands** (`gcb_builder/cli/judge.py`)
  - Test case management
  - Accuracy testing
  - Prompt editing
  
- [ ] **Version commands** (`gcb_builder/cli/version.py`)
  - Version creation
  - Question assembly
  - Validation
  - Publishing
  
- [ ] **Explore command** (`gcb_builder/cli/explore.py`)
  - Datasette launcher
  - Database browser

### 5.2 Question Generation System

- [ ] **Generator implementation** (`gcb_builder/generation/generator.py`)
  - Prompt loading
  - LLM orchestration
  - Response parsing
  - Question creation in database
  
- [ ] **Prompt loader** (`gcb_builder/generation/prompts/` or `prompt_loader.py`)
  - Load markdown prompts from root `prompts/` directory
  - Template rendering
  - Category mapping
  - Note: The actual prompt files live in `prompts/` at project root, not in the package

### 5.3 Curation Workflow

- [ ] **Question review system**
  - Status transitions (draft → review → approved → locked)
  - Locking mechanism
  - Bulk operations with lock protection
  
- [ ] **Datasette integration**
  - Metadata configuration
  - Custom queries
  - Faceted browsing setup

### 5.4 Version Building

- [ ] **Version builder** (`gcb_builder/versioning/builder.py`)
  - Question assembly
  - Tier distribution validation
  - Category coverage checking
  
- [ ] **Validator** (`gcb_builder/versioning/validator.py`)
  - Pre-publish validation
  - All checks from spec (category coverage, tier distribution, etc.)
  
- [ ] **Publisher** (`gcb_builder/versioning/publisher.py`)
  - Version locking
  - Checksum generation
  - JSON export

### 5.5 Export System

- [ ] **JSON export** (`gcb_builder/export/question_export.py`)
  - Format version 2.0 compliance
  - All required fields
  - Checksum calculation
  
- [ ] **Bundle compiler** (`gcb_builder/versioning/bundle_compiler.py`)
  - Compress + base64 encode
  - Generate Python bundle files
  - Checksum verification

**Reference:** spec-export-schema-validation.md for export format

---

## 6. NON-BLOCKING: Documentation

These can be done in parallel with implementation:

### 6.1 User Documentation

- [ ] **CLI Builder README** (`gcb-builder/README.md`)
  - Installation instructions
  - Quick start guide
  - Workflow overview
  
- [ ] **Version Builder Guide**
  - Complete workflow documentation
  - Best practices
  - Troubleshooting

### 6.2 Developer Documentation

- [ ] **Local Development Setup**
  - Environment setup
  - Database initialization
  - Testing procedures
  
- [ ] **Contribution Guidelines** (may already exist)
  - Code style
  - Pull request process
  
- [ ] **Testing Strategies**
  - Unit test examples
  - Integration test approach

---

## 7. DECISIONS ALREADY MADE (No Action Needed)

The following decisions have been finalized per Technical-Decisions.md:

✅ **Minimum question count for V1:** Full expected build (210 Tier 1, 60 Tier 2, 30 Tier 3)  
✅ **Question generation models:** OpenRouter: GPT 5.2, Gemini 3, Claude Opus  
✅ **Judge prompt accuracy threshold:** ≥90%  
✅ **Judge model:** OpenAI gpt-oss-20b  
✅ **Manual upload workflow:** Selected for builder-to-platform  
✅ **Automatic version checking:** Enabled for CLI updates  

---

## 8. SPECIFICATIONS TO REFERENCE

All specifications are complete and ready for implementation:

✅ **cli-builder-specifications.md** - Complete implementation spec  
✅ **cli-builder-tech-stack.md** - Technology choices  
✅ **spec-builder-to-platform.md** - Export workflow  
✅ **spec-builder-to-runner.md** - Bundle compilation  
✅ **spec-export-schema-validation.md** - Export format schema  
✅ **spec-curation-guidelines.md** - Curation process  
✅ **benchmark-categories.md** - Category definitions  
✅ **benchmark-scoring.md** - Scoring methodology  

---

## 9. PRIORITY ORDER FOR IMPLEMENTATION

### Phase 1: Foundation (Week 1)
1. Create project structure
2. Set up pyproject.toml
3. Create database models
4. Set up database connection
5. Define category constants

### Phase 2: Prompts (Week 1-2)
1. Write all 19 generation prompts
2. Finalize 3 judge prompts
3. Create prompt loading system

### Phase 3: Core Generation (Week 2-3)
1. Implement LLM backends
2. Build question generator
3. Create basic CLI skeleton
4. Test generation workflow

### Phase 4: Curation & Workflow (Week 3-4)
1. Build curation commands
2. Implement locking mechanism
3. Set up Datasette integration
4. Test full workflow

### Phase 5: Version Building (Week 4-5)
1. Build version assembly
2. Implement validation
3. Create export system
4. Build bundle compiler

### Phase 6: Testing & Refinement (Week 5-6)
1. Test with real questions
2. Validate judge prompts
3. Test export format
4. Documentation

---

## 10. BLOCKERS IDENTIFIED

### Critical Blockers (Must Complete Before Building)

1. **Generation Prompts (19 total)** - Cannot generate questions without prompts
2. **Judge Prompts (3 total)** - Cannot validate questions without judge prompts
3. **Category Definitions** - Core constant definitions needed
4. **Database Schema** - Foundation for all data storage

### Medium Blockers (Can Start But Need Soon)

1. **LLM Backend Adapters** - Needed for generation, but can mock initially
2. **Judge Testing Framework** - Needed for validation, but can be basic initially

### Low Priority (Can Be Done Later)

1. **Documentation** - Can be written in parallel
2. **Advanced features** - Can be added iteratively

---

## 11. RECOMMENDATIONS

### Immediate Actions

1. **Start with prompt writing** - This is the most time-consuming and blocking task
   - Begin with Tier 1 categories (most important, 70% weight)
   - Use existing drafts in cli-builder-specifications.md as starting points
   - Focus on 3.2 and 3.6 which have partial drafts

2. **Set up project structure** - Can be done in parallel with prompt writing
   - Create folder structure
   - Set up pyproject.toml
   - Initialize git repository

3. **Create category constants** - Quick win, enables other work
   - Reference benchmark-categories.md
   - Create Python constants/enums

### Best Practices

1. **Iterative development** - Build MVP first, then enhance
   - Start with basic generation (no metadata)
   - Add metadata support later
   - Add advanced features incrementally

2. **Test early and often** - Validate each component
   - Test prompt loading
   - Test LLM integration
   - Test database operations
   - Test export format

3. **Document as you go** - Don't leave documentation for the end
   - Document decisions
   - Document workflows
   - Document gotchas

---

## 12. NEXT STEPS

### Recommended Starting Point

1. **Create gcb-builder folder structure**
2. **Set up pyproject.toml with dependencies**
3. **Create category constants file**
4. **Write first 3-5 generation prompts** (start with Tier 1)
5. **Set up basic database models**
6. **Create minimal CLI entry point**

### Questions to Resolve

- [ ] **Prompt writing approach:** Individual files vs. template system?
- [ ] **Database location:** Relative path vs. absolute path?
- [ ] **Testing strategy:** Unit tests vs. integration tests first?
- [ ] **Version control:** Separate repo vs. monorepo?

---

## Summary

**Total Critical Items:** ~50+ tasks  
**Estimated Time:** 5-6 weeks for full implementation  
**Blocking Items:** 19 generation prompts, 3 judge prompts, foundation setup  

**Ready to Begin:** ✅ Yes, with the understanding that prompt writing will be the primary focus for the first 1-2 weeks.

**Recommendation:** Start with foundation setup and prompt writing in parallel. The technical implementation can proceed once the first few prompts are ready.

---

*This checklist should be updated as items are completed. Mark items as done and add new items as they are discovered during implementation.*