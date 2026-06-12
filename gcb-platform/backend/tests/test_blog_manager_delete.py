"""Regression tests for blog-manager post deletion."""
from uuid import uuid4

from app.db.models.blog_category import BlogCategory
from app.db.models.blog_post import BlogPost
from app.db.models.newsletter_campaign_send import NewsletterCampaignSend


def test_delete_post_with_related_rows_cascades(client, db_session, admin_user, test_model):
    from main import app
    from app.api.v1.endpoints.blog import require_blog_manager
    from app.core.auth import get_current_user

    async def override_auth():
        return admin_user

    app.dependency_overrides[get_current_user] = override_auth
    app.dependency_overrides[require_blog_manager] = override_auth

    category = BlogCategory(
        name=f"Highlights {uuid4()}",
        slug=f"highlights-{uuid4()}",
    )
    post = BlogPost(
        title="Old Highlight Draft",
        slug=f"old-highlight-draft-{uuid4()}",
        content="draft",
        status="draft",
        author_id=admin_user.id,
    )
    post.categories = [category]
    post.models = [test_model]
    db_session.add(post)
    db_session.commit()
    db_session.refresh(post)

    send_log = NewsletterCampaignSend(
        post_id=post.id,
        audience="test",
        campaign_type="highlight",
        status="sent",
        provider="mailerlite",
        sent_by_user_id=admin_user.id,
    )
    db_session.add(send_log)
    db_session.commit()

    response = client.delete(f"/api/admin/blog/posts/{post.id}")

    assert response.status_code == 200
    assert db_session.query(BlogPost).filter(BlogPost.id == post.id).first() is None
    assert db_session.query(NewsletterCampaignSend).filter(
        NewsletterCampaignSend.post_id == post.id
    ).first() is None

    app.dependency_overrides.clear()
