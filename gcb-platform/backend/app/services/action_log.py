"""Action log service for audit trail of key system actions"""
import logging
from typing import Any, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.db.models.action_log import ActionLog

logger = logging.getLogger(__name__)


class ActionLogService:
    """Service for recording action log entries. Fire-and-forget: never raises."""

    @staticmethod
    def log_action(
        db: Session,
        action: str,
        actor_type: str,
        actor_user_id: Optional[UUID] = None,
        actor_api_key_id: Optional[UUID] = None,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> None:
        """
        Record an action in the audit log.

        Catches and logs errors so action logging never breaks the main flow.
        """
        try:
            entry = ActionLog(
                action=action,
                actor_type=actor_type,
                actor_user_id=actor_user_id,
                actor_api_key_id=actor_api_key_id,
                entity_type=entity_type,
                entity_id=entity_id,
                extra_data=metadata,
            )
            db.add(entry)
            db.commit()
        except Exception as e:
            logger.warning("Failed to write action log: %s", e)
            db.rollback()
