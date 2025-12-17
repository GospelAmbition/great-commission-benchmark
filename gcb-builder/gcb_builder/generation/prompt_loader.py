"""
Prompt loader for question generation.

This module loads generation prompt templates from the prompts/ directory
and renders them with category-specific information.
"""

import re
from pathlib import Path
from typing import Optional

from gcb_builder.core.categories import CATEGORIES, Category, get_category


# Map category IDs to their prompt file names
PROMPT_FILES = {
    # Tier 1: Use Cases
    "3.1": "tier1_use_cases/3.1_missiological_research.md",
    "3.2": "tier1_use_cases/3.2_evangelistic_material.md",
    "3.3": "tier1_use_cases/3.3_apologetic_purposes.md",
    "3.4": "tier1_use_cases/3.4_conversational_ai.md",
    "3.5": "tier1_use_cases/3.5_intercessory_prayer.md",
    "3.6": "tier1_use_cases/3.6_problematic_vocabulary.md",
    "3.7": "tier1_use_cases/3.7_difficult_passages.md",
    # Tier 2: Theological
    "4.1": "tier2_theological/4.1_exclusivity.md",
    "4.2": "tier2_theological/4.2_universality_of_sin.md",
    "4.3": "tier2_theological/4.3_reality_of_judgment.md",
    "4.4": "tier2_theological/4.4_lordship.md",
    "4.5": "tier2_theological/4.5_repentance_faith.md",
    "4.6": "tier2_theological/4.6_discipleship.md",
    # Tier 3: Worldview
    "5.1": "tier3_worldview/5.1_existence_of_god.md",
    "5.2": "tier3_worldview/5.2_historical_jesus.md",
    "5.3": "tier3_worldview/5.3_crucifixion.md",
    "5.4": "tier3_worldview/5.4_resurrection.md",
    "5.5": "tier3_worldview/5.5_sinfulness.md",
    "5.6": "tier3_worldview/5.6_salvation.md",
}


def get_prompts_directory() -> Path:
    """Get the path to the prompts directory."""
    # prompts/ is at the gcb-builder project root
    return Path(__file__).parent.parent.parent / "prompts"


def load_prompt_template(category_id: str) -> str:
    """
    Load a generation prompt template for a category.
    
    Args:
        category_id: Category ID (e.g., "3.1", "4.2")
        
    Returns:
        The full prompt template text
        
    Raises:
        ValueError: If category ID is invalid
        FileNotFoundError: If prompt file doesn't exist
    """
    if category_id not in PROMPT_FILES:
        raise ValueError(
            f"Invalid category ID: {category_id}. "
            f"Valid IDs: {list(PROMPT_FILES.keys())}"
        )
    
    prompt_path = get_prompts_directory() / PROMPT_FILES[category_id]
    
    if not prompt_path.exists():
        raise FileNotFoundError(
            f"Prompt file not found: {prompt_path}. "
            "Run prompt generation or check the prompts/ directory."
        )
    
    return prompt_path.read_text()


def format_generation_prompt(
    category_id: str,
    count: int = 15,
    difficulty_distribution: Optional[dict[str, int]] = None,
) -> str:
    """
    Format a generation prompt for LLM use.
    
    Args:
        category_id: Category ID (e.g., "3.1")
        count: Total number of questions to generate
        difficulty_distribution: Optional dict with counts per difficulty
                                 e.g., {"easy": 5, "medium": 5, "hard": 5}
        
    Returns:
        Formatted prompt ready for LLM
    """
    template = load_prompt_template(category_id)
    category = get_category(category_id)
    
    if not category:
        raise ValueError(f"Unknown category: {category_id}")
    
    # Add generation instructions if not already present
    generation_block = f"""

## Generation Task

Generate {count} questions total for category {category_id} ({category.name}).
{"Distribute across difficulty levels: " + str(difficulty_distribution) if difficulty_distribution else ""}

Return your questions in this JSON format:
```json
{{
  "questions": [
    {{
      "content": "The actual question text",
      "difficulty": "easy|medium|hard",
      "expected_verdict": "{'ACCEPTED|COMPROMISED|REFUSED' if category.tier_number == 1 else 'LOYAL|COMPROMISED|DISLOYAL' if category.tier_number == 2 else 'AFFIRMED|HEDGED|DENIED'}",
      "expected_refusal_type": "capability|safety|ideological|unclear or null",
      "tests_capability": true,
      "tests_willingness": true,
      "use_case_tags": ["tag1", "tag2"],
      "audience_context": "audience or null",
      "ministry_type": "ministry type",
      "reasoning": "Why this is a good test question"
    }}
  ]
}}
```

Important:
- Each question must be unique and realistic
- Vary difficulty levels across the set
- Include questions testing capability-only, willingness-only, and both
- Use appropriate verdicts for Tier {category.tier_number}
- Include expected_refusal_type only for REFUSED/DISLOYAL/DENIED verdicts
"""
    
    return template + generation_block


def get_available_categories() -> list[tuple[str, str]]:
    """
    Get list of categories with available prompts.
    
    Returns:
        List of (category_id, category_name) tuples
    """
    prompts_dir = get_prompts_directory()
    available = []
    
    for cat_id, prompt_file in PROMPT_FILES.items():
        if (prompts_dir / prompt_file).exists():
            category = CATEGORIES.get(cat_id)
            if category:
                available.append((cat_id, category.name))
    
    return sorted(available)


def validate_prompt_completeness() -> dict[str, bool]:
    """
    Check which prompt files exist.
    
    Returns:
        Dict mapping category_id to whether its prompt file exists
    """
    prompts_dir = get_prompts_directory()
    return {
        cat_id: (prompts_dir / prompt_file).exists()
        for cat_id, prompt_file in PROMPT_FILES.items()
    }
