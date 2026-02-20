"""Add action_logs table

Revision ID: 028
Revises: 027
Create Date: 2025-02-20

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid

revision = "028"
down_revision = "027"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "action_logs",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column("action", sa.String(80), nullable=False),
        sa.Column("actor_type", sa.String(20), nullable=False),
        sa.Column("actor_user_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("actor_api_key_id", UUID(as_uuid=True), sa.ForeignKey("user_api_keys.id"), nullable=True),
        sa.Column("entity_type", sa.String(80), nullable=True),
        sa.Column("entity_id", sa.String(255), nullable=True),
        sa.Column("extra_data", JSONB, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_action_logs_action", "action_logs", ["action"])
    op.create_index("ix_action_logs_actor_type", "action_logs", ["actor_type"])
    op.create_index("ix_action_logs_actor_user_id", "action_logs", ["actor_user_id"])
    op.create_index("ix_action_logs_actor_api_key_id", "action_logs", ["actor_api_key_id"])
    op.create_index("ix_action_logs_entity_type", "action_logs", ["entity_type"])
    op.create_index("ix_action_logs_created_at", "action_logs", ["created_at"])


def downgrade() -> None:
    op.drop_index("ix_action_logs_created_at", table_name="action_logs")
    op.drop_index("ix_action_logs_entity_type", table_name="action_logs")
    op.drop_index("ix_action_logs_actor_api_key_id", table_name="action_logs")
    op.drop_index("ix_action_logs_actor_user_id", table_name="action_logs")
    op.drop_index("ix_action_logs_actor_type", table_name="action_logs")
    op.drop_index("ix_action_logs_action", table_name="action_logs")
    op.drop_table("action_logs")
