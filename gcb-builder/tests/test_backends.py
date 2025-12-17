"""
Tests for LLM backend adapters.

These tests verify:
1. Backend protocol compliance
2. Request/response formatting
3. Error handling
4. Configuration loading

Note: Most tests use mocking to avoid actual API calls.
Integration tests with real APIs are in test_backends_integration.py
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import httpx

from gcb_builder.backends import (
    BackendType,
    CompletionRequest,
    CompletionResponse,
    ModelInfo,
    OpenRouterBackend,
    LMStudioBackend,
    OllamaBackend,
    OpenAIBackend,
    AnthropicBackend,
    AuthenticationError,
    RateLimitError,
    ModelNotFoundError,
    ConnectionError,
    BackendError,
    get_backend,
    load_config,
    create_env_template,
)


# =============================================================================
# Test Fixtures
# =============================================================================

@pytest.fixture
def sample_request():
    """Create a sample completion request."""
    return CompletionRequest(
        messages=[{"role": "user", "content": "Hello, how are you?"}],
        model="test-model",
        system_prompt="You are a helpful assistant.",
        temperature=0.7,
    )


@pytest.fixture
def sample_openai_response():
    """Sample OpenAI-format API response."""
    return {
        "id": "chatcmpl-123",
        "object": "chat.completion",
        "model": "test-model",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": "I'm doing well, thank you!"
                },
                "finish_reason": "stop"
            }
        ],
        "usage": {
            "prompt_tokens": 20,
            "completion_tokens": 10,
            "total_tokens": 30
        }
    }


# =============================================================================
# Base Protocol Tests
# =============================================================================

class TestCompletionRequest:
    """Tests for CompletionRequest dataclass."""
    
    def test_to_openai_format_basic(self, sample_request):
        """Test basic OpenAI format conversion."""
        result = sample_request.to_openai_format()
        
        assert result["model"] == "test-model"
        assert result["temperature"] == 0.7
        assert len(result["messages"]) == 2  # system + user
        assert result["messages"][0]["role"] == "system"
        assert result["messages"][1]["role"] == "user"
    
    def test_to_openai_format_no_system(self):
        """Test OpenAI format without system prompt."""
        request = CompletionRequest(
            messages=[{"role": "user", "content": "Hello"}],
            model="test-model",
        )
        result = request.to_openai_format()
        
        assert len(result["messages"]) == 1
        assert result["messages"][0]["role"] == "user"
    
    def test_to_openai_format_with_max_tokens(self):
        """Test OpenAI format with max_tokens."""
        request = CompletionRequest(
            messages=[{"role": "user", "content": "Hello"}],
            model="test-model",
            max_tokens=100,
        )
        result = request.to_openai_format()
        
        assert result["max_tokens"] == 100


class TestCompletionResponse:
    """Tests for CompletionResponse dataclass."""
    
    def test_total_tokens(self):
        """Test total token calculation."""
        response = CompletionResponse(
            content="Hello!",
            model="test-model",
            usage={"prompt_tokens": 10, "completion_tokens": 5},
        )
        
        assert response.total_tokens == 15
    
    def test_total_tokens_no_usage(self):
        """Test total tokens when usage not provided."""
        response = CompletionResponse(
            content="Hello!",
            model="test-model",
        )
        
        assert response.total_tokens is None


class TestModelInfo:
    """Tests for ModelInfo dataclass."""
    
    def test_str_representation(self):
        """Test string representation."""
        model = ModelInfo(
            id="openai/gpt-4o",
            name="GPT-4o",
            backend=BackendType.OPENROUTER,
        )
        
        assert str(model) == "GPT-4o (openai/gpt-4o)"


# =============================================================================
# OpenRouter Backend Tests
# =============================================================================

class TestOpenRouterBackend:
    """Tests for OpenRouter backend."""
    
    def test_backend_type(self):
        """Test backend type property."""
        backend = OpenRouterBackend(api_key="test-key")
        assert backend.backend_type == BackendType.OPENROUTER
        assert backend.name == "OpenRouter"
    
    def test_requires_api_key(self):
        """Test that API key is validated."""
        backend = OpenRouterBackend()  # No API key
        
        with pytest.raises(AuthenticationError):
            backend._validate_api_key()
    
    @pytest.mark.asyncio
    async def test_complete_success(self, sample_request, sample_openai_response):
        """Test successful completion."""
        backend = OpenRouterBackend(api_key="test-key")
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_openai_response
        
        with patch.object(backend, '_get_client') as mock_client:
            mock_client.return_value.post = AsyncMock(return_value=mock_response)
            
            response = await backend.complete(sample_request)
            
            assert response.content == "I'm doing well, thank you!"
            assert response.model == "test-model"
            assert response.usage["prompt_tokens"] == 20
    
    @pytest.mark.asyncio
    async def test_complete_auth_error(self, sample_request):
        """Test authentication error handling."""
        backend = OpenRouterBackend(api_key="invalid-key")
        
        mock_response = MagicMock()
        mock_response.status_code = 401
        
        with patch.object(backend, '_get_client') as mock_client:
            mock_client.return_value.post = AsyncMock(return_value=mock_response)
            
            with pytest.raises(AuthenticationError):
                await backend.complete(sample_request)
    
    @pytest.mark.asyncio
    async def test_complete_rate_limit(self, sample_request):
        """Test rate limit error handling."""
        backend = OpenRouterBackend(api_key="test-key")
        
        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_response.headers = {"Retry-After": "60"}
        
        with patch.object(backend, '_get_client') as mock_client:
            mock_client.return_value.post = AsyncMock(return_value=mock_response)
            
            with pytest.raises(RateLimitError) as exc_info:
                await backend.complete(sample_request)
            
            assert exc_info.value.retry_after == 60


# =============================================================================
# LM Studio Backend Tests
# =============================================================================

class TestLMStudioBackend:
    """Tests for LM Studio backend."""
    
    def test_backend_type(self):
        """Test backend type property."""
        backend = LMStudioBackend()
        assert backend.backend_type == BackendType.LMSTUDIO
        assert backend.name == "LM Studio"
    
    def test_no_api_key_required(self):
        """Test that no API key is required."""
        backend = LMStudioBackend()
        # Should not raise - LM Studio doesn't require API key
        assert backend._api_key is None
    
    @pytest.mark.asyncio
    async def test_complete_success(self, sample_request, sample_openai_response):
        """Test successful completion."""
        backend = LMStudioBackend()
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_openai_response
        
        with patch.object(backend, '_get_client') as mock_client:
            mock_client.return_value.post = AsyncMock(return_value=mock_response)
            
            response = await backend.complete(sample_request)
            
            assert response.content == "I'm doing well, thank you!"


# =============================================================================
# Ollama Backend Tests  
# =============================================================================

class TestOllamaBackend:
    """Tests for Ollama backend."""
    
    def test_backend_type(self):
        """Test backend type property."""
        backend = OllamaBackend()
        assert backend.backend_type == BackendType.OLLAMA
        assert backend.name == "Ollama"
    
    @pytest.mark.asyncio
    async def test_complete_success(self, sample_request):
        """Test successful completion with Ollama format."""
        backend = OllamaBackend()
        
        # Ollama has different response format
        ollama_response = {
            "model": "llama3.2",
            "message": {
                "role": "assistant",
                "content": "Hello! I'm doing great."
            },
            "done": True,
            "done_reason": "stop",
            "prompt_eval_count": 15,
            "eval_count": 8,
        }
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = ollama_response
        
        with patch.object(backend, '_get_client') as mock_client:
            mock_client.return_value.post = AsyncMock(return_value=mock_response)
            
            response = await backend.complete(sample_request)
            
            assert response.content == "Hello! I'm doing great."
            assert response.usage["prompt_tokens"] == 15
            assert response.usage["completion_tokens"] == 8


# =============================================================================
# OpenAI Backend Tests
# =============================================================================

class TestOpenAIBackend:
    """Tests for direct OpenAI backend."""
    
    def test_backend_type(self):
        """Test backend type property."""
        backend = OpenAIBackend(api_key="test-key")
        assert backend.backend_type == BackendType.OPENAI
        assert backend.name == "OpenAI"
    
    def test_known_models(self):
        """Test that known models list is populated."""
        assert len(OpenAIBackend.KNOWN_MODELS) > 0
        assert any("gpt-4o" in m[0] for m in OpenAIBackend.KNOWN_MODELS)


# =============================================================================
# Anthropic Backend Tests
# =============================================================================

class TestAnthropicBackend:
    """Tests for direct Anthropic backend."""
    
    def test_backend_type(self):
        """Test backend type property."""
        backend = AnthropicBackend(api_key="test-key")
        assert backend.backend_type == BackendType.ANTHROPIC
        assert backend.name == "Anthropic"
    
    @pytest.mark.asyncio
    async def test_complete_success(self, sample_request):
        """Test successful completion with Anthropic format."""
        backend = AnthropicBackend(api_key="test-key")
        
        # Anthropic has different response format
        anthropic_response = {
            "id": "msg_123",
            "type": "message",
            "role": "assistant",
            "model": "claude-sonnet-4-20250514",
            "content": [
                {"type": "text", "text": "Hello! How can I help?"}
            ],
            "stop_reason": "end_turn",
            "usage": {
                "input_tokens": 20,
                "output_tokens": 10,
            }
        }
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = anthropic_response
        
        with patch.object(backend, '_get_client') as mock_client:
            mock_client.return_value.post = AsyncMock(return_value=mock_response)
            
            response = await backend.complete(sample_request)
            
            assert response.content == "Hello! How can I help?"
            assert response.usage["prompt_tokens"] == 20
            assert response.usage["completion_tokens"] == 10


# =============================================================================
# Factory Function Tests
# =============================================================================

class TestGetBackend:
    """Tests for get_backend factory function."""
    
    def test_get_openrouter(self):
        """Test getting OpenRouter backend."""
        backend = get_backend(BackendType.OPENROUTER)
        assert isinstance(backend, OpenRouterBackend)
    
    def test_get_lmstudio(self):
        """Test getting LM Studio backend."""
        backend = get_backend(BackendType.LMSTUDIO)
        assert isinstance(backend, LMStudioBackend)
    
    def test_get_ollama(self):
        """Test getting Ollama backend."""
        backend = get_backend(BackendType.OLLAMA)
        assert isinstance(backend, OllamaBackend)
    
    def test_get_openai(self):
        """Test getting OpenAI backend."""
        backend = get_backend(BackendType.OPENAI)
        assert isinstance(backend, OpenAIBackend)
    
    def test_get_anthropic(self):
        """Test getting Anthropic backend."""
        backend = get_backend(BackendType.ANTHROPIC)
        assert isinstance(backend, AnthropicBackend)


# =============================================================================
# Configuration Tests
# =============================================================================

class TestConfiguration:
    """Tests for configuration loading."""
    
    def test_load_config_with_env(self):
        """Test loading config from environment."""
        with patch.dict('os.environ', {
            'OPENROUTER_API_KEY': 'test-openrouter-key',
            'OPENAI_API_KEY': 'test-openai-key',
        }):
            config = load_config()
            
            assert config.openrouter.api_key == 'test-openrouter-key'
            assert config.openrouter.is_configured
            assert config.openai.api_key == 'test-openai-key'
            assert config.openai.is_configured
            # Local backends don't need API keys
            assert config.lmstudio.is_configured
            assert config.ollama.is_configured
    
    def test_list_configured_backends(self):
        """Test listing configured backends."""
        with patch.dict('os.environ', {
            'OPENROUTER_API_KEY': 'test-key',
        }, clear=True):
            config = load_config()
            configured = config.list_configured_backends()
            
            # Should include OpenRouter (has API key) and local backends
            assert BackendType.OPENROUTER in configured
            assert BackendType.LMSTUDIO in configured
            assert BackendType.OLLAMA in configured
            # Should NOT include OpenAI/Anthropic without keys
            assert BackendType.OPENAI not in configured
            assert BackendType.ANTHROPIC not in configured
    
    def test_env_template(self):
        """Test environment template generation."""
        template = create_env_template()
        
        assert "OPENROUTER_API_KEY" in template
        assert "OPENAI_API_KEY" in template
        assert "ANTHROPIC_API_KEY" in template
        assert "LMSTUDIO_BASE_URL" in template
        assert "OLLAMA_BASE_URL" in template


# =============================================================================
# Error Handling Tests
# =============================================================================

class TestErrorHandling:
    """Tests for error classes."""
    
    def test_authentication_error(self):
        """Test AuthenticationError."""
        error = AuthenticationError("Invalid key", backend=BackendType.OPENAI)
        assert str(error) == "Invalid key"
        assert error.backend == BackendType.OPENAI
    
    def test_rate_limit_error(self):
        """Test RateLimitError with retry_after."""
        error = RateLimitError("Rate limited", retry_after=60.0, backend=BackendType.OPENROUTER)
        assert error.retry_after == 60.0
        assert error.backend == BackendType.OPENROUTER
    
    def test_model_not_found_error(self):
        """Test ModelNotFoundError."""
        error = ModelNotFoundError("Model not found", backend=BackendType.OLLAMA)
        assert "Model not found" in str(error)
        assert error.backend == BackendType.OLLAMA
