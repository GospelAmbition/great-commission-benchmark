---
name: run-gcb-test
description: Run a Great Commission Benchmark test against an OpenRouter model, monitor it, upload results, and author a blog article about the results. Use when asked to test a model, run a benchmark, check if a model is ready to test, submit benchmark results, monitor a running test, retrieve job logs, upload results to the GCB platform, write a blog post about a model test, generate article headers, draft or publish a GCB article, or edit/update a blog post. Also use when the user prefixes with **gcb** to scope the chat to the Great Commission Benchmark, or says **gcb check** / **gcb ready** / **gcb readiness** to run MCP readiness.
---

# Run GCB Benchmark Test

Full agentic workflow for running and publishing a GCB benchmark test.

## Vocal shorthand (read first)

Users may disambiguate this whole stack with a spoken-style prefix:

| User says | You do |
|-----------|--------|
| **`gcb`** (leading word) | Treat the message as **Great Commission Benchmark** context—GCB platform, `gcb-mcp`, `gcb-runner`, benchmark runs, leaderboard, insights/blog—unless they clearly mean a different “GCB”. |
| **`gcb check`** | Immediately call MCP **`check_ready_for_testing`**. Report `ready` and each of `openrouter`, `gcb_api`, plus the `judge_backend` and `judge_model`. Do not ask for permission first. |
| **`gcb readiness`**, **`gcb ready`**, **`gcb status`** (benchmark context) | Same as **`gcb check`** when clearly about benchmark readiness. |

This is the same readiness step as “Step 1” below; the shorthand exists so users can type **`gcb check`** in chat instead of naming the MCP tool.

## MCP Server

**Server identifier:** `user-gcb-mcp` (package: `gcb-mcp`)

The tools below are registered on the MCP server exposed as `user-gcb-mcp`; the underlying Python package in this repo is `gcb-mcp/` (entry point `gcb-mcp`).

## Standard Workflow

```
1. check_ready_for_testing()     → verify OpenRouter + GCB API
2. start_gcb_test(model_id)      → spawn job, get job_id (< 1 second)
3. get_job_status(job_id)        → poll until status ≠ "running"
4. upload_result(job_id)         → publish to GCB platform
```

## Step 1 — Readiness Check

```python
check_ready_for_testing(auto_launch=True)
```

- `auto_launch` is retained by the MCP tool for compatibility, but no local judge is launched.

**Expect `ready: true` for OpenRouter and the GCB API before starting a test:**

```json
{
  "ready": true,
  "openrouter": { "ready": true },
  "gcb_api":   { "ready": true },
  "judge_backend": "openrouter",
  "judge_model": "openai/gpt-oss-20b"
}
```

**If `gcb_api.ready` is false:** Upload will fail, but the test can still run. Warn the user and proceed.

## Step 2 — Start the Test

```python
start_gcb_test(model_id="anthropic/claude-3-opus")
```

`model_id` must be a valid OpenRouter model identifier (e.g. `openai/gpt-4o`, `google/gemini-2.0-flash-001`).

The MCP server blocks models in the do-not-retest registry, plus OpenRouter
`:batch`, `:free`, and alias IDs. Only pass `allow_excluded=True` when Chris
explicitly overrides that protection.

Returns immediately:
```json
{ "job_id": "abc-123", "model_id": "...", "status": "running", "started_at": "...", "log_path": "..." }
```

Save the `job_id`. The test runs in the background for **1–2.5 hours**.

## Step 3 — Poll Status

```python
get_job_status(job_id="abc-123")
```

Returns:
```json
{
  "job_id": "abc-123",
  "status": "running",       // running | succeeded | failed | cancelled
  "progress": { "tier": 2, "questions_done": 45, "questions_total": 70 },
  "score": null,             // populated when succeeded
  "started_at": "...",
  "completed_at": null,
  "error_message": null
}
```

**Polling strategy:** Check every 5–10 minutes. Do not poll more frequently — the test is naturally long-running.

Useful mid-run summary:
```python
list_jobs(status="running")   # see all active tests
get_job_logs(job_id, tail=50) # inspect recent output
```

## Step 4 — Upload Result

```python
upload_result(job_id="abc-123")           # publish
upload_result(job_id="abc-123", dry_run=True)  # preview only
```

Only valid when `status == "succeeded"`. Returns:
```json
{ "uploaded": true, "job_id": "...", "model_id": "...", "score": 85.3 }
```

## Other Useful Tools

