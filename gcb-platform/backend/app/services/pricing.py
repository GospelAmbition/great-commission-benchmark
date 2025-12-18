"""Pricing calculation service"""
from typing import Dict, Optional
from decimal import Decimal
from app.services.openrouter import OpenRouterClient


class PricingService:
    """Service for calculating test pricing"""
    
    # Fixed processing fee in USD
    PROCESSING_FEE = Decimal("2.00")
    
    @staticmethod
    async def calculate_test_cost(
        model_id: str,
        question_count: int,
        estimated_tokens_per_question: int = 500
    ) -> Dict[str, Decimal]:
        """
        Calculate the cost for running a test
        
        Args:
            model_id: Model identifier (e.g., "anthropic/claude-3.5-sonnet")
            question_count: Number of questions in the test
            estimated_tokens_per_question: Estimated tokens per question
        
        Returns:
            Dict with breakdown:
            - api_cost: Cost for API calls
            - processing_fee: Fixed processing fee
            - total: Total cost
        """
        # Get model pricing from OpenRouter
        openrouter = OpenRouterClient()
        try:
            pricing_info = await openrouter.get_model_pricing(model_id)
            pricing = pricing_info.get("pricing", {})
            
            # Calculate API cost
            prompt_price_per_1k = Decimal(str(pricing.get("prompt", 0)))
            completion_price_per_1k = Decimal(str(pricing.get("completion", 0)))
            
            # Estimate tokens: prompt + completion
            # Assume prompt is ~70% of tokens, completion is ~30%
            prompt_tokens = int(estimated_tokens_per_question * 0.7 * question_count)
            completion_tokens = int(estimated_tokens_per_question * 0.3 * question_count)
            
            prompt_cost = (Decimal(prompt_tokens) / 1000) * prompt_price_per_1k
            completion_cost = (Decimal(completion_tokens) / 1000) * completion_price_per_1k
            api_cost = prompt_cost + completion_cost
            
        except Exception:
            # Fallback to default estimate if pricing unavailable
            api_cost = Decimal("15.00")
        finally:
            await openrouter.close()
        
        # Add processing fee
        processing_fee = PricingService.PROCESSING_FEE
        
        # Calculate total
        total = api_cost + processing_fee
        
        return {
            "api_cost": api_cost,
            "processing_fee": processing_fee,
            "total": total
        }
    
    @staticmethod
    def calculate_with_tip(base_cost: Decimal, tip_percentage: Optional[int] = None) -> Dict[str, Decimal]:
        """
        Calculate total cost with optional tip
        
        Args:
            base_cost: Base cost (without tip)
            tip_percentage: Tip percentage (0-100), or None for no tip
        
        Returns:
            Dict with breakdown:
            - base_cost: Original cost
            - tip_amount: Tip amount
            - total: Total with tip
        """
        if tip_percentage is None or tip_percentage == 0:
            return {
                "base_cost": base_cost,
                "tip_amount": Decimal("0.00"),
                "total": base_cost
            }
        
        tip_amount = (base_cost * Decimal(str(tip_percentage))) / 100
        total = base_cost + tip_amount
        
        return {
            "base_cost": base_cost,
            "tip_amount": tip_amount,
            "total": total
        }
