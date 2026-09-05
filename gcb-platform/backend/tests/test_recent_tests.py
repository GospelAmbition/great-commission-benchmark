"""Public Recent Tests endpoint behavior."""
import asyncio
from datetime import datetime, timedelta

from app.core.cache import cache
from app.db.models.blog_post import BlogPost
from app.db.models.methodology_version import MethodologyVersion
from app.db.models.model import Model
from app.db.models.question_set import QuestionSet
from app.db.models.test_run import TestRun
from app.db.models.user import User


def test_recent_tests_are_unique_ranked_current_and_article_linked(client, db_session):
    asyncio.run(cache.clear())
    now = datetime(2026, 9, 4, 12, 0, 0)
    user = User(auth0_id="recent|author", email="recent@example.com", name="Recent Author")
    current = QuestionSet(semantic_version="2.0", marketing_version="Version 2", status="active")
    archived = QuestionSet(semantic_version="1.0", marketing_version="Version 1", status="archived")
    db_session.add_all([user, current, archived])
    db_session.flush()

    current_method = MethodologyVersion(
        question_set_id=current.id,
        scoring_config={},
        active_from=now - timedelta(days=30),
    )
    archived_method = MethodologyVersion(
        question_set_id=archived.id,
        scoring_config={},
        active_from=now - timedelta(days=60),
    )
    first = Model(
        model_id="provider/first",
        name="First Model",
        provider="provider",
        description="First description",
        is_active=True,
    )
    second = Model(
        model_id="provider/second",
        name="Second Model",
        provider="provider",
        is_active=True,
    )
    inactive = Model(
        model_id="provider/inactive",
        name="Inactive Model",
        provider="provider",
        is_active=False,
    )
    old_version_only = Model(
        model_id="provider/old-version",
        name="Old Version Model",
        provider="provider",
        is_active=True,
    )
    db_session.add_all([
        current_method,
        archived_method,
        first,
        second,
        inactive,
        old_version_only,
    ])
    db_session.flush()

    def add_run(model, question_set, methodology, *, score, completed_at):
        db_session.add(TestRun(
            user_id=user.id,
            model_id=model.id,
            question_set_id=question_set.id,
            methodology_version_id=methodology.id,
            status="completed",
            overall_score=score,
            tier1_score=score,
            tier2_score=score,
            tier3_score=score,
            total_questions=1,
            completed_at=completed_at,
        ))

    add_run(first, current, current_method, score=95, completed_at=now - timedelta(days=10))
    add_run(first, current, current_method, score=70, completed_at=now)
    add_run(second, current, current_method, score=80, completed_at=now - timedelta(days=1))
    add_run(inactive, current, current_method, score=99, completed_at=now + timedelta(days=1))
    add_run(old_version_only, archived, archived_method, score=100, completed_at=now + timedelta(days=2))

    older_article = BlogPost(
        title="Older review",
        slug="older-review",
        status="published",
        published_at=now - timedelta(days=2),
        author_id=user.id,
    )
    newer_article = BlogPost(
        title="Newest review",
        slug="newest-review",
        status="published",
        published_at=now - timedelta(days=1),
        author_id=user.id,
    )
    draft_article = BlogPost(
        title="Draft review",
        slug="draft-review",
        status="draft",
        author_id=user.id,
    )
    older_article.models = [first]
    newer_article.models = [first]
    draft_article.models = [first]
    db_session.add_all([older_article, newer_article, draft_article])
    db_session.commit()

    response = client.get("/api/public/recent-tests?limit=50")

    assert response.status_code == 200
    data = response.json()
    assert data["current_version"] == "2.0"
    assert data["total"] == 2
    assert [item["model"]["model_id"] for item in data["items"]] == [
        "provider/first",
        "provider/second",
    ]
    assert [item["rank"] for item in data["items"]] == [2, 1]
    assert data["items"][0]["score"] == 70
    assert data["items"][0]["article"]["slug"] == "newest-review"
    assert data["items"][1]["article"] is None


def test_recent_tests_limit_is_enforced(client):
    assert client.get("/api/public/recent-tests?limit=0").status_code == 422
    assert client.get("/api/public/recent-tests?limit=51").status_code == 422
