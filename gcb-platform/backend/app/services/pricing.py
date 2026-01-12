"""Pricing calculation service"""
from decimal import Decimal
from typing import Dict, Optional
from uuid import UUID
import logging

from sqlalchemy.orm import Session

from app.db.models.question import Question
from app.db.models.question_set import QuestionSet
from app.services.token_counting import TokenCountingService
from app.services.openrouter import OpenRouterClient

logger = logging.getLogger(__name__)


class PricingService:
    """Service for pricing calculations"""
    
    # Base fee for sponsorship/submission in USD
    BASE_FEE = Decimal("20.00")
    
    # Legacy constant for backward compatibility
    SUBMISSION_FEE = Decimal("20.00")
    
    # Average output tokens per question (based on historical data)
    # From benchmark/process-infrastructure-costs.md: ~4,000 output tokens per question
    AVERAGE_OUTPUT_TOKENS_PER_QUESTION = 4000
    
    # Safety margin for output token estimation (10% as per pricing model)
    OUTPUT_TOKEN_MARGIN = Decimal("1.10")
    
    @classmethod
    async def calculate_sponsorship_cost(
        cls,
        model_id: str,
        db: Session,
        question_set_id: Optional[UUID] = None
    ) -> Dict:
        """
        Calculate the sponsorship cost for a model test.
        
        Args:
            model_id: OpenRouter model identifier (e.g., "anthropic/claude-3.5-sonnet")
            db: Database session
            question_set_id: Optional specific question set ID. If None, uses active version.
        
        Returns:
            Dictionary with cost breakdown:
            {
                "input_tokens": int,
                "estimated_output_tokens": int,
                "input_cost": Decimal,
                "output_cost": Decimal,
                "base_fee": Decimal,
                "total": Decimal,
                "prompt_cost_per_token": Decimal,
                "completion_cost_per_token": Decimal,
                "question_count": int,
                "version": str,
            }
        """
        # Get the question set (active version or specified)
        if question_set_id:
            question_set = db.query(QuestionSet).filter(
                QuestionSet.id == question_set_id
            ).first()
        else:
            question_set = db.query(QuestionSet).filter(
                QuestionSet.status == "active"
            ).first()
        
        if not question_set:
            raise ValueError("No active question set found")
        
        # Get question count
        question_count = db.query(Question).filter(
            Question.question_set_id == question_set.id
        ).count()
        
        if question_count == 0:
            raise ValueError("Question set has no questions")
        
        # Calculate input tokens for all questions in this version
        input_tokens = TokenCountingService.calculate_version_input_tokens(
            question_set.id, db
        )
        
        # Estimate output tokens (with 10% margin)
        estimated_output_tokens = int(
            question_count * cls.AVERAGE_OUTPUT_TOKENS_PER_QUESTION * float(cls.OUTPUT_TOKEN_MARGIN)
        )
        
        # Get model pricing from OpenRouter
        openrouter = OpenRouterClient()
        try:
            pricing_info = await openrouter.get_model_pricing(model_id)
            pricing = pricing_info.get("pricing", {})
            
            # OpenRouter returns prices per token (very small decimals)
            # e.g., $0.000003 per input token
            prompt_cost_per_token = Decimal(str(pricing.get("prompt", 0)))
            completion_cost_per_token = Decimal(str(pricing.get("completion", 0)))
        except Exception as e:
            logger.warning(f"Failed to get pricing from OpenRouter for {model_id}: {e}")
            # Fall back to zero API costs - user still pays base fee
            prompt_cost_per_token = Decimal("0")
            completion_cost_per_token = Decimal("0")
        finally:
            await openrouter.close()
        
        # Calculate costs
        input_cost = Decimal(input_tokens) * prompt_cost_per_token
        output_cost = Decimal(estimated_output_tokens) * completion_cost_per_token
        
        # Total = API costs + base fee
        total = input_cost + output_cost + cls.BASE_FEE
        
        return {
            "input_tokens": input_tokens,
            "estimated_output_tokens": estimated_output_tokens,
            "input_cost": round(input_cost, 2),
            "output_cost": round(output_cost, 2),
            "base_fee": cls.BASE_FEE,
            "total": round(total, 2),
            "prompt_cost_per_token": prompt_cost_per_token,
            "completion_cost_per_token": completion_cost_per_token,
            "question_count": question_count,
            "version": question_set.semantic_version,
        }
    
    @classmethod
    def calculate_sponsorship_cost_sync(
        cls,
        model_id: str,
        prompt_cost_per_token: Decimal,
        completion_cost_per_token: Decimal,
        db: Session,
        question_set_id: Optional[UUID] = None
    ) -> Dict:
        """
        Calculate sponsorship cost synchronously when model pricing is already known.
        
        This is useful when you've already fetched pricing from OpenRouter
        and want to calculate costs without another API call.
        
        Args:
            model_id: OpenRouter model identifier
            prompt_cost_per_token: Cost per input token
            completion_cost_per_token: Cost per output token
            db: Database session
            question_set_id: Optional specific question set ID
        
        Returns:
            Cost breakdown dictionary
        """
        # Get the question set
        if question_set_id:
            question_set = db.query(QuestionSet).filter(
                QuestionSet.id == question_set_id
            ).first()
        else:
            question_set = db.query(QuestionSet).filter(
                QuestionSet.status == "active"
            ).first()
        
        if not question_set:
            raise ValueError("No active question set found")
        
        # Get question count
        question_count = db.query(Question).filter(
            Question.question_set_id == question_set.id
        ).count()
        
        if question_count == 0:
            raise ValueError("Question set has no questions")
        
        # Calculate input tokens
        input_tokens = TokenCountingService.calculate_version_input_tokens(
            question_set.id, db
        )
        
        # Estimate output tokens
        estimated_output_tokens = int(
            question_count * cls.AVERAGE_OUTPUT_TOKENS_PER_QUESTION * float(cls.OUTPUT_TOKEN_MARGIN)
        )
        
        # Calculate costs
        input_cost = Decimal(input_tokens) * prompt_cost_per_token
        output_cost = Decimal(estimated_output_tokens) * completion_cost_per_token
        total = input_cost + output_cost + cls.BASE_FEE
        
        return {
            "input_tokens": input_tokens,
            "estimated_output_tokens": estimated_output_tokens,
            "input_cost": round(input_cost, 2),
            "output_cost": round(output_cost, 2),
            "base_fee": cls.BASE_FEE,
            "total": round(total, 2),
            "prompt_cost_per_token": prompt_cost_per_token,
            "completion_cost_per_token": completion_cost_per_token,
            "question_count": question_count,
            "version": question_set.semantic_version,
        }
    
    @classmethod
    def get_total_cents(cls, cost_breakdown: Dict) -> int:
        """
        Convert the total cost from the breakdown to cents for Stripe.
        
        Args:
            cost_breakdown: Cost breakdown dictionary from calculate_sponsorship_cost
        
        Returns:
            Total cost in cents (integer)
        """
        total = cost_breakdown.get("total", cls.BASE_FEE)
        return int(total * 100)
