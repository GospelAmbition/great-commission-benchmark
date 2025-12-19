"""Add CASCADE delete to question_set foreign keys

Revision ID: 007
Revises: 006
Create Date: 2025-12-19 16:00:00.000000

This migration updates the foreign key constraints on questions.question_set_id
and methodology_versions.question_set_id to include ON DELETE CASCADE.
This ensures that when a QuestionSet is deleted, all associated questions
and methodology versions are automatically deleted, preventing orphaned records.

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '007'
down_revision = '006'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # --- Questions table ---
    op.drop_constraint(
        'questions_question_set_id_fkey',
        'questions',
        type_='foreignkey'
    )
    op.create_foreign_key(
        'questions_question_set_id_fkey',
        'questions',
        'question_sets',
        ['question_set_id'],
        ['id'],
        ondelete='CASCADE'
    )
    
    # --- Methodology versions table ---
    op.drop_constraint(
        'methodology_versions_question_set_id_fkey',
        'methodology_versions',
        type_='foreignkey'
    )
    op.create_foreign_key(
        'methodology_versions_question_set_id_fkey',
        'methodology_versions',
        'question_sets',
        ['question_set_id'],
        ['id'],
        ondelete='CASCADE'
    )


def downgrade() -> None:
    # --- Questions table ---
    op.drop_constraint(
        'questions_question_set_id_fkey',
        'questions',
        type_='foreignkey'
    )
    op.create_foreign_key(
        'questions_question_set_id_fkey',
        'questions',
        'question_sets',
        ['question_set_id'],
        ['id']
    )
    
    # --- Methodology versions table ---
    op.drop_constraint(
        'methodology_versions_question_set_id_fkey',
        'methodology_versions',
        type_='foreignkey'
    )
    op.create_foreign_key(
        'methodology_versions_question_set_id_fkey',
        'methodology_versions',
        'question_sets',
        ['question_set_id'],
        ['id']
    )
