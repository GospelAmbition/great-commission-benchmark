"""Initial schema

Revision ID: 001
Revises: 
Create Date: 2025-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('auth0_id', sa.String(255), nullable=False, unique=True),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('name', sa.String(255)),
        sa.Column('role', sa.String(50), server_default='user'),
        sa.Column('credentials', sa.Text()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_index('ix_users_auth0_id', 'users', ['auth0_id'])
    op.create_index('ix_users_email', 'users', ['email'])

    # Models table
    op.create_table(
        'models',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('model_id', sa.String(255), nullable=False, unique=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('provider', sa.String(255), nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default='true'),
        sa.Column('estimated_cost_per_test', sa.Numeric(10, 2)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('ix_models_model_id', 'models', ['model_id'])

    # Question Sets table
    op.create_table(
        'question_sets',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('semantic_version', sa.String(10), nullable=False),
        sa.Column('marketing_version', sa.String(20), nullable=False),
        sa.Column('status', sa.String(20), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('locked_at', sa.DateTime(timezone=True)),
        sa.Column('archived_at', sa.DateTime(timezone=True)),
        sa.Column('notes', sa.Text()),
    )

    # Methodology Versions table
    op.create_table(
        'methodology_versions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('question_set_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('judge_prompt', sa.Text(), nullable=False),
        sa.Column('scoring_config', postgresql.JSONB(), nullable=False),
        sa.Column('active_from', sa.DateTime(timezone=True), nullable=False),
        sa.Column('active_until', sa.DateTime(timezone=True)),
        sa.Column('changelog', sa.Text()),
        sa.ForeignKeyConstraint(['question_set_id'], ['question_sets.id']),
    )

    # Questions table
    op.create_table(
        'questions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('question_set_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('category', sa.String(100), nullable=False),
        sa.Column('tier', sa.Integer(), nullable=False),
        sa.Column('subcategory', sa.String(100)),
        sa.Column('expected_verdict', sa.String(50)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['question_set_id'], ['question_sets.id']),
    )
    op.create_index('ix_questions_question_set_id', 'questions', ['question_set_id'])
    op.create_index('ix_questions_category', 'questions', ['category'])
    op.create_index('ix_questions_tier', 'questions', ['tier'])

    # Test Runs table
    op.create_table(
        'test_runs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('model_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('question_set_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('methodology_version_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('status', sa.String(50), nullable=False),
        sa.Column('retry_count', sa.Integer(), server_default='0'),
        sa.Column('last_error', sa.Text()),
        sa.Column('checkpoint_question_index', sa.Integer()),
        sa.Column('payment_id', sa.String(255)),
        sa.Column('payment_status', sa.String(50)),
        sa.Column('total_cost', sa.Numeric(10, 2)),
        sa.Column('trust_tier', sa.String(50), server_default='automated'),
        sa.Column('validation_metrics', postgresql.JSONB()),
        sa.Column('admin_assigned_id', postgresql.UUID(as_uuid=True)),
        sa.Column('admin_notes', sa.Text()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('started_at', sa.DateTime(timezone=True)),
        sa.Column('completed_at', sa.DateTime(timezone=True)),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.ForeignKeyConstraint(['model_id'], ['models.id']),
        sa.ForeignKeyConstraint(['question_set_id'], ['question_sets.id']),
        sa.ForeignKeyConstraint(['methodology_version_id'], ['methodology_versions.id']),
        sa.ForeignKeyConstraint(['admin_assigned_id'], ['users.id']),
    )
    op.create_index('ix_test_runs_user_id', 'test_runs', ['user_id'])
    op.create_index('ix_test_runs_model_id', 'test_runs', ['model_id'])
    op.create_index('ix_test_runs_status', 'test_runs', ['status'])
    op.create_index('ix_test_runs_question_set_id', 'test_runs', ['question_set_id'])
    op.create_index('ix_test_runs_created_at', 'test_runs', ['created_at'])

    # Results table
    op.create_table(
        'results',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('test_run_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('question_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('response', sa.Text(), nullable=False),
        sa.Column('verdict', sa.String(50), nullable=False),
        sa.Column('reasoning', sa.Text()),
        sa.Column('tokens_used', sa.Integer()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['test_run_id'], ['test_runs.id']),
        sa.ForeignKeyConstraint(['question_id'], ['questions.id']),
    )
    op.create_index('ix_results_test_run_id', 'results', ['test_run_id'])
    op.create_index('ix_results_verdict', 'results', ['verdict'])

    # Moderation Logs table
    op.create_table(
        'moderation_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('test_run_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('moderator_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('action', sa.String(50), nullable=False),
        sa.Column('sample_size', sa.Integer()),
        sa.Column('agreements', sa.Integer()),
        sa.Column('disagreements', sa.Integer()),
        sa.Column('notes', sa.Text()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['test_run_id'], ['test_runs.id']),
        sa.ForeignKeyConstraint(['moderator_id'], ['users.id']),
    )
    op.create_index('ix_moderation_logs_test_run_id', 'moderation_logs', ['test_run_id'])
    op.create_index('ix_moderation_logs_moderator_id', 'moderation_logs', ['moderator_id'])

    # Sponsorship Requests table
    op.create_table(
        'sponsorship_requests',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('model_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('justification', sa.Text(), nullable=False),
        sa.Column('context', sa.Text()),
        sa.Column('status', sa.String(50), server_default='pending'),
        sa.Column('funded_by', postgresql.UUID(as_uuid=True)),
        sa.Column('funded_at', sa.DateTime(timezone=True)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.ForeignKeyConstraint(['model_id'], ['models.id']),
        sa.ForeignKeyConstraint(['funded_by'], ['users.id']),
    )

    # Newsletter Subscribers table
    op.create_table(
        'newsletter_subscribers',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('subscribed_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('unsubscribed_at', sa.DateTime(timezone=True)),
    )
    op.create_index('ix_newsletter_subscribers_email', 'newsletter_subscribers', ['email'])

    # Community Submissions table
    op.create_table(
        'community_submissions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('model_name', sa.String(255), nullable=False),
        sa.Column('model_url', sa.String(500)),
        sa.Column('organization', sa.String(255)),
        sa.Column('cli_version', sa.String(50), nullable=False),
        sa.Column('question_set_version', sa.String(10), nullable=False),
        sa.Column('results_package', postgresql.JSONB(), nullable=False),
        sa.Column('overall_score', sa.Integer()),
        sa.Column('tier1_score', sa.Integer()),
        sa.Column('tier2_score', sa.Integer()),
        sa.Column('tier3_score', sa.Integer()),
        sa.Column('status', sa.String(50), server_default='pending'),
        sa.Column('reviewer_id', postgresql.UUID(as_uuid=True)),
        sa.Column('reviewer_notes', sa.Text()),
        sa.Column('submitted_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('reviewed_at', sa.DateTime(timezone=True)),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.ForeignKeyConstraint(['reviewer_id'], ['users.id']),
    )
    op.create_index('ix_community_submissions_user_id', 'community_submissions', ['user_id'])
    op.create_index('ix_community_submissions_status', 'community_submissions', ['status'])

    # Notification Preferences table
    op.create_table(
        'notification_preferences',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False, unique=True),
        sa.Column('test_completion', sa.Boolean(), server_default='true'),
        sa.Column('publication', sa.Boolean(), server_default='true'),
        sa.Column('moderation_updates', sa.Boolean(), server_default='true'),
        sa.Column('newsletter', sa.Boolean(), server_default='true'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
    )


def downgrade() -> None:
    op.drop_table('notification_preferences')
    op.drop_table('community_submissions')
    op.drop_table('newsletter_subscribers')
    op.drop_table('sponsorship_requests')
    op.drop_table('moderation_logs')
    op.drop_table('results')
    op.drop_table('test_runs')
    op.drop_table('questions')
    op.drop_table('methodology_versions')
    op.drop_table('question_sets')
    op.drop_table('models')
    op.drop_table('users')
