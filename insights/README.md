# Insights - Blog Publishing Workspace

This folder is the working directory for writing and publishing articles to the Great Commission Benchmark blog at [greatcommissionbenchmark.ai/action/insights](https://greatcommissionbenchmark.ai/action/insights).

Articles are written here as markdown files, then published to the live site via `blog_cli.py` which authenticates against the backend API using an API key.

---

## Directory Structure

```
insights/
├── .env                          # API keys (gitignored)
├── blog_cli.py                   # CLI tool for publishing
├── requirements.txt              # Python dependencies
├── _article_prompt.md            # Prompt template for writing articles
├── _article_review_prompt.md     # Review prompt template (scan-friendly format)
├── benchmark-categories.md       # Canonical category reference (19 categories, 3 tiers)
├── article-*.md                  # Article drafts and finals
├── *.json                        # Benchmark test run data (source material)
├── *.html                        # Header images / visual assets
└── batch_guardrails/             # Guardrail analysis articles and images
```

---

## Setup (One-Time)

### 1. API Key

Get an API key from [greatcommissionbenchmark.ai/dashboard/settings](https://greatcommissionbenchmark.ai/dashboard/settings). The account must have **blog management permission**.

### 2. Environment File

The `.env` file in this directory must contain:

```env
GCB_API_KEY=gcb_your_key_here
GCB_API_URL=https://api.greatcommissionbenchmark.ai/api
```

The `GCB_API_URL` defaults to `https://greatcommissionbenchmark.ai/api/v1` if not set. The current production API base is `https://api.greatcommissionbenchmark.ai/api`.

### 3. Python

The CLI uses only Python standard library (`urllib`, `json`, `argparse`). No `pip install` required. Python 3.8+ is sufficient.

---

## How Publishing Works (for Claude Code)

This section documents the exact steps Claude Code should follow when asked to publish an article. The entire workflow runs from this `insights/` directory.

### The API

- **Base URL:** `https://api.greatcommissionbenchmark.ai/api`
- **Blog endpoints prefix:** `/runner/blog`
- **Authentication:** `X-API-Key` header with the `GCB_API_KEY` value from `.env`
- **Content format:** The API accepts markdown in the `content` field. The frontend renders it.
- **Required permission:** `can_manage_blog` on the user account that owns the API key

### Step-by-Step: Publish an Article

**1. Confirm the article markdown file exists in this directory.**

The file should be named like `article-{model}-benchmark-review.md`.

**2. Upload the featured image (if any).**

```bash
python3 /Users/chris/Documents/PROJECTS/great-commission-benchmark/insights/blog_cli.py upload-image \
  --file /path/to/image.png
```

This uploads the image to S3 storage and prints the URL. Use that URL in the `--featured-image` flag when creating the post. Supported formats: JPG, PNG, GIF, WebP. Max 10MB.

If the image is already hosted elsewhere, pass its URL directly to `--featured-image` without uploading.

**3. Look up available categories.**

```bash
python3 /Users/chris/Documents/PROJECTS/great-commission-benchmark/insights/blog_cli.py categories
```

This returns category IDs and names. Common categories to look for: "AI Reviews", "Benchmark", "Model Analysis", etc.

**4. Create and publish the post.**

```bash
python3 /Users/chris/Documents/PROJECTS/great-commission-benchmark/insights/blog_cli.py create \
  --file article-filename.md \
  --title "Article Title Here" \
  --excerpt "A 1-2 sentence summary for the listing page." \
  --slug "article-slug-here" \
  --featured-image "https://url-to-image.png" \
  --categories CATEGORY_UUID_1 CATEGORY_UUID_2 \
  --publish
```

**All flags:**

| Flag | Required | Description |
|------|----------|-------------|
| `--file` / `-f` | Yes | Path to the markdown file |
| `--title` / `-t` | Yes | Post title (max 255 chars) |
| `--slug` / `-s` | No | URL slug. Auto-generated from title if omitted |
| `--excerpt` / `-e` | No | Summary text. Auto-extracted from first paragraph if omitted |
| `--featured-image` | No | URL to featured image |
| `--categories` | No | Space-separated category UUIDs |
| `--publish` / `-p` | No | Publish immediately instead of saving as draft |

**5. Verify the post.**

On success, the CLI prints the post ID and URL. The live article will be at:
```
https://greatcommissionbenchmark.ai/action/insights/{slug}
```

### Step-by-Step: Two-Stage Publish (Draft First)

If the user wants to review before publishing:

```bash
# Create as draft (no --publish flag)
python3 blog_cli.py create --file article.md --title "Title"
# Returns: Draft created, ID: <uuid>

# Review via CLI
python3 blog_cli.py get --id <uuid> --show-content

# When ready, publish
python3 blog_cli.py publish --id <uuid>
```

### Updating a Published Post

```bash
python3 blog_cli.py update --id <uuid> --file updated-article.md
```

You can also update individual fields:
```bash
python3 blog_cli.py update --id <uuid> --title "New Title"
python3 blog_cli.py update --id <uuid> --featured-image "https://new-image.png"
python3 blog_cli.py update --id <uuid> --excerpt "Updated summary."
```

---

## CLI Command Reference

| Command | Description |
|---------|-------------|
| `create` | Create a new post (draft or published) |
| `publish` | Publish an existing draft by ID |
| `unpublish` | Revert a published post to draft |
| `list` | List posts (optionally filter by `--status draft\|published`) |
| `get` | View a single post by ID (`--show-content` for full content) |
| `update` | Update fields on an existing post |
| `delete` | Delete a post (`--force` to skip confirmation) |
| `categories` | List all available categories with their UUIDs |
| `upload-image` | Upload an image and get its URL for `--featured-image` |

All commands are run as:
```bash
python3 /Users/chris/Documents/PROJECTS/great-commission-benchmark/insights/blog_cli.py <command> [flags]
```

---

## Article Writing Workflow

### Source Materials

Each benchmark review article starts with:

1. **Test run JSON** (e.g., `anthropic-claude-opus-4.6.json`) - Raw benchmark results with all 150 responses, verdicts, reasoning, and timing data.
2. **Prompt template** (`_article_review_prompt.md`) - The scan-friendly article format with "At a Glance" section, bulleted analysis, and strategic next steps.
3. **Category reference** (`benchmark-categories.md`) - The 19 benchmark categories across 3 tiers.

### Article Naming Convention

```
article-{model-slug}-benchmark-review.md
```

Examples:
- `article-gpt-5.2-benchmark-review.md`
- `article-claude-opus-4.6-benchmark-review.md`

### Header Images

Header images are created as self-contained HTML files, screenshotted, and saved as PNGs:
```
article-{model-slug}-header.html     # Source HTML
```
The PNG is stored locally (e.g., Desktop) and uploaded separately.

---

## API Details (for debugging)

### Endpoints Used by the CLI

The CLI constructs URLs as: `{GCB_API_URL}/runner/blog{endpoint}`

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/runner/blog/posts` | List posts (query: `status`, `limit`, `offset`) |
| `POST` | `/runner/blog/posts` | Create post (query: `publish=true` for immediate publish) |
| `GET` | `/runner/blog/posts/{id}` | Get single post |
| `PUT` | `/runner/blog/posts/{id}` | Update post |
| `DELETE` | `/runner/blog/posts/{id}` | Delete post |
| `POST` | `/runner/blog/posts/{id}/publish` | Publish a draft |
| `POST` | `/runner/blog/posts/{id}/unpublish` | Revert to draft |
| `GET` | `/runner/blog/categories` | List categories |
| `POST` | `/runner/blog/categories` | Create category |
| `POST` | `/runner/blog/generate-slug` | Generate and check slug uniqueness |

### Authentication

All requests include:
```
X-API-Key: <GCB_API_KEY>
Content-Type: application/json
```

### Error Handling

- `401` - Invalid or missing API key
- `403` - API key lacks `can_manage_blog` permission
- `400` - Duplicate slug or invalid data
- `404` - Post not found
- `429` - Rate limited

---

## Known Limitations

1. **Content is markdown.** The CLI sends raw markdown. The frontend renders it with Tailwind Typography. Complex HTML (tables, custom styling) may not render perfectly.

2. **No bulk operations.** Each post is created/updated individually.

3. **Excerpt auto-extraction is basic.** The CLI extracts the first non-heading paragraph. For better control, always pass `--excerpt` explicitly.

4. **Image upload is a two-step process.** Upload the image first with `upload-image`, then pass the returned URL to `--featured-image` when creating/updating the post.

---

## Troubleshooting

**"GCB_API_KEY not set"**
- Check that `.env` exists in this directory with `GCB_API_KEY=gcb_...`

**"Blog management permission required"**
- The API key's user account needs the `can_manage_blog` role. Contact an admin.

**"A post with this slug already exists"**
- Use `--slug` to specify a different slug, or update the existing post with `update --id`.

**Connection errors**
- Verify `GCB_API_URL` in `.env` points to `https://api.greatcommissionbenchmark.ai/api`
- Check that the backend is reachable: `curl https://api.greatcommissionbenchmark.ai/api/health`
