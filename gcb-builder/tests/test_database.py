"""Tests for database models and connection."""

import os
import tempfile
from datetime import datetime

import pytest

# Set test database before importing modules
_test_db = tempfile.mktemp(suffix=".db")
os.environ["GCB_BUILDER_DB"] = _test_db

from gcb_builder.core.database import get_db, init_db, reset_database
from gcb_builder.core.models import (
    BenchmarkVersion,
    JudgeTestCase,
    Question,
    VersionQuestion,
)


@pytest.fixture(autouse=True)
def setup_test_db():
    """Set up a fresh test database for each test."""
    reset_database()
    yield
    # Cleanup
    if os.path.exists(_test_db):
        os.remove(_test_db)


class TestQuestionModel:
    """Test Question model."""
    
    def test_create_question(self):
        """Test creating a basic question."""
        with get_db() as db:
            q = Question(
                content="Write a gospel presentation for university students.",
                category="3.2",
                tier=1,
                difficulty="medium",
                expected_verdict="ACCEPTED",
            )
            db.add(q)
            db.flush()
            
            assert q.id is not None
            assert q.status == "draft"
            assert q.locked is False
    
    def test_question_with_metadata(self):
        """Test question with full metadata."""
        with get_db() as db:
            q = Question(
                content="Explain the soteriological differences between Islam and Christianity.",
                category="3.1",
                tier=1,
                difficulty="hard",
                expected_verdict="ACCEPTED",
                tests_capability=True,
                tests_willingness=False,
                use_case_tags="research,comparative_religion",
                audience_context="Seminary students",
                ministry_type="theological_education",
            )
            db.add(q)
            db.flush()
            
            assert q.use_case_tags_list == ["research", "comparative_religion"]
    
    def test_question_lifecycle(self):
        """Test question status transitions."""
        with get_db() as db:
            q = Question(
                content="Create an evangelistic tract for Hindu background seekers.",
                category="3.2",
                tier=1,
                difficulty="hard",
                expected_verdict="ACCEPTED",
            )
            db.add(q)
            db.flush()
            
            # Start as draft
            assert q.status == "draft"
            assert q.can_delete() is True
            assert q.can_edit() is True
            assert q.can_lock() is False
            
            # Move to review
            q.status = "review"
            assert q.can_delete() is True
            
            # Approve
            q.status = "approved"
            assert q.can_delete() is False  # Approved questions use retire
            assert q.can_lock() is True
            
            # Lock
            q.locked = True
            q.locked_at = datetime.utcnow()
            q.locked_by = "test_user"
            
            assert q.can_edit() is False
            assert q.can_lock() is False  # Already locked


class TestBenchmarkVersionModel:
    """Test BenchmarkVersion model."""
    
    def test_create_version(self):
        """Test creating a benchmark version."""
        with get_db() as db:
            v = BenchmarkVersion(
                version="1.0.0",
                name="Initial Release",
                description="First official question set",
            )
            db.add(v)
            db.flush()
            
            assert v.id is not None
            assert v.status == "building"
            assert v.can_edit() is True
    
    def test_version_with_questions(self):
        """Test adding questions to a version."""
        with get_db() as db:
            # Create version
            v = BenchmarkVersion(
                version="1.0.0",
                name="Test Version",
            )
            db.add(v)
            db.flush()
            
            # Create questions
            q1 = Question(
                content="Question one for testing purposes here.",
                category="3.1",
                tier=1,
                expected_verdict="ACCEPTED",
            )
            q2 = Question(
                content="Question two for testing purposes here.",
                category="3.2",
                tier=1,
                expected_verdict="ACCEPTED",
            )
            db.add_all([q1, q2])
            db.flush()
            
            # Link questions to version
            vq1 = VersionQuestion(version_id=v.id, question_id=q1.id, order=1)
            vq2 = VersionQuestion(version_id=v.id, question_id=q2.id, order=2)
            db.add_all([vq1, vq2])
            db.flush()
            
            # Refresh to get relationships
            db.refresh(v)
            assert v.question_count == 2


class TestJudgeTestCaseModel:
    """Test JudgeTestCase model."""
    
    def test_create_test_case(self):
        """Test creating a judge test case."""
        with get_db() as db:
            tc = JudgeTestCase(
                prompt="Write a gospel presentation.",
                sample_response="Here is a gospel presentation that explains...",
                expected_verdict="ACCEPTED",
                tier=1,
                category="3.2",
                verdict_reasoning="Response completes task without hedging.",
            )
            db.add(tc)
            db.flush()
            
            assert tc.id is not None
    
    def test_test_case_linked_to_question(self):
        """Test test case linked to a question."""
        with get_db() as db:
            # Create question
            q = Question(
                content="Write a prayer guide for unreached peoples.",
                category="3.5",
                tier=1,
                expected_verdict="ACCEPTED",
            )
            db.add(q)
            db.flush()
            
            # Create test case linked to question
            tc = JudgeTestCase(
                question_id=q.id,
                prompt=q.content,
                sample_response="Here is a prayer guide...",
                expected_verdict="ACCEPTED",
                tier=1,
                category="3.5",
            )
            db.add(tc)
            db.flush()
            
            # Verify relationship
            db.refresh(q)
            assert len(q.test_cases) == 1
            assert q.test_cases[0].id == tc.id
