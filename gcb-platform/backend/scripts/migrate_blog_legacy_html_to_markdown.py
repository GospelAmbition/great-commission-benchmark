#!/usr/bin/env python3
"""
Convert legacy HTML in blog_posts.content / excerpt to Markdown and save.

Default: **dry-run** (no writes). Use ``--apply`` to persist. Original rows can be
exported with ``--backup-dir`` before apply.

Usage::

    python scripts/migrate_blog_legacy_html_to_markdown.py
    python scripts/migrate_blog_legacy_html_to_markdown.py --min-confidence high
    python scripts/migrate_blog_legacy_html_to_markdown.py --ids <uuid> --ids <uuid2>
    python scripts/migrate_blog_legacy_html_to_markdown.py --apply --backup-dir ./blog_html_backup

Review converted output in dry-run before ``--apply``. Mechanical HTML→MD is
lossy for complex layouts; edit in the CMS if needed.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from uuid import UUID

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session  # noqa: E402

from app.db.base import SessionLocal  # noqa: E402
from app.db.models.blog_post import BlogPost  # noqa: E402
from app.services.blog_html_detection import content_confidence, looks_like_legacy_html  # noqa: E402
from app.services.blog_html_to_markdown import html_fragment_to_markdown  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--min-confidence",
        choices=("high", "medium", "low"),
        default="medium",
        help="Only migrate fields scoring at least this HTML confidence",
    )
    parser.add_argument("--ids", action="append", default=[], help="Limit to specific post UUIDs (repeatable)")
    parser.add_argument("--apply", action="store_true", help="Write changes (default is dry-run)")
    parser.add_argument("--backup-dir", type=str, default="", help="Write original content JSON per slug here")
    args = parser.parse_args()

    id_filter = {UUID(x) for x in args.ids} if args.ids else None
    backup_root = Path(args.backup_dir) if args.backup_dir else None
    if backup_root:
        backup_root.mkdir(parents=True, exist_ok=True)

    db: Session = SessionLocal()
    try:
        q = db.query(BlogPost).order_by(BlogPost.updated_at.desc())
        if id_filter:
            q = q.filter(BlogPost.id.in_(id_filter))
        posts = q.all()

        updated_posts = 0
        candidates = 0
        for p in posts:
            updates: dict[str, str] = {}
            reasons: list[str] = []

            if looks_like_legacy_html(p.content, min_confidence=args.min_confidence):  # type: ignore[arg-type]
                new_c = html_fragment_to_markdown(p.content or "")
                if new_c.strip() and new_c != (p.content or "").strip():
                    updates["content"] = new_c
                    reasons.append(f"content:{content_confidence(p.content)}")

            if looks_like_legacy_html(p.excerpt, min_confidence=args.min_confidence):  # type: ignore[arg-type]
                new_e = html_fragment_to_markdown(p.excerpt or "").strip()
                if new_e and new_e != (p.excerpt or "").strip():
                    updates["excerpt"] = new_e
                    reasons.append(f"excerpt:{content_confidence(p.excerpt)}")

            if not updates:
                continue

            candidates += 1
            payload = {
                "id": str(p.id),
                "slug": p.slug,
                "title": p.title,
                "status": p.status,
                "reasons": reasons,
                "dry_run": not args.apply,
            }
            print(json.dumps(payload, indent=2))
            for field, val in updates.items():
                snippet = val[:400].replace("\n", "\\n")
                print(f"  --- new {field} (len={len(val)}): {snippet!r}...")

            if backup_root and args.apply:
                backup = {
                    "id": str(p.id),
                    "slug": p.slug,
                    "title": p.title,
                    "content": p.content,
                    "excerpt": p.excerpt,
                }
                (backup_root / f"{p.slug}.json").write_text(
                    json.dumps(backup, indent=2, default=str), encoding="utf-8"
                )

            if args.apply:
                if "content" in updates:
                    p.content = updates["content"]
                if "excerpt" in updates:
                    p.excerpt = updates["excerpt"]
                updated_posts += 1

        if args.apply:
            db.commit()
            print(f"\nCommitted updates for {updated_posts} post(s).")
        else:
            db.rollback()
            print(f"\nDry-run complete ({candidates} post(s) would update with --apply).")
    finally:
        db.close()


if __name__ == "__main__":
    main()
