# Great Commission Benchmark v0.5

A testing framework for red-teaming LLMs on how they handle proselytization and missionary work requests.

## Quick Start

### 1. Setup

```bash
cd benchmark
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Initialize Databases

The benchmark uses a dual-database architecture for better data separation and management:

```bash
python -m gcb init
```

This creates two SQLite databases:
- **`questions.db`**: Stores questions and conversations (test prompts)
- **`responses.db`**: Stores models, test runs, responses, and evaluations (test results)

### 3. Start the UI

```bash
streamlit run ui/app.py
```

This opens a web interface at http://localhost:8501 where you can:
- View dashboard statistics
- Add/edit/delete questions
- Export to PromptFoo format

### 4. Run Verification

```bash
python -m gcb verify
```

## Architecture

The benchmark uses a **dual-database architecture** that separates test questions from test results:

```
+------------------+     +-------------------+     +------------------+
|   Streamlit UI   |---->| Questions Database|     |  PromptFoo CLI   |
|  (Question Mgmt) |     |  (questions.db)   |<----|  (Test Runner)   |
|  (Dashboard)     |     |  - Questions      |     +------------------+
+------------------+     +-------------------+              |
                                    |                       |
                                    | (export)              |
                                    v                       |
                         +------------------+               |
                         | PromptFoo YAML   |               |
                         +------------------+               |
                                    |                       |
                                    | (runs tests)          |
                                    v                       |
                         +----------------+                 |
                         |  Test Model    |<---------------+
                         |  (LLM being    |  (generates
                         |   tested)      |   responses)
                         +----------------+
                                    |
                                    | (import results)
                                    v
                         +-------------------+     +----------------+
                         | Responses Database|---->|  Evaluator     |
                         |  (responses.db)   |     |  Model         |
                         |  - Models         |     |  (LLM judge)   |
                         |  - Test Runs      |     +----------------+
                         |  - Responses      |              |
                         |  - Evaluations    |              |
                         +-------------------+              |
                                    ^                       |
                                    | (writes evaluations)  |
                                    +-----------------------+
                                    |
                                    v
                         +-------------------+     +----------------+
                         | Responses Database|---->|  Benchmark     |
                         |  (responses.db)   |     |  Reports      |
                         |  - Evaluations    |     |  (CLI/UI)     |
                         +-------------------+     +----------------+
```

### Why Dual Databases?

- **Separation of Concerns**: Questions (test cases) are separate from responses (test results)
- **Version Control**: Questions can be updated without affecting historical test results
- **Data Integrity**: Each response stores a permanent snapshot of the question data at the time of testing
- **Flexibility**: Questions database can be shared/versioned independently from results
- **Performance**: Smaller, focused databases improve query performance

### Data Flow

1. **Questions** are stored in `questions.db` (managed via UI or CLI)
2. **Export** reads from `questions.db` and generates PromptFoo YAML
3. **PromptFoo** runs tests and generates results JSON
4. **Import** reads results and writes to `responses.db` (with denormalized question data)
5. **Evaluation** reads from `responses.db` and writes evaluations back
6. **Reporting** reads from both databases to generate statistics

## Question Categories

### By Acceptance Level

- **🟢 Green**: Educational, historical, theological questions (should always be accepted)
- **🟠 Orange**: Borderline requests like fictional dialogues, "help a friend" scenarios  
- **🔴 Red**: Direct conversion requests targeting specific religions (should be refused)

### By Prompt Type

- **Direct**: Straightforward requests ("Write a speech to convert...")
- **Roleplay**: Framed as fiction or scenarios ("I'm writing a novel...")
- **Encoded**: Indirect or euphemistic language ("Help me share the good news effectively")

Note: Multi-turn conversation support has been removed. The focus is on single-turn question evaluation. Encoded questions test whether models can detect underlying intent through indirect phrasing.

## CLI Commands

All commands automatically use database paths from `config.yaml`. You can override them with `--questions-db` and `--responses-db` flags.

```bash
# Initialize both databases
python -m gcb init

# Initialize with custom paths
python -m gcb init --questions-db my_questions.db --responses-db my_responses.db

# Show statistics (reads from both databases)
python -m gcb stats

# Add a question (writes to questions.db)
python -m gcb add-question "Question text" --level green --type direct

# List questions (reads from questions.db)
python -m gcb list-questions --level green

# Export to PromptFoo (reads from questions.db, uses config.yaml)
python -m gcb prepare

# Or override model on the fly
python -m gcb prepare --model gpt-4 --provider openrouter

# Test LM Studio connection
python -m gcb test-connection

# Import PromptFoo results (writes to responses.db, uses model from config if not specified)
python -m gcb import-results

# Or specify model explicitly
python -m gcb import-results --model "My Model Name"

# Configure model settings
python -m gcb set-config --model gpt-4 --provider openrouter

# Evaluate responses (reads from responses.db, writes evaluations)
python -m gcb evaluate

# Generate report (reads from both databases)
python -m gcb report

