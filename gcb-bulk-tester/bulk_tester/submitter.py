"""Submit benchmark results directly via the bulk-submit API endpoint."""

from typing import Any

from gcb_runner.api.client import PlatformAPIClient
from gcb_runner.config import Config


class BulkSubmitter:
    """Client for submitting results via the admin-only bulk-submit endpoint.
    
    This bypasses the normal submission flow (CommunitySubmission, payment,
    moderation) and publishes results directly to the leaderboard with
    trust_tier="automated".
    """
    
    def __init__(self, config: Config):
        self._client = PlatformAPIClient(
            api_key=config.platform.api_key or "",
            base_url=config.platform.url,
        )
    
    async def submit(self, export_data: dict[str, Any]) -> dict[str, Any]:
        """Submit a single model's results for direct publication.
        
        Args:
            export_data: The full export JSON dict (same format as gcb-runner export)
            
        Returns:
            Response dict with status, test_run_id, results_created, score, message
            
        Raises:
            Exception: If submission fails (permissions, validation, server error)
        """
        return await self._client._request(
            "POST",
            "/api/runner/bulk-submit",
            json={"export_data": export_data},
        )
    
    async def verify_admin_access(self) -> dict[str, Any]:
        """Verify the API key has admin access.
        
        Calls GET /api/runner/user-info and checks permissions.
        
        Returns:
            User info dict with role and permissions
            
        Raises:
            PermissionError: If user does not have admin access
        """
        user_info = await self._client._request("GET", "/api/runner/user-info")
        
        permissions = user_info.get("permissions", {})
        if not permissions.get("can_admin", False):
            raise PermissionError(
                f"Admin access required for bulk testing. "
                f"Your role: {user_info.get('role', 'unknown')}. "
                f"Contact a GCB administrator to get admin access."
            )
        
        return user_info
    
    async def close(self) -> None:
        """Close the HTTP client."""
        await self._client.close()
