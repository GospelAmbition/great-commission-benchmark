# GCB Agent Routing

This repository is for the Great Commission Benchmark (GCB). When the user says
`gcb`, assume they mean Great Commission Benchmark context unless they clearly
refer to something else.

## Benchmark Test Shorthand

When the user asks to run a GCB test or benchmark on a model, treat the model
string as an OpenRouter model id and route directly to the GCB MCP tools. Do not
search the repository first.

Examples:

- `run a gcb test on microsoft/wizardlm-2-8x22b`
- `gcb test microsoft/wizardlm-2-8x22b`
- `benchmark microsoft/wizardlm-2-8x22b`
- `run benchmark test on microsoft/wizardlm-2-8x22b`

Use this workflow:

1. Call `run_gcb_test(model_id="<model_id>")` when available.
2. If `run_gcb_test` is unavailable, call `check_ready_for_testing(auto_launch=true)`.
3. If OpenRouter is ready, call `start_gcb_test(model_id="<model_id>")`.
4. Report the returned `job_id`, `status`, `model_id`, and `log_path`.
5. Tell the user the run continues in the background and can be checked with
   `get_job_status(job_id)`.

Preserve exact model ids, including slashes, punctuation, and provider prefixes.

## Readiness Shorthand

When the user says `gcb check`, `gcb ready`, `gcb readiness`, or `gcb status` in
benchmark context, call `check_ready_for_testing(auto_launch=true)` immediately
and report `ready`, `openrouter`, `gcb_api`, `judge_backend`, and `judge_model`.
