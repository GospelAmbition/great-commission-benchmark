---
name: gcb-newsletter
description: Draft, review, publish, and distribute the monthly Great Commission Benchmark insights newsletter. Use when asked to write a newsletter, monthly digest, email roundup of model tests, send the newsletter to subscribers, or render newsletter HTML. Aligns tone with Great Commission Benchmark model review articles.
---

# Great Commission Benchmark monthly newsletter

## Naming and brand (required for reader-facing copy)

Recognition of the initials **“GCB”** is still low. In newsletter **titles**, **email subject lines**, **excerpts**, and **opening sections**, use the full name **Great Commission Benchmark** (at least once near the top, ideally in the title or first short block). Do **not** rely on “GCB” alone for public audience copy. Internal identifiers (MCP server name `gcb-mcp`, tool names, file paths) may still say `gcb`.

## Dates and model context (required)

- **Dates:** Never leave raw ISO timestamps (e.g. `2026-04-15T18:32:01+00:00`) in reader-facing copy. Use **human-readable calendar dates** (e.g. **April 15, 2026**). State clearly that publication times are **UTC** when precision matters (benchmark “went live” time).
- **Model descriptions:** When the platform exposes a vendor/catalog **description** for a model, **use it** to orient readers who do not follow model IDs daily. In spotlights, a short blockquote or italic line is appropriate; in dense lists, a **trimmed one-line “about”** is better than nothing. If no description exists, rely on name + provider + link to the model detail page—do not invent product claims.

## Tone and audience (required)

Before writing or editing newsletter prose, read the repository file **`insights/_article_review_prompt.md`** (Great Commission Benchmark workspace). Match its audience (ministry and technical leaders), spiritual voice, technical voice, style guidelines, and “what to avoid” sections. The newsletter is **shorter** than a full model review (digest, not 1,200+ words), but the **voice must match** model reviews: professional, strategic, warm, scan-friendly (short paragraphs, bullets, clear headings).

## Forward-facing communication (not an internal report)

The newsletter is **outward-facing**: email and web readers who may not know our tools or workflows.

- **Do not** sound like a technical appendix, QA log, or CMS instruction sheet. Avoid internal phrases such as “blog index,” “link a review when published,” or “Model detail & charts” unless you intentionally mirror public UI copy—and even then prefer plain English (“See full benchmark result,” “Read the insight article”).
- **Do not** paste the same long “ministry takeaway” or governance disclaimer **under every model**. If stewardship needs a reminder, say it **once** for the spotlight section (or the whole issue), in warm, non-repetitive language.
- **Include only what helps the reader decide or explore:** the **overall score** (single composite 0–100), human-readable dates, vendor description when available, and **working links** to benchmark results and (when they exist) insight articles. If there is no insight article yet, **say nothing**—do not apologize for missing content or instruct editors inside reader-facing copy.

## Scores in the digest (required)

- In newsletter **spotlights** and similar reader-facing blocks, show **only the overall score** (one number, 0–100). **Do not** list Tier 1, Tier 2, and Tier 3 in the email or digest body—those who want tier breakdowns follow **See full benchmark result** / **View result** on the site.
- Optional MCP **`selection="tier1_score"`** only changes **which two models** are chosen for the spotlight; it does **not** change the rule above: still quote **overall score** only in the digest copy.

## Default selection policy (“top two”)

When using **`create_monthly_newsletter_draft`** without overrides:

- **Window:** benchmark runs **newly published on the Great Commission Benchmark leaderboard** in the last **30 days** (`completed_at`), not OpenRouter “new model” dates.
- **Spotlight models:** top **two** in that window by **`overall_score`** (higher is better). Optional MCP argument **`selection="tier1_score"`** ranks candidates by Tier 1 instead when choosing who to feature; the digest still displays **overall score only** for those picks.

Document in the excerpt if you use `tier1_score` selection so readers are not misled about how spotlights were chosen.

## MCP workflow

### 1) Draft on the platform (automated assembly)

```
create_monthly_newsletter_draft(
  days_back=30,
  selection="overall_score",   # or "tier1_score"
  top_spotlights=2,
)
```

This creates a **draft** insights post (usually under the **Newsletters** category when it exists). It pulls leaderboard data, resolves insight URLs and **reuses model-review header images** when a published post is linked to that `model_id`.

### 2) Human review and edits

```
get_blog_post(post_id="<uuid>")
update_blog_post(post_id="...", content="...", title="...", excerpt="...")
```

Examples of human requests mapped to edits:

- “Change the second paragraph to focus on Tier 1” → update `content` (and keep headings consistent).
- “Swap spotlight model A for model B and summarize B” → rewrite the spotlight section; optionally refresh `model_ids` / `featured_image_url` via **`generate_and_upload_header`** if there is no review image for B.

### 3) Publish to the website

```
publish_blog_post(post_id="...")
```

Live URL: `https://greatcommissionbenchmark.ai/insights/{slug}`

### 4) Email preview (optional)

```
render_newsletter_email_html(post_id="...")
```

Returns **HTML** suitable for email clients (sanitized). Use before sending.

### 5) Send to subscribers (explicit step only)

```
send_newsletter_to_subscribers(post_id="...", dry_run=true)   # validate first
send_newsletter_to_subscribers(post_id="...", dry_run=false) # sends via MailerLite
```

**Never** call `dry_run=false` until a human has approved the draft and the preview. Sending requires **admin** API access and MailerLite configuration on the server (see backend README).

## Canonical links for CTAs

Use full `https://` URLs in email HTML; markdown on the blog can use site-relative paths if the renderer adds the host.

| Purpose | Path |
|--------|------|
| Leaderboard | `https://greatcommissionbenchmark.ai/leaderboard` |
| Insights index | `https://greatcommissionbenchmark.ai/insights` |
| Contribute / test / volunteer | `https://greatcommissionbenchmark.ai/contribute` |
| Subscribe | `https://greatcommissionbenchmark.ai/newsletter` |
| Model detail | `https://greatcommissionbenchmark.ai/leaderboard/models/{url-encoded-model_id}` |
| Insight article | `https://greatcommissionbenchmark.ai/insights/{slug}` |

## Images

Prefer **`featured_image_url`** from the existing **published** model review post for each spotlight model. If none exists, ask whether to run **`generate_and_upload_header`** for that model before publishing.

## Server name

MCP server: **`gcb-mcp`** (same stack as benchmark tests and blog tools).
