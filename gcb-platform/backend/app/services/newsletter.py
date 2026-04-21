"""Newsletter service with MailerLite integration"""
import logging
import re
import httpx
from typing import Optional, Dict, Any, List, Tuple, Literal
from app.core.config import settings

logger = logging.getLogger(__name__)


class NewsletterService:
    """Service for managing newsletter subscriptions via MailerLite"""
    
    MAILERLITE_API_BASE = "https://connect.mailerlite.com/api"
    
    @staticmethod
    def _get_headers() -> Dict[str, str]:
        """Get headers for MailerLite API requests"""
        return {
            "Authorization": f"Bearer {settings.MAILERLITE_API_KEY}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    
    @staticmethod
    def is_configured() -> bool:
        """Check if MailerLite is configured"""
        return bool(settings.MAILERLITE_API_KEY)

    @staticmethod
    def production_group_id() -> str:
        """Resolve production audience group with backward compatibility."""
        return settings.MAILERLITE_PROD_GROUP_ID or settings.MAILERLITE_GROUP_ID

    @staticmethod
    def test_group_id() -> str:
        """Resolve test audience group."""
        return settings.MAILERLITE_TEST_GROUP_ID

    @staticmethod
    def audience_group_id(audience: Literal["test", "production"]) -> str:
        """Resolve MailerLite group ID for the requested audience."""
        if audience == "test":
            return NewsletterService.test_group_id()
        return NewsletterService.production_group_id()

    @staticmethod
    async def sync_subscriber_to_group(email: str, group_id: Optional[str]) -> Optional[str]:
        """Add or update a subscriber and optionally attach them to a specific group."""
        if not NewsletterService.is_configured():
            print(f"MailerLite not configured - skipping sync for {email}")
            return None

        try:
            async with httpx.AsyncClient() as client:
                payload: Dict[str, Any] = {
                    "email": email,
                    "status": "active",
                }
                if group_id:
                    payload["groups"] = [group_id]

                response = await client.post(
                    f"{NewsletterService.MAILERLITE_API_BASE}/subscribers",
                    headers=NewsletterService._get_headers(),
                    json=payload,
                    timeout=10.0,
                )

                if response.status_code in (200, 201):
                    data = response.json()
                    subscriber_id = data.get("data", {}).get("id")
                    print(f"MailerLite: Synced subscriber {email} (ID: {subscriber_id})")
                    return str(subscriber_id) if subscriber_id else None
                if response.status_code == 422:
                    existing = await NewsletterService.get_mailerlite_subscriber(email)
                    if existing:
                        return existing.get("id")
                    return None

                print(f"MailerLite API error: {response.status_code} - {response.text}")
                return None

        except httpx.TimeoutException:
            print(f"MailerLite API timeout for {email}")
            return None
        except Exception as e:
            print(f"MailerLite sync failed for {email}: {str(e)}")
            return None
    
    @staticmethod
    async def sync_subscriber_to_mailerlite(email: str) -> Optional[str]:
        """
        Add or update a subscriber in MailerLite.
        
        Args:
            email: Subscriber email address
        
        Returns:
            MailerLite subscriber ID if successful, None otherwise
        """
        production_group = NewsletterService.production_group_id()
        return await NewsletterService.sync_subscriber_to_group(email, production_group)
    
    @staticmethod
    async def remove_subscriber_from_mailerlite(email: str) -> bool:
        """
        Remove/unsubscribe a subscriber from MailerLite.
        
        Args:
            email: Subscriber email address
        
        Returns:
            True if successful, False otherwise
        """
        if not NewsletterService.is_configured():
            print(f"MailerLite not configured - skipping removal for {email}")
            return False
        
        try:
            # First get the subscriber to get their ID
            subscriber = await NewsletterService.get_mailerlite_subscriber(email)
            if not subscriber:
                print(f"MailerLite: Subscriber {email} not found")
                return True  # Already not in MailerLite
            
            subscriber_id = subscriber.get("id")
            
            async with httpx.AsyncClient() as client:
                # Update subscriber status to unsubscribed
                response = await client.put(
                    f"{NewsletterService.MAILERLITE_API_BASE}/subscribers/{subscriber_id}",
                    headers=NewsletterService._get_headers(),
                    json={"status": "unsubscribed"},
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    print(f"MailerLite: Unsubscribed {email}")
                    return True
                else:
                    print(f"MailerLite unsubscribe error: {response.status_code} - {response.text}")
                    return False
                    
        except httpx.TimeoutException:
            print(f"MailerLite API timeout for unsubscribe {email}")
            return False
        except Exception as e:
            print(f"MailerLite unsubscribe failed for {email}: {str(e)}")
            return False

    @staticmethod
    async def remove_subscriber_from_group(email: str, group_id: str) -> bool:
        """Remove a subscriber from a specific MailerLite group without global unsubscribe."""
        if not NewsletterService.is_configured() or not group_id:
            return False

        try:
            subscriber = await NewsletterService.get_mailerlite_subscriber(email)
            if not subscriber:
                return True

            subscriber_id = subscriber.get("id")
            if not subscriber_id:
                return False

            async with httpx.AsyncClient() as client:
                response = await client.delete(
                    f"{NewsletterService.MAILERLITE_API_BASE}/groups/{group_id}/subscribers/{subscriber_id}",
                    headers=NewsletterService._get_headers(),
                    timeout=10.0,
                )
                if response.status_code in (200, 202, 204, 404):
                    return True

                print(f"MailerLite remove-from-group error: {response.status_code} - {response.text}")
                return False
        except httpx.TimeoutException:
            print(f"MailerLite API timeout removing {email} from group {group_id}")
            return False
        except Exception as e:
            print(f"MailerLite remove-from-group failed for {email}: {str(e)}")
            return False
    
    @staticmethod
    async def get_mailerlite_subscriber(email: str) -> Optional[Dict[str, Any]]:
        """
        Get subscriber details from MailerLite.
        
        Args:
            email: Subscriber email address
        
        Returns:
            Subscriber data dict if found, None otherwise
        """
        if not NewsletterService.is_configured():
            return None
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{NewsletterService.MAILERLITE_API_BASE}/subscribers/{email}",
                    headers=NewsletterService._get_headers(),
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return data.get("data")
                elif response.status_code == 404:
                    return None
                else:
                    print(f"MailerLite get subscriber error: {response.status_code}")
                    return None
                    
        except httpx.TimeoutException:
            print(f"MailerLite API timeout getting {email}")
            return None
        except Exception as e:
            print(f"MailerLite get subscriber failed for {email}: {str(e)}")
            return None
    
    @staticmethod
    async def reactivate_subscriber(email: str) -> Optional[str]:
        """
        Reactivate a previously unsubscribed subscriber in MailerLite.
        
        Args:
            email: Subscriber email address
        
        Returns:
            MailerLite subscriber ID if successful, None otherwise
        """
        if not NewsletterService.is_configured():
            return None
        
        try:
            subscriber = await NewsletterService.get_mailerlite_subscriber(email)
            if not subscriber:
                # Not in MailerLite, create new
                return await NewsletterService.sync_subscriber_to_mailerlite(email)
            
            subscriber_id = subscriber.get("id")
            
            async with httpx.AsyncClient() as client:
                response = await client.put(
                    f"{NewsletterService.MAILERLITE_API_BASE}/subscribers/{subscriber_id}",
                    headers=NewsletterService._get_headers(),
                    json={"status": "active"},
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    print(f"MailerLite: Reactivated {email}")
                    return str(subscriber_id)
                else:
                    print(f"MailerLite reactivate error: {response.status_code} - {response.text}")
                    return None
                    
        except Exception as e:
            print(f"MailerLite reactivate failed for {email}: {str(e)}")
            return None

    @staticmethod
    async def list_mailerlite_subscribers(
        cursor: Optional[str] = None,
        limit: int = 50
    ) -> Tuple[List[Dict[str, Any]], Optional[str]]:
        """
        List subscribers from MailerLite with cursor-based pagination.
        
        If MAILERLITE_GROUP_ID is set, lists subscribers in that group.
        Otherwise lists all subscribers.
        
        Args:
            cursor: Pagination cursor from previous response
            limit: Number of subscribers per page (max 50)
        
        Returns:
            Tuple of (subscriber list, next_cursor or None)
        """
        if not NewsletterService.is_configured():
            return [], None
        
        try:
            params: Dict[str, Any] = {"limit": min(limit, 50)}
            if cursor:
                params["cursor"] = cursor
            
            # Use production group-specific endpoint if configured.
            production_group = NewsletterService.production_group_id()
            if production_group:
                url = f"{NewsletterService.MAILERLITE_API_BASE}/groups/{production_group}/subscribers"
            else:
                url = f"{NewsletterService.MAILERLITE_API_BASE}/subscribers"
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url,
                    headers=NewsletterService._get_headers(),
                    params=params,
                    timeout=15.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    subscribers = data.get("data", [])
                    next_cursor = data.get("meta", {}).get("next_cursor")
                    return subscribers, next_cursor
                else:
                    print(f"MailerLite list subscribers error: {response.status_code} - {response.text}")
                    return [], None
                    
        except httpx.TimeoutException:
            print("MailerLite API timeout listing subscribers")
            return [], None
        except Exception as e:
            print(f"MailerLite list subscribers failed: {str(e)}")
            return [], None

    @staticmethod
    def _strip_html_for_plain(html: str, max_len: int = 12000) -> str:
        text = re.sub(r"<[^>]+>", " ", html or "")
        text = re.sub(r"\s+", " ", text).strip()
        return text[:max_len]

    @staticmethod
    async def create_and_send_instant_regular_campaign(
        *,
        name: str,
        subject: str,
        html_content: str,
        group_id: str,
        from_email: str,
        from_name: str,
    ) -> Dict[str, Any]:
        """
        Create a MailerLite ``regular`` campaign with HTML content and send immediately.

        Uses ``POST /api/campaigns`` then ``POST /api/campaigns/{id}/schedule`` with
        ``{"delivery": "instant"}`` per MailerLite's current API.
        """
        if not NewsletterService.is_configured():
            return {"ok": False, "error": "mailerlite_not_configured"}
        if not group_id:
            return {"ok": False, "error": "missing_group_id"}

        plain = NewsletterService._strip_html_for_plain(html_content)
        payload: Dict[str, Any] = {
            "name": name[:255],
            "type": "regular",
            "emails": [
                {
                    "subject": subject[:255],
                    "from": from_email,
                    "from_name": from_name[:255],
                    "content": html_content,
                    "plain_text": plain,
                }
            ],
            "groups": [group_id],
        }

        try:
            async with httpx.AsyncClient() as client:
                create = await client.post(
                    f"{NewsletterService.MAILERLITE_API_BASE}/campaigns",
                    headers=NewsletterService._get_headers(),
                    json=payload,
                    timeout=60.0,
                )
        except httpx.TimeoutException:
            return {"ok": False, "error": "timeout", "step": "create"}
        except Exception as exc:
            logger.exception("MailerLite campaign create failed")
            return {"ok": False, "error": "request_failed", "message": str(exc), "step": "create"}

        if create.status_code not in (200, 201):
            return {
                "ok": False,
                "error": "create_failed",
                "status_code": create.status_code,
                "detail": NewsletterService._safe_json(create),
                "step": "create",
            }

        created = create.json()
        campaign_id = (created.get("data") or {}).get("id")
        if not campaign_id:
            return {"ok": False, "error": "missing_campaign_id", "detail": created, "step": "create"}

        schedule_url = f"{NewsletterService.MAILERLITE_API_BASE}/campaigns/{campaign_id}/schedule"
        schedule_body = {"delivery": "instant"}

        try:
            async with httpx.AsyncClient() as client:
                sched = await client.post(
                    schedule_url,
                    headers=NewsletterService._get_headers(),
                    json=schedule_body,
                    timeout=60.0,
                )
        except httpx.TimeoutException:
            return {
                "ok": False,
                "error": "timeout",
                "step": "schedule",
                "campaign_id": str(campaign_id),
            }
        except Exception as exc:
            logger.exception("MailerLite campaign schedule failed")
            return {
                "ok": False,
                "error": "request_failed",
                "message": str(exc),
                "step": "schedule",
                "campaign_id": str(campaign_id),
            }

        if sched.status_code not in (200, 201, 202, 204):
            return {
                "ok": False,
                "error": "schedule_failed",
                "status_code": sched.status_code,
                "detail": NewsletterService._safe_json(sched),
                "step": "schedule",
                "campaign_id": str(campaign_id),
            }

        out: Dict[str, Any] = {"ok": True, "campaign_id": str(campaign_id)}
        if sched.content:
            try:
                out["schedule_response"] = sched.json()
            except Exception:
                out["schedule_response"] = sched.text
        return out

    @staticmethod
    def _safe_json(resp: httpx.Response) -> Any:
        try:
            return resp.json()
        except Exception:
            return resp.text
