"""Newsletter service with MailerLite integration"""
import httpx
from typing import Optional, Dict, Any, List, Tuple
from app.core.config import settings


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
    async def sync_subscriber_to_mailerlite(email: str) -> Optional[str]:
        """
        Add or update a subscriber in MailerLite.
        
        Args:
            email: Subscriber email address
        
        Returns:
            MailerLite subscriber ID if successful, None otherwise
        """
        if not NewsletterService.is_configured():
            print(f"MailerLite not configured - skipping sync for {email}")
            return None
        
        try:
            async with httpx.AsyncClient() as client:
                # Create/update subscriber
                payload: Dict[str, Any] = {
                    "email": email,
                    "status": "active"
                }
                
                # Add to specific group if configured
                if settings.MAILERLITE_GROUP_ID:
                    payload["groups"] = [settings.MAILERLITE_GROUP_ID]
                
                response = await client.post(
                    f"{NewsletterService.MAILERLITE_API_BASE}/subscribers",
                    headers=NewsletterService._get_headers(),
                    json=payload,
                    timeout=10.0
                )
                
                if response.status_code in (200, 201):
                    data = response.json()
                    subscriber_id = data.get("data", {}).get("id")
                    print(f"MailerLite: Synced subscriber {email} (ID: {subscriber_id})")
                    return str(subscriber_id) if subscriber_id else None
                elif response.status_code == 422:
                    # Subscriber already exists - try to get their ID
                    existing = await NewsletterService.get_mailerlite_subscriber(email)
                    if existing:
                        return existing.get("id")
                    return None
                else:
                    print(f"MailerLite API error: {response.status_code} - {response.text}")
                    return None
                    
        except httpx.TimeoutException:
            print(f"MailerLite API timeout for {email}")
            return None
        except Exception as e:
            print(f"MailerLite sync failed for {email}: {str(e)}")
            return None
    
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
            
            # Use group-specific endpoint if group ID is configured
            if settings.MAILERLITE_GROUP_ID:
                url = f"{NewsletterService.MAILERLITE_API_BASE}/groups/{settings.MAILERLITE_GROUP_ID}/subscribers"
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
