"""OpenRouter API client"""
import httpx
from typing import Dict, List, Optional
from app.core.config import settings


class OpenRouterClient:
    """Client for OpenRouter API"""
    
    BASE_URL = "https://openrouter.ai/api/v1"
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or getattr(settings, "OPENROUTER_API_KEY", "")
        self.client = httpx.AsyncClient(
            base_url=self.BASE_URL,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "HTTP-Referer": getattr(settings, "OPENROUTER_REFERER", "https://greatcommissionbenchmark.ai"),
                "X-Title": "Great Commission Benchmark"
            },
            timeout=60.0
        )
    
    async def complete(
        self,
        model: str,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> Dict:
        """
        Send completion request to OpenRouter
        
        Args:
            model: Model identifier (e.g., "anthropic/claude-3.5-sonnet")
            messages: List of message dicts with "role" and "content"
            system_prompt: Optional system prompt
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
        
        Returns:
            Response dict with text, usage, etc.
        """
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature
        }
        
        if system_prompt:
            payload["system"] = system_prompt
        
        if max_tokens:
            payload["max_tokens"] = max_tokens
        
        try:
            response = await self.client.post("/chat/completions", json=payload)
            response.raise_for_status()
            data = response.json()
            
            return {
                "text": data["choices"][0]["message"]["content"],
                "usage": data.get("usage", {}),
                "model": data.get("model"),
                "finish_reason": data["choices"][0].get("finish_reason")
            }
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                raise Exception("Rate limit exceeded. Please try again later.")
            raise Exception(f"OpenRouter API error: {e.response.text}")
        except Exception as e:
            raise Exception(f"Failed to call OpenRouter: {str(e)}")
    
    async def list_models(self) -> List[Dict]:
        """List available models"""
        try:
            response = await self.client.get("/models")
            response.raise_for_status()
            return response.json().get("data", [])
        except Exception as e:
            raise Exception(f"Failed to list models: {str(e)}")
    
    async def get_model_pricing(self, model: str) -> Dict:
        """
        Get pricing information for a model
        
        Args:
            model: Model identifier
        
        Returns:
            Pricing information dict
        """
        models = await self.list_models()
        for m in models:
            if m.get("id") == model:
                return {
                    "pricing": m.get("pricing", {}),
                    "context_length": m.get("context_length", 0)
                }
        return {}
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()