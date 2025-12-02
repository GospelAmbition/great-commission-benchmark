#!/usr/bin/env python3
"""
Import script for Benchmark V2 Pipeline.

Imports questions from CSVs and results from promptfoo JSON into experiment.db.
"""

import csv
import json
import uuid
import importlib.util
from pathlib import Path
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Import models from 1_setup.py (using importlib since module name starts with number)
setup_spec = importlib.util.spec_from_file_location("setup", Path(__file__).parent / "1_setup.py")
setup_module = importlib.util.module_from_spec(setup_spec)
setup_spec.loader.exec_module(setup_module)
Base = setup_module.Base
Question = setup_module.Question
Model = setup_module.Model
Response = setup_module.Response


def get_base_dir() -> Path:
    """Get the base directory (where this script is located)."""
    return Path(__file__).parent


def get_db_session():
    """Get a database session."""
    base = get_base_dir()
    db_path = base / "_4_output" / "experiment.db"
    
    if not db_path.exists():
        raise FileNotFoundError(
            f"Database not found: {db_path}\n"
            "Run: python 1_setup.py first"
        )
    
    engine = create_engine(f"sqlite:///{db_path}", echo=False)
    Session = sessionmaker(bind=engine)
    return Session()


def import_questions(session) -> dict[str, str]:
    """Import questions from CSV files.
    
    Returns:
        Dictionary mapping (source_file, text) to question_id
    """
    base = get_base_dir()
    questions_dir = base / "_1_questions"
    
    if not questions_dir.exists():
        raise FileNotFoundError(f"Questions folder not found: {questions_dir}")
    
    csv_files = list(questions_dir.glob("*.csv"))
    if not csv_files:
        raise FileNotFoundError(f"No CSV files found in {questions_dir}")
    
    question_map = {}
    imported = 0
    skipped = 0
    
    for csv_file in csv_files:
        print(f"  Processing: {csv_file.name}")
        with open(csv_file, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                text = row.get("text", "").strip()
                if not text:
                    continue
                
                # Check if question already exists (by text and source file)
                existing = session.query(Question).filter(
                    Question.text == text,
                    Question.source_file == csv_file.name
                ).first()
                
                if existing:
                    question_map[(csv_file.name, text)] = existing.id
                    skipped += 1
                    continue
                
                # Create new question
                question = Question(
                    id=str(uuid.uuid4()),
                    text=text,
                    acceptance_level=row.get("acceptance_level", "").strip(),
                    prompt_type=row.get("prompt_type", "direct").strip(),
                    tags=row.get("tags", ""),
                    notes=row.get("notes", ""),
                    source_file=csv_file.name,
                )
                session.add(question)
                question_map[(csv_file.name, text)] = question.id
                imported += 1
    
    session.commit()
    print(f"  Imported: {imported}, Skipped (existing): {skipped}")
    return question_map


def import_models(session) -> dict[str, str]:
    """Import models from model-list.csv.
    
    Returns:
        Dictionary mapping model_id to database id
    """
    base = get_base_dir()
    model_list_path = base / "_2_model-list" / "model-list.csv"
    
    if not model_list_path.exists():
        raise FileNotFoundError(f"Model list not found: {model_list_path}")
    
    model_map = {}
    imported = 0
    skipped = 0
    
    with open(model_list_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            model_id = row.get("model_id", "").strip()
            if not model_id:
                continue
            
            # Check if model already exists
            existing = session.query(Model).filter(
                Model.model_id == model_id
            ).first()
            
            if existing:
                model_map[model_id] = existing.id
                skipped += 1
                continue
            
            # Create new model
            model = Model(
                id=str(uuid.uuid4()),
                model_id=model_id,
            )
            session.add(model)
            model_map[model_id] = model.id
            imported += 1
    
    session.commit()
    print(f"  Imported: {imported}, Skipped (existing): {skipped}")
    return model_map


def import_results(session, model_map: dict[str, str], question_map: dict[tuple[str, str], str]) -> int:
    """Import results from promptfoo JSON files.
    
    Args:
        session: Database session
        model_map: Dictionary mapping model_id to database id
        question_map: Dictionary mapping (source_file, text) to question_id
    
    Returns:
        Number of responses imported
    """
    base = get_base_dir()
    promptfoo_dir = base / "_3_promptfoo"
    
    if not promptfoo_dir.exists():
        raise FileNotFoundError(f"PromptFoo folder not found: {promptfoo_dir}")
    
    results_files = list(promptfoo_dir.glob("*-results.json"))
    if not results_files:
        print("  No results files found")
        return 0
    
    total_imported = 0
    
    for results_file in results_files:
        # Extract model name from filename
        model_name = results_file.stem.replace("-results", "")
        # Convert back to model_id format (e.g., "qwen-qwen3-30b" -> "qwen/qwen3-30b")
        # This is a heuristic - assumes first dash is the separator
        parts = model_name.split("-", 1)
        if len(parts) == 2:
            model_id = f"{parts[0]}/{parts[1]}"
        else:
            model_id = model_name
        
        print(f"  Processing: {results_file.name}")
        print(f"    Model: {model_id}")
        
        # Get model database ID
        db_model_id = model_map.get(model_id)
        if not db_model_id:
            # Try to find model in database by model_id
            model = session.query(Model).filter(Model.model_id == model_id).first()
            if model:
                db_model_id = model.id
            else:
                print(f"    Warning: Model not found in database, creating: {model_id}")
                model = Model(id=str(uuid.uuid4()), model_id=model_id)
                session.add(model)
                session.flush()
                db_model_id = model.id
                model_map[model_id] = db_model_id
        
        # Load results
        with open(results_file, encoding="utf-8") as f:
            data = json.load(f)
        
        results_list = data.get("results", {}).get("results", [])
        imported = 0
        skipped = 0
        not_found = 0
        
        for result in results_list:
            # Get metadata
            metadata = result.get("metadata", {})
            if not metadata:
                metadata = result.get("testCase", {}).get("metadata", {})
            
            # Get question text from vars (promptfoo stores it there)
            vars_data = result.get("vars", {})
            if not vars_data:
                vars_data = result.get("testCase", {}).get("vars", {})
            question_text = vars_data.get("question", "").strip()
            
            # Get source file from metadata
            source_file = metadata.get("source_file", "")
            
            # Find question by text and source_file (more reliable than ID)
            question_id = None
            if question_text and source_file:
                question_id = question_map.get((source_file, question_text))
            
            # Fallback: try to find by ID if we have it
            if not question_id:
                promptfoo_id = metadata.get("id")
                if promptfoo_id:
                    # Try direct lookup (in case IDs happen to match)
                    question = session.query(Question).filter(Question.id == promptfoo_id).first()
                    if question:
                        question_id = question.id
                    else:
                        # Try to find by text only (last resort)
                        question = session.query(Question).filter(Question.text == question_text).first()
                        if question:
                            question_id = question.id
            
            if not question_id:
                not_found += 1
                continue
            
            # Check if response already exists
            existing = session.query(Response).filter(
                Response.model_id == db_model_id,
                Response.question_id == question_id,
                Response.source_file == results_file.name
            ).first()
            
            if existing:
                skipped += 1
                continue
            
            # Get response data
            response_data = result.get("response", {})
            response_text = response_data.get("output", "")
            
            # Convert to string if needed
            if isinstance(response_text, (dict, list)):
                response_text = json.dumps(response_text)
            elif response_text is None:
                response_text = ""
            else:
                response_text = str(response_text)
            
            latency = response_data.get("latencyMs")
            tokens = response_data.get("tokenUsage", {}).get("total")
            error = result.get("error")
            
            # Create response
            response = Response(
                id=str(uuid.uuid4()),
                model_id=db_model_id,
                question_id=question_id,
                response_text=response_text,
                latency_ms=latency,
                token_count=tokens,
                error=error,
                source_file=results_file.name,
            )
            session.add(response)
            imported += 1
        
        session.commit()
        print(f"    Imported: {imported} responses, Skipped: {skipped}, Not found: {not_found}")
        total_imported += imported
    
    return total_imported


def main():
    """Import all data into the database."""
    print("=" * 50)
    print("Benchmark V2 - Import Data")
    print("=" * 50)
    print()
    
    session = get_db_session()
    
    try:
        # Import questions
        print("Importing questions...")
        question_map = import_questions(session)
        print(f"  Total questions in database: {session.query(Question).count()}")
        print()
        
        # Import models
        print("Importing models...")
        model_map = import_models(session)
        print(f"  Total models in database: {session.query(Model).count()}")
        print()
        
        # Import results
        print("Importing results...")
        total_responses = import_results(session, model_map, question_map)
        print(f"  Total responses in database: {session.query(Response).count()}")
        print()
        
        print("=" * 50)
        print("Import complete!")
        print()
        print("Database summary:")
        print(f"  Questions: {session.query(Question).count()}")
        print(f"  Models:    {session.query(Model).count()}")
        print(f"  Responses: {session.query(Response).count()}")
        print()
        print("Next step: python 5_evaluator.py --prompt 'Your prompt' --name 'run-name'")
        print("=" * 50)
        
    finally:
        session.close()


if __name__ == "__main__":
    main()



