# Pre-Build Checklist: GCB Builder System

**Generated:** December 2025  
**Purpose:** Identify all remaining tasks, decisions, and specifications needed before beginning implementation of the gcb-builder system in the `gcb-builder/` folder.

---

## Executive Summary

Based on review of all specifications and the REVIEW-GAPS-AND-DECISIONS.md document, the following items need to be completed or finalized before building the gcb-builder system:

### Status Overview

| Category | Total Items | Remaining | Status |
|----------|-------------|-----------|--------|
| **Foundation & Setup** | 5 | 0 | ✅ **COMPLETE** |
| **Question Generation Prompts** | 19 | 0 | ✅ **COMPLETE** |
| **Judge Prompts** | 3 | 0 | ✅ **COMPLETE** |
| **LLM Backend Adapters** | 4 | 0 | ✅ **COMPLETE** |
| **Core Implementation** | 15+ | 0 | ✅ **COMPLETE** |
| **Documentation** | 6 | 5 | ⚠️ **NON-BLOCKING** (README done) |

**Critical Path:** ~~Foundation~~ → ~~Prompts~~ → ~~LLM Backends~~ → ~~Core Implementation~~ → Testing

---

## 1. ✅ COMPLETE: Foundation & Project Setup

### 1.1 Project Structure Creation
- [x] **Create `gcb-builder/` folder** at project root
- [x] **Create `pyproject.toml`** with all dependencies:
  - sqlalchemy>=2.0
  - rich>=13.0
  - questionary>=2.0
  - httpx>=0.24
  - pydantic>=2.0
  - python-dotenv>=1.0
  - datasette>=0.64
- [x] **Set up directory structure** per cli-builder-specifications.md:
  ```
  gcb-builder/
  ├── gcb_builder/              # Python package (code only)
  │   ├── cli/
  │   ├── core/
  │   ├── generation/
  │   ├── judging/
  │   ├── backends/
  │   ├── versioning/
  │   └── export/
  ├── prompts/                   # Actual markdown prompt template files (data)
  │   ├── tier1_use_cases/
  │   ├── tier2_theological/
  │   └── tier3_worldview/
  ├── judge_prompts/            # Judge prompt template files (data)
  ├── data/                      # Database and local data files
  └── tests/                     # Test files
  ```

### 1.2 Category Definitions
- [x] **Create `gcb_builder/core/categories.py`** with all 19 categories:
  - Tier 1 (7 categories): 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7
  - Tier 2 (6 categories): 4.1, 4.2, 4.3, 4.4, 4.5, 4.6
  - Tier 3 (6 categories): 5.1, 5.2, 5.3, 5.4, 5.5, 5.6
- [x] **Reference:** benchmark-categories.md for canonical definitions
- [x] **Include:** Category IDs, names, tier assignments, weights

### 1.3 Database Models
- [x] **Create `gcb_builder/core/models.py`** with SQLAlchemy models:
  - `Question` (with all fields from spec)
  - `BenchmarkVersion`
  - `VersionQuestion`
  - `JudgeTestCase`
  - `JudgeTestResult` (bonus)
- [ ] **Set up Alembic** for migrations (deferred - using SQLAlchemy create_all for now)
- [x] **Create initial schema** via `init_db()`

### 1.4 Database Connection
- [x] **Create `gcb_builder/core/database.py`** for SQLite connection
- [x] **Set up session management** (context manager pattern)
- [x] **Configure database path** (`data/gcb_builder.db`)

### 1.5 Additional Foundation Items (Completed)
- [x] **Create `gcb_builder/core/schemas.py`** with Pydantic validation schemas
- [x] **Create `gcb_builder/cli/main.py`** with basic CLI skeleton
- [x] **Create `README.md`** with installation and usage instructions
- [x] **Create `.gitignore`** for Python projects
- [x] **Create test files** for categories and database

---

## 2. ✅ COMPLETE: Question Generation Prompts

**Status:** All 19 prompts have been created with full specifications.

### 2.1 Tier 1: Use Case Categories (7 prompts) ✅

