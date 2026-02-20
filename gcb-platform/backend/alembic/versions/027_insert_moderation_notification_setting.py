"""Insert moderation notification setting

Revision ID: 027
Revises: 026
Create Date: 2025-02-20

Inserts the default notification setting for community submission moderation
alerts. Must run after 026 so the enum value is committed and available.
"""
from alembic import op

revision = "027"
down_revision = "026"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        INSERT INTO notification_settings (id, notification_type, recipient_email, is_enabled, description)
        VALUES (gen_random_uuid(), 'moderation', NULL, true, 'Notified when a community submission enters the moderation queue.')
        ON CONFLICT (notification_type) DO NOTHING
    """)


def downgrade() -> None:
    op.execute("DELETE FROM notification_settings WHERE notification_type = 'moderation'")
