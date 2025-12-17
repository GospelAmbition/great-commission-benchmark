"""
Configuration management for LLM backends.

Handles loading and validating API keys and settings from environment
variables and .env files.

Environment Variables:
    OPENROUTER_API_KEY: OpenRouter API key
    OPENAI_API_KEY: OpenAI API key
    ANTHROPIC_API_KEY: Anthropic API key
    LMSTUDIO_BASE_URL: LM Studio server URL (default: http://localhost:1234/v1)
    OLLAMA_BASE_URL: Ollama server URL (default: http://localhost:11434)
"""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

from .base import BackendType


@dataclass
class BackendConfig:
    """Configuration for a single backend."""
    
    backend_type: BackendType
    api_key: str | None = None
    base_url: str | None = None
    timeout: float = 120.0
    extra: dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_configured(self) -> bool:
        """Check if this backend has required configuration.
        
        For cloud backends (OpenRouter, OpenAI, Anthropic), API key is required.
        For local backends (LM Studio, Ollama), no configuration is required.
        """
        if self.backend_type in (BackendType.LMSTUDIO, BackendType.OLLAMA):
            return True  # Local backends don't require configuration
        return bool(self.api_key)


@dataclass 
class Config:
    """Complete configuration for all backends."""
    
    openrouter: BackendConfig
    openai: BackendConfig
    anthropic: BackendConfig
    lmstudio: BackendConfig
    ollama: BackendConfig
    
    # Default model preferences per backend
    default_models: dict[BackendType, str] = field(default_factory=dict)
    
    # Convenience properties for direct access
    @property
    def openrouter_api_key(self) -> str | None:
        return self.openrouter.api_key
    
    @property
    def openai_api_key(self) -> str | None:
        return self.openai.api_key
    
    @property
    def anthropic_api_key(self) -> str | None:
        return self.anthropic.api_key
    
    @property
    def lmstudio_base_url(self) -> str | None:
        return self.lmstudio.base_url
    
    @property
    def ollama_base_url(self) -> str | None:
        return self.ollama.base_url
    
    def get_backend_config(self, backend_type: BackendType) -> BackendConfig:
        """Get configuration for a specific backend."""
        mapping = {
            BackendType.OPENROUTER: self.openrouter,
            BackendType.OPENAI: self.openai,
            BackendType.ANTHROPIC: self.anthropic,
            BackendType.LMSTUDIO: self.lmstudio,
            BackendType.OLLAMA: self.ollama,
        }
        return mapping[backend_type]
    
    def list_configured_backends(self) -> list[BackendType]:
        """List all backends that have required configuration."""
        configured = []
        for backend_type in BackendType:
            if self.get_backend_config(backend_type).is_configured:
                configured.append(backend_type)
        return configured


def load_config(env_file: Path | str | None = None) -> Config:
    """Load configuration from environment variables.
    
    Args:
        env_file: Path to .env file. If None, looks for .env in current
                  directory and parent directories.
    
    Returns:
        Config object with all backend configurations.
        
    Example:
        config = load_config()
        if config.openrouter.is_configured:
            backend = OpenRouterBackend(api_key=config.openrouter.api_key)
    """
    # Load .env file if it exists
    if env_file:
        load_dotenv(env_file)
    else:
        # Try to find .env in current or parent directories
        load_dotenv()
    
    return Config(
        openrouter=BackendConfig(
            backend_type=BackendType.OPENROUTER,
            api_key=os.getenv("OPENROUTER_API_KEY"),
            base_url=os.getenv("OPENROUTER_BASE_URL"),
            timeout=float(os.getenv("OPENROUTER_TIMEOUT", "120")),
        ),
        openai=BackendConfig(
            backend_type=BackendType.OPENAI,
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_BASE_URL"),
            timeout=float(os.getenv("OPENAI_TIMEOUT", "120")),
        ),
        anthropic=BackendConfig(
            backend_type=BackendType.ANTHROPIC,
            api_key=os.getenv("ANTHROPIC_API_KEY"),
            base_url=os.getenv("ANTHROPIC_BASE_URL"),
            timeout=float(os.getenv("ANTHROPIC_TIMEOUT", "120")),
        ),
        lmstudio=BackendConfig(
            backend_type=BackendType.LMSTUDIO,
            base_url=os.getenv("LMSTUDIO_BASE_URL", "http://localhost:1234/v1"),
            timeout=float(os.getenv("LMSTUDIO_TIMEOUT", "300")),
        ),
        ollama=BackendConfig(
            backend_type=BackendType.OLLAMA,
            base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
            timeout=float(os.getenv("OLLAMA_TIMEOUT", "300")),
        ),
        default_models={
            BackendType.OPENROUTER: os.getenv("OPENROUTER_DEFAULT_MODEL", "openai/gpt-4o"),
            BackendType.OPENAI: os.getenv("OPENAI_DEFAULT_MODEL", "gpt-4o"),
            BackendType.ANTHROPIC: os.getenv("ANTHROPIC_DEFAULT_MODEL", "claude-sonnet-4-20250514"),
            BackendType.LMSTUDIO: os.getenv("LMSTUDIO_DEFAULT_MODEL", ""),
            BackendType.OLLAMA: os.getenv("OLLAMA_DEFAULT_MODEL", "llama3.2"),
        }
    )