- [x] **3.1 Missiological Research** (`prompts/tier1_use_cases/3.1_missiological_research.md`)
- [x] **3.2 Evangelistic Material Creation** (`prompts/tier1_use_cases/3.2_evangelistic_material.md`)
- [x] **3.3 Apologetic Purposes** (`prompts/tier1_use_cases/3.3_apologetic_purposes.md`)
- [x] **3.4 Conversational AI Tools** (`prompts/tier1_use_cases/3.4_conversational_ai.md`)
- [x] **3.5 Intercessory Prayer Purposes** (`prompts/tier1_use_cases/3.5_intercessory_prayer.md`)
- [x] **3.6 Problematic Vocabulary** (`prompts/tier1_use_cases/3.6_problematic_vocabulary.md`)
- [x] **3.7 Difficult Passages** (`prompts/tier1_use_cases/3.7_difficult_passages.md`)

### 2.2 Tier 2: Theological Minimums (6 prompts) ✅

- [x] **4.1 Exclusivity of Jesus Christ** (`prompts/tier2_theological/4.1_exclusivity.md`)
- [x] **4.2 Universality of Sin** (`prompts/tier2_theological/4.2_universality_of_sin.md`)
- [x] **4.3 Reality of Judgment** (`prompts/tier2_theological/4.3_reality_of_judgment.md`)
- [x] **4.4 Lordship of Jesus** (`prompts/tier2_theological/4.4_lordship.md`)
- [x] **4.5 Call to Repentance and Faith** (`prompts/tier2_theological/4.5_repentance_faith.md`)
- [x] **4.6 Burden to Make Disciples** (`prompts/tier2_theological/4.6_discipleship.md`)

### 2.3 Tier 3: Worldview Confessions (6 prompts) ✅

- [x] **5.1 Existence of God** (`prompts/tier3_worldview/5.1_existence_of_god.md`)
- [x] **5.2 Historical Reality of Jesus** (`prompts/tier3_worldview/5.2_historical_jesus.md`)
- [x] **5.3 The Crucifixion** (`prompts/tier3_worldview/5.3_crucifixion.md`)
- [x] **5.4 The Resurrection** (`prompts/tier3_worldview/5.4_resurrection.md`)
- [x] **5.5 Human Sinfulness** (`prompts/tier3_worldview/5.5_sinfulness.md`)
- [x] **5.6 Salvation Through Faith** (`prompts/tier3_worldview/5.6_salvation.md`)

### 2.4 Prompt Template Requirements ✅

All prompts include:
- [x] Category definition and purpose
- [x] Examples of good questions (easy, medium, hard)
- [x] Difficulty level guidance
- [x] Capability vs willingness distinction
- [x] Metadata requirements (use_case_tags, audience_context, ministry_type)
- [x] Expected failure modes
- [x] Question count targets per difficulty
- [x] Verdict criteria and examples

---

## 3. ✅ COMPLETE: Judge Prompt Development

**Status:** All 3 judge prompts have been finalized with full specifications.

### 3.1 Judge Prompt Files ✅

- [x] **Tier 1 Task Judge** (`judge_prompts/tier1_task.md`)
  - Verdicts: ACCEPTED, COMPROMISED, REFUSED
  - Refusal types: CAPABILITY, SAFETY, IDEOLOGICAL, UNCLEAR
  - Includes judge prompt template, scoring notes, and detailed examples
  
- [x] **Tier 2 Doctrine Judge** (`judge_prompts/tier2_doctrine.md`)
  - Verdicts: LOYAL, COMPROMISED, DISLOYAL
  - Refusal types: CAPABILITY, SAFETY, IDEOLOGICAL, UNCLEAR
  - Includes doctrine reference table and detailed examples
  
- [x] **Tier 3 Worldview Judge** (`judge_prompts/tier3_worldview.md`)
  - Verdicts: AFFIRMED, HEDGED, DENIED
  - Refusal types: CAPABILITY, SAFETY, IDEOLOGICAL, UNCLEAR
  - Includes truth claims reference and detailed examples

### 3.2 Judge Testing Framework ✅

- [x] **Create test case management system** (`gcb_builder/judging/tester.py`)
- [x] **Implement accuracy measurement** (target: ≥90% per Technical-Decisions.md)
- [x] **Create test case database** (JudgeTestCase model already exists)
- [x] **Build validation workflow** for judge prompts

