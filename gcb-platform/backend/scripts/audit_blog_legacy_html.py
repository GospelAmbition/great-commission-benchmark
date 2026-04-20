#!/usr/bin/env python3
"""
Audit blog_posts.content (and excerpt) for legacy HTML vs Markdown storage.

Usage (from backend/ directory, with DATABASE_URL or .env):

    python scripts/audit_blog_legacy_html.py
    python scripts/audit_blog_legacy_html.py --min-confidence high
    python scripts/audit_blog_legacy_html.py --json > report.json

Exit code 0 always unless DB connection fails.
"""
from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session  # noqa: E402

from app.db.base import SessionLocal  # noqa: E402
from app.db.models.blog_post import BlogPost  # noqa: E402
from app.services.blog_html_detection import (  # noqa: E402
    content_confidence,
    markdownish_score,
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--min-confidence",
        choices=("high", "medium", "low", "none"),
        default="medium",
        help="Report rows where content OR excerpt meets at least this HTML signal",
    )
    parser.add_argument("--json", action="store_true", help="Print JSON array instead of table")
    args = parser.parse_args()

    order = {"none": 0, "low": 1, "medium": 2, "high": 3}
    min_o = order[args.min_confidence]

    db: Session = SessionLocal()
    try:
        posts = db.query(BlogPost).order_by(BlogPost.updated_at.desc()).all()
        rows: list[dict] = []
        for p in posts:
            c_conf = content_confidence(p.content)
            e_conf = content_confidence(p.excerpt)
            if max(order[c_conf], order[e_conf]) < min_o:
                continue
            rows.append(
                {
                    "id": str(p.id),
                    "slug": p.slug,
                    "title": p.title,
                    "status": p.status,
                    "content_confidence": c_conf,
                    "excerpt_confidence": e_conf,
                    "markdownish_score": round(markdownish_score(p.content), 3),
                    "content_preview": (p.content or "")[:240].replace("\n", " "),
                }
            )

        if args.json:
            print(json.dumps(rows, indent=2))
            return

        print(f"Posts with HTML signal >= {args.min_confidence}: {len(rows)} / {len(posts)}")
        print("-" * 100)
        for r in rows:
            print(
                f"{r['status']:10} {r['content_confidence']:7} {r['excerpt_confidence']:7} "
                f"md~{r['markdownish_score']:.2f}  {r['slug']}\n  {r['title'][:80]}\n  id={r['id']}\n"
            )
    finally:
        db.close()


if __name__ == "__main__":
    main()
