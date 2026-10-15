"""Preview-first pull of the configured MailerLite production group.

No provider writes. Every status and cursor page must be read successfully before
any local changes. Apply refetches the group and requires the reviewed snapshot.
"""
import asyncio
import csv
import hashlib
import io
import json
from collections import Counter
from urllib.parse import quote

from app.schemas.newsletter_import import NewsletterImportRequest
from app.services.newsletter import NewsletterService
from app.services.newsletter_import import import_subscribers, MAX_ROWS, MAX_BYTES
from app.services.newsletter_sync import MailerLiteError

STATUSES = ("active", "unsubscribed", "unconfirmed", "bounced", "junk")


class SnapshotChanged(ValueError):
    pass


async def read_group(api, group_id):
    rows = []
    for status in STATUSES:
        cursor, seen = None, set()
        for _ in range(100):
            params = {"limit": 1000, "filter[status]": status}
            if cursor:
                params["cursor"] = cursor
            response = await api.request("GET", f"/groups/{quote(group_id, safe='')}/subscribers", params=params, envelope=True)
            if not isinstance(response, dict) or not isinstance(response.get("data"), list) or not isinstance(response.get("meta"), dict) or "next_cursor" not in response["meta"]:
                raise MailerLiteError("Incomplete MailerLite subscriber page; no import applied")
            for record in response["data"]:
                if (not isinstance(record, dict) or not record.get("id") or
                        not isinstance(record.get("email"), str) or record.get("status") != status or
                        not isinstance(record.get("fields", {}), dict)):
                    raise MailerLiteError("Invalid MailerLite subscriber record; no import applied")
                name = record.get("fields", {}).get("name") or ""
                if not isinstance(name, str):
                    raise MailerLiteError("Invalid MailerLite subscriber name; no import applied")
                rows.append({"id": str(record["id"]), "email": record["email"].strip().lower(),
                             "name": name, "status": status})
                if len(rows) > MAX_ROWS:
                    raise ValueError("This group exceeds 10,000 records. Export all statuses from MailerLite and use reviewed CSV batches instead.")
            cursor = response["meta"]["next_cursor"]
            if cursor is None:
                break
            if not isinstance(cursor, str) or not cursor or cursor in seen:
                raise MailerLiteError("Invalid MailerLite pagination; no import applied")
            seen.add(cursor)
        else:
            raise MailerLiteError("MailerLite pagination limit reached; no import applied")
    return sorted(rows, key=lambda row: (row["email"], row["status"], row["id"], row["name"]))


async def pull_subscribers(db, request, actor_id, api):
    group = NewsletterService.production_group_id()
    if not NewsletterService.is_configured() or not group:
        raise ValueError("Configure the MailerLite API key and production group first")
    if group == NewsletterService.test_group_id():
        raise ValueError("Production and test groups must be different")
    if not request.dry_run and not request.snapshot_sha256:
        raise ValueError("Preview the MailerLite group before importing")
    try:
        async with asyncio.timeout(45):
            rows = await read_group(api, group)
    except TimeoutError as exc:
        raise MailerLiteError("MailerLite group scan timed out; no import applied. Retry or use CSV batches.") from exc
    digest = hashlib.sha256(json.dumps({"group": group, "rows": rows}, sort_keys=True).encode()).hexdigest()
    if not request.dry_run and digest != request.snapshot_sha256:
        raise SnapshotChanged("MailerLite contacts changed since preview. Preview again before importing.")
    if not rows:
        raise ValueError("The configured production group has no subscribers in any status")
    output = io.StringIO(newline="")
    writer = csv.writer(output)
    writer.writerow(["email", "name", "status"])
    writer.writerows([row["email"], row["name"], row["status"]] for row in rows)
    if len(output.getvalue().encode("utf-8")) > MAX_BYTES:
        raise ValueError("This group exceeds the 2 MB import limit. Use reviewed CSV batches instead.")
    imported = NewsletterImportRequest(
        csv_content=output.getvalue(), source=f"MailerLite group {group}"[:120],
        email_column="email", name_column="name", status_column="status",
        confirm_subscribed=request.confirm_subscribed, consent_note=request.consent_note,
        dry_run=True,
    )
    preview = import_subscribers(db, imported, actor_id)
    if preview.counts.get("invalid"):
        raise ValueError("MailerLite contains invalid emails or names. Correct them or use a reviewed CSV export; no import applied.")
    if not request.dry_run:
        imported.dry_run = False
        preview = import_subscribers(db, imported, actor_id)
    return {**preview.model_dump(), "snapshot_sha256": digest, "group_id": group,
            "remote_status_counts": dict(Counter(row["status"] for row in rows))}
