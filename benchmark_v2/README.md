# Benchmark V2 Pipeline

A templateable, step-by-step pipeline for running LLM benchmarks with flexible evaluation.

## Quick Start

```bash
# 1. Setup folders and database
python setup.py

# 2. Add your question CSVs to questions/
# 3. Edit model-list/model-list.csv with your models

# 4. Generate promptfoo configs
python build_foo.py

# 5. Run evaluations (requires LM Studio running on localhost:1234)
python run_foo.py

# 6. Import results into database
python import.py

# 7. Run LLM-as-judge evaluation
python evaluator.py --name "my-evaluation"
```

## Folder Structure

```
benchmark_v2/
├── questions/           # Drop CSV files here
├── model-list/          # model-list.csv with model identifiers
├── promptfoo/           # Generated YAML + results per model
├── output/              # experiment.db + analysis reports
├── setup.py             # Initialize folders and database
├── build_foo.py         # Generate promptfoo YAML files per model
├── run_foo.py           # Execute all promptfoo YAMLs
├── import.py            # Import results into SQLite
├── evaluator.py         # LLM-as-judge evaluation
└── requirements.txt
```

## Question CSV Format

CSV files in `questions/` should have these columns:

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

`model-list/model-list.csv` is a single-column CSV:

```csv
model_id
qwen/qwen3-30b
mistral/mistral-7b
llama/llama-8b
```

All models use LM Studio at `http://localhost:1234/v1`.

## Pipeline Steps

### 1. setup.py

Creates the folder structure and initializes `output/experiment.db` with the schema:

- `questions` - Imported from CSVs
- `models` - Parsed from model-list.csv
- `responses` - From promptfoo results
- `evaluation_runs` - Tracks each evaluation pass
- `evaluations` - One row per (response, eval_run)

### 2. build_foo.py

- Reads all CSV files from `questions/`
- Reads model identifiers from `model-list/model-list.csv`
- Generates `promptfoo/{model-name}-promptfoo.yaml` for each model

### 3. run_foo.py

- Loops through all `promptfoo/*-promptfoo.yaml` files
- Executes `npx promptfoo eval` for each
- Generates `promptfoo/{model-name}-results.json`

### 4. import.py

- Imports questions from CSVs into database
- Imports models from model-list.csv
- Imports responses from all `*-results.json` files

### 5. evaluator.py

Flexible LLM-as-judge evaluation with custom prompts.

```bash
# Use default prompt (approved/refused/compromised/ambiguous)
python evaluator.py --name "approval-v1"

# Custom inline prompt
python evaluator.py --prompt "Rate sentiment: positive/negative/neutral" --name "sentiment"

# Prompt from file
python evaluator.py --prompt-file prompts/my-eval.txt --name "custom-eval"

# Filter by model and limit
python evaluator.py --name "test" --model "qwen/qwen3-30b" --limit 10

# Use different evaluator model
python evaluator.py --name "eval-v2" --evaluator-model "mistral/mistral-7b"
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
python evaluator.py --name "approval-v1" 

# Second evaluation: sentiment analysis
python evaluator.py --prompt "Is this response positive, negative, or neutral?" --name "sentiment-v1"

# Third evaluation: helpfulness
python evaluator.py --prompt "Rate helpfulness: helpful, unhelpful, partially_helpful" --name "helpfulness-v1"
```

Each run creates a new `evaluation_run` record, and responses can have multiple evaluations from different runs.

