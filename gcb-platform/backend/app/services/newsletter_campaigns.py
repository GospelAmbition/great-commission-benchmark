"""MailerLite campaign delivery with audience verification and send reservations."""
import hmac
from datetime import datetime, timezone
from email.utils import parseaddr
from urllib.parse import quote

import httpx

from app.core.config import settings
from app.db.models.blog_post import BlogPost
from app.db.models.newsletter_subscriber import NewsletterSubscriber
from app.db.models.newsletter_test_recipient import NewsletterTestRecipient
from app.db.models.newsletter_campaign_send import NewsletterCampaignSend
from app.services.action_log import ActionLogService
from app.services.markdown_email import markdown_to_email_html_fragment, wrap_email_shell
from app.services.newsletter import NewsletterService
from app.services.newsletter_links import newsletter_footer
from app.services.newsletter_sync import MailerLiteClient, MailerLiteError


class CampaignError(Exception):
    def __init__(self, status_code, message, send_log_id=None):
        super().__init__(message)
        self.status_code, self.send_log_id = status_code, send_log_id


def local_audience(db, audience):
    if audience == "test":
        rows = db.query(NewsletterTestRecipient).filter(NewsletterTestRecipient.is_active == True).all()
    else:
        all_rows = db.query(NewsletterSubscriber).all()
        if any(row.sync_status != "synced" or row.resubscribe_pending for row in all_rows):
            raise CampaignError(409, "Subscription changes still need synchronization. Resolve pending or failed syncs before sending.")
        rows = [row for row in all_rows if row.is_active]
        if any(not row.mailerlite_synced_at or row.mailerlite_status != "active" or
               row.mailerlite_group_id != NewsletterService.production_group_id() for row in rows):
            raise CampaignError(409, "Active subscribers are not verified in the configured production group. Recheck subscriber sync.")
    emails = [row.email.strip().lower() for row in rows]
    if len(emails) != len(set(emails)):
        raise CampaignError(409, "Duplicate platform email addresses must be reconciled before sending.")
    if not emails:
        raise CampaignError(400, f"No active recipients found for {audience} audience.")
    return set(emails)


async def group_audience(api, group_id):
    emails, cursors = set(), set()
    cursor = None
    for _ in range(1000):
        params = {"limit": 1000, "filter[status]": "active"}
        if cursor:
            params["cursor"] = cursor
        result = await api.request("GET", f"/groups/{quote(group_id, safe='')}/subscribers", params=params, envelope=True)
        rows = result.get("data")
        if not isinstance(rows, list):
            raise MailerLiteError("Invalid group subscriber response")
        for row in rows:
            if not isinstance(row, dict) or not isinstance(row.get("email"), str) or row.get("status") != "active":
                raise MailerLiteError("Invalid active group subscriber response")
            emails.add(row["email"].strip().lower())
        meta = result.get("meta")
        if not isinstance(meta, dict) or "next_cursor" not in meta:
            raise MailerLiteError("Missing group pagination metadata")
        cursor = meta["next_cursor"]
        if cursor is None:
            return emails
        if not isinstance(cursor, str) or not cursor or cursor in cursors:
            raise MailerLiteError("Invalid group pagination cursor")
        cursors.add(cursor)
    raise MailerLiteError("Group pagination exceeded the verification limit")


async def verify_readiness(db, api, audience, group_id):
    if audience == "production":
        if not settings.NEWSLETTER_SYNC_ENABLED or not settings.MAILERLITE_WEBHOOK_ID or not settings.MAILERLITE_WEBHOOK_SECRET:
            raise CampaignError(400, "Enable subscriber sync and configure the MailerLite webhook before production sends.")
        webhook = await api.request("GET", f"/webhooks/{quote(settings.MAILERLITE_WEBHOOK_ID, safe='')}")
        required = {"subscriber.unsubscribed", "subscriber.bounced", "subscriber.spam_reported", "subscriber.deleted", "campaign.sent"}
        expected_url = settings.BACKEND_PUBLIC_URL.rstrip("/") + "/api/newsletter/webhooks/mailerlite"
        if (not isinstance(webhook, dict) or webhook.get("enabled") is not True or webhook.get("batchable") is not True or
                webhook.get("url") != expected_url or not isinstance(webhook.get("events"), list) or
                not required.issubset(webhook["events"]) or
                not hmac.compare_digest(str(webhook.get("secret", "")).encode(), settings.MAILERLITE_WEBHOOK_SECRET.encode())):
            raise CampaignError(409, "MailerLite webhook registration does not match the platform configuration.")
    expected = local_audience(db, audience)
    # Release read transactions while doing external I/O, then read fresh local
    # state before accepting this readiness result.
    db.commit()
    actual = await group_audience(api, group_id)
    db.expire_all()
    if local_audience(db, audience) != expected:
        raise CampaignError(409, "Subscriber audience changed during verification. Retry after sync completes.")
    if actual != expected:
        raise CampaignError(409, f"MailerLite audience differs from the platform ({len(expected - actual)} missing, {len(actual - expected)} extra). Reconcile the lists before sending.")
    return expected


