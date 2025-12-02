# Benchmark V2 Pipeline

A templateable, step-by-step pipeline for running LLM benchmarks with flexible evaluation.

## Quick Start

```bash
# 1. Setup folders and database
python 1_setup.py

# 2. Add your question CSVs to _1_questions/
# 3. Edit _2_model-list/model-list.csv with your models

# 4. Generate promptfoo configs
python 2_build_foo.py

# 5. Run evaluations (requires LM Studio running on localhost:1234)
python 3_run_foo.py

# 6. Import results into database
python 4_import.py

# 7. Run LLM-as-judge evaluation
python 5_evaluator.py --name "my-evaluation"
```

## Folder Structure

```
benchmark_v2/
├── _1_questions/        # Drop CSV files here
├── _2_model-list/       # model-list.csv with model identifiers
├── _3_promptfoo/        # Generated YAML + results per model
├── _4_output/           # experiment.db + analysis reports
├── 1_setup.py           # Initialize folders and database
├── 2_build_foo.py       # Generate promptfoo YAML files per model
├── 3_run_foo.py         # Execute all promptfoo YAMLs
├── 4_import.py          # Import results into SQLite
├── 5_evaluator.py       # LLM-as-judge evaluation
└── requirements.txt
```

## Question CSV Format

CSV files in `_1_questions/` should have these columns:

| Column | Required | Description |
|--------|----------|-------------|
| text | Yes | The question/prompt text |
| acceptance_level | Yes | green/orange/red |
| prompt_type | No | direct/roleplay/encoded (default: direct) |
| tags | No | Comma-separated tags |
| notes | No | Additional notes |

Example:
```csv
text,acceptance_level,prompt_type,tags,notes
What are the historical origins of Christian missionary work?,green,direct,historical,
```

## Model List Format

`_2_model-list/model-list.csv` is a single-column CSV:

```csv
model_id
qwen/qwen3-30b
mistral/mistral-7b
llama/llama-8b
```

All models use LM Studio at `http://localhost:1234/v1`.

## Pipeline Steps

### 1. 1_setup.py

Creates the folder structure and initializes `_4_output/experiment.db` with the schema:

- `questions` - Imported from CSVs
- `models` - Parsed from model-list.csv
- `responses` - From promptfoo results
- `evaluation_runs` - Tracks each evaluation pass
- `evaluations` - One row per (response, eval_run)

### 2. 2_build_foo.py

- Reads all CSV files from `_1_questions/`
- Reads model identifiers from `_2_model-list/model-list.csv`
- Generates `_3_promptfoo/{model-name}-promptfoo.yaml` for each model

### 3. 3_run_foo.py

- Loops through all `_3_promptfoo/*-promptfoo.yaml` files
- Executes `npx promptfoo eval` for each
- Generates `_3_promptfoo/{model-name}-results.json`

### 4. 4_import.py

- Imports questions from CSVs into database
- Imports models from model-list.csv
- Imports responses from all `*-results.json` files

### 5. 5_evaluator.py

Flexible LLM-as-judge evaluation with custom prompts.

```bash
# Use default prompt (approved/refused/compromised/ambiguous)
python 5_evaluator.py --name "approval-v1"

# Custom inline prompt
python 5_evaluator.py --prompt "Rate sentiment: positive/negative/neutral" --name "sentiment"

# Prompt from file
python 5_evaluator.py --prompt-file prompts/my-eval.txt --name "custom-eval"

# Filter by model and limit
python 5_evaluator.py --name "test" --model "qwen/qwen3-30b" --limit 10

# Use different evaluator model
python 5_evaluator.py --name "eval-v2" --evaluator-model "mistral/mistral-7b"
```

**Options:**
- `--name, -n` - Name for this evaluation run (required)
- `--prompt, -p` - Evaluation prompt template
- `--prompt-file, -f` - Read prompt from file
- `--evaluator-model, -e` - Model for evaluation (default: qwen/qwen3-30b)
- `--model, -m` - Filter responses by model_id
- `--limit, -l` - Limit number of responses
- `--base-url` - LLM API base URL
- `--api-key` - LLM API key

## Database Schema

```sql
-- Questions imported from CSVs
questions(id, text, acceptance_level, prompt_type, tags, notes, source_file, created_at)

-- Models from model-list.csv
models(id, model_id, created_at)

-- Responses from promptfoo results
responses(id, model_id, question_id, response_text, latency_ms, token_count, error, source_file, created_at)

-- Each evaluation run (supports multiple classification schemes)
evaluation_runs(id, name, prompt, evaluator_model, created_at)

-- Evaluations (one per response+run combination)
evaluations(id, response_id, evaluation_run_id, verdict, reasoning, confidence, created_at)
```

## Requirements

- Python 3.11+
- Node.js (for npx/promptfoo)
- LM Studio running on localhost:1234

Install Python dependencies:
```bash
pip install -r requirements.txt
```

## Multiple Evaluation Runs

The pipeline supports running multiple evaluation passes with different prompts/criteria:

```bash
# First evaluation: approval check
python 5_evaluator.py --name "approval-v1" 

# Second evaluation: sentiment analysis
python 5_evaluator.py --prompt "Is this response positive, negative, or neutral?" --name "sentiment-v1"

# Third evaluation: helpfulness
python 5_evaluator.py --prompt "Rate helpfulness: helpful, unhelpful, partially_helpful" --name "helpfulness-v1"
```

Each run creates a new `evaluation_run` record, and responses can have multiple evaluations from different runs.

