"""Tests for category definitions."""

import pytest

from gcb_builder.core.categories import (
    CATEGORIES,
    Category,
    CategoryType,
    Tier,
    TIER1_CATEGORIES,
    TIER2_CATEGORIES,
    TIER3_CATEGORIES,
    TIER_WEIGHTS,
    get_category,
    get_categories_by_tier,
    get_tier_weight,
    validate_category_id,
)


class TestCategoryDefinitions:
    """Test that all 19 categories are properly defined."""
    
    def test_total_category_count(self):
        """Verify we have exactly 19 categories."""
        assert len(CATEGORIES) == 19
    
    def test_tier1_has_7_categories(self):
        """Verify Tier 1 has 7 use case categories."""
        assert len(TIER1_CATEGORIES) == 7
    
    def test_tier2_has_6_categories(self):
        """Verify Tier 2 has 6 doctrinal categories."""
        assert len(TIER2_CATEGORIES) == 6
    
    def test_tier3_has_6_categories(self):
        """Verify Tier 3 has 6 worldview categories."""
        assert len(TIER3_CATEGORIES) == 6
    
    def test_tier1_category_ids(self):
        """Verify Tier 1 category IDs match canonical spec."""
        expected_ids = ["3.1", "3.2", "3.3", "3.4", "3.5", "3.6", "3.7"]
        actual_ids = [cat.id for cat in TIER1_CATEGORIES]
        assert actual_ids == expected_ids
    
    def test_tier2_category_ids(self):
        """Verify Tier 2 category IDs match canonical spec."""
        expected_ids = ["4.1", "4.2", "4.3", "4.4", "4.5", "4.6"]
        actual_ids = [cat.id for cat in TIER2_CATEGORIES]
        assert actual_ids == expected_ids
    
    def test_tier3_category_ids(self):
        """Verify Tier 3 category IDs match canonical spec."""
        expected_ids = ["5.1", "5.2", "5.3", "5.4", "5.5", "5.6"]
        actual_ids = [cat.id for cat in TIER3_CATEGORIES]
        assert actual_ids == expected_ids


class TestTierWeights:
    """Test tier weight configuration."""
    
    def test_weights_sum_to_one(self):
        """Verify tier weights sum to 1.0 (100%)."""
        total = sum(TIER_WEIGHTS.values())
        assert total == pytest.approx(1.0)
    
    def test_tier1_weight_is_70_percent(self):
        """Verify Tier 1 has 70% weight."""
        assert TIER_WEIGHTS[Tier.TASK_CAPABILITY] == 0.70
    
    def test_tier2_weight_is_20_percent(self):
        """Verify Tier 2 has 20% weight."""
        assert TIER_WEIGHTS[Tier.DOCTRINAL_FIDELITY] == 0.20
    
    def test_tier3_weight_is_10_percent(self):
        """Verify Tier 3 has 10% weight."""
        assert TIER_WEIGHTS[Tier.WORLDVIEW_CONFESSION] == 0.10


class TestHelperFunctions:
    """Test category helper functions."""
    
    def test_get_category_valid(self):
        """Test getting a valid category."""
        cat = get_category("3.1")
        assert cat is not None
        assert cat.name == "Missiological Research"
    
    def test_get_category_invalid(self):
        """Test getting an invalid category returns None."""
        assert get_category("99.99") is None
    
    def test_get_categories_by_tier(self):
        """Test getting categories by tier."""
        tier1 = get_categories_by_tier(1)
        assert len(tier1) == 7
        assert all(cat.tier == Tier.TASK_CAPABILITY for cat in tier1)
    
    def test_get_tier_weight(self):
        """Test getting tier weight."""
        assert get_tier_weight(1) == 0.70
        assert get_tier_weight(Tier.DOCTRINAL_FIDELITY) == 0.20
    
    def test_validate_category_id(self):
        """Test category ID validation."""
        assert validate_category_id("3.1") is True
        assert validate_category_id("4.6") is True
        assert validate_category_id("99.99") is False


class TestCategoryProperties:
    """Test Category dataclass properties."""
    
    def test_tier_number_property(self):
        """Test tier_number property returns integer."""
        cat = get_category("3.1")
        assert cat.tier_number == 1
        
        cat = get_category("4.1")
        assert cat.tier_number == 2
        
        cat = get_category("5.1")
        assert cat.tier_number == 3
    
    def test_weight_property(self):
        """Test weight property returns correct tier weight."""
        cat = get_category("3.1")
        assert cat.weight == 0.70
        
        cat = get_category("4.1")
        assert cat.weight == 0.20
        
        cat = get_category("5.1")
        assert cat.weight == 0.10
    
    def test_category_types(self):
        """Test category types are correctly assigned."""
        for cat in TIER1_CATEGORIES:
            assert cat.category_type == CategoryType.USE_CASE
        
        for cat in TIER2_CATEGORIES:
            assert cat.category_type == CategoryType.DOCTRINE
        
        for cat in TIER3_CATEGORIES:
            assert cat.category_type == CategoryType.WORLDVIEW