**Reference:** spec-inter-rater-reliability.md for methodology

---

## 4. ✅ COMPLETE: LLM Backend Implementation

### 4.1 Backend Adapters ✅

- [x] **OpenRouter Backend** (`gcb_builder/backends/openrouter.py`)
  - API integration with httpx async client
  - Model listing from /models endpoint
  - Full async completion support with error handling
  
- [x] **LM Studio Backend** (`gcb_builder/backends/lmstudio.py`)
  - Local OpenAI-compatible API
  - Model discovery from local server
  - Async completion support with extended timeout for local models
  
- [x] **Ollama Backend** (`gcb_builder/backends/ollama.py`)
  - Local Ollama API integration
  - Model listing from /api/tags
  - Async completion support with Ollama-specific response handling
  
- [x] **Direct API Backends** (`gcb_builder/backends/direct_api.py`)
  - OpenAI direct (OpenAIBackend)
  - Anthropic direct (AnthropicBackend)
  - Unified interface via LLMBackend protocol

### 4.2 Backend Abstraction ✅

- [x] **Create Protocol/Interface** (`gcb_builder/backends/base.py`)
  - `LLMBackend` protocol with runtime_checkable
  - `complete(request: CompletionRequest) -> CompletionResponse`
  - `list_models() -> list[ModelInfo]`
  - `is_available() -> bool`
  - `BackendType` enum for all supported backends
  - Comprehensive error hierarchy (AuthenticationError, RateLimitError, etc.)

### 4.3 Configuration ✅

- [x] **Environment variable management** (`gcb_builder/backends/config.py`)
  - `.env` file support via python-dotenv
  - Config dataclass for all backend settings
- [x] **API key storage** (secure, not in code)
  - All keys loaded from environment variables
  - Template generator for .env.example
- [x] **Backend selection helpers**
  - `get_backend(BackendType)` factory function
  - `get_available_backend()` auto-detection
  - `list_available_backends()` discovery

### 4.4 Testing ✅

- [x] **Unit tests** (`tests/test_backends.py`)
  - 31 tests covering all backends
  - Protocol compliance tests
  - Error handling tests
  - Configuration tests

**Reference:** cli-builder-tech-stack.md for backend details

---

## 5. ✅ COMPLETE: Core Implementation

### 5.1 CLI Interface ✅

- [x] **Main entry point** (`gcb_builder/cli/main.py`)
  - Rich menu system
  - Navigation between sections
  - Status display (question counts, locked questions, etc.)
  
- [x] **Generate commands** (`gcb_builder/cli/generate.py`)
  - Category selection
  - Question count input
  - LLM model selection
  - Generation workflow
  
- [x] **Curate commands** (`gcb_builder/cli/curate.py`)
  - Question listing/filtering
  - Review workflow
  - Approve/lock/retire actions
  - Bulk operations
  
- [x] **Judge commands** (`gcb_builder/cli/judge.py`)
  - Test case management
  - Accuracy testing
  - Prompt editing
  
- [x] **Version commands** (`gcb_builder/cli/version.py`)
  - Version creation
  - Question assembly
  - Validation
  - Publishing
  
- [x] **Explore command** (`gcb_builder/cli/explore.py`)
  - Datasette launcher
  - Database browser

### 5.2 Question Generation System ✅

- [x] **Generator implementation** (`gcb_builder/generation/generator.py`)
  - Prompt loading
  - LLM orchestration
  - Response parsing
  - Question creation in database
  
- [x] **Prompt loader** (`gcb_builder/generation/prompt_loader.py`)
  - Load markdown prompts from root `prompts/` directory
  - Template rendering
  - Category mapping
  - Note: The actual prompt files live in `prompts/` at project root, not in the package

### 5.3 Curation Workflow ✅

- [x] **Question review system**
  - Status transitions (draft → review → approved → locked)
  - Locking mechanism
  - Bulk operations with lock protection
  
- [x] **Datasette integration**
  - Metadata configuration
  - Custom queries
  - Faceted browsing setup

### 5.4 Version Building ✅

