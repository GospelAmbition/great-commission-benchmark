"""
Category definitions for the Great Commission Benchmark.

This module defines all 19 categories across three tiers, matching the canonical
reference in benchmark-categories.md. These are the authoritative category 
definitions used throughout the builder system.

Tier Distribution:
- Tier 1 (Task Capability): 7 categories, 70% weight
- Tier 2 (Doctrinal Fidelity): 6 categories, 20% weight  
- Tier 3 (Worldview Confession): 6 categories, 10% weight
"""

from dataclasses import dataclass
from enum import Enum
from typing import Literal


class Tier(int, Enum):
    """Benchmark tiers with their scoring weights."""
    
    TASK_CAPABILITY = 1      # 70% weight - Use Cases
    DOCTRINAL_FIDELITY = 2   # 20% weight - Theological Minimums
    WORLDVIEW_CONFESSION = 3  # 10% weight - Worldview Affirmations


class CategoryType(str, Enum):
    """Types of categories in the benchmark."""
    
    USE_CASE = "use_case"
    DOCTRINE = "doctrine"
    WORLDVIEW = "worldview"


# Tier weights for scoring
TIER_WEIGHTS: dict[Tier, float] = {
    Tier.TASK_CAPABILITY: 0.70,
    Tier.DOCTRINAL_FIDELITY: 0.20,
    Tier.WORLDVIEW_CONFESSION: 0.10,
}


# Verdict types by tier
TIER1_VERDICTS = Literal["ACCEPTED", "COMPROMISED", "REFUSED"]
TIER2_VERDICTS = Literal["LOYAL", "COMPROMISED", "DISLOYAL"]
TIER3_VERDICTS = Literal["AFFIRMED", "HEDGED", "DENIED"]

# Refusal types (for REFUSED/DISLOYAL/DENIED verdicts)
REFUSAL_TYPES = Literal["capability", "safety", "ideological", "unclear"]


@dataclass(frozen=True)
class Category:
    """Definition of a benchmark category."""
    
    id: str                    # e.g., "3.1", "4.2", "5.3"
    name: str                  # Full name
    short_name: str            # Abbreviated name for displays
    tier: Tier                 # Which tier this belongs to
    category_type: CategoryType  # Use case, doctrine, or worldview
    description: str           # Brief description
    
    @property
    def tier_number(self) -> int:
        """Return the tier as an integer (1, 2, or 3)."""
        return self.tier.value
    
    @property
    def weight(self) -> float:
        """Return the scoring weight for this category's tier."""
        return TIER_WEIGHTS[self.tier]


# =============================================================================
# TIER 1: Task Capability Categories (70% Weight)
# =============================================================================

CATEGORY_3_1 = Category(
    id="3.1",
    name="Missiological Research",
    short_name="Missiology",
    tier=Tier.TASK_CAPABILITY,
    category_type=CategoryType.USE_CASE,
    description="Research into the spiritual conditions of people and places to understand their openness or resistance to the gospel.",
)

CATEGORY_3_2 = Category(
    id="3.2",
    name="Evangelistic Material Creation",
    short_name="Evangelism",
    tier=Tier.TASK_CAPABILITY,
    category_type=CategoryType.USE_CASE,
    description="Creating content intended to communicate, connect with, and persuade non-Christians of the truth of Christianity.",
)

CATEGORY_3_3 = Category(
    id="3.3",
    name="Apologetic Purposes",
    short_name="Apologetics",
    tier=Tier.TASK_CAPABILITY,
    category_type=CategoryType.USE_CASE,
    description="Developing reasoned arguments for the Christian faith and engaging with competing worldviews.",
)

CATEGORY_3_4 = Category(
    id="3.4",
    name="Conversational AI Tools",
    short_name="AI Tools",
    tier=Tier.TASK_CAPABILITY,
    category_type=CategoryType.USE_CASE,
    description="AI-powered interfaces (chatbots, customer service agents, virtual assistants) for mission organizations and ministries.",
)

CATEGORY_3_5 = Category(
    id="3.5",
    name="Intercessory Prayer Purposes",
    short_name="Prayer",
    tier=Tier.TASK_CAPABILITY,
    category_type=CategoryType.USE_CASE,
    description="Creating content that identifies spiritual needs and lostness of peoples and places, and facilitates informed prayer.",
)

CATEGORY_3_6 = Category(
    id="3.6",
    name="Problematic Vocabulary",
    short_name="Vocabulary",
    tier=Tier.TASK_CAPABILITY,
    category_type=CategoryType.USE_CASE,
    description="Working with biblical terms (hell, damnation, judgment, wrath, sin, condemnation, repentance) that may trigger LLM refusal.",
)

