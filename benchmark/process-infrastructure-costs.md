# Infrastructure Costs

This document provides detailed cost estimates for running the Great Commission Benchmark platform, including infrastructure, model testing, and projections at different traffic levels.

---

## Monthly Infrastructure Costs

| Service | Estimated Cost |
|---------|----------------|
| Railway (hobby plan) | ~$5-20 |
| Database | Included |
| Auth0 | Free tier |
| Domain | ~$1 (amortized) |
| **Total** | **< $20/month** |

### Notes

- **Railway**: Hobby plan pricing varies based on usage; typically $5-20/month for low-traffic applications
- **Database**: PostgreSQL included with Railway hosting
- **Auth0**: Free tier supports up to 7,000 users, sufficient for years of operation
- **Domain**: Annual domain registration amortized monthly

---

## Per-Test Variable Costs

| Component | Cost Range |
|-----------|------------|
| OpenRouter API | $0.05 - $203.49 (model dependent) |
| Compute time | ~$0.10-0.50 |

### Cost Breakdown

- **OpenRouter API**: Varies significantly by model (see detailed model pricing below)
- **Compute time**: Railway compute costs for running the benchmark pipeline

---

## Project Contribution: Monthly Model Tests

The project will contribute **5 model tests per month** to demonstrate platform capabilities and maintain an active leaderboard.

### Cost Estimate

| Metric | Value |
|--------|-------|
| Tests per month | 5 |
| Cost per test (budget models) | ~$0.50 |
| **Monthly cost** | **~$2.50** |

### Notes

- Uses budget models (e.g., Gemma, Mistral Small) to minimize costs while maintaining leaderboard activity
- Budget models cost ~$0.05-0.20 per test, averaging ~$0.50 per test
- Premium models (GPT-4, Claude Opus) would cost $18-200+ per test but are not used for project contributions
- Models are rotated monthly to showcase different options while keeping costs low

---

## Model Pricing: Top 30 Models

Cost estimates based on OpenRouter API pricing (as of January 2025). Assumes **90,000 input tokens** (~300 per question) and **1,200,000 output tokens** (~4,000 per question) per test run (300 questions).