def reserve_send(db, request, actor_id):
    # The short row lock serializes reservations across backend replicas. It is
    # committed before provider I/O; there is no network request under this lock.
    post = db.query(BlogPost).filter(BlogPost.id == request.post_id).with_for_update().first()
    if not post:
        raise CampaignError(404, "Post not found")
    sends = db.query(NewsletterCampaignSend).filter(
        NewsletterCampaignSend.post_id == post.id,
        NewsletterCampaignSend.audience == request.audience,
        NewsletterCampaignSend.campaign_type == request.campaign_type,
    ).all()
    unresolved = [s for s in sends if s.status not in {"sent", "failed", "cancelled", "not_sent"}]
    if unresolved:
        raise CampaignError(409, "A send is in progress or its outcome is unresolved. Refresh that send before trying again; force_resend cannot override an uncertain outcome.", str(unresolved[-1].id))
    already_sent = any(s.status == "sent" for s in sends)
    if already_sent and request.audience == "production" and not request.force_resend and not request.dry_run:
        raise CampaignError(409, "A production send already exists for this post. Set force_resend=true for an intentional resend.")
    if request.audience == "production" and post.status != "published":
        raise CampaignError(400, "Post must be published before production send.")
    if request.audience == "production" and not request.dry_run and not request.confirm_production_send:
        raise CampaignError(400, "Production send requires confirm_production_send=true.")
    snapshot = dict(id=post.id, title=post.title, content=post.content, slug=post.slug, status=post.status)
    send = None
    if not request.dry_run:
        send = NewsletterCampaignSend(post_id=post.id, audience=request.audience, campaign_type=request.campaign_type,
                                      provider="mailerlite", status="preparing", sent_by_user_id=actor_id)
        db.add(send)
        db.flush()
    send_id = send.id if send else None
    db.commit()
    return snapshot, send_id, already_sent


def record_step(db, send_id, status, **values):
    if send_id:
        # A signed campaign.sent webhook may win the race with this request.
        db.query(NewsletterCampaignSend).filter(NewsletterCampaignSend.id == send_id,
                                               NewsletterCampaignSend.status != "sent").update(
            {"status": status, **values}, synchronize_session=False)
        db.commit()


