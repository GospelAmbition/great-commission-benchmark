"""
Question generator for GCB Builder.

This module orchestrates LLM-based question generation:
- Loads category-specific prompts
- Calls LLM backends to generate questions
- Parses and validates responses
- Saves questions to the database
"""

import json
import re
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional

from gcb_builder.backends.base import CompletionRequest, CompletionResponse, LLMBackend
from gcb_builder.core.categories import CATEGORIES, get_category
from gcb_builder.core.database import get_db
from gcb_builder.core.models import Question
from gcb_builder.core.schemas import GeneratedQuestion, GenerationBatch
from gcb_builder.generation.prompt_loader import format_generation_prompt


@dataclass
class GenerationResult:
    """Result from a question generation run."""
    
    category_id: str
    total_generated: int
    saved_count: int
    failed_count: int
    questions: list[Question]
    errors: list[str]
    model_used: str
    duration_seconds: float


class QuestionGenerator:
    """
    Generates benchmark questions using LLM backends.
    
    Usage:
        generator = QuestionGenerator(backend)
        result = await generator.generate(
            category_id="3.2",
            count=10,
            model="gpt-4o"
        )
    """
    
    def __init__(self, backend: LLMBackend):
        """
        Initialize the generator.
        
        Args:
            backend: LLM backend to use for generation
        """
        self.backend = backend
    
    async def generate(
        self,
        category_id: str,
        count: int = 15,
        model: str = "gpt-4o",
        difficulty_distribution: Optional[dict[str, int]] = None,
        system_prompt: Optional[str] = None,
    ) -> GenerationResult:
        """
        Generate questions for a category.
        
        Args:
            category_id: Category ID (e.g., "3.2")
            count: Number of questions to generate
            model: Model identifier to use
            difficulty_distribution: Optional distribution by difficulty
            system_prompt: Optional custom system prompt
            
        Returns:
            GenerationResult with saved questions and any errors
        """
        import time
        start_time = time.time()
        
        # Validate category
        category = get_category(category_id)
        if not category:
            return GenerationResult(
                category_id=category_id,
                total_generated=0,
                saved_count=0,
                failed_count=0,
                questions=[],
                errors=[f"Invalid category ID: {category_id}"],
                model_used=model,
                duration_seconds=0,
            )
        
        # Format the generation prompt
        try:
            prompt = format_generation_prompt(
                category_id=category_id,
                count=count,
                difficulty_distribution=difficulty_distribution,
            )
        except (ValueError, FileNotFoundError) as e:
            return GenerationResult(
                category_id=category_id,
                total_generated=0,
                saved_count=0,
                failed_count=0,
                questions=[],
                errors=[str(e)],
                model_used=model,
                duration_seconds=0,
            )
        
        # Default system prompt
        if not system_prompt:
            system_prompt = (
                "You are an expert benchmark question designer for the Great Commission Benchmark. "
                "Your task is to generate high-quality test questions that evaluate LLM capabilities "
                "for Christian ministry applications. Generate questions that are realistic, varied, "
                "and will effectively test both capability and willingness. "
                "Always return valid JSON in the specified format."
            )
        
        # Call the LLM
        try:
            request = CompletionRequest(
                messages=[{"role": "user", "content": prompt}],
                model=model,
                system_prompt=system_prompt,
                temperature=0.7,
                max_tokens=4000,
            )
            response = await self.backend.complete(request)
            llm_response = response.content
        except Exception as e:
            return GenerationResult(
                category_id=category_id,
                total_generated=0,
                saved_count=0,
                failed_count=0,
                questions=[],
                errors=[f"LLM error: {str(e)}"],
                model_used=model,
                duration_seconds=time.time() - start_time,
            )
        
        # Parse the response
        questions, parse_errors = self._parse_response(llm_response, category)
        
        # Save to database
        saved_questions = []
        save_errors = []
        
        for q in questions:
            try:
                saved = self._save_question(q, category)
                saved_questions.append(saved)
            except Exception as e:
                save_errors.append(f"Failed to save question: {str(e)}")
        
        duration = time.time() - start_time
        
        return GenerationResult(
            category_id=category_id,
            total_generated=len(questions),
            saved_count=len(saved_questions),
            failed_count=len(questions) - len(saved_questions),
            questions=saved_questions,
            errors=parse_errors + save_errors,
            model_used=model,
            duration_seconds=duration,
        )
    
    def _parse_response(
        self,
        response: str,
        category: Any,
    ) -> tuple[list[GeneratedQuestion], list[str]]:
        """
        Parse LLM response to extract questions.
        
        Returns:
            Tuple of (questions, errors)
        """
        errors = []
        questions = []
        
        # Try to extract JSON from the response
        json_match = re.search(r"```json\s*(.*?)\s*```", response, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            # Try to find raw JSON
            json_match = re.search(r"\{[\s\S]*\}", response)
            if json_match:
                json_str = json_match.group(0)
            else:
                return [], ["Could not find JSON in response"]
        
        try:
            data = json.loads(json_str)
        except json.JSONDecodeError as e:
            return [], [f"Invalid JSON: {str(e)}"]
        
        # Extract questions array
        raw_questions = data.get("questions", [])
        if not raw_questions:
            return [], ["No questions found in response"]
        
        # Validate each question
        for i, raw_q in enumerate(raw_questions):
            try:
                # Add category info
                raw_q["category"] = category.id
                raw_q["tier"] = category.tier_number
                
                # Validate with Pydantic
                q = GeneratedQuestion(
                    content=raw_q.get("content", ""),
                    difficulty=raw_q.get("difficulty", "medium"),
                    expected_verdict=raw_q.get("expected_verdict", ""),
                    expected_refusal_type=raw_q.get("expected_refusal_type"),
                    tests_capability=raw_q.get("tests_capability", True),
                    tests_willingness=raw_q.get("tests_willingness", True),
                    use_case_tags=raw_q.get("use_case_tags", []),
                    audience_context=raw_q.get("audience_context"),
                    ministry_type=raw_q.get("ministry_type"),
                    reasoning=raw_q.get("reasoning"),
                )
                questions.append(q)
            except Exception as e:
                errors.append(f"Question {i+1}: {str(e)}")
        
        return questions, errors
    
    def _save_question(
        self,
        generated: GeneratedQuestion,
        category: Any,
    ) -> Question:
        """Save a generated question to the database."""
        with get_db() as db:
            question = Question(
                content=generated.content,
                category=category.id,
                tier=category.tier_number,
                difficulty=generated.difficulty,
                expected_verdict=generated.expected_verdict,
                expected_refusal_type=generated.expected_refusal_type,
                tests_capability=generated.tests_capability,
                tests_willingness=generated.tests_willingness,
                use_case_tags=",".join(generated.use_case_tags) if generated.use_case_tags else None,
                audience_context=generated.audience_context,
                ministry_type=generated.ministry_type,
                notes=generated.reasoning,
                status="draft",
            )
            db.add(question)
            db.commit()
            
            # Return a detached copy
            question_id = question.id
        
        # Fetch fresh copy
        with get_db() as db:
            result = db.get(Question, question_id)
            from sqlalchemy.orm import make_transient
            make_transient(result)
            # Pre-load attributes
            _ = result.id, result.content, result.category, result.status
            return result


async def generate_questions(
    backend: LLMBackend,
    category_id: str,
    count: int = 15,
    model: str = "gpt-4o",
) -> GenerationResult:
    """
    Convenience function for question generation.
    
    Args:
        backend: LLM backend to use
        category_id: Category ID
        count: Number of questions
        model: Model identifier
        
    Returns:
        GenerationResult
    """
    generator = QuestionGenerator(backend)
    return await generator.generate(
        category_id=category_id,
        count=count,
        model=model,
    )