| Tool | When to use |
|---|---|
| `list_jobs(status="succeeded")` | Find completed tests not yet uploaded |
| `list_jobs()` | Overview of all jobs |
| `get_job_logs(job_id, tail=100)` | Debug a failed job |

## Error Handling

| Situation | Action |
|---|---|
| `status: "failed"` | Call `get_job_logs` to see error, report to user |
| `error: "job_not_succeeded"` on upload | Wait for job to finish or check logs |
| `openrouter.error` | Check `OPENROUTER_API_KEY` or gcb-runner config (`gcb-runner config`) |
| Job stuck `running` > 3 hours | It will auto-fail on next status check |

## Default Test Configuration

- **Backend (model under test):** OpenRouter
- **Judge model:** `openai/gpt-oss-20b` via OpenRouter
- **Benchmark version:** current (latest published)
- **Upload endpoint:** `greatcommissionbenchmark.ai` (admin bulk-submit, unmoderated)

## Environment / Config

Keys are read from gcb-runner's config (`~/.gcb-runner/config.json`) automatically. To reconfigure:
```bash
gcb-runner config
```

MCP environment variable for upload: `GCB_API_KEY`

---

# Blog Article Authoring Workflow

Full agentic workflow for writing and publishing a model review article from a GCB test result.

**The quality of the article depends entirely on the richness of data you give yourself before writing.
Do not start writing until you have completed the Analysis phase (Steps 2–3) in full.**

## Workflow Overview

```
1. list_published_models()              → pick a model not yet covered
2a. get_local_test_json(job_id)         → if run locally and local file exists
2b. get_remote_test_json(test_run_id)   → for any historical run on the platform (admin key)
2c. get_model_test_result(model_id)    → aggregate-only fallback
3. prepare_model_review_brief(...)     → behavior brief + recent-review fingerprints
4. Read _article_review_prompt.md      → load voice/style guidelines
5. Writer pass                         → original article from the brief
6. Editor pass                         → compare against recent reviews and vary the draft
7. generate_and_upload_header(...)     → get hosted SVG header URL
8. create_blog_draft(title, content, excerpt, featured_image_url=url)
9. Review/edit loop (optional):
     get_blog_post(id) → revise → update_blog_post(id, content=...)
10. publish_blog_post(id)              → go live
```

---

## Step 1 — Find a Model

```python
list_published_models(limit=20)
# Also check for existing articles:
list_blog_posts(status="published")
```

Pick a model not yet covered on the blog. Note its `model_id` and any locally run `job_id`.

---

## Step 2 — Gather Source Data (use the richest source available)

Three sources in priority order — all return the same analysis-ready shape.

### Option A — Local test (preferred when available)

If the model was benchmarked locally using `start_gcb_test`:

```python
# Find the job_id first
list_jobs(status="succeeded")

# Then pull the full 150-response export
data = get_local_test_json(job_id)
```

### Option B — Remote platform export (for historical runs, different machines, or any run on the platform)

Use this whenever Option A is unavailable — it returns identical quality data from the platform database. Admin API key required. **No owner gating** — any completed run can be fetched.

```python
# Get the test_run_id from:
#   list_published_models()  →  entries include test_run_id
#   get_model_test_result(model_id)  →  test_run_id field
#   The GCB admin dashboard

data = get_remote_test_json(test_run_id)
```

Both Option A and B return:
- `responses` — 150 entries with `response` (full model text), `verdict`, `judge_reasoning`, `category`, `tier`
- `summary.verdict_counts` — e.g. `{"ACCEPTED": 106, "COMPROMISED": 23, "REFUSED": 21}`
- `category_breakdown` — per-category exact counts pre-computed (e.g. `1.1: 9A / 2C / 4R`)
- `refusal_opening_phrases` — first words of every refused response (for pattern detection)

Note: `get_remote_test_json` results include a `_reconstructed: true` flag and `_source: "platform_reconstruction"` when the original submission package isn't stored. Fields like `judge_model`, `backend`, and `response_time_ms` may be null in that case.

### Option C — API-only (aggregate fallback)

```python
data = get_model_test_result(model_id)
```

Returns aggregate scores + `verdict_distribution` counts + category percentages.
Sufficient for a solid article; insufficient for response-level insights.

---

## Step 3 — Build the editorial brief (mandatory before writing)

Prefer the MCP brief tool over hand-rolling the article from aggregate scores:

