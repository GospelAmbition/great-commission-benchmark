"""Add contact_submissions and notification_settings tables

Revision ID: 022
Revises: 021
Create Date: 2025-01-16 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, ENUM
import uuid

# revision identifiers, used by Alembic.
revision = '022'
down_revision = '021'
branch_labels = None
depends_on = None

# Define enums
contact_status_enum = ENUM('new', 'read', 'responded', name='contactstatus', create_type=False)
contact_subject_enum = ENUM('general', 'technical', 'partnership', 'media', 'feedback', 'other', name='contactsubject', create_type=False)
notification_type_enum = ENUM('sponsorship', 'volunteer', 'contact', name='notificationtype', create_type=False)


def upgrade() -> None:
    # Create enums
    contact_status_enum.create(op.get_bind(), checkfirst=True)
    contact_subject_enum.create(op.get_bind(), checkfirst=True)
    notification_type_enum.create(op.get_bind(), checkfirst=True)
    
    # Create contact_submissions table
    op.create_table(
        'contact_submissions',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('email', sa.String(255), nullable=False, index=True),
        sa.Column('subject', contact_subject_enum, nullable=False, server_default='general'),
        sa.Column('message', sa.Text, nullable=False),
        sa.Column('status', contact_status_enum, nullable=False, server_default='new'),
        sa.Column('admin_notes', sa.Text, nullable=True),
        sa.Column('responded_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('responded_by', UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    
    # Create notification_settings table
    op.create_table(
        'notification_settings',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('notification_type', notification_type_enum, unique=True, nullable=False),
        sa.Column('recipient_email', sa.String(255), nullable=True),
        sa.Column('is_enabled', sa.Boolean, nullable=False, server_default='true'),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('updated_by_id', UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=True),
    )
    
    # Insert initial notification settings with proper UUID generation
    op.execute("""
        INSERT INTO notification_settings (id, notification_type, recipient_email, is_enabled, description)
        VALUES 
            (gen_random_uuid(), 'sponsorship', NULL, true, 'Notified when a new sponsorship or model request is submitted.'),
            (gen_random_uuid(), 'volunteer', NULL, true, 'Notified when someone applies to volunteer.'),
            (gen_random_uuid(), 'contact', NULL, true, 'Notified when someone submits the contact form.')
    """)


def downgrade() -> None:
    # Drop tables
    op.drop_table('notification_settings')
    op.drop_table('contact_submissions')
    
    # Drop enums
    notification_type_enum.drop(op.get_bind(), checkfirst=True)
    contact_subject_enum.drop(op.get_bind(), checkfirst=True)
    contact_status_enum.drop(op.get_bind(), checkfirst=True)
