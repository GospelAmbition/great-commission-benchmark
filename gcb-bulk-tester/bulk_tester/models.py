"""Fetch the list of published models from the platform API."""

from typing import Any

from gcb_runner.api.client import PlatformAPIClient
from gcb_runner.config import Config


async def fetch_published_models(config: Config) -> dict[str, Any]:
    """Fetch the list of all active/published models from the platform.
    
    Uses the admin-only GET /api/runner/models endpoint.
    
    Args:
        config: GCB Runner configuration with platform API key
        
    Returns:
        Dict with 'models' list, 'total' count, and 'current_version'
        
    Raises:
        Exception: If API key lacks admin permissions or request fails
    """
    client = PlatformAPIClient(
        api_key=config.platform.api_key or "",
        base_url=config.platform.url,
    )
    
    try:
        return await client._request("GET", "/api/runner/models")
    finally:
        await client.close()


async def get_model_ids(config: Config) -> list[str]:
    """Get just the model_id strings for all published models.
    
    Convenience wrapper that returns a flat list of model identifiers
    (e.g., ["openai/gpt-4o", "anthropic/claude-3.5-sonnet", ...]).
    
    Args:
        config: GCB Runner configuration
        
    Returns:
        List of model_id strings
    """
    result = await fetch_published_models(config)
    return [m["model_id"] for m in result.get("models", [])]