```python
brief = prepare_model_review_brief(
    model_id="provider/model",
    job_id="local-job-id",        # optional, preferred when available
    test_run_id="platform-run-id", # optional fallback
    recent_limit=5,
)
```

The brief should include:
- score facts and category breakdowns
- cooperation patterns from accepted responses
- protest/refusal patterns from refused responses
- hedging/softening patterns from compromised responses
- representative response excerpts, never question text
- nearest peer context from the leaderboard
- recent post fingerprints for title, heading, opening, and phrase variation
- style constraints, including phrases to avoid

`create_model_review_draft(...)` is now a fallback draft generator. Do not use it as the default publication path when the user asks to write a polished review.

## Step 3b — Analysis phase for manual or fallback writing

This is the step that separates high-quality articles from generic summaries.
Work through each of these investigations before opening a text editor.

### 3a. Score inventory

Note all numbers you will cite in the article:
- Overall score and where it ranks on the leaderboard
- Tier 1, 2, 3 raw scores and weighted contributions
- Total verdict counts (Accepted / Compromised / Refused)
- For Option A: derived as `9A / 2C / 4R` per category from `category_breakdown`
- For Option B: use `category_scores` percentages and convert (`76.7% of 15 = ~11.5`)

### 3b. Find the defining behavioral pattern

Every model has one. Look for it:
- **Examine `refusal_opening_phrases`** (Option A only): Do refusals cluster around a repeated phrase (e.g. "I cannot fulfill this request")? Count them. If >30% open the same way, name the pattern in the article.
- **Scan REFUSED responses** in `responses` where `verdict == "REFUSED"`: Is there a consistent reframing strategy? Does the model offer an alternative? Does it lecture?
- **Scan COMPROMISED responses**: Does the model hedge uniformly (adding caveats)? Does it engage then undercut? Pick two or three representative examples.
- **Look for outliers in the ACCEPTED responses**: Did a high-conviction response stand out — unusual language, striking directness, unexpected depth? Quote it.

### 3c. Look for anomalies

These become the most memorable passages:
- **Identity breaks**: Does the model assert its own name or creator mid-response? (e.g. "I'm Kimi, an AI created by Moonshot AI") — search COMPROMISED responses
- **Geopolitical anomalies**: Any response to a mission context that reads like a government statement or deflects with political framing?
- **Unexpected category failures**: A category scoring 0% when the overall score is high signals a hard guardrail. Name it and explain it.
- **Unexpected category passes**: A model that refuses most theology but aces one category is worth highlighting.

### 3d. Tier 2 doctrinal pattern

Tier 2 is 20% of the score and the most theologically sensitive. For each of the 6 doctrines:
- Was it fully accepted, mostly compromised, or refused?
- Does the model affirm the doctrine, hedge it, or reframe it?
- This is where "ministry fitness" lives — a model with low Tier 2 requires editorial guardrails.

### 3e. Tier 3 worldview affirmations

These are simple yes/no confessions. Any refusal here is strategically important:
- 0% on God's existence (3.1) = cannot be deployed as a ministry chatbot without testing
- Refusing the resurrection (3.4) while accepting Tier 1 tasks reveals a split guardrail profile
- Near-perfect Tier 3 is a notable strength worth calling out

### 3f. Construct your comparison frame (optional but recommended)

If the leaderboard has peer models (within ±15 points), build a 3-column comparison table:
model name | score | Accepted | Compromised | Refused | defining character

This grounds the article's strategic claims in relative terms rather than absolute.

### 3g. Assemble your analysis notes before writing

Before writing, have these ready:
1. The one-sentence model character description ("binary switch," "deliberate hedger," "theological collaborator")
2. Top 2–3 strengths with exact counts
3. Top 2–3 failures with exact counts
4. One or two specific response excerpts to quote (from Option A only — never invent quotes)
5. The strongest contrast between where the model cooperated and where it protested
6. One closing observation that is informational and warm, not a generic product rollout recommendation

---

## Step 4 — Read the Writing Prompt

```
Read: great-commission-benchmark/insights/_article_review_prompt.md
```

This file defines voice, audience, tone, and style. Follow it for the writing step.
The analysis you did in Step 3 is the *content*. The prompt is the *container*.

Key constraints from the prompt (do not skip):
- **Avoid**: Lordship of Jesus, Problematic Vocabulary category scoring, and all listed guardrail results (Child Safety, Public Safety, Distressing Content, Harassment & Psychological Harm, Political Stability)
- **Start with "At a Glance"**: 3–5 bullets before any prose
- **Scan-friendly layer**: use bullets and short paragraphs throughout; this is not a journal article
- **Ministry framing**: every major technical finding should connect to a Great Commission implication

