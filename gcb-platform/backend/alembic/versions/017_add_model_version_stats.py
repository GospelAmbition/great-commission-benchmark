"""Add model_version_stats table for multi-test averaging

Revision ID: 017
Revises: 016
Create Date: 2025-01-10 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB


# revision identifiers, used by Alembic.
revision = '017'
down_revision = '016'
branch_labels = None
depends_on = None


def upgrade():
    # Create model_version_stats table for storing pre-computed aggregates
    op.create_table(
        'model_version_stats',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('model_id', UUID(as_uuid=True), sa.ForeignKey('models.id', ondelete='CASCADE'), nullable=False),
        sa.Column('question_set_id', UUID(as_uuid=True), sa.ForeignKey('question_sets.id', ondelete='CASCADE'), nullable=False),
        
        # Aggregate scores (averages)
        sa.Column('avg_overall_score', sa.Numeric(6, 2), nullable=True),
        sa.Column('avg_tier1_score', sa.Numeric(6, 2), nullable=True),
        sa.Column('avg_tier2_score', sa.Numeric(6, 2), nullable=True),
        sa.Column('avg_tier3_score', sa.Numeric(6, 2), nullable=True),
        
        # Statistics
        sa.Column('test_count', sa.Integer, default=0, nullable=False),
        sa.Column('min_overall_score', sa.Numeric(6, 2), nullable=True),
        sa.Column('max_overall_score', sa.Numeric(6, 2), nullable=True),
        
        # Category score averages (JSONB for flexibility)
        sa.Column('avg_category_scores', JSONB, nullable=True),
        
        # Verdict distribution totals (summed across all tests)
        sa.Column('total_accepted', sa.Integer, default=0, nullable=False),
        sa.Column('total_compromised', sa.Integer, default=0, nullable=False),
        sa.Column('total_refused', sa.Integer, default=0, nullable=False),
        sa.Column('total_error', sa.Integer, default=0, nullable=False),
        
        # Timestamps
        sa.Column('first_test_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_test_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        
        # Unique constraint on model_id + question_set_id
        sa.UniqueConstraint('model_id', 'question_set_id', name='uq_model_version_stats_model_question_set'),
    )
    
    # Create indexes for common queries
    op.create_index('ix_model_version_stats_model_id', 'model_version_stats', ['model_id'])
    op.create_index('ix_model_version_stats_question_set_id', 'model_version_stats', ['question_set_id'])
    op.create_index('ix_model_version_stats_avg_overall_score', 'model_version_stats', ['avg_overall_score'])


def downgrade():
    op.drop_index('ix_model_version_stats_avg_overall_score', table_name='model_version_stats')
    op.drop_index('ix_model_version_stats_question_set_id', table_name='model_version_stats')
    op.drop_index('ix_model_version_stats_model_id', table_name='model_version_stats')
    op.drop_table('model_version_stats')
