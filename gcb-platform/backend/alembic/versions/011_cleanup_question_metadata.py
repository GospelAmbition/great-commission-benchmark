"""Clean up unused fields from question_metadata JSONB

This migration removes vestigial metadata fields that were designed but never implemented:
- expected_refusal_type
- tests_capability
- tests_willingness
- use_case_tags
- audience_context
- ministry_type
- reasoning

It also consolidates expected_verdict from metadata to the top-level column.

Revision ID: 011
Revises: 010
Create Date: 2025-12-27

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

# revision identifiers, used by Alembic.
revision = '011'
down_revision = '010'
branch_labels = None
depends_on = None

# Fields to remove from question_metadata JSONB
FIELDS_TO_REMOVE = [
    'expected_refusal_type',
    'tests_capability',
    'tests_willingness',
    'use_case_tags',
    'audience_context',
    'ministry_type',
    'reasoning',
]


def upgrade() -> None:
    """
    Clean up question_metadata JSONB by removing unused fields.
    Also migrate expected_verdict from metadata to column if not already set.
    """
    conn = op.get_bind()
    
    # Step 1: Migrate expected_verdict from metadata to column where column is NULL
    # This ensures we don't lose any data
    conn.execute(sa.text("""
        UPDATE questions 
        SET expected_verdict = question_metadata->>'expected_verdict'
        WHERE expected_verdict IS NULL 
          AND question_metadata->>'expected_verdict' IS NOT NULL
    """))
    
    # Step 2: Remove unused fields from question_metadata JSONB
    # Using jsonb - text[] removes multiple keys at once
    for field in FIELDS_TO_REMOVE:
        conn.execute(sa.text(f"""
            UPDATE questions 
            SET question_metadata = question_metadata - '{field}'
            WHERE question_metadata ? '{field}'
        """))
    
    # Step 3: Also remove expected_verdict from metadata (now in column)
    conn.execute(sa.text("""
        UPDATE questions 
        SET question_metadata = question_metadata - 'expected_verdict'
        WHERE question_metadata ? 'expected_verdict'
    """))
    
    # Step 4: Set question_metadata to NULL if it's now empty
    conn.execute(sa.text("""
        UPDATE questions 
        SET question_metadata = NULL
        WHERE question_metadata = '{}'::jsonb
    """))


def downgrade() -> None:
    """
    Note: This downgrade cannot restore the removed metadata fields
    as they were unused and their data is not preserved.
    
    It will migrate expected_verdict back to metadata if desired.
    """
    conn = op.get_bind()
    
    # Optionally restore expected_verdict to metadata
    conn.execute(sa.text("""
        UPDATE questions 
        SET question_metadata = COALESCE(question_metadata, '{}'::jsonb) || 
            jsonb_build_object('expected_verdict', expected_verdict)
        WHERE expected_verdict IS NOT NULL
    """))