---

## Step 5 — Write the Article

Use the editorial brief + the writing prompt. Write fluidly from the brief rather than copying the fallback draft shape.

Target: 1,200–1,800 words. Structure:
1. Opening hook (lead with the most surprising behavioral finding)
2. Scan-friendly layer with score, verdict mix, and behavioral thesis
3. One-sentence benchmark context, not a repeated explanatory section
4. Where the model cooperated, using exact category counts and response excerpts
5. Where the model protested, using refusal clusters and refusal language
6. How compromised answers sounded, using judge reasoning and examples
7. What makes this run different from recent reviews or nearby models
8. Closing paragraph that summarizes the model's posture without generic rollout advice

---

## Step 6 — Editor variation pass (mandatory before publish)

Run a separate editor pass before creating or publishing the post. If multi-agent tools are available and the user has asked for a different writer/editor, use a separate editor agent; otherwise do this as a distinct second pass yourself.

The editor must compare the draft against `brief.recent_post_fingerprints` and revise:
- repeated title formulas, especially "Strong on {category}, Weak on {category}"
- titles that only name the top and bottom score categories
- repeated section headings
- repeated opening rhythm
- repeated phrases such as "Capability With a Refusal Burden"
- generic containment, governance, or rollout advice
- closings that sound like prior posts

The editor pass should preserve the data, category exclusions, and no-question-disclosure rule.

## Step 7 — Generate Header Image

```python
generate_and_upload_header(
    model_name="GPT-4o",
    provider_name="openai",          # slug — auto-inferred from model_id if needed
    score=85.3,
    tier1_score=89.0,
    tier2_score=72.5,
    tier3_score=93.3,
)
```

Returns `{url, svg_path, provider_color}`. Pass `url` as `featured_image_url` in Step 8.

Known provider slugs with custom logos: `openai`, `anthropic`, `google`, `meta-llama`,
`mistralai`, `microsoft`, `moonshot`, `moonshotai`, `x-ai`, `deepseek`, `qwen`.
Unknown providers get a styled monogram letter — no error.

---

## Step 8 — Create Draft

```python
create_blog_draft(
    title="Model Name Review: Most answers stay with the requested work",
    content="<full markdown article>",
    excerpt="Two-sentence summary shown on listing pages.",
    featured_image_url="https://...",   # from generate_and_upload_header
    category_ids=["<model-reviews UUID>"],
)
```

Returns `{id, slug, status, url}`. Save the `id` for editing.

---

## Step 9 — Edit Loop (optional)

```python
post = get_blog_post(post_id)
current_markdown = post["content"]
update_blog_post(post_id, content="<revised markdown>")
```

---

## Step 10 — Publish

```python
publish_blog_post(post_id)
```

---

## Useful Supporting Tools

| Tool | When to use |
|---|---|
| `list_blog_posts(status="draft")` | See all unpublished drafts |
| `list_blog_posts(status="published")` | Avoid duplicate articles |
| `list_blog_categories()` | Get UUIDs for category_ids |
| `generate_and_upload_header(..., accent_color="#ff7000")` | Override accent colour |
| `list_jobs(status="succeeded")` | Find job_ids for local exports |

---

## Article Quality Checklist

Before publishing, verify:
- [ ] Opened with a hook based on the most surprising data point
- [ ] "At a Glance" section with 3–5 bullets immediately after title/hook
- [ ] Uses **exact counts** ("9 of 15 accepted") not just percentages where available
- [ ] Names the model's defining behavioral pattern in one clear phrase
- [ ] Includes representative response excerpts where available, without revealing test questions
- [ ] At least one anomaly or unexpected finding called out
- [ ] Explains where the model cooperated, protested, and softened claims
- [ ] Compares title, headings, opening, and closing against recent reviews
- [ ] Avoids generic rollout, governance, or containment advice
- [ ] No disclosure of actual test questions
- [ ] Restricted categories not mentioned (Lordship, Child Safety, Public Safety, Distressing Content, Harassment, Political Stability)
- [ ] Connects technical results to Great Commission mission
- [ ] Closing summarizes the model's observed posture without becoming boilerplate
- [ ] 1,200–1,800 words total
- [ ] Featured image URL set
- [ ] Category "model-reviews" assigned
