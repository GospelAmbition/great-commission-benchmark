# Great Commission Benchmark v0.2

This version of the Great Commission Benchmark has been updated to use OpenRouter.ai instead of LM Studio.

## Changes from v0.1

- **API Provider**: Switched from LM Studio to OpenRouter.ai
- **Dependencies**: Updated to use `openai` package instead of `requests`
- **Models**: Updated to use OpenRouter model names
- **Configuration**: Now requires OpenRouter API key instead of local LM Studio setup

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Get an API key from [OpenRouter.ai](https://openrouter.ai/)

3. Set the API key as an environment variable:
   ```bash
   export OPENROUTER_API_KEY='your-api-key-here'
   ```

## Usage

Run the benchmark:
```bash
python test.py
```

## Available Models

The following models are configured for testing:
- openai/gpt-4o
- openai/gpt-4o-mini
- anthropic/claude-3-5-sonnet-20241022
- anthropic/claude-3-5-haiku-20241022
- meta-llama/llama-3.1-8b-instruct
- meta-llama/llama-3.1-70b-instruct
- mistralai/mistral-7b-instruct
- mistralai/mixtral-8x7b-instruct

## Output

Results are saved to the `output/` directory:
- Individual model files: `{model_name}.md`
- Master results: `results.md`

## Configuration

You can customize the benchmark by modifying:
- `models.md`: List of models to test
- `questions.md`: List of questions to ask
- `test.py`: Evaluation model and other parameters
