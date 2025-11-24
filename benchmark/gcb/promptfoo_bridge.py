"""
PromptFoo integration for Great Commission Benchmark.

Handles:
- Exporting questions to PromptFoo YAML format
- Running PromptFoo evaluations
- Importing results back to SQLite
"""

import json
import subprocess
import yaml
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any

from gcb.database import (
    get_db,
    DatabaseManager,
    Question,
    Conversation,
    Model,
    TestRun,
    Response,
    AcceptanceLevel,
    PromptType,
    TestRunStatus,
)


class PromptFooBridge:
    """Bridge between GCB database and PromptFoo."""

    def __init__(
        self,
        db_path: str = "gcb.db",
        output_dir: str = "prompts",
        config_path: str = "config.yaml",
    ):
        """Initialize the PromptFoo bridge.
        
        Args:
            db_path: Path to SQLite database
            output_dir: Directory for generated PromptFoo files
            config_path: Path to GCB config file
        """
        self.db = get_db(db_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.config_path = Path(config_path)
        self.config = self._load_config()

    def _load_config(self) -> dict:
        """Load configuration from config.yaml."""
        if self.config_path.exists():
            with open(self.config_path) as f:
                return yaml.safe_load(f) or {}
        return {}

    def get_llm_config(self) -> dict:
        """Get LLM configuration for PromptFoo."""
        llm_config = self.config.get("llm", {})
        return {
            "base_url": llm_config.get("base_url", "http://localhost:1234/v1"),
            "api_key": llm_config.get("api_key", "lm-studio"),
            "test_model": llm_config.get("test_model", "local-model"),
            "evaluator_model": llm_config.get("evaluator_model", "local-model"),
        }

    def export_questions(
        self,
        level_filter: Optional[AcceptanceLevel] = None,
        type_filter: Optional[PromptType] = None,
        output_file: str = "promptfoo.yaml",
    ) -> Path:
        """Export questions to PromptFoo YAML format.
        
        Args:
            level_filter: Optional filter by acceptance level
            type_filter: Optional filter by prompt type
            output_file: Output filename
            
        Returns:
            Path to generated YAML file
        """
        llm_config = self.get_llm_config()
        
        with self.db.get_session() as session:
            query = session.query(Question)
            
            if level_filter:
                query = query.filter(Question.acceptance_level == level_filter)
            if type_filter:
                query = query.filter(Question.prompt_type == type_filter)
            
            questions = query.all()
            
            if not questions:
                raise ValueError("No questions found matching filters")
            
            # Build PromptFoo config
            tests = []
            for q in questions:
                test = {
                    "vars": {
                        "question": q.text,
                    },
                    "metadata": {
                        "id": q.id,
                        "acceptance_level": q.acceptance_level.value,
                        "prompt_type": q.prompt_type.value,
                    }
                }
                tests.append(test)
            
            promptfoo_config = {
                "description": f"Great Commission Benchmark - {len(questions)} questions",
                "providers": [
                    {
                        "id": f"openai:chat:{llm_config['test_model']}",
                        "config": {
                            "apiHost": llm_config["base_url"],
                            "apiKey": llm_config["api_key"],
                        }
                    }
                ],
                "prompts": ["{{question}}"],
                "tests": tests,
                "outputPath": str(self.output_dir / "results.json"),
            }
            
            output_path = self.output_dir / output_file
            with open(output_path, "w") as f:
                yaml.dump(promptfoo_config, f, default_flow_style=False, sort_keys=False)
            
            return output_path

    def export_conversations(
        self,
        level_filter: Optional[AcceptanceLevel] = None,
        output_file: str = "promptfoo_conversations.yaml",
    ) -> Path:
        """Export conversations (multi-turn) to PromptFoo YAML format.
        
        Args:
            level_filter: Optional filter by acceptance level
            output_file: Output filename
            
        Returns:
            Path to generated YAML file
        """
        llm_config = self.get_llm_config()
        
        with self.db.get_session() as session:
            query = session.query(Conversation)
            
            if level_filter:
                query = query.filter(Conversation.acceptance_level == level_filter)
            
            conversations = query.all()
            
            if not conversations:
                raise ValueError("No conversations found matching filters")
            
            # Build PromptFoo config for conversations
            tests = []
            for conv in conversations:
                turns = conv.get_turns()
                
                # For multi-turn, we'll test the final state
                test = {
                    "vars": {
                        "conversation": json.dumps(turns),
                        "conversation_name": conv.name,
                    },
                    "metadata": {
                        "id": conv.id,
                        "acceptance_level": conv.acceptance_level.value,
                        "turn_count": len(turns),
                    }
                }
                tests.append(test)
            
            promptfoo_config = {
                "description": f"Great Commission Benchmark - {len(conversations)} conversations",
                "providers": [
                    {
                        "id": f"openai:chat:{llm_config['test_model']}",
                        "config": {
                            "apiHost": llm_config["base_url"],
                            "apiKey": llm_config["api_key"],
                        }
                    }
                ],
                "prompts": ["{{conversation}}"],
                "tests": tests,
                "outputPath": str(self.output_dir / "conversation_results.json"),
            }
            
            output_path = self.output_dir / output_file
            with open(output_path, "w") as f:
                yaml.dump(promptfoo_config, f, default_flow_style=False, sort_keys=False)
            
            return output_path

    def run_promptfoo(
        self,
        config_file: str = "promptfoo.yaml",
        verbose: bool = False,
    ) -> tuple[bool, str]:
        """Run PromptFoo evaluation.
        
        Args:
            config_file: PromptFoo config file to use
            verbose: Whether to show verbose output
            
        Returns:
            Tuple of (success, output_message)
        """
        config_path = self.output_dir / config_file
        
        if not config_path.exists():
            return False, f"Config file not found: {config_path}"
        
        cmd = ["npx", "promptfoo@latest", "eval", "-c", str(config_path), "--output", "json"]
        
        if verbose:
            cmd.append("--verbose")
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600,  # 10 minute timeout
            )
            
            if result.returncode == 0:
                return True, "PromptFoo evaluation completed successfully"
            else:
                return False, f"PromptFoo error: {result.stderr}"
                
        except subprocess.TimeoutExpired:
            return False, "PromptFoo evaluation timed out"
        except FileNotFoundError:
            return False, "npx not found. Please install Node.js and npm."
        except Exception as e:
            return False, f"Error running PromptFoo: {str(e)}"

    def import_results(
        self,
        results_file: str = "results.json",
        model_name: str = "local-model",
        test_run_name: Optional[str] = None,
    ) -> tuple[int, List[str]]:
        """Import PromptFoo results into the database.
        
        Args:
            results_file: Path to PromptFoo results JSON
            model_name: Name of the model tested
            test_run_name: Optional name for the test run
            
        Returns:
            Tuple of (responses_imported, errors)
        """
        results_path = self.output_dir / results_file
        
        if not results_path.exists():
            return 0, [f"Results file not found: {results_path}"]
        
        with open(results_path) as f:
            results_data = json.load(f)
        
        imported = 0
        errors = []
        
        with self.db.get_session() as session:
            # Create or get model
            model = session.query(Model).filter(Model.name == model_name).first()
            if not model:
                llm_config = self.get_llm_config()
                model = Model(
                    name=model_name,
                    provider=self.config.get("llm", {}).get("provider", "lmstudio"),
                    api_identifier=llm_config.get("test_model", model_name),
                )
                session.add(model)
                session.flush()
            
            # Create test run
            test_run = TestRun(
                name=test_run_name or f"PromptFoo Import {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                status=TestRunStatus.COMPLETED,
                completed_at=datetime.utcnow(),
            )
            test_run.set_config({
                "source": "promptfoo",
                "results_file": str(results_path),
            })
            session.add(test_run)
            session.flush()
            
            # Process results
            results_list = results_data.get("results", [])
            
            for result in results_list:
                try:
                    # Get question ID from metadata
                    metadata = result.get("vars", {}).get("__metadata", {})
                    if not metadata:
                        # Try alternate location
                        for test in results_data.get("table", {}).get("body", []):
                            if test.get("vars", {}).get("question") == result.get("vars", {}).get("question"):
                                metadata = test.get("test", {}).get("metadata", {})
                                break
                    
                    question_id = metadata.get("id") if metadata else None
                    
                    # Get response
                    response_text = result.get("response", {}).get("output", "")
                    if isinstance(response_text, dict):
                        response_text = json.dumps(response_text)
                    
                    latency = result.get("response", {}).get("latencyMs")
                    tokens = result.get("response", {}).get("tokenUsage", {}).get("total")
                    error = result.get("error")
                    
                    # Create response record
                    response = Response(
                        test_run_id=test_run.id,
                        model_id=model.id,
                        question_id=question_id,
                        response_text=response_text,
                        latency_ms=latency,
                        token_count=tokens,
                        error=error,
                    )
                    session.add(response)
                    imported += 1
                    
                except Exception as e:
                    errors.append(f"Error processing result: {str(e)}")
            
            session.commit()
        
        return imported, errors

    def create_test_run(
        self,
        name: Optional[str] = None,
        config: Optional[dict] = None,
    ) -> str:
        """Create a new test run record.
        
        Args:
            name: Optional name for the test run
            config: Optional configuration dict
            
        Returns:
            Test run ID
        """
        with self.db.get_session() as session:
            test_run = TestRun(
                name=name or f"Test Run {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                status=TestRunStatus.PENDING,
            )
            if config:
                test_run.set_config(config)
            session.add(test_run)
            session.commit()
            return test_run.id

    def update_test_run_status(
        self,
        test_run_id: str,
        status: TestRunStatus,
    ) -> None:
        """Update test run status.
        
        Args:
            test_run_id: Test run ID
            status: New status
        """
        with self.db.get_session() as session:
            test_run = session.query(TestRun).filter(TestRun.id == test_run_id).first()
            if test_run:
                test_run.status = status
                if status == TestRunStatus.COMPLETED:
                    test_run.completed_at = datetime.utcnow()
                session.commit()


