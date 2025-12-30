"""Platform API client for fetching benchmark questions."""

from typing import Any, cast

import httpx


class PlatformAPIError(Exception):
    """Exception raised for Platform API errors."""
    
    def __init__(self, message: str, status_code: int | None = None):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class PlatformAPIClient:
    """Client for the GCB Platform API."""
    
    def __init__(self, api_key: str, base_url: str = "https://api.greatcommissionbenchmark.ai"):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self._client: httpx.AsyncClient | None = None
    
    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create the HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                headers={
                    "X-API-Key": self.api_key,
                    "User-Agent": "gcb-runner/0.1.1",
                },
                timeout=30.0,
            )
        return self._client
    
    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None
    
    async def _request(self, method: str, path: str, **kwargs: Any) -> dict[str, Any]:
        """Make a request to the API."""
        client = await self._get_client()
        
        try:
            response = await client.request(method, path, **kwargs)
            
            if response.status_code == 401:
                raise PlatformAPIError("Invalid or missing API key", 401)
            elif response.status_code == 404:
                raise PlatformAPIError("Resource not found", 404)
            elif response.status_code == 429:
                raise PlatformAPIError("Rate limit exceeded. Please try again later.", 429)
            elif response.status_code >= 400:
                raise PlatformAPIError(f"API error: {response.text}", response.status_code)
            
            return cast(dict[str, Any], response.json())
            
        except httpx.TimeoutException as e:
            raise PlatformAPIError("Request timed out") from e
        except httpx.RequestError as e:
            raise PlatformAPIError(f"Network error: {e}") from e
    
    async def list_versions(self, include_drafts: bool = False) -> dict[str, Any]:
        """List available benchmark versions.
        
        Args:
            include_drafts: If True, include draft and locked versions for testing.
                           Default is False (only published versions).
        """
        params = {"include_drafts": "true"} if include_drafts else {}
        return await self._request("GET", "/api/runner/versions", params=params)
    
    async def get_questions(self, version: str | None = "current") -> dict[str, Any]:
        """Fetch the complete question set for a benchmark version.
        
        Args:
            version: The semantic version (e.g. "1.0.0") or "current" for the active version.
                     If None or empty, uses "current".
        """
        # Handle None/empty as current - no version param means get the active/current version
        params = {} if not version or version == "current" else {"version": version}
        
        return await self._request("GET", "/api/runner/questions", params=params)
    
    async def get_judge_prompts(self, version: str = "current") -> dict[str, Any]:
        """Fetch judge prompts for a benchmark version."""
        return await self._request("GET", "/api/runner/judge-prompts", params={"version": version})
    
    async def get_user_info(self) -> dict[str, Any]:
        """Fetch user information for the authenticated API key.
        
        Returns:
            dict with role, is_admin, is_benchmark_developer, is_moderator, email, name
        """
        return await self._request("GET", "/api/runner/user-info")


def get_user_info_sync(api_key: str, base_url: str = "https://api.greatcommissionbenchmark.ai") -> dict[str, Any] | None:
    """Synchronous function to fetch user info for the results viewer.
    
    This is a standalone sync function (not a method) for use in the synchronous
    HTTP server that powers the results viewer.
    
    Args:
        api_key: The platform API key
        base_url: The platform API base URL
        
    Returns:
        dict with role, is_admin, is_benchmark_developer, is_moderator, email, name
        Returns None if the request fails or API key is invalid.
    """
    if not api_key:
        return None
    
    try:
        with httpx.Client(
            base_url=base_url.rstrip("/"),
            headers={
                "X-API-Key": api_key,
                "User-Agent": "gcb-runner/0.1.1",
            },
            timeout=10.0,
        ) as client:
            response = client.get("/api/runner/user-info")
            
            if response.status_code == 200:
                return cast(dict[str, Any], response.json())
            else:
                return None
                
    except (httpx.TimeoutException, httpx.RequestError):
        return None