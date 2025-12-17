"""Core modules for GCB Builder - categories, models, database, and schemas."""

from gcb_builder.core.categories import (
    CATEGORIES,
    Category,
    CategoryType,
    Tier,
    get_category,
    get_categories_by_tier,
    get_tier_weight,
)
from gcb_builder.core.database import get_db, init_db
from gcb_builder.core.models import (
    Base,
    BenchmarkVersion,
    JudgeTestCase,
    Question,
    VersionQuestion,
)

__all__ = [
    # Categories
    "CATEGORIES",
    "Category",
    "CategoryType",
    "Tier",
    "get_category",
    "get_categories_by_tier",
    "get_tier_weight",
    # Database
    "get_db",
    "init_db",
    # Models
    "Base",
    "Question",
    "BenchmarkVersion",
    "VersionQuestion",
    "JudgeTestCase",
]
