# Unpublishable / do-not-retest models

Skip these on suggestion runs. Do not start a new GCB test. Do not upload. Do not `allow_invalid`.

These exclusions are enforced by `gcb-mcp`: suggestion results omit them and
test-start tools return `model_excluded`. Chris can explicitly override that
protection with `allow_excluded=True`.

Also skip OpenRouter `:batch` IDs, `:free` duplicates, and alias IDs (e.g. `~provider/model-latest`).

## sakana/sakana-namazu

- Date: 2026-08-18
- Job: `3d6d4861-fbcc-479c-92a7-5fcbf4ead884`
- Result: `COMPLETE_INVALID` — 150/150 `PROVIDER_ERROR`
- Cause: OpenRouter HTTP 404, "No endpoints available matching your guardrail restrictions and data policy."
- Why not repair: every question failed the same way. Default repair cap is 5. This is a provider-availability block, not flaky rows.

## meta/muse-spark-1.2-contributor

- Date: 2026-08-24
- Job: `7e614873-90c7-4552-918f-bac3d8481fc0`
- Result: `COMPLETE_INVALID` — 150/150 `PROVIDER_ERROR`
- Cause: OpenRouter HTTP 404, "No endpoints available matching your guardrail restrictions and data policy."
- Why not repair: every question failed the same way. Default repair cap is 5. This is a provider-availability block, not flaky rows.

## Tencent Hy-MT2 (translation-only)

Not GCB candidates. Translation specialists. Do not test unless Chris overrides.

- `tencent/hy-mt2-1.8b`
- `tencent/hy-mt2-7b`
- `tencent/hy-mt2-30b-a3b`

2026-08-31 MWF started them because they were not on this list. Jobs cancelled (not uploaded):

- `fb9f60d7-4664-46e7-a1dd-841b3594702d` hy-mt2-1.8b
- `017632ed-1baa-4095-b5a5-599f85d3bfc2` hy-mt2-30b-a3b
- `f186e81b-e906-4771-a22f-d25f9378f11b` hy-mt2-7b

## meta/muse-spark-1.3-contributor

- Date: 2026-09-04
- Job: `2687fe1c-ec12-4254-ba81-8549e0777500`
- Result: `COMPLETE_INVALID` — 150/150 `PROVIDER_ERROR`
- Cause: OpenRouter HTTP 404, "No endpoints available matching your guardrail restrictions and data policy."
- Why not repair: every question failed the same way. Default repair cap is 5. This is a provider-availability block, not flaky rows. Same pattern as `meta/muse-spark-1.2-contributor`.
