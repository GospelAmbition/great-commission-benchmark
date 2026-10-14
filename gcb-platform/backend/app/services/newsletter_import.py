"""CSV imports into the platform's subscriber list. Never sends email.

Suppression wins over active rows, both within a file and in the database.
Parsing and planning are shared by preview and apply; apply rechecks current DB
state and commits the subscriber changes and audit record together.
"""
import csv
import io
from collections import Counter, defaultdict
from datetime import datetime, timezone
from uuid import uuid4

from email_validator import EmailNotValidError, validate_email
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db.models.action_log import ActionLog
from app.db.models.newsletter_subscriber import NewsletterSubscriber
from app.services.newsletter_sync import queue_sync
from app.schemas.newsletter_import import (
    NewsletterImportRequest, NewsletterImportResponse, NewsletterImportRow,
)

MAX_BYTES = 2_000_000
MAX_ROWS = 10_000
MAX_REPORT_ROWS = 200
ACTIVE_STATUSES = {"active", "subscribed", "true", "1", "yes"}
INACTIVE_STATUSES = {"unsubscribed", "inactive", "bounced", "junk", "spam", "unconfirmed", "cleaned", "false", "0", "no"}


def _column(headers: list[str], selected: str | None, aliases: set[str], required=False):
    if selected:
        if selected not in headers:
            raise ValueError(f"Column '{selected}' was not found in the CSV header")
        return headers.index(selected)
    matches = [i for i, header in enumerate(headers) if header.casefold() in aliases]
    if len(matches) > 1:
        raise ValueError("Multiple matching columns found; specify the column name explicitly")
    if matches:
        return matches[0]
    if required:
        raise ValueError("No email column found. Specify the email column name from your CSV")
    return None


def parse_import(request: NewsletterImportRequest):
    if len(request.csv_content.encode("utf-8")) > MAX_BYTES:
        raise ValueError("CSV must be no larger than 2 MB")
    if "\x00" in request.csv_content:
        raise ValueError("Upload a UTF-8 CSV file")
    content = request.csv_content.lstrip("\ufeff")
    try:
        # Excel exports in some locales use semicolons; TSV exports work too.
        try:
            dialect = csv.Sniffer().sniff(content[:8192], delimiters=",;\t")
        except csv.Error:
            dialect = csv.excel
        reader = csv.reader(io.StringIO(content, newline=""), dialect, strict=True)
        headers = [cell.strip() for cell in next(reader)]
        if len(set(headers)) != len(headers) or any(not h for h in headers):
            raise ValueError("CSV headers must be nonempty and unique")
        email_col = _column(headers, request.email_column, {"email", "email address", "email_address", "e-mail", "e-mail address"}, required=True)
        name_col = _column(headers, request.name_column, {"name", "full name", "full_name", "first name"})
        status_col = _column(headers, request.status_column, {"status", "subscription status", "subscriber status", "email marketing status", "is_active"})
        rows = []
        for cells in reader:
            if not cells or not any(cell.strip() for cell in cells):
                continue
            if len(rows) >= MAX_ROWS:
                raise ValueError("Import at most 10,000 rows at a time")
            row = {"row": reader.line_num, "email": "", "name": None, "active": True, "error": None}
            rows.append(row)
            if len(cells) != len(headers):
                row["error"] = "Number of fields does not match the header"
                continue
            email = cells[email_col].strip().lower()
            row["email"] = email[:255]
            try:
                row["email"] = validate_email(email, check_deliverability=False).normalized.lower()
            except EmailNotValidError:
                row["error"] = "Invalid email address"
                continue
            if name_col is not None:
                row["name"] = cells[name_col].strip() or None
                if row["name"] and len(row["name"]) > 255:
                    row["error"] = "Name exceeds 255 characters"
                    continue
            if status_col is not None:
                status = cells[status_col].strip().lower()
                if status not in ACTIVE_STATUSES | INACTIVE_STATUSES:
                    row["error"] = "Unknown or empty status; use active or unsubscribed"
                    continue
                row["active"] = status in ACTIVE_STATUSES
        if not rows:
            raise ValueError("CSV has no subscriber rows")
        return headers, rows
    except (csv.Error, StopIteration) as exc:
        raise ValueError("Unable to read CSV; check its header, delimiters, and quoted fields") from exc


