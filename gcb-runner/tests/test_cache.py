"""Tests for the question cache."""

import json
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from gcb_runner.api.cache import QuestionCache


class TestQuestionCache:
    """Tests for QuestionCache class."""
    
    def test_store_and_get(self, tmp_path):
        """Test storing and retrieving cached questions."""
        cache = QuestionCache(cache_dir=tmp_path)
        
        data = {
            "version": {"semantic_version": "2.0"},
            "questions": [{"id": 1, "content": "Test question"}],
            "judge_prompts": {"tier1": "Test prompt"}
        }
        
        cache.store("2.0", data)
        
        # Retrieve
        cached = cache.get("2.0")
        assert cached is not None
        assert cached["questions"][0]["id"] == 1
        assert cached["judge_prompts"]["tier1"] == "Test prompt"
    
    def test_get_nonexistent(self, tmp_path):
        """Test getting non-existent cached version."""
        cache = QuestionCache(cache_dir=tmp_path)
        
        cached = cache.get("9.9")
        assert cached is None
    
    def test_is_stale_fresh_cache(self, tmp_path):
        """Test that fresh cache is not stale."""
        cache = QuestionCache(cache_dir=tmp_path)
        
        data = {"questions": []}
        cache.store("2.0", data)
        
        assert not cache.is_stale("2.0")
    
    def test_is_stale_old_cache(self, tmp_path):
        """Test that old cache is stale."""
        cache = QuestionCache(cache_dir=tmp_path)
        
        # Store with old timestamp
        version_dir = cache._get_version_dir("2.0")
        meta_path = version_dir / "metadata.json"
        
        old_time = datetime.now() - timedelta(days=10)
        metadata = {
            "version": "2.0",
            "cached_at": old_time.isoformat(),
        }
        meta_path.write_text(json.dumps(metadata))
        
        assert cache.is_stale("2.0")
    
    def test_is_stale_no_cache(self, tmp_path):
        """Test that non-existent cache is considered stale."""
        cache = QuestionCache(cache_dir=tmp_path)
        
        assert cache.is_stale("9.9")
    
    def test_judge_prompts_stored_separately(self, tmp_path):
        """Test that judge prompts are stored in separate file."""
        cache = QuestionCache(cache_dir=tmp_path)
        
        data = {
            "questions": [],
            "judge_prompts": {
                "tier1": "Prompt 1",
                "tier2": "Prompt 2"
            }
        }
        
        cache.store("2.0", data)
        
        # Check separate file exists
        prompts_path = tmp_path / "v2.0" / "judge-prompts.json"
        assert prompts_path.exists()
        
        prompts = json.loads(prompts_path.read_text())
        assert prompts["tier1"] == "Prompt 1"
    
    def test_get_judge_prompts(self, tmp_path):
        """Test getting cached judge prompts."""
        cache = QuestionCache(cache_dir=tmp_path)
        
        data = {
            "questions": [],
            "judge_prompts": {
                "tier1": "Prompt 1",
                "tier2": "Prompt 2",
                "tier3": "Prompt 3"
            }
        }
        
        cache.store("2.0", data)
        
        prompts = cache.get_judge_prompts("2.0")
        assert prompts is not None
        assert prompts["tier1"] == "Prompt 1"
        assert prompts["tier2"] == "Prompt 2"
        assert prompts["tier3"] == "Prompt 3"
    
    def test_versions_list_caching(self, tmp_path):
        """Test caching of versions list."""
        cache = QuestionCache(cache_dir=tmp_path)
        
        versions = {
            "versions": [
                {"semantic_version": "2.0", "status": "current"},
                {"semantic_version": "1.2", "status": "archived"}
            ],
            "current_version": "2.0"
        }
        
        cache.store_versions_list(versions)
        
        cached = cache.get_versions_list()
        assert cached is not None
        assert cached["current_version"] == "2.0"
        assert len(cached["versions"]) == 2
    
    def test_clear_specific_version(self, tmp_path):
        """Test clearing a specific version from cache."""
        cache = QuestionCache(cache_dir=tmp_path)
        
        cache.store("2.0", {"questions": []})
        cache.store("1.2", {"questions": []})
        
        assert cache.get("2.0") is not None
        assert cache.get("1.2") is not None
        
        cache.clear("2.0")
        
        assert cache.get("2.0") is None
        assert cache.get("1.2") is not None
    
    def test_clear_all(self, tmp_path):
        """Test clearing all cached versions."""
        cache = QuestionCache(cache_dir=tmp_path)
        
        cache.store("2.0", {"questions": []})
        cache.store("1.2", {"questions": []})
        cache.store_versions_list({"versions": []})
        
        cache.clear()
        
        assert cache.get("2.0") is None
        assert cache.get("1.2") is None