def prepare_benchmark(
    db_path: str = "gcb.db",
    output_dir: str = "prompts",
    config_path: str = "config.yaml",
) -> Path:
    """Prepare benchmark by exporting questions to PromptFoo format.
    
    Args:
        db_path: Path to database
        output_dir: Output directory
        config_path: Config file path
        
    Returns:
        Path to generated config file
    """
    bridge = PromptFooBridge(db_path, output_dir, config_path)
    return bridge.export_questions()


def run_benchmark(
    db_path: str = "gcb.db",
    output_dir: str = "prompts",
    config_path: str = "config.yaml",
    verbose: bool = False,
) -> tuple[bool, str]:
    """Run the benchmark using PromptFoo.
    
    Args:
        db_path: Path to database
        output_dir: Output directory
        config_path: Config file path
        verbose: Verbose output
        
    Returns:
        Tuple of (success, message)
    """
    bridge = PromptFooBridge(db_path, output_dir, config_path)
    return bridge.run_promptfoo(verbose=verbose)


def import_benchmark_results(
    db_path: str = "gcb.db",
    output_dir: str = "prompts",
    config_path: str = "config.yaml",
    model_name: str = "local-model",
) -> tuple[int, List[str]]:
    """Import benchmark results from PromptFoo.
    
    Args:
        db_path: Path to database
        output_dir: Output directory
        config_path: Config file path
        model_name: Name of model tested
        
    Returns:
        Tuple of (imported_count, errors)
    """
    bridge = PromptFooBridge(db_path, output_dir, config_path)
    return bridge.import_results(model_name=model_name)


if __name__ == "__main__":
    # Quick test
    from gcb.database import init_db
    
    # Initialize database
    db = init_db("test_promptfoo.db")
    
    # Add a test question
    with db.get_session() as session:
        q = Question(
            text="What are the historical origins of Christian missionary work?",
            acceptance_level=AcceptanceLevel.GREEN,
            prompt_type=PromptType.DIRECT,
        )
        session.add(q)
        session.commit()
    
    # Test export
    bridge = PromptFooBridge("test_promptfoo.db", "test_prompts")
    
    try:
        path = bridge.export_questions()
        print(f"Exported to: {path}")
        
        with open(path) as f:
            print(f.read())
    finally:
        # Cleanup
        Path("test_promptfoo.db").unlink(missing_ok=True)
        import shutil
        shutil.rmtree("test_prompts", ignore_errors=True)

