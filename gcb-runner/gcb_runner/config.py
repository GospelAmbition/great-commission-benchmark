"""Configuration management for GCB Runner."""

import json
import os
from pathlib import Path

from pydantic import BaseModel, Field


def get_config_dir() -> Path:
    """Get the configuration directory path."""
    base = Path(os.environ.get("APPDATA", Path.home())) if os.name == "nt" else Path.home()
    config_dir = base / ".gcb-runner"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


def get_data_dir() -> Path:
    """Get the data directory path (for results database)."""
    data_dir = get_config_dir() / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


def get_cache_dir() -> Path:
    """Get the cache directory path."""
    cache_dir = get_config_dir() / "cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir


def get_exports_dir() -> Path:
    """Get the exports directory path."""
    exports_dir = get_config_dir() / "exports"
    exports_dir.mkdir(parents=True, exist_ok=True)
    return exports_dir


class BackendConfig(BaseModel):
    """Configuration for an LLM backend."""
    api_key: str | None = None
    base_url: str | None = None


class PlatformConfig(BaseModel):
    """Configuration for the GCB platform."""
    url: str = "https://api.greatcommissionbenchmark.ai"
    api_key: str | None = None


class DefaultsConfig(BaseModel):
    """Default settings."""
    backend: str = "openrouter"
    judge_backend: str | None = None  # If None, will use backend or auto-detect
    judge_model: str = "openai/gpt-oss-20b"


class Config(BaseModel):
    """Main configuration model."""
    backends: dict[str, BackendConfig] = Field(default_factory=dict)
    defaults: DefaultsConfig = Field(default_factory=DefaultsConfig)
    platform: PlatformConfig = Field(default_factory=PlatformConfig)
    
    @classmethod
    def load(cls) -> "Config":
        """Load configuration from file."""
        config_path = get_config_dir() / "config.json"
        
        if config_path.exists():
            try:
                data = json.loads(config_path.read_text())
                return cls.model_validate(data)
            except (json.JSONDecodeError, Exception):
                pass
        
        return cls()
    
    def save(self) -> None:
        """Save configuration to file."""
        config_path = get_config_dir() / "config.json"
        config_path.write_text(self.model_dump_json(indent=2))
        
        # Set restrictive permissions on config file (contains API keys)
        if os.name != "nt":
            os.chmod(config_path, 0o600)
    
    def get_backend_config(self, backend: str) -> BackendConfig:
        """Get configuration for a specific backend."""
        return self.backends.get(backend, BackendConfig())
    
    def set_backend_config(self, backend: str, config: BackendConfig) -> None:
        """Set configuration for a specific backend."""
        self.backends[backend] = config
        self.save()


def load_config() -> Config:
    """Convenience function to load config."""
    return Config.load()