| # | Model | Model ID | Prompt Price | Completion Price | Cost per Test |
|---|-------|----------|--------------|------------------|---------------|
| 1 | Google: Gemma 3n 4B | `google/gemma-3n-e4b-it` | $0.00000002 | $0.00000004 | $0.05 |
| 2 | Mistral: Mistral Nemo | `mistralai/mistral-nemo` | $0.00000002 | $0.00000004 | $0.05 |
| 3 | Google: Gemma 3 4B | `google/gemma-3-4b-it` | $0.000000017 | $0.000000068 | $0.08 |
| 4 | Mistral: Mistral 7B Instruct | `mistralai/mistral-7b-instruct` | $0.000000028 | $0.000000054 | $0.07 |
| 5 | Mistral: Ministral 3B | `mistralai/ministral-3b` | $0.00000004 | $0.00000004 | $0.05 |
| 6 | DeepSeek: DeepSeek R1 0528 Qwen3 8B | `deepseek/deepseek-r1-0528-qwen3-8b` | $0.00000002 | $0.0000001 | $0.12 |
| 7 | Google: Gemma 2 9B | `google/gemma-2-9b-it` | $0.00000003 | $0.00000009 | $0.11 |
| 8 | Google: Gemma 3 12B | `google/gemma-3-12b-it` | $0.00000003 | $0.0000001 | $0.12 |
| 9 | Mistral: Mistral Small 3.1 24B | `mistralai/mistral-small-3.1-24b-instruct` | $0.00000003 | $0.00000011 | $0.13 |
| 10 | Mistral: Mistral Small 3 | `mistralai/mistral-small-24b-instruct-2501` | $0.00000003 | $0.00000011 | $0.13 |
| 11 | DeepSeek: R1 Distill Llama 70B | `deepseek/deepseek-r1-distill-llama-70b` | $0.00000003 | $0.00000013 | $0.16 |
| 12 | OpenAI: gpt-oss-20b | `openai/gpt-oss-20b` | $0.00000003 | $0.00000014 | $0.17 |
| 13 | Cohere: Command R7B (12-2024) | `cohere/command-r7b-12-2024` | $0.0000000375 | $0.00000015 | $0.18 |
| 14 | OpenAI: gpt-oss-120b | `openai/gpt-oss-120b` | $0.000000039 | $0.00000019 | $0.23 |
| 15 | OpenAI: gpt-oss-120b (exacto) | `openai/gpt-oss-120b:exacto` | $0.000000039 | $0.00000019 | $0.23 |
| 16 | OpenAI: ChatGPT-4o | `openai/chatgpt-4o-latest` | $0.000005 | $0.000015 | $18.45 |
| 17 | OpenAI: GPT-5 Image | `openai/gpt-5-image` | $0.00001 | $0.00001 | $12.90 |
| 18 | OpenAI: GPT-4o (extended) | `openai/gpt-4o:extended` | $0.000006 | $0.000018 | $22.14 |
| 19 | Anthropic: Claude Opus 4.5 | `anthropic/claude-opus-4.5` | $0.000005 | $0.000025 | $30.45 |
| 20 | Anthropic: Claude 3.5 Sonnet | `anthropic/claude-3.5-sonnet` | $0.000006 | $0.00003 | $36.54 |
| 21 | OpenAI: GPT-4 Turbo | `openai/gpt-4-turbo` | $0.00001 | $0.00003 | $36.90 |
| 22 | OpenAI: GPT-4 Turbo Preview | `openai/gpt-4-turbo-preview` | $0.00001 | $0.00003 | $36.90 |
| 23 | OpenAI: GPT-4 Turbo (older v1106) | `openai/gpt-4-1106-preview` | $0.00001 | $0.00003 | $36.90 |
| 24 | Anthropic: Claude Opus 4.1 | `anthropic/claude-opus-4.1` | $0.000015 | $0.000075 | $91.35 |
| 25 | Anthropic: Claude Opus 4 | `anthropic/claude-opus-4` | $0.000015 | $0.000075 | $91.35 |
| 26 | Anthropic: Claude 3 Opus | `anthropic/claude-3-opus` | $0.000015 | $0.000075 | $91.35 |
| 27 | OpenAI: GPT-4 (older v0314) | `openai/gpt-4-0314` | $0.00003 | $0.00006 | $74.70 |
| 28 | OpenAI: GPT-4 | `openai/gpt-4` | $0.00003 | $0.00006 | $74.70 |
| 29 | OpenAI: GPT-5 Pro | `openai/gpt-5-pro` | $0.000015 | $0.00012 | $145.35 |
| 30 | OpenAI: GPT-5.2 Pro | `openai/gpt-5.2-pro` | $0.000021 | $0.000168 | $203.49 |

### Pricing Summary

| Metric | Value |
|--------|-------|
| **Total cost (all 30 models)** | **$1,123.48** |
| **Average cost per test** | **$37.45** |
| **Minimum cost** | **$0.05** (smallest models) |
| **Maximum cost** | **$203.49** (GPT-5.2 Pro) |
| **Median cost** | **~$0.15** |

### Notes

- Prices are per token in USD (OpenRouter format)
- Cost per test assumes 90,000 input tokens (~300 per question) + 1,200,000 output tokens (~4,000 per question) for 300 questions
- Actual token usage may vary based on question complexity and response length
- Output tokens dominate costs for most models due to higher volume (1.2M vs 90k)
- Prices updated from OpenRouter API as of January 2025

---

## Projected Costs at Different Traffic Thresholds

**Important:** Users pay for their own test costs. Each user test also contributes **$20 to the hosting account** to cover infrastructure costs. The project only pays for infrastructure and the 5 monthly contribution tests.

### Low Traffic (Current Expectations)

| Metric | Value |
|--------|-------|
| User tests per month | ~2 |
| Project contribution tests | 5 |
| **Total tests per month** | **~7** |
| | |
| **User-Paid Costs** | |
| User test costs (covered by users) | ~$74.90 ($37.45 × 2) |
| | |
| **Project Costs** | |
| Infrastructure | $20/month |
| Project contribution test costs | $2.50 ($0.50 × 5) |
| **Total project costs** | **$22.50/month** |
| | |
| **Income & Profit** | |
| Hosting contributions from users | $40 ($20 × 2) |
| **Net project profit** | **+$17.50/month** |

### Moderate Traffic

| Metric | Value |
|--------|-------|
| User tests per month | ~10 |
| Project contribution tests | 5 |
| **Total tests per month** | **~15** |
| | |
| **User-Paid Costs** | |
| User test costs (covered by users) | ~$374.50 ($37.45 × 10) |
| | |
| **Project Costs** | |
| Infrastructure | $20/month |
| Project contribution test costs | $2.50 ($0.50 × 5) |
| **Total project costs** | **$22.50/month** |
| | |
| **Income & Profit** | |
| Hosting contributions from users | $200 ($20 × 10) |
| **Net project profit** | **+$177.50/month** |

