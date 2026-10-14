"""Purpose-bound unsubscribe links containing no email address."""
import hashlib
import hmac
import time
from html import escape
from urllib.parse import urlencode
from uuid import UUID

from app.core.config import settings


def signing_key():
    key = settings.NEWSLETTER_TOKEN_SECRET or settings.NEXTAUTH_SECRET
    if len(key) < 32:
        raise ValueError("Configure a newsletter signing secret of at least 32 characters")
    return key.encode()


def unsubscribe_token(subscriber_id):
    value = f"unsubscribe.v1.{UUID(str(subscriber_id))}"
    signature = hmac.new(signing_key(), value.encode(), hashlib.sha256).hexdigest()
    return f"{value}.{signature}"


def read_unsubscribe_token(token):
    if not isinstance(token, str) or not token.isascii() or len(token) > 150:
        raise ValueError("Invalid unsubscribe link")
    try:
        purpose, version, subject, signature = token.split(".")
        subscriber_id = UUID(subject)
    except (ValueError, AttributeError) as exc:
        raise ValueError("Invalid unsubscribe link") from exc
    if purpose != "unsubscribe" or version != "v1" or not hmac.compare_digest(token, unsubscribe_token(subscriber_id)):
        raise ValueError("Invalid unsubscribe link")
    return subscriber_id


def unsubscribe_url(subscriber_id=None):
    base = f"{settings.NEWSLETTER_PUBLIC_URL.rstrip('/')}/newsletter/unsubscribe"
    return f"{base}?{urlencode({'token': unsubscribe_token(subscriber_id)})}" if subscriber_id else base


def newsletter_footer(url):
    return (
        '<p style="font-size:12px;line-height:1.5;color:#666;margin:0;">'
        'You are receiving the Great Commission Benchmark newsletter. '
        f'<a href="{escape(url, quote=True)}">Unsubscribe</a> or '
        f'<a href="{escape(settings.NEWSLETTER_PUBLIC_URL.rstrip("/") + "/newsletter", quote=True)}">subscribe to updates</a>.'
        '</p>'
    )


def resubscribe_token(subscriber_id, nonce, *, expires=None):
    expires = expires if expires is not None else int(time.time()) + 86400
    value = f"resubscribe.v1.{UUID(str(subscriber_id))}.{UUID(str(nonce))}.{expires}"
    signature = hmac.new(signing_key(), value.encode(), hashlib.sha256).hexdigest()
    return f"{value}.{signature}"


def read_resubscribe_token(token):
    if not isinstance(token, str) or not token.isascii() or len(token) > 250:
        raise ValueError("Invalid confirmation link")
    try:
        purpose, version, subject, nonce, expiry, signature = token.split(".")
        subject, nonce, expiry = UUID(subject), UUID(nonce), int(expiry)
    except (ValueError, AttributeError) as exc:
        raise ValueError("Invalid confirmation link") from exc
    expected = resubscribe_token(subject, nonce, expires=expiry)
    if purpose != "resubscribe" or version != "v1" or expiry <= time.time() or not hmac.compare_digest(token, expected):
        raise ValueError("Invalid or expired confirmation link")
    return subject, nonce


def resubscribe_url(subscriber_id, nonce):
    base = settings.NEWSLETTER_PUBLIC_URL.rstrip("/")
    return f"{base}/newsletter/confirm?{urlencode({'token': resubscribe_token(subscriber_id, nonce)})}"