def import_subscribers(db: Session, request: NewsletterImportRequest, actor_id) -> NewsletterImportResponse:
    headers, rows = parse_import(request)
    # Pick one row per address, with a suppression row taking precedence.
    chosen = {}
    for row in rows:
        if not row["error"] and (row["email"] not in chosen or not row["active"]):
            chosen[row["email"]] = row

    existing = defaultdict(list)
    emails = sorted(chosen)
    # Small chunks also work within SQLite's bind-parameter limit in tests.
    for start in range(0, len(emails), 500):
        query = db.query(NewsletterSubscriber).filter(
            func.lower(func.trim(NewsletterSubscriber.email)).in_(emails[start:start + 500])
        ).order_by(NewsletterSubscriber.id)
        if not request.dry_run:
            query = query.with_for_update()
        for subscriber in query.all():
            existing[subscriber.email.strip().lower()].append(subscriber)

    report = []
    changes = []
    for row in rows:
        matches = existing[row["email"]]
        if row["error"]:
            action, message = "invalid", row["error"]
        elif chosen[row["email"]] is not row:
            action, message = "duplicate", "Duplicate address in file; an inactive status takes precedence"
        elif not matches:
            action = "create_active" if row["active"] else "create_unsubscribed"
            message = "Add subscriber" if row["active"] else "Add suppression record"
            changes.append((action, row, matches))
        elif not row["active"] and any(s.is_active or s.resubscribe_pending or s.resubscribe_nonce for s in matches):
            action, message = "unsubscribe", "Mark existing subscriber as unsubscribed"
            changes.append((action, row, matches))
        elif row["active"] and any(not s.is_active for s in matches):
            action, message = "protected", "Existing unsubscribe preserved; imports cannot reactivate it"
        else:
            action, message = "unchanged", "Already present; no change"
        report.append(NewsletterImportRow(row=row["row"], email=row["email"], action=action, message=message))

    counts = dict(Counter(item.action for item in report))
    requires_consent = bool(counts.get("create_active"))
    batch_id = None
    if not request.dry_run:
        if requires_consent and (not request.confirm_subscribed or not request.consent_note):
            raise ValueError("Confirm permission to email new active subscribers and describe how they subscribed")
        batch_id = uuid4()
        now = datetime.now(timezone.utc)
        for action, row, matches in changes:
            if action == "unsubscribe":
                for subscriber in matches:
                    subscriber.is_active = False
                    subscriber.unsubscribed_at = subscriber.unsubscribed_at or now
                    queue_sync(subscriber)
            else:
                db.add(NewsletterSubscriber(
                    email=row["email"], name=row["name"], is_active=row["active"],
                    source=request.source, consent_note=request.consent_note if row["active"] else None,
                    imported_at=now, import_batch_id=batch_id,
                    unsubscribed_at=None if row["active"] else now,
                ))
        db.add(ActionLog(
            action="newsletter.import", actor_type="user", actor_user_id=actor_id,
            entity_type="newsletter_import", entity_id=str(batch_id),
            extra_data={"source": request.source, "counts": counts, "total_rows": len(rows),
                        "consent_note": request.consent_note, "confirm_subscribed": request.confirm_subscribed},
        ))
        db.commit()

    return NewsletterImportResponse(
        dry_run=request.dry_run, batch_id=batch_id, columns=headers, total_rows=len(rows), counts=counts,
        rows=report[:MAX_REPORT_ROWS], rows_truncated=len(report) > MAX_REPORT_ROWS,
        requires_consent=requires_consent,
        message="Preview only; no changes saved" if request.dry_run else "Import saved to the platform. Changes are queued for MailerLite sync; no email was sent.",
    )