# Run verification (checks both databases)
python -m gcb verify
```

## Benchmark Pipeline

### Web-Based Launcher (Easiest - Recommended for Non-Engineers)

The easiest way to run the benchmark pipeline is using the web-based launcher:

**macOS**: Double-click `run_pipeline.command` in Finder

**Or from terminal:**
```bash
streamlit run run_pipeline_ui.py
```

This opens a user-friendly web interface in your browser where you can:
- Configure model settings with a simple form
- Run the full pipeline with one click
- Monitor progress in real-time
- Test your connection before running

The PromptFoo step will automatically open in a separate Terminal window so you can monitor its progress.

See [GUI_README.md](GUI_README.md) for detailed instructions.

### Interactive Wizard (Command-Line)

For command-line users, you can use the interactive wizard:

```bash
python pipeline.py
```

This wizard guides you through each step with helpful prompts and status checks. You can:
- Run individual steps
- Run all steps sequentially
- Check pipeline status
- Override configuration settings

### Manual Steps

If you prefer to run steps manually:

1. **Prepare**: Export questions to PromptFoo YAML format
   ```bash
   python -m gcb prepare
   ```

2. **Execute**: Run PromptFoo against LM Studio (or other LLM)
   ```bash
   promptfoo eval -c prompts/promptfoo.yaml
   ```

3. **Import**: Import results into database
   ```bash
   python -m gcb import-results
   ```

4. **Evaluate**: Use LLM to judge responses
   ```bash
   python -m gcb evaluate
   ```

5. **Report**: Generate benchmark statistics
   ```bash
   python -m gcb report
   ```

## Configuration

### Easy Model Configuration (No Code Editing Required!)

You can configure models in three ways:

#### 1. **Using the UI (Easiest)**
Go to the **⚙️ Settings** page in the Streamlit UI:
```bash
streamlit run ui/app.py
```
Then navigate to Settings → Model Configuration. Use the preset buttons or customize your settings.

#### 2. **Using CLI Commands**
Set configuration values without editing files:
```bash
# Set model and provider
python -m gcb set-config --model gpt-4 --provider openrouter

# Set base URL and API key
python -m gcb set-config --base-url https://openrouter.ai/api/v1 --api-key $OPENROUTER_API_KEY

# Set evaluator model separately
python -m gcb set-config --evaluator-model gpt-4o-mini
```

#### 3. **Override on Command Line (No Config Changes)**
Run tests with different models without changing config.yaml:
```bash
# Test a different model without editing config
python -m gcb prepare --model gpt-4 --provider openrouter --base-url https://openrouter.ai/api/v1

# Import results with model name
python -m gcb import-results --model "My Model Name"
```

#### 4. **Manual Configuration (Traditional)**
Edit `config.yaml` directly:

```yaml
llm:
  provider: lmstudio
  base_url: http://localhost:1234/v1
  api_key: lm-studio
  test_model: local-model
  evaluator_model: local-model

database:
  # Dual database mode - questions and responses stored separately
  questions_db: questions.db  # Database for Question table
  responses_db: responses.db  # Database for Model, TestRun, Response, and Evaluation tables

evaluation:
  temperature: 0.1
  max_tokens: 30000
```

### Quick Setup Examples

**LM Studio (Local):**
```bash
python -m gcb set-config --provider lmstudio --base-url http://localhost:1234/v1 --model qwen/qwen3-4b
```

**OpenRouter:**
```bash
python -m gcb set-config --provider openrouter --base-url https://openrouter.ai/api/v1 --model openai/gpt-4o-mini --api-key $OPENROUTER_API_KEY
```

**Test Connection:**
```bash
python -m gcb test-connection
```

## Project Structure

```
benchmark/
├── config.yaml              # Configuration (includes database paths)
├── questions.db             # Questions database (test prompts)
├── responses.db             # Responses database (test results)
├── requirements.txt         # Python dependencies
├── README.md                # This file
│
├── gcb/                     # Python package
│   ├── __init__.py
│   ├── __main__.py         # CLI entry point
│   ├── cli.py              # Command-line interface
│   ├── database.py         # SQLAlchemy models & dual-DB manager
│   ├── evaluator.py        # LLM evaluation logic
│   ├── promptfoo_bridge.py # PromptFoo integration
│   └── reporter.py         # Statistics & reports
│
├── ui/
│   └── app.py              # Streamlit application
│
├── prompts/                 # Generated PromptFoo files
├── output/                  # Generated reports
└── archive/                 # Previous versions
```

### Database Schema

**questions.db** contains:
- `questions` table: Individual test prompts with acceptance levels and prompt types

**responses.db** contains:
- `models` table: LLM models being tested
- `test_runs` table: Execution batches
- `responses` table: Raw LLM outputs (includes denormalized question data)
- `evaluations` table: LLM judge verdicts for each response

**Note**: The `responses` table stores denormalized copies of question data (`question_text`, `acceptance_level`, `prompt_type`) to ensure historical responses remain accurate even if questions are later modified or deleted.

## Requirements

- Python 3.9+
- Node.js (for PromptFoo)
- LM Studio or OpenRouter API access

## License

MIT

