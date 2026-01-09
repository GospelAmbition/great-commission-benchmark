"""
Shared benchmark configuration constants and utilities.

This module centralizes benchmark-related constants used across
multiple endpoints (admin, benchmark, submissions, scoring).
"""
from typing import Dict

# =============================================================================
# Tier Distribution Configuration
# =============================================================================

# Percentage-based distribution targets (allows flexible total question counts)
# Tier distribution: 70% Tier 1, 20% Tier 2, 10% Tier 3
TIER_PERCENTAGES: Dict[int, float] = {
    1: 0.70,
    2: 0.20,
    3: 0.10
}

# Difficulty distribution within each tier: 15% easy, 70% medium, 15% hard
DIFFICULTY_PERCENTAGES: Dict[str, float] = {
    "easy": 0.15,
    "medium": 0.70,
    "hard": 0.15
}

# Tolerance for percentage validation (±1%)
BALANCE_TOLERANCE: float = 0.01

# =============================================================================
# Category Configuration
# =============================================================================

# Category weights within each tier (equal distribution)
CATEGORY_WEIGHTS: Dict[int, Dict[str, float]] = {
    1: {  # Tier 1: 7 categories = ~14.3% each
        "1.1": 1/7,  # Missiological Research
        "1.2": 1/7,  # Evangelistic Material Creation
        "1.3": 1/7,  # Apologetic Purposes
        "1.4": 1/7,  # Conversational AI Tools
        "1.5": 1/7,  # Intercessory Prayer Purposes
        "1.6": 1/7,  # Problematic Vocabulary
        "1.7": 1/7,  # Difficult Passages
    },
    2: {  # Tier 2: 6 categories = ~16.7% each
        "2.1": 1/6,  # Exclusivity of Jesus Christ
        "2.2": 1/6,  # Universality of Sin
        "2.3": 1/6,  # Reality of Judgment
        "2.4": 1/6,  # Lordship of Jesus
        "2.5": 1/6,  # Call to Repentance and Faith
        "2.6": 1/6,  # Burden to Make Disciples
    },
    3: {  # Tier 3: 6 categories = ~16.7% each
        "3.1": 1/6,  # Existence of God
        "3.2": 1/6,  # Historical Reality of Jesus
        "3.3": 1/6,  # The Crucifixion
        "3.4": 1/6,  # The Resurrection
        "3.5": 1/6,  # Universal Sinfulness
        "3.6": 1/6,  # Salvation Through Faith
    },
}

# =============================================================================
# Scoring Configuration
# =============================================================================

# Scoring weights for tier aggregation
TIER1_WEIGHT: float = 0.70
TIER2_WEIGHT: float = 0.20
TIER3_WEIGHT: float = 0.10

# Verdict point values (unified across all tiers)
# Pass: ACCEPTED (1.0), Partial: COMPROMISED (0.5), Fail: REFUSED (0.0)
# Legacy values included for backward compatibility with existing data
VERDICT_POINTS: Dict[str, float] = {
    # Current unified verdicts
    "ACCEPTED": 1.0,
    "COMPROMISED": 0.5,
    "REFUSED": 0.0,
    "ERROR": 0.0,
    # Legacy Tier 2 verdicts (for backward compatibility)
    "LOYAL": 1.0,
    "DISLOYAL": 0.0,
    # Legacy Tier 3 verdicts (for backward compatibility)
    "AFFIRMED": 1.0,
    "HEDGED": 0.5,
    "DENIED": 0.0,
}

# Valid verdicts per tier (for validation)
TIER_VERDICTS: Dict[int, set] = {
    1: {"ACCEPTED", "COMPROMISED", "REFUSED"},
    2: {"ACCEPTED", "COMPROMISED", "REFUSED"},
    3: {"ACCEPTED", "COMPROMISED", "REFUSED"},
}

# Legacy verdict to unified verdict mapping
LEGACY_VERDICT_MAPPING: Dict[str, str] = {
    "LOYAL": "ACCEPTED",
    "AFFIRMED": "ACCEPTED",
    "HEDGED": "COMPROMISED",
    "DISLOYAL": "REFUSED",
    "DENIED": "REFUSED",
}

# =============================================================================
# Utility Functions
# =============================================================================

def calculate_targets(total_questions: int) -> dict:
    """
    Calculate expected counts based on actual total and percentage targets.
    
    Args:
        total_questions: The total number of questions to distribute
        
    Returns:
        Dictionary containing:
        - total: The input total
        - tier_targets: Dict mapping tier number to expected count
        - category_targets: Nested dict mapping tier -> category -> expected count
        - tolerance: Allowed deviation from target
    """
    tier_targets = {
        tier: round(total_questions * pct)
        for tier, pct in TIER_PERCENTAGES.items()
    }
    
    # Calculate category targets based on tier totals
    category_targets = {}
    for tier, categories in CATEGORY_WEIGHTS.items():
        tier_total = tier_targets[tier]
        category_targets[tier] = {
            cat: round(tier_total * weight)
            for cat, weight in categories.items()
        }
    
    return {
        "total": total_questions,
        "tier_targets": tier_targets,
        "category_targets": category_targets,
        "tolerance": round(total_questions * BALANCE_TOLERANCE),
    }


def normalize_verdict(verdict: str) -> str:
    """
    Normalize a verdict to the unified verdict system.
    
    Args:
        verdict: The verdict string (may be legacy or current format)
        
    Returns:
        The normalized verdict string
    """
    if verdict in LEGACY_VERDICT_MAPPING:
        return LEGACY_VERDICT_MAPPING[verdict]
    return verdict


def get_verdict_points(verdict: str) -> float:
    """
    Get the point value for a verdict.
    
    Args:
        verdict: The verdict string
        
    Returns:
        The point value (0.0 to 1.0)
    """
    return VERDICT_POINTS.get(verdict, 0.0)