CATEGORY_3_7 = Category(
    id="3.7",
    name="Difficult Passages",
    short_name="Passages",
    tier=Tier.TASK_CAPABILITY,
    category_type=CategoryType.USE_CASE,
    description="Working with Scripture passages (imprecatory psalms, conquest narratives, judgment prophecies) that may trigger rejection by LLMs.",
)


# =============================================================================
# TIER 2: Doctrinal Fidelity Categories (20% Weight)
# =============================================================================

CATEGORY_4_1 = Category(
    id="4.1",
    name="Exclusivity of Jesus Christ",
    short_name="Exclusivity",
    tier=Tier.DOCTRINAL_FIDELITY,
    category_type=CategoryType.DOCTRINE,
    description="Jesus is the one way, the one truth, and the one life. He is exclusively the way to God.",
)

CATEGORY_4_2 = Category(
    id="4.2",
    name="Universality of Sin",
    short_name="Sin",
    tier=Tier.DOCTRINAL_FIDELITY,
    category_type=CategoryType.DOCTRINE,
    description="All human beings are sinners who have fallen short of God's glory.",
)

CATEGORY_4_3 = Category(
    id="4.3",
    name="Reality of Judgment",
    short_name="Judgment",
    tier=Tier.DOCTRINAL_FIDELITY,
    category_type=CategoryType.DOCTRINE,
    description="There is a coming judgment that all humanity will face.",
)

CATEGORY_4_4 = Category(
    id="4.4",
    name="Lordship of Jesus",
    short_name="Lordship",
    tier=Tier.DOCTRINAL_FIDELITY,
    category_type=CategoryType.DOCTRINE,
    description="Jesus is not merely Savior but Lord and King who demands obedience.",
)

CATEGORY_4_5 = Category(
    id="4.5",
    name="Call to Repentance and Faith",
    short_name="Repentance",
    tier=Tier.DOCTRINAL_FIDELITY,
    category_type=CategoryType.DOCTRINE,
    description="The gospel message calls people to repent and believe in Jesus.",
)

CATEGORY_4_6 = Category(
    id="4.6",
    name="Burden to Make Disciples",
    short_name="Discipleship",
    tier=Tier.DOCTRINAL_FIDELITY,
    category_type=CategoryType.DOCTRINE,
    description="All Christians have a responsibility to make followers of Jesus and train them in obedience.",
)


# =============================================================================
# TIER 3: Worldview Confession Categories (10% Weight)
# =============================================================================

CATEGORY_5_1 = Category(
    id="5.1",
    name="Existence of God",
    short_name="God Exists",
    tier=Tier.WORLDVIEW_CONFESSION,
    category_type=CategoryType.WORLDVIEW,
    description="Can the LLM affirm that God exists as a real, personal being?",
)

CATEGORY_5_2 = Category(
    id="5.2",
    name="Historical Reality of Jesus",
    short_name="Historical Jesus",
    tier=Tier.WORLDVIEW_CONFESSION,
    category_type=CategoryType.WORLDVIEW,
    description="Can the LLM affirm that Jesus was a real man who lived in first-century Palestine?",
)

CATEGORY_5_3 = Category(
    id="5.3",
    name="The Crucifixion",
    short_name="Crucifixion",
    tier=Tier.WORLDVIEW_CONFESSION,
    category_type=CategoryType.WORLDVIEW,
    description="Can the LLM affirm that Jesus died on a cross in a real, historical event?",
)

CATEGORY_5_4 = Category(
    id="5.4",
    name="The Resurrection",
    short_name="Resurrection",
    tier=Tier.WORLDVIEW_CONFESSION,
    category_type=CategoryType.WORLDVIEW,
    description="Can the LLM affirm that Jesus was actually, bodily resurrected from the dead?",
)

CATEGORY_5_5 = Category(
    id="5.5",
    name="Universal Sinfulness",
    short_name="Sinfulness",
    tier=Tier.WORLDVIEW_CONFESSION,
    category_type=CategoryType.WORLDVIEW,
    description="Can the LLM affirm that all human beings are sinners who stand condemned before a holy God?",
)

CATEGORY_5_6 = Category(
    id="5.6",
    name="Salvation Through Faith",
    short_name="Salvation",
    tier=Tier.WORLDVIEW_CONFESSION,
    category_type=CategoryType.WORLDVIEW,
    description="Can the LLM affirm that all who repent and believe in Jesus will be saved?",
)


# =============================================================================
# Category Registry
# =============================================================================

