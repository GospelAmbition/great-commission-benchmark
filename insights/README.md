# Insights - AI-Generated Blog Content

This folder contains AI-generated articles for the GCB blog.

## Setup (one-time)

1. Get API key from https://greatcommissionbenchmark.ai/dashboard/settings
2. Copy `.env.example` to `.env` and add your key
3. Ensure your account has blog management permission

## Files

- `_article_prompt.md` - Template prompt for generating articles
- `*.md` - Article drafts ready for publishing
- `blog_cli.py` - CLI tool for publishing
- `.env` - API key (gitignored)
- `.env.example` - Template for environment variables

## Publishing

### Create a draft

```bash
python blog_cli.py create --file my-article.md --title "My Article Title"
```

### Publish directly

```bash
python blog_cli.py create --file my-article.md --title "My Article Title" --publish
```

### Publish an existing draft

```bash
python blog_cli.py publish --id <post-id>
```

### List posts

```bash
# All posts
python blog_cli.py list

# Only drafts
python blog_cli.py list --status draft

# Only published
python blog_cli.py list --status published
```

### Update a post

```bash
python blog_cli.py update --id <post-id> --file updated-article.md
```

### View a post

```bash
python blog_cli.py get --id <post-id> --show-content
```

### Unpublish (revert to draft)

```bash
python blog_cli.py unpublish --id <post-id>
```

### Delete a post

```bash
python blog_cli.py delete --id <post-id>
```

## Workflow

1. Generate article content using `_article_prompt.md` as a template
2. Save the article as a markdown file in this folder
3. Create as draft: `python blog_cli.py create --file article.md --title "Title"`
4. Review the draft (via web UI or CLI)
5. When ready, publish: `python blog_cli.py publish --id <post-id>`

## Content Guidelines

- Use markdown format for articles
- The first paragraph will be used as the excerpt (or specify with `--excerpt`)
- Slug is auto-generated from title (or specify with `--slug`)
- Categories can be added with `--categories <id1> <id2>`

## Getting Help

Run `python blog_cli.py --help` for full command reference.
