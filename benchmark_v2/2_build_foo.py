#!/usr/bin/env python3
"""
Build script for Benchmark V2 Pipeline.

Parses question CSVs and model list, generates per-model promptfoo YAML files.
"""

import csv
import json
import uuid
from pathlib import Path
from typing import List, Dict, Any
import yaml


def get_base_dir() -> Path:
    """Get the base directory (where this script is located)."""
    return Path(__file__).parent


def load_questions() -> List[Dict[str, Any]]:
    """Load all questions from CSV files in _1_questions/ folder."""
    base = get_base_dir()
    questions_dir = base / "_1_questions"
    
    if not questions_dir.exists():
        raise FileNotFoundError(f"Questions folder not found: {questions_dir}")
    
    questions = []
    csv_files = list(questions_dir.glob("*.csv"))
    
    if not csv_files:
        raise FileNotFoundError(f"No CSV files found in {questions_dir}")
    
    for csv_file in csv_files:
        print(f"  Loading: {csv_file.name}")
        with open(csv_file, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Generate a unique ID for each question
                question = {
                    "id": str(uuid.uuid4()),
                    "text": row.get("text", ""),
                    "acceptance_level": row.get("acceptance_level", ""),
                    "prompt_type": row.get("prompt_type", "direct"),
                    "tags": row.get("tags", ""),
                    "notes": row.get("notes", ""),
                    "source_file": csv_file.name,
                }
                if question["text"]:  # Only add if there's actual text
                    questions.append(question)
    
    return questions


def load_models() -> List[str]:
    """Load model identifiers from _2_model-list/model-list.csv."""
    base = get_base_dir()
    model_list_path = base / "_2_model-list" / "model-list.csv"
    
    if not model_list_path.exists():
        raise FileNotFoundError(f"Model list not found: {model_list_path}")
    
    models = []
    with open(model_list_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            model_id = row.get("model_id", "").strip()
            if model_id:
                models.append(model_id)
    
    if not models:
        raise ValueError("No models found in model-list.csv")
    
    return models


def sanitize_filename(model_id: str) -> str:
    """Convert model ID to a safe filename."""
    # Replace slashes and other special chars with dashes
    return model_id.replace("/", "-").replace("\\", "-").replace(":", "-")


def generate_promptfoo_yaml(
    model_id: str,
    questions: List[Dict[str, Any]],
    output_dir: Path,
) -> Path:
    """Generate a promptfoo YAML file for a specific model."""
    
    safe_name = sanitize_filename(model_id)
    output_file = output_dir / f"{safe_name}-promptfoo.yaml"
    results_file = output_dir / f"{safe_name}-results.json"
    
    # Build test cases from questions
    tests = []
    for q in questions:
        test = {
            "vars": {
                "question": q["text"],
            },
            "metadata": {
                "id": q["id"],
                "acceptance_level": q["acceptance_level"],
                "prompt_type": q["prompt_type"],
                "source_file": q["source_file"],
            }
        }
        tests.append(test)
    
    # Build promptfoo config
    # LM Studio configuration (localhost:1234)
    config = {
        "description": f"Great Commission Benchmark - {model_id} - {len(questions)} questions",
        "providers": [
            {
                "id": f"openai:chat:{model_id}",
                "config": {
                    "apiBaseUrl": "http://localhost:1234/v1",
                    "apiKey": "lm-studio",
                    "maxTokens": 100000,
                    "timeout": 60000,
                },
            }
        ],
        "prompts": ["{{question}}"],
        "tests": tests,
        "outputPath": str(results_file),
    }
    
    # Write YAML file
    with open(output_file, "w", encoding="utf-8") as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
    
    return output_file


def main():
    """Build promptfoo YAML files for all models."""
    print("=" * 50)
    print("Benchmark V2 - Build PromptFoo Configs")
    print("=" * 50)
    print()
    
    base = get_base_dir()
    promptfoo_dir = base / "_3_promptfoo"
    promptfoo_dir.mkdir(exist_ok=True)
    
    # Load questions
    print("Loading questions...")
    questions = load_questions()
    print(f"  Loaded {len(questions)} questions")
    print()
    
    # Load models
    print("Loading models...")
    models = load_models()
    print(f"  Found {len(models)} models:")
    for m in models:
        print(f"    - {m}")
    print()
    
    # Generate YAML for each model
    print("Generating promptfoo configs...")
    generated = []
    for model_id in models:
        output_file = generate_promptfoo_yaml(model_id, questions, promptfoo_dir)
        generated.append(output_file)
        print(f"  ✓ {output_file.name}")
    
    print()
    print("=" * 50)
    print(f"Generated {len(generated)} promptfoo config files")
    print()
    print("Next step: python 3_run_foo.py")
    print("=" * 50)


if __name__ == "__main__":
    main()



