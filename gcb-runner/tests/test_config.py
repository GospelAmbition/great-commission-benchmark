"""Tests for configuration management."""

import json
import tempfile
from pathlib import Path

import pytest

from gcb_runner.config import Config, BackendConfig, PlatformConfig, DefaultsConfig


class TestConfig:
    """Tests for Config class."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = Config()
        
        assert config.backends == {}
        assert config.defaults.backend == "openrouter"
        assert config.defaults.judge_model == "openai/gpt-4o"
        assert config.platform.url == "https://api.greatcommissionbenchmark.ai"
        assert config.platform.api_key is None
    
    def test_save_and_load(self, tmp_path, monkeypatch):
        """Test saving and loading configuration."""
        # Patch the config directory
        monkeypatch.setattr("gcb_runner.config.get_config_dir", lambda: tmp_path)
        
        config = Config()
        config.backends["openrouter"] = BackendConfig(api_key="test-key")
        config.platform.api_key = "platform-key"
        config.save()
        
        # Load and verify
        loaded = Config.load()
        assert loaded.backends["openrouter"].api_key == "test-key"
        assert loaded.platform.api_key == "platform-key"
    
    def test_get_backend_config(self):
        """Test getting backend configuration."""
        config = Config()
        config.backends["openrouter"] = BackendConfig(api_key="test-key")
        
        # Existing backend
        backend_config = config.get_backend_config("openrouter")
        assert backend_config.api_key == "test-key"
        
        # Non-existing backend
        backend_config = config.get_backend_config("nonexistent")
        assert backend_config.api_key is None
    
    def test_set_backend_config(self, tmp_path, monkeypatch):
        """Test setting backend configuration."""
        monkeypatch.setattr("gcb_runner.config.get_config_dir", lambda: tmp_path)
        
        config = Config()
        config.set_backend_config("openai", BackendConfig(api_key="openai-key"))
        
        assert config.backends["openai"].api_key == "openai-key"


class TestBackendConfig:
    """Tests for BackendConfig class."""
    
    def test_default_values(self):
        """Test default backend config values."""
        config = BackendConfig()
        assert config.api_key is None
        assert config.base_url is None
    
    def test_with_values(self):
        """Test backend config with values."""
        config = BackendConfig(api_key="test", base_url="http://localhost:8000")
        assert config.api_key == "test"
        assert config.base_url == "http://localhost:8000"