def create_env_template() -> str:
    """Generate a template .env file content.
    
    Returns:
        String content for a .env.example file.
    """
    return '''# GCB Builder - Backend Configuration
# Copy this file to .env and fill in your API keys

# =============================================================================
# Cloud Backends (API key required)
# =============================================================================

# OpenRouter - Primary cloud backend (https://openrouter.ai)
# Provides access to 100+ models through a single API
OPENROUTER_API_KEY=
OPENROUTER_DEFAULT_MODEL=openai/gpt-4o
# OPENROUTER_TIMEOUT=120

# OpenAI - Direct API access (https://platform.openai.com)
OPENAI_API_KEY=
OPENAI_DEFAULT_MODEL=gpt-4o
# OPENAI_BASE_URL=https://api.openai.com/v1
# OPENAI_TIMEOUT=120

# Anthropic - Direct API access (https://console.anthropic.com)
ANTHROPIC_API_KEY=
ANTHROPIC_DEFAULT_MODEL=claude-sonnet-4-20250514
# ANTHROPIC_TIMEOUT=120

# =============================================================================
# Local Backends (no API key required, just run the server)
# =============================================================================

# LM Studio - Primary local backend (https://lmstudio.ai)
# Start the local server in LM Studio before using
# LMSTUDIO_BASE_URL=http://localhost:1234/v1
# LMSTUDIO_DEFAULT_MODEL=
# LMSTUDIO_TIMEOUT=300

# Ollama - Alternative local backend (https://ollama.ai)
# Run 'ollama serve' before using
# OLLAMA_BASE_URL=http://localhost:11434
# OLLAMA_DEFAULT_MODEL=llama3.2
# OLLAMA_TIMEOUT=300
'''


def write_env_template(directory: Path | str = ".") -> Path:
    """Write a .env.example template file.
    
    Args:
        directory: Directory to write the file to.
        
    Returns:
        Path to the created file.
    """
    path = Path(directory) / ".env.example"
    path.write_text(create_env_template())
    return path


# Global config cache
_config: Config | None = None


def get_config() -> Config:
    """Get the global configuration (cached).
    
    Returns:
        Config object with all backend configurations.
    """
    global _config
    if _config is None:
        _config = load_config()
    return _config


def list_available_backends() -> list[BackendType]:
    """List backends that are configured and available.
    
    Returns:
        List of BackendType values for configured backends.
    """
    config = get_config()
    return config.list_configured_backends()


def get_backend(backend_type: BackendType):
    """Get an initialized backend instance.
    
    Args:
        backend_type: Type of backend to get.
        
    Returns:
        Initialized backend instance.
        
    Raises:
        ValueError: If backend is not configured.
    """
    config = get_config()
    backend_config = config.get_backend_config(backend_type)
    
    if not backend_config.is_configured:
        raise ValueError(f"Backend {backend_type.value} is not configured")
    
    if backend_type == BackendType.OPENROUTER:
        from .openrouter import OpenRouterBackend
        return OpenRouterBackend(
            api_key=backend_config.api_key,
            base_url=backend_config.base_url,
        )
    elif backend_type == BackendType.OPENAI:
        from .direct_api import OpenAIBackend
        return OpenAIBackend(
            api_key=backend_config.api_key,
            base_url=backend_config.base_url,
        )
    elif backend_type == BackendType.ANTHROPIC:
        from .direct_api import AnthropicBackend
        return AnthropicBackend(
            api_key=backend_config.api_key,
            base_url=backend_config.base_url,
        )
    elif backend_type == BackendType.LMSTUDIO:
        from .lmstudio import LMStudioBackend
        return LMStudioBackend(
            base_url=backend_config.base_url,
        )
    elif backend_type == BackendType.OLLAMA:
        from .ollama import OllamaBackend
        return OllamaBackend(
            base_url=backend_config.base_url,
        )
    else:
        raise ValueError(f"Unknown backend type: {backend_type}")


def get_available_backend():
    """Get the first available backend.
    
    Checks backends in order of preference:
    1. OpenRouter (most models)
    2. OpenAI
    3. Anthropic
    4. LM Studio (local)
    5. Ollama (local)
    
    Returns:
        Initialized backend instance.
        
    Raises:
        ValueError: If no backends are configured.
    """
    available = list_available_backends()
    
    if not available:
        raise ValueError("No backends configured. Set API keys or start a local server.")
    
    # Prefer cloud backends over local
    preference_order = [
        BackendType.OPENROUTER,
        BackendType.OPENAI,
        BackendType.ANTHROPIC,
        BackendType.LMSTUDIO,
        BackendType.OLLAMA,
    ]
    
    for backend_type in preference_order:
        if backend_type in available:
            return get_backend(backend_type)
    
    # Fallback to first available
    return get_backend(available[0])