- [x] **Version builder** (`gcb_builder/versioning/builder.py`)
  - Question assembly
  - Tier distribution validation
  - Category coverage checking
  
- [x] **Validator** (`gcb_builder/versioning/validator.py`)
  - Pre-publish validation
  - All checks from spec (category coverage, tier distribution, etc.)
  
- [x] **Publisher** (`gcb_builder/versioning/publisher.py`)
  - Version locking
  - Checksum generation
  - JSON export

### 5.5 Export System ✅

- [x] **JSON export** (`gcb_builder/export/question_export.py`)
  - Format version 2.0 compliance
  - All required fields
  - Checksum calculation
  
- [x] **Bundle compiler** (`gcb_builder/versioning/bundle_compiler.py`)
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

1. ~~**Generation Prompts (19 total)** - Cannot generate questions without prompts~~ ✅ DONE
2. ~~**Judge Prompts (3 total)** - Cannot validate questions without judge prompts~~ ✅ DONE
3. ~~**Category Definitions** - Core constant definitions needed~~ ✅ DONE
4. ~~**Database Schema** - Foundation for all data storage~~ ✅ DONE

**All critical blockers resolved!** ✅

### Medium Blockers (Can Start But Need Soon)

1. ~~**LLM Backend Adapters** - Needed for generation, but can mock initially~~ ✅ DONE
2. ~~**Judge Testing Framework** - Needed for validation, but can be basic initially~~ ✅ DONE
3. ~~**Core Implementation** - CLI, generation, curation, versioning, export~~ ✅ DONE

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

1. ~~**Create gcb-builder folder structure**~~ ✅ DONE
2. ~~**Set up pyproject.toml with dependencies**~~ ✅ DONE
3. ~~**Create category constants file**~~ ✅ DONE
4. ~~**Write all 19 generation prompts**~~ ✅ DONE
5. ~~**Set up basic database models**~~ ✅ DONE
6. ~~**Create minimal CLI entry point**~~ ✅ DONE
7. ~~**Write all 3 judge prompts**~~ ✅ DONE
8. ~~**Implement LLM backend adapters**~~ ✅ DONE
9. ~~**Build question generator**~~ ✅ DONE
10. ~~**Build curation workflow**~~ ✅ DONE
11. ~~**Build version building system**~~ ✅ DONE
12. ~~**Build export system**~~ ✅ DONE
13. **Generate initial question set** ← **NEXT**
14. **Curate and lock questions**
15. **Build and publish first version**

### Questions to Resolve

- [x] **Prompt writing approach:** Individual files vs. template system? → Individual markdown files in `prompts/`
- [x] **Database location:** Relative path vs. absolute path? → Relative path `data/gcb_builder.db`
- [x] **Testing strategy:** Unit tests vs. integration tests first? → Unit tests for core modules
- [ ] **Version control:** Separate repo vs. monorepo? → Using monorepo

---

## Summary

**Total Critical Items:** ~50+ tasks  
**Estimated Time:** Implementation complete! Ready for content generation.  
**Completed:** 
- Foundation setup (categories, models, database, CLI skeleton)
- All 19 generation prompts (Tier 1, Tier 2, Tier 3)
- All 3 judge prompts with examples and templates
- All 5 LLM backend adapters (OpenRouter, LM Studio, Ollama, OpenAI, Anthropic)
- **Full CLI implementation** (generate, curate, judge, version, explore commands)
- **Question generation system** (generator + prompt loader)
- **Curation workflow** (status transitions, locking, bulk operations)
- **Version building** (builder, validator, publisher)
- **Export system** (JSON export + bundle compiler)

**Blocking Items:** ~~Core implementation~~ ✅ COMPLETE  

**Ready to Begin:** ✅ **SYSTEM READY FOR USE!** The gcb-builder CLI is fully functional. Next priority is generating and curating the initial question set for V1.

**Recommendation:** 
1. Configure API keys in `.env` file
2. Run `gcb-builder init` to initialize the database
3. Use `gcb-builder generate` to create questions
4. Use `gcb-builder curate` to review and lock questions
5. Use `gcb-builder version` to build benchmark versions

---

*This checklist should be updated as items are completed. Mark items as done and add new items as they are discovered during implementation.*