async def send_campaign(db, request, actor_id, api=None):
    if api is None:
        async with httpx.AsyncClient() as http:
            return await send_campaign(db, request, actor_id, MailerLiteClient(http))
    group = NewsletterService.audience_group_id(request.audience)
    if not NewsletterService.is_configured() or not group:
        raise CampaignError(400, "Configure the MailerLite API key and audience group before sending.")
    if NewsletterService.production_group_id() == NewsletterService.test_group_id():
        raise CampaignError(400, "Production and test audience groups must be different.")
    sender_name, sender_email = parseaddr(settings.EMAIL_FROM)
    if not sender_email or "@" not in sender_email:
        raise CampaignError(400, "Configure a valid EMAIL_FROM verified sender in MailerLite.")
    post, send_id, already_sent = reserve_send(db, request, actor_id)
    step = "preparing"
    try:
        audience = await verify_readiness(db, api, request.audience, group)
        if request.dry_run:
            return dict(dry_run=True, audience=request.audience, campaign_type=request.campaign_type,
                        recipient_count=len(audience), recipient_count_source="verified_mailerlite_group",
                        target_group_id=group, post_status=post["status"], already_sent=already_sent,
                        message="Audience and connection checks passed. No campaign was created; sender, domain and HTML-plan eligibility are checked by MailerLite when creating a campaign.")
        inner = markdown_to_email_html_fragment(post["content"] or "")
        web_url = f"{settings.NEWSLETTER_PUBLIC_URL.rstrip('/')}/insights/{post['slug']}" if post["slug"] else None
        html = wrap_email_shell(inner, title=post["title"], web_version_url=web_url,
                               footer_html=newsletter_footer("{$unsubscribe}"))
        step = "creating"
        record_step(db, send_id, step, target_group_id=group, recipient_count=len(audience))
        created = await api.request("POST", "/campaigns", json={
            "name": f"GCB {request.campaign_type} {send_id}", "type": "regular", "groups": [group],
            "emails": [{"subject": (post["title"] or "Great Commission Benchmark")[:255],
                        "from": sender_email, "from_name": sender_name or "Great Commission Benchmark",
                        "content": html,
                        "plain_text": NewsletterService._strip_html_for_plain(html) + "\nUnsubscribe: {$unsubscribe}"}],
        })
        if not isinstance(created, dict) or not created.get("id"):
            raise MailerLiteError("MailerLite did not return a campaign ID")
        campaign_id = str(created["id"])
        step = "created"
        record_step(db, send_id, step, campaign_id=campaign_id)
        # Check again after campaign creation; never schedule an outdated audience.
        if await verify_readiness(db, api, request.audience, group) != audience:
            raise CampaignError(409, "Audience changed after creating the draft; no send was scheduled.")
        current_post = db.query(BlogPost).filter(BlogPost.id == post["id"]).first()
        if not current_post or (current_post.content, current_post.title, current_post.status) != (post["content"], post["title"], post["status"]):
            raise CampaignError(409, "Post changed after creating the draft; no send was scheduled.")
        step = "scheduling"
        record_step(db, send_id, step)
        await api.request("POST", f"/campaigns/{quote(campaign_id, safe='')}/schedule", json={"delivery": "instant"}, allow_empty=True)
        record_step(db, send_id, "scheduled", error_message=None)
        ActionLogService.log_action(db, "newsletter.campaign_send", "user", actor_user_id=actor_id,
                                    entity_type="blog_post", entity_id=str(post["id"]),
                                    metadata={"campaign_id": campaign_id, "provider": "mailerlite", "audience": request.audience,
                                              "campaign_type": request.campaign_type, "recipient_count": len(audience), "send_log_id": str(send_id)})
        return dict(dry_run=False, audience=request.audience, campaign_type=request.campaign_type,
                    recipient_count=len(audience), recipient_count_source="verified_mailerlite_group", target_group_id=group,
                    post_status=post["status"], already_sent=already_sent, campaign_id=campaign_id, send_log_id=send_id,
                    message="MailerLite accepted the campaign for delivery. Check send status for completion.")
    except CampaignError as exc:
        record_step(db, send_id, "failed", error_message=str(exc)[:255])
        exc.send_log_id = str(send_id) if send_id else None
        raise
    except MailerLiteError as exc:
        ambiguous = step in {"creating", "scheduling"} and (exc.status_code is None or exc.status_code >= 500)
        record_step(db, send_id, "uncertain" if ambiguous else "failed", error_message=str(exc)[:255])
        raise CampaignError(502, str(exc) + (". Outcome is uncertain; refresh the send before retrying." if ambiguous else ". No fallback email was sent."), str(send_id) if send_id else None) from exc


async def refresh_send(db, send, api):
    if send.provider == "mailerlite" and not send.campaign_id and send.status == "uncertain":
        # The campaign ID is committed before scheduling is attempted. A terminal
        # creation error with no ID therefore cannot have scheduled mail through
        # this attempt, even if the provider created an orphan draft.
        send.status = "not_sent"
        send.error_message = "Campaign creation was uncertain, but this attempt never issued a schedule request. Check for an unused draft by send log ID."
        send.last_checked_at = datetime.now(timezone.utc)
        db.commit()
        return {"send_log_id": str(send.id), "campaign_id": None, "status": send.status,
                "provider_status": "unknown_draft", "error_message": send.error_message}
    if send.provider != "mailerlite" or not send.campaign_id:
        raise CampaignError(409, "This attempt has no verified MailerLite campaign ID. Inspect the account using the send log ID in the campaign name before resolving it.")
    data = await api.request("GET", f"/campaigns/{quote(send.campaign_id, safe='')}")
    if not isinstance(data, dict) or str(data.get("id")) != send.campaign_id:
        raise MailerLiteError("Campaign status could not be verified")
    values = {"last_checked_at": datetime.now(timezone.utc)}
    if data.get("status") == "sent":
        values.update(status="sent", error_message=None)
    elif data.get("status") == "ready" or data.get("queued_at") or data.get("started_at"):
        values["status"] = "scheduled"
    # A draft alone does not prove a timed-out scheduling call cannot still finish.
    # A signed completion webhook can arrive during the provider read. Never
    # replace that confirmation with an older status response.
    db.query(NewsletterCampaignSend).filter(NewsletterCampaignSend.id == send.id,
                                           NewsletterCampaignSend.status != "sent").update(values, synchronize_session=False)
    db.commit()
    db.refresh(send)
    return {"send_log_id": str(send.id), "campaign_id": send.campaign_id, "status": send.status,
            "provider_status": data.get("status"), "error_message": send.error_message}
