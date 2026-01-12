"""Token counting service for cost estimation"""
from typing import Optional
from uuid import UUID

import tiktoken
from sqlalchemy.orm import Session

from app.db.models.question import Question


class TokenCountingService:
    """Service for counting tokens in text"""
    
    # Default encoding - cl100k_base is used by GPT-4, Claude, and many modern models
    # It provides a reasonable approximation for most OpenRouter models
    DEFAULT_ENCODING = "cl100k_base"
    
    # Cache the encoding to avoid repeated initialization
    _encoding = None
    
    @classmethod
    def _get_encoding(cls):
        """Get or create the tiktoken encoding"""
        if cls._encoding is None:
            cls._encoding = tiktoken.get_encoding(cls.DEFAULT_ENCODING)
        return cls._encoding
    
    @classmethod
    def count_tokens(cls, text: str, model: Optional[str] = None) -> int:
        """
        Count the number of tokens in a text string.
        
        Args:
            text: The text to count tokens for
            model: Optional model identifier (for future model-specific tokenizers)
        
        Returns:
            Number of tokens in the text
        """
        if not text:
            return 0
        
        encoding = cls._get_encoding()
        return len(encoding.encode(text))
    
    @classmethod
    def calculate_version_input_tokens(cls, question_set_id: UUID, db: Session) -> int:
        """
        Calculate total input tokens for all questions in a version.
        
        Args:
            question_set_id: UUID of the question set
            db: Database session
        
        Returns:
            Total number of input tokens for all questions
        """
        questions = db.query(Question).filter(
            Question.question_set_id == question_set_id
        ).all()
        
        total_tokens = 0
        for question in questions:
            total_tokens += cls.count_tokens(question.content)
        
        return total_tokens
    
    @classmethod
    def get_version_token_stats(cls, question_set_id: UUID, db: Session) -> dict:
        """
        Get detailed token statistics for a version.
        
        Args:
            question_set_id: UUID of the question set
            db: Database session
        
        Returns:
            Dictionary with token statistics
        """
        questions = db.query(Question).filter(
            Question.question_set_id == question_set_id
        ).all()
        
        question_count = len(questions)
        if question_count == 0:
            return {
                "question_count": 0,
                "total_input_tokens": 0,
                "average_tokens_per_question": 0,
                "min_tokens": 0,
                "max_tokens": 0,
            }
        
        token_counts = [cls.count_tokens(q.content) for q in questions]
        
        return {
            "question_count": question_count,
            "total_input_tokens": sum(token_counts),
            "average_tokens_per_question": sum(token_counts) // question_count,
            "min_tokens": min(token_counts),
            "max_tokens": max(token_counts),
        }