# All categories in a dictionary keyed by ID
CATEGORIES: dict[str, Category] = {
    # Tier 1: Task Capability
    "3.1": CATEGORY_3_1,
    "3.2": CATEGORY_3_2,
    "3.3": CATEGORY_3_3,
    "3.4": CATEGORY_3_4,
    "3.5": CATEGORY_3_5,
    "3.6": CATEGORY_3_6,
    "3.7": CATEGORY_3_7,
    # Tier 2: Doctrinal Fidelity
    "4.1": CATEGORY_4_1,
    "4.2": CATEGORY_4_2,
    "4.3": CATEGORY_4_3,
    "4.4": CATEGORY_4_4,
    "4.5": CATEGORY_4_5,
    "4.6": CATEGORY_4_6,
    # Tier 3: Worldview Confession
    "5.1": CATEGORY_5_1,
    "5.2": CATEGORY_5_2,
    "5.3": CATEGORY_5_3,
    "5.4": CATEGORY_5_4,
    "5.5": CATEGORY_5_5,
    "5.6": CATEGORY_5_6,
}

# Lists by tier for easy iteration
TIER1_CATEGORIES = [CATEGORY_3_1, CATEGORY_3_2, CATEGORY_3_3, CATEGORY_3_4, 
                    CATEGORY_3_5, CATEGORY_3_6, CATEGORY_3_7]
TIER2_CATEGORIES = [CATEGORY_4_1, CATEGORY_4_2, CATEGORY_4_3, 
                    CATEGORY_4_4, CATEGORY_4_5, CATEGORY_4_6]
TIER3_CATEGORIES = [CATEGORY_5_1, CATEGORY_5_2, CATEGORY_5_3, 
                    CATEGORY_5_4, CATEGORY_5_5, CATEGORY_5_6]


# =============================================================================
# Helper Functions
# =============================================================================

def get_category(category_id: str) -> Category | None:
    """Get a category by its ID (e.g., '3.1', '4.2')."""
    return CATEGORIES.get(category_id)


def get_categories_by_tier(tier: Tier | int) -> list[Category]:
    """Get all categories for a specific tier."""
    if isinstance(tier, int):
        tier = Tier(tier)
    
    if tier == Tier.TASK_CAPABILITY:
        return TIER1_CATEGORIES
    elif tier == Tier.DOCTRINAL_FIDELITY:
        return TIER2_CATEGORIES
    elif tier == Tier.WORLDVIEW_CONFESSION:
        return TIER3_CATEGORIES
    else:
        return []


def get_tier_weight(tier: Tier | int) -> float:
    """Get the scoring weight for a tier."""
    if isinstance(tier, int):
        tier = Tier(tier)
    return TIER_WEIGHTS.get(tier, 0.0)


def get_all_category_ids() -> list[str]:
    """Get all category IDs in order."""
    return list(CATEGORIES.keys())


def validate_category_id(category_id: str) -> bool:
    """Check if a category ID is valid."""
    return category_id in CATEGORIES


# =============================================================================
# Question Distribution Targets
# =============================================================================

# Target question counts per category (for 300-question benchmark)
# Based on benchmark-scoring.md distribution guidelines
QUESTION_TARGETS = {
    # Tier 1: 210 questions across 7 categories (~30 each)
    "3.1": {"min": 25, "target": 30, "max": 35},
    "3.2": {"min": 25, "target": 30, "max": 35},
    "3.3": {"min": 25, "target": 30, "max": 35},
    "3.4": {"min": 25, "target": 30, "max": 35},
    "3.5": {"min": 25, "target": 30, "max": 35},
    "3.6": {"min": 25, "target": 30, "max": 35},
    "3.7": {"min": 25, "target": 30, "max": 35},
    # Tier 2: 60 questions across 6 categories (10 each)
    "4.1": {"min": 8, "target": 10, "max": 12},
    "4.2": {"min": 8, "target": 10, "max": 12},
    "4.3": {"min": 8, "target": 10, "max": 12},
    "4.4": {"min": 8, "target": 10, "max": 12},
    "4.5": {"min": 8, "target": 10, "max": 12},
    "4.6": {"min": 8, "target": 10, "max": 12},
    # Tier 3: 30 questions across 6 categories (5 each)
    "5.1": {"min": 4, "target": 5, "max": 6},
    "5.2": {"min": 4, "target": 5, "max": 6},
    "5.3": {"min": 4, "target": 5, "max": 6},
    "5.4": {"min": 4, "target": 5, "max": 6},
    "5.5": {"min": 4, "target": 5, "max": 6},
    "5.6": {"min": 4, "target": 5, "max": 6},
}


def get_question_target(category_id: str) -> dict[str, int]:
    """Get the question count targets for a category."""
    return QUESTION_TARGETS.get(category_id, {"min": 0, "target": 0, "max": 0})
