"""Cache, rate-limit, and scanner-guard coverage for crawler hardening."""
from datetime import datetime, timezone
from unittest.mock import patch

import pytest
from sqlalchemy import event

from app.core.http_cache import PUBLIC_CACHE_CONTROL
from app.core.rate_limit import RATE_LIMITS, should_skip_rate_limit
from app.core.scanner_paths import is_scanner_path
from app.db.models.blog_post import BlogPost
from app.services.published_cache import DERIVED_NAMESPACES


SCANNER_PATHS = [
    "/.env",
    "/.env.local",
    "/actuator/env",
    "/phpinfo.php",
    "/phpinfo",
    "/wp-admin",
    "/wp-login.php",
    "/.git/config",
]


@pytest.mark.parametrize("path", SCANNER_PATHS)
def test_is_scanner_path_matches_known_probes(path):
    assert is_scanner_path(path) is True


@pytest.mark.parametrize(
    "path",
    ["/", "/health", "/api/public/leaderboard", "/api/public/models/by-id", "/leaderboard"],
)
def test_is_scanner_path_allows_real_routes(path):
    assert is_scanner_path(path) is False


@pytest.mark.parametrize("path", SCANNER_PATHS)
def test_scanner_paths_return_fast_404(client, path):
    response = client.get(path)
    assert response.status_code == 404
    assert response.text == "Not Found"


def test_health_is_not_rate_limited_or_blocked(client):
    for _ in range(5):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


def test_should_skip_rate_limit_for_webhooks_and_health():
    assert should_skip_rate_limit("/health", "GET") is True
    assert should_skip_rate_limit("/api/health", "GET") is True
    assert should_skip_rate_limit("/api/webhooks/stripe", "POST") is True
    assert should_skip_rate_limit("/api/newsletter/webhooks/mailerlite", "POST") is True
    assert should_skip_rate_limit("/api/public/leaderboard", "GET") is False
    assert should_skip_rate_limit("/api/public/leaderboard", "OPTIONS") is True


def test_public_get_sets_cache_control(client):
    response = client.get("/api/public/stats")
    assert response.status_code == 200
    assert response.headers["cache-control"] == PUBLIC_CACHE_CONTROL


def test_public_rate_limit_middleware_returns_429(client, monkeypatch):
    monkeypatch.setitem(RATE_LIMITS, "public", {"limit": 3, "window": 60})
    monkeypatch.setitem(RATE_LIMITS, "public_burst", {"limit": 3, "window": 10})

    for _ in range(3):
        assert client.get("/api/public/stats").status_code == 200
    blocked = client.get("/api/public/stats")
    assert blocked.status_code == 429
    assert blocked.headers["X-RateLimit-Remaining"] == "0"
    assert "Retry-After" in blocked.headers
    assert blocked.json()["detail"]["error"] == "Rate limit exceeded"


def test_public_burst_limit_returns_429(client, monkeypatch):
    monkeypatch.setitem(RATE_LIMITS, "public", {"limit": 180, "window": 60})
    monkeypatch.setitem(RATE_LIMITS, "public_burst", {"limit": 2, "window": 10})

    assert client.get("/api/public/stats").status_code == 200
    assert client.get("/api/public/stats").status_code == 200
    blocked = client.get("/api/public/stats")
    assert blocked.status_code == 429
    assert blocked.json()["detail"]["window_seconds"] == 10


def test_models_by_id_is_cached(db_session, test_model, test_results, client):
    path = f"/api/public/models/by-id?model_id={test_model.model_id}"

    cold = client.get(path)
    assert cold.status_code == 200
    assert cold.headers.get("x-cache") == "MISS"
    assert cold.headers["cache-control"] == PUBLIC_CACHE_CONTROL

    statements = []

    def count_statement(*args):
        statements.append(args[2])

    event.listen(db_session.bind, "before_cursor_execute", count_statement)
    try:
        warm = client.get(path)
    finally:
        event.remove(db_session.bind, "before_cursor_execute", count_statement)

    assert warm.status_code == 200
    assert warm.headers.get("x-cache") == "HIT"
    assert warm.json() == cold.json()
    assert statements == []


def test_model_uuid_detail_is_cached(db_session, test_model, test_results, client):
    path = f"/api/public/models/{test_model.id}"

    cold = client.get(path)
    assert cold.status_code == 200
    assert cold.headers.get("x-cache") == "MISS"

    warm = client.get(path)
    assert warm.status_code == 200
    assert warm.headers.get("x-cache") == "HIT"
    assert warm.json() == cold.json()


def test_provider_articles_are_cached(db_session, test_user, test_model, client):
    post = BlogPost(
        title="Provider article",
        slug="provider-article",
        excerpt="Excerpt",
        content="Body",
        status="published",
        author_id=test_user.id,
        published_at=datetime.now(timezone.utc),
    )
    db_session.add(post)
    db_session.commit()
    db_session.refresh(post)
    post.models.append(test_model)
    db_session.commit()

    path = f"/api/public/providers/{test_model.provider}/articles"
    cold = client.get(path)
    assert cold.status_code == 200
    assert cold.headers.get("x-cache") == "MISS"
    assert len(cold.json()["articles"]) == 1

    warm = client.get(path)
    assert warm.status_code == 200
    assert warm.headers.get("x-cache") == "HIT"
    assert warm.json() == cold.json()


def test_unpublished_model_by_id_is_not_cached_as_hit(client, test_model):
    response = client.get(f"/api/public/models/by-id?model_id={test_model.model_id}")
    assert response.status_code == 404
    assert response.headers.get("x-cache") != "HIT"


def test_derived_namespaces_include_new_public_payloads():
    assert "model_by_id" in DERIVED_NAMESPACES
    assert "model_details" in DERIVED_NAMESPACES
    assert "provider_articles" in DERIVED_NAMESPACES


def test_db_engine_uses_fail_fast_pool():
    from app.db.base import engine

    assert engine.pool.size() == 5
    assert engine.pool.timeout() == 5
    assert engine.pool._max_overflow == 10


def test_redis_cache_configures_fail_fast_timeouts():
    from app.core.cache import RedisCache

    fake_redis = object()
    with patch("redis.asyncio.from_url", return_value=fake_redis) as from_url:
        client = RedisCache("redis://localhost:6379/0")

    assert client._redis is fake_redis
    kwargs = from_url.call_args.kwargs
    assert kwargs["socket_timeout"] == RedisCache.SOCKET_TIMEOUT_SECONDS
    assert kwargs["socket_connect_timeout"] == RedisCache.SOCKET_TIMEOUT_SECONDS
    assert kwargs["retry_on_timeout"] is False
    assert kwargs["max_connections"] == RedisCache.MAX_CONNECTIONS
