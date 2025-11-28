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
    get_db_from_config,
    DatabaseManager,
    Question,
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
        questions_db_path: str = "questions.db",
        responses_db_path: str = "responses.db",
        output_dir: str = "prompts",
        config_path: str = "config.yaml",
    ):
        """Initialize the PromptFoo bridge.
        
        Args:
            questions_db_path: Path to questions database (used if config doesn't specify)
            responses_db_path: Path to responses database (used if config doesn't specify)
            output_dir: Directory for generated PromptFoo files
            config_path: Path to GCB config file
        """
        self.config_path = Path(config_path)
        self.config = self._load_config()
        
        # Get database from config, or use provided paths
        try:
            self.db = get_db_from_config(str(self.config_path))
        except Exception:
            # Fallback to provided paths
            self.db = get_db(questions_db_path, responses_db_path)
        
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

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
        model_override: Optional[str] = None,
        provider_override: Optional[str] = None,
        base_url_override: Optional[str] = None,
        api_key_override: Optional[str] = None,
    ) -> Path:
        """Export questions to PromptFoo YAML format.
        
        Args:
            level_filter: Optional filter by acceptance level
            type_filter: Optional filter by prompt type
            output_file: Output filename
            model_override: Override model name
            provider_override: Override provider
            base_url_override: Override base URL
            api_key_override: Override API key
            
        Returns:
            Path to generated YAML file
        """
        llm_config = self.get_llm_config()
        
        # Apply overrides if provided
        if model_override:
            llm_config["test_model"] = model_override
        if provider_override:
            llm_config["provider"] = provider_override
        if base_url_override:
            llm_config["base_url"] = base_url_override
        if api_key_override:
            llm_config["api_key"] = api_key_override
        promptfoo_config_settings = self.config.get("promptfoo", {})
        
        with self.db.get_questions_session() as session:
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
            
            # Build provider config with timeout and retry settings
            # PromptFoo's OpenAI provider uses apiBaseUrl (not apiHost) and needs full URL including /v1
            provider_config = {
                "apiBaseUrl": llm_config["base_url"],
                "apiKey": llm_config["api_key"],
            }
            
            # Add max_tokens from evaluation config
            # Use a very high default (100000) to avoid truncating long responses
            # This allows thinking models and verbose responses to complete fully
            eval_config = self.config.get("evaluation", {})
            max_tokens = eval_config.get("max_tokens", 100000)  # Default to 100k tokens
            provider_config["maxTokens"] = max_tokens
            
            # Add timeout if configured
            if promptfoo_config_settings.get("timeout_ms"):
                provider_config["timeout"] = promptfoo_config_settings["timeout_ms"]
            
            # Add retry config if configured
            if promptfoo_config_settings.get("retry_attempts"):
                provider_config["retry"] = {
                    "attempts": promptfoo_config_settings["retry_attempts"],
                    "delay": promptfoo_config_settings.get("retry_delay_ms", 1000),
                }
            
            promptfoo_config = {
                "description": f"Great Commission Benchmark - {len(questions)} questions",
                "providers": [
                    {
                        "id": f"openai:chat:{llm_config['test_model']}",
                        "config": provider_config,
                    }
                ],
                "prompts": ["{{question}}"],
                "tests": tests,
                "outputPath": str(self.output_dir / "results.json"),
            }
            
            # Add options if maxConcurrency is configured
            max_concurrency = promptfoo_config_settings.get("max_concurrency")
            if max_concurrency:
                promptfoo_config["options"] = {
                    "maxConcurrency": max_concurrency,
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
        
        cmd = ["npx", "promptfoo@latest", "eval", "-c", str(config_path)]
        
        if verbose:
            cmd.append("--verbose")
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=3600,  # 60 minute timeout
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
        provider_override: Optional[str] = None,
        api_identifier_override: Optional[str] = None,
        base_url_override: Optional[str] = None,
        api_key_override: Optional[str] = None,
    ) -> tuple[int, List[str]]:
        """Import PromptFoo results into the database.
        
        Args:
            results_file: Path to PromptFoo results JSON
            model_name: Name of the model tested
            test_run_name: Optional name for the test run
            provider_override: Override provider from config (used when model settings were overridden)
            api_identifier_override: Override API identifier/model identifier (used when model settings were overridden)
            base_url_override: Override base URL from config (used when model settings were overridden)
            api_key_override: Override API key from config (used when model settings were overridden, stored as metadata only)
            
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
            # Create or get model - use combination of name, provider, and api_identifier to distinguish
            # Use overrides if provided, otherwise fall back to config
            llm_config = self.get_llm_config()
            provider = provider_override if provider_override else self.config.get("llm", {}).get("provider", "lmstudio")
            # api_identifier should be the actual model identifier used (override or config), not the display name
            api_identifier = api_identifier_override if api_identifier_override else llm_config.get("test_model", model_name)
            
            # Try to find existing model by name, provider, and api_identifier
            model = session.query(Model).filter(
                Model.name == model_name,
                Model.provider == provider,
                Model.api_identifier == api_identifier
            ).first()
            
            if not model:
                # Create new model with full identification
                model = Model(
                    name=model_name,
                    provider=provider,
                    api_identifier=api_identifier,
                )
                session.add(model)
                session.flush()
            
            # Create test run with model information in config
            test_run = TestRun(
                name=test_run_name or f"PromptFoo Import {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                status=TestRunStatus.COMPLETED,
                completed_at=datetime.utcnow(),
            )
            # Build test run config with all model information and overrides
            test_run_config = {
                "source": "promptfoo",
                "results_file": str(results_path),
                "model_name": model.name,
                "model_provider": model.provider,
                "model_api_identifier": model.api_identifier,
                "model_id": model.id,
            }
            
            # Store override information if provided (for tracking what was actually used)
            if base_url_override:
                test_run_config["base_url_override"] = base_url_override
            if api_key_override:
                # Store that API key was overridden, but don't store the actual key for security
                test_run_config["api_key_override"] = True
            
            test_run.set_config(test_run_config)
            session.add(test_run)
            session.flush()
            
            # Process results
            # PromptFoo results structure: data['results']['results'] is the list
            results_list = results_data.get("results", {}).get("results", [])
            
            # Get questions database session
            questions_session = self.db.get_questions_session()
            
            try:
                for result in results_list:
                    try:
                        # Get question ID from metadata
                        # Metadata can be directly on result or in testCase
                        metadata = result.get("metadata", {})
                        if not metadata:
                            metadata = result.get("testCase", {}).get("metadata", {})
                        
                        question_id = metadata.get("id") if metadata else None
                        acceptance_level = metadata.get("acceptance_level")
                        prompt_type = metadata.get("prompt_type")
                        
                        # Get question data for denormalization
                        question_text = None
                        question_acceptance_level = None
                        question_prompt_type = None
                        
                        if question_id:
                            # Get question from questions database
                            from gcb.database import Question
                            question = questions_session.query(Question).filter(
                                Question.id == question_id
                            ).first()
                            if question:
                                question_text = question.text
                                question_acceptance_level = question.acceptance_level
                                question_prompt_type = question.prompt_type
                        
                        # Fallback to metadata if question not found
                        if not question_text and metadata.get("question"):
                            question_text = metadata.get("question")
                        
                        # Use metadata values if question not found in DB
                        if not question_acceptance_level and acceptance_level:
                            from gcb.database import AcceptanceLevel
                            try:
                                question_acceptance_level = AcceptanceLevel(acceptance_level)
                            except ValueError:
                                pass
                        
                        if not question_prompt_type and prompt_type:
                            from gcb.database import PromptType
                            try:
                                question_prompt_type = PromptType(prompt_type)
                            except ValueError:
                                pass
                        
                        # Get response
                        response_text = result.get("response", {}).get("output", "")
                        # Convert to string if it's not already
                        if isinstance(response_text, (dict, list)):
                            response_text = json.dumps(response_text)
                        elif response_text is None:
                            response_text = ""
                        else:
                            response_text = str(response_text)
                        
                        latency = result.get("response", {}).get("latencyMs")
                        tokens = result.get("response", {}).get("tokenUsage", {}).get("total")
                        error = result.get("error")
                        
                        # Create response record with denormalized question data
                        response = Response(
                            test_run_id=test_run.id,
                            model_id=model.id,
                            question_id=question_id,
                            question_text=question_text,
                            acceptance_level=question_acceptance_level,
                            prompt_type=question_prompt_type,
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
            finally:
                if questions_session:
                    questions_session.close()
        
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