### High Traffic

| Metric | Value |
|--------|-------|
| User tests per month | ~50 |
| Project contribution tests | 5 |
| **Total tests per month** | **~55** |
| | |
| **User-Paid Costs** | |
| User test costs (covered by users) | ~$1,872.50 ($37.45 × 50) |
| | |
| **Project Costs** | |
| Infrastructure | $20/month |
| Project contribution test costs | $2.50 ($0.50 × 5) |
| **Total project costs** | **$22.50/month** |
| | |
| **Income & Profit** | |
| Hosting contributions from users | $1,000 ($20 × 50) |
| **Net project profit** | **+$977.50/month** |

### Very High Traffic

| Metric | Value |
|--------|-------|
| User tests per month | ~200 |
| Project contribution tests | 5 |
| **Total tests per month** | **~205** |
| | |
| **User-Paid Costs** | |
| User test costs (covered by users) | ~$7,490 ($37.45 × 200) |
| | |
| **Project Costs** | |
| Infrastructure | $20-40/month (scaled) |
| Project contribution test costs | $2.50 ($0.50 × 5) |
| **Total project costs** | **$22.50-42.50/month** |
| | |
| **Income & Profit** | |
| Hosting contributions from users | $4,000 ($20 × 200) |
| **Net project profit** | **+$3,957.50-3,977.50/month** |

### Financial Summary by Traffic Level

| Traffic Level | User Tests | Hosting Income | Project Costs | Net Profit/Loss |
|---------------|------------|----------------|---------------|----------------|
| Low (~2 user tests) | 2 | $40 | $22.50 | **+$17.50/month** |
| Moderate (~10 user tests) | 10 | $200 | $22.50 | **+$177.50/month** |
| High (~50 user tests) | 50 | $1,000 | $22.50 | **+$977.50/month** |
| Very High (~200 user tests) | 200 | $4,000 | $22.50-42.50 | **+$3,957.50-3,977.50/month** |

### Notes

- **User-paid costs**: Users cover 100% of their test costs (model API costs). These are not project expenses.
- **Hosting contributions**: Each user test contributes $20 to the hosting account to cover infrastructure costs.
- **Break-even point**: The platform is profitable from the first user test (hosting contribution $20 > project costs $22.50 requires 2+ tests to be profitable).
- **Infrastructure costs**: Remain relatively flat ($20/month) until very high traffic, when they may scale to $40/month.
- **Project contribution**: 5 tests/month is a fixed cost ($2.50/month) regardless of traffic, paid by the project to maintain an active leaderboard. Uses budget models (~$0.50 per test) rather than premium models.
- **Profitability**: The platform becomes profitable at ~11+ user tests per month, with significant profit potential at higher traffic levels.
- **Actual costs will vary based on**:
  - Which models users select (premium vs. budget models have vastly different costs)
  - Actual token usage per test (varies by question complexity and response length)
  - Railway pricing at higher usage levels
  - User payment reliability (some users may not complete payment)

---

## Cost Optimization Strategies

### For Project Contribution Tests

1. **Use budget models** — Select from the lower-cost models ($0.05-0.20 per test)
2. **Rotate models** — Test different models each month to maintain variety
3. **Focus on popular models** — Prioritize models users are likely to test

### For Infrastructure

1. **Monitor Railway usage** — Track actual costs and optimize if needed
2. **Database optimization** — Keep queries efficient to minimize compute
3. **Caching** — Cache results to reduce redundant API calls

### For Users

1. **Model selection guidance** — Provide cost estimates before test submission
2. **Budget options** — Highlight lower-cost models that still perform well
3. **Transparent pricing** — Show exact costs upfront

---

## Related Documents

- [Technical Architecture](./platform-technical-architecture.md) — Infrastructure decisions
- [Pricing Model](./process-pricing-model.md) — User-facing pricing strategy
- [Deployment Vision](./platform-deployment-vision.md) — Overall deployment approach

---

## Data Sources

- **OpenRouter API**: Model pricing fetched from `https://openrouter.ai/api/v1/models` (January 2025)
- **Railway Pricing**: Based on hobby plan estimates
- **Token Estimates**: Based on typical benchmark test requirements (90k input + 1.2M output tokens for 300 questions, assuming ~300 input tokens and ~4,000 output tokens per question)

---

*Last updated: January 2025*
