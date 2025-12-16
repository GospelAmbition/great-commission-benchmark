# Technical Architecture

This document defines the infrastructure decisions for the Great Commission Benchmark platform.

---

## Stack Overview

| Component | Technology | Rationale |
|-----------|------------|-----------|
| **API Backend** | Python + FastAPI | Matches existing pipeline code; handles benchmark execution |
| **Frontend** | React + Next.js + Tailwind | SSR/SSG for SEO; modern DX; popular ecosystem |
| **Hosting** | Railway | Familiar stack, cost bundling with other projects |
| **Authentication** | Auth0 | Industry-standard OAuth, free tier available |
| **Database** | PostgreSQL | Already in use for pipeline; robust and reliable |
| **LLM Access** | OpenRouter | Single API for 100+ models; pay-per-use |
| **Payments** | Stripe | Industry standard; handles cards and compliance |

---

## Why Railway

### Reasons for Selection

1. **Familiarity** — Preferred stack from prior experience
2. **Cost bundling** — Already part of other projects, infrastructure costs bundled
3. **Simple deployment** — Good Python/Node support
4. **Reasonable pricing** — Cost-effective for low-traffic projects

### Alternatives Considered

| Platform | Notes |
|----------|-------|
| **Render** | Most similar DX to Railway |
| **Fly.io** | Global edge deployment |
| **Vercel** | Next.js optimized, but backend limitations |
| **Cloud Run** | Google Cloud, more complex setup |
| **DigitalOcean App Platform** | Good alternative, different pricing model |

### Migration Path

If Railway becomes unsuitable (pricing changes, shutdown, issues):
- Standard containerized deployment
- Migrate to Render, Fly.io, or other container platforms
- No vendor lock-in on core architecture

---

## Why OpenRouter

### Reasons for Selection

1. **Single API** — Access 100+ models through one interface
2. **Pay-per-use** — No subscriptions, pay only for tokens used
3. **Consistent interface** — Simplifies testing pipeline
4. **Community sponsorship** — Anyone can sponsor tests of any available model

### API Format Compatibility

Built following the **OpenAI API format** (the de facto standard):
- Portable to other providers
- Can add direct API integrations as needed
- Not hard-locked to OpenRouter

### Fallback Strategy

If OpenRouter has significant downtime or discontinues service:
1. **Primary fallback** — Direct API integrations (OpenAI, Anthropic, etc.)
2. **Alternative aggregators** — Together.ai, Replicate
3. **Architecture support** — System designed to support multiple providers

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     Public Website (Next.js)                     │
│                    SSR / SSG / React SPA                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────────┐ │
│  │Leaderboard│  │Model     │  │Category  │  │Community        │ │
│  │Dashboard │  │Comparison│  │Deep-Dive │  │(Newsletter, etc)│ │
│  └──────────┘  └──────────┘  └──────────┘  └──────────────────┘ │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │              Next.js API Routes (light tasks)               │ │
│  │      Auth callbacks · Simple queries · Newsletter signup    │ │
│  └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                 FastAPI Backend (Heavy Lifting)                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────────┐ │
│  │Results   │  │Benchmark │  │Result    │  │Moderation        │ │
│  │API       │  │Executor  │  │Processing│  │Workflows         │ │
│  └──────────┘  └──────────┘  └──────────┘  └──────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
        ┌──────────┐   ┌──────────┐   ┌──────────────┐
        │PostgreSQL│   │OpenRouter│   │Auth0         │
        │(Results) │   │(LLM API) │   │(Identity)    │
        └──────────┘   └──────────┘   └──────────────┘
                              │
                              ▼
                       ┌──────────┐
                       │ Stripe   │
                       │(Payments)│
                       └──────────┘
```

---

## Backend Responsibilities

### Next.js (Node.js)

| Responsibility | Description |
|----------------|-------------|
| Page rendering | SSR/SSG for leaderboards, model pages |
| Auth callbacks | Handle Auth0 redirects |
| Light queries | Simple data fetches for UI |
| Static assets | Serve images, CSS, JS |
| Newsletter signup | Simple form submissions |
| Simple CRUD | Basic data operations |

### FastAPI (Python)

| Responsibility | Description |
|----------------|-------------|
| Benchmark execution | Run the full testing pipeline |
| LLM API calls | Communicate with OpenRouter |
| Heavy computation | Evaluation logic, result processing |
| Database writes | Store results, verdicts, responses |
| Moderation workflows | Handle review queues and escalations |
| Payment processing | Stripe integration for charges |

---

## Database Design

### Core Tables

```
┌────────────────┐     ┌────────────────┐     ┌────────────────┐
│ Users          │     │ TestRuns       │     │ Results        │
├────────────────┤     ├────────────────┤     ├────────────────┤
│ id             │────▶│ user_id        │     │ test_run_id    │
│ auth0_id       │     │ model_id       │     │ question_id    │
│ email          │     │ question_set_id│     │ response       │
│ role           │     │ status         │     │ verdict        │
│ created_at     │     │ created_at     │     │ reasoning      │
└────────────────┘     │ completed_at   │     └────────────────┘
                       │ payment_id     │
                       └────────────────┘

┌────────────────┐     ┌────────────────┐     ┌────────────────┐
│ QuestionSets   │     │ Questions      │     │ ModerationLogs │
├────────────────┤     ├────────────────┤     ├────────────────┤
│ id             │────▶│ question_set_id│     │ test_run_id    │
│ version        │     │ content        │     │ moderator_id   │
│ status         │     │ category       │     │ action         │
│ created_at     │     │ tier           │     │ notes          │
│ locked_at      │     └────────────────┘     │ created_at     │
└────────────────┘                            └────────────────┘
```

### Data Characteristics

- **All text data** — No heavy media or binary storage
- **Low volume** — ~600 tests/models maximum anticipated
- **Simple queries** — Leaderboard aggregations, filtering

---

## Backup & Recovery

### Two-Tier Strategy

| Tier | Provider | Frequency | Purpose |
|------|----------|-----------|---------|
| **Primary** | Railway | Automated/daily | Regular operational backup |
| **Secondary** | Google Cloud Bucket (TBD) | Occasional/weekly | Redundancy across providers |

### Why Two Tiers

- **Primary (Railway):** Handles day-to-day backup needs automatically
- **Secondary (external):** Protects against Railway-specific issues (outage, shutdown, data loss)

### Recovery Expectations

- **RPO (Recovery Point Objective):** < 24 hours data loss acceptable
- **RTO (Recovery Time Objective):** < 4 hours to restore service

---

## Capacity & Scaling

### Expected Load

| Metric | Expectation |
|--------|-------------|
| **Submissions per month** | ~2 |
| **Total submissions** | ~600 lifetime |
| **Concurrent tests** | 1-2 typical |
| **Peak concurrent** | Maybe 5-10 |

### Capacity Assessment

| Component | Capacity | Assessment |
|-----------|----------|------------|
| **Railway** | Handles moderate traffic | More than sufficient |
| **OpenRouter** | No simultaneous call limits | No concerns |
| **PostgreSQL** | Millions of rows | Vastly oversized |
| **Auth0 free tier** | 7,000 users | Sufficient for years |

### Scaling Strategy

Given low expected traffic:
- **No queue system initially** — Direct execution
- **Add queue if needed** — If concurrent demand exceeds capacity
- **Railway autoscaling** — Can handle spikes automatically

---

## Security Considerations

### Authentication

- **Auth0** handles all authentication
- **OAuth/social login** support
- **Role-based access** (user, moderator, admin)
- **API tokens** for programmatic access

### API Security

- **HTTPS only** — All traffic encrypted
- **Rate limiting** — Prevent abuse
- **Input validation** — FastAPI automatic validation
- **SQL injection protection** — ORM parameterized queries

### Question Security

- **Server-side only** — Questions never sent to client browser
- **Authenticated access** — Only registered testers
- **Audit logging** — Track all question access

### Payment Security

- **Stripe handles PCI compliance** — No card data on our servers
- **Webhook verification** — Validate Stripe events
- **Idempotency** — Prevent double charges

---

## Monitoring & Observability

### Logging

| What | Where |
|------|-------|
| Application logs | Railway built-in |
| Error tracking | Sentry (optional) |
| API request logs | FastAPI middleware |
| Moderation activity | Database |

### Metrics

| Metric | Purpose |
|--------|---------|
| Test completion rate | Track failures |
| Response times | Performance monitoring |
| API costs per test | Cost tracking |
| Moderation queue depth | Workflow health |

### Alerting

- **Test failure spikes** — Email to admins
- **Payment failures** — Immediate notification
- **Infrastructure issues** — Railway notifications

---

## Development Workflow

### Environments

| Environment | Purpose | Hosting |
|-------------|---------|---------|
| **Local** | Development | Developer machine |
| **Staging** | Testing | Railway (separate project) |
| **Production** | Live | Railway |

### Deployment

- **Git-based** — Push to main deploys to production
- **Preview deploys** — PRs get temporary environments
- **Database migrations** — Run automatically on deploy

---

## Cost Estimates

### Monthly Infrastructure

| Service | Estimated Cost |
|---------|----------------|
| Railway (hobby plan) | ~$5-20 |
| Database | Included |
| Auth0 | Free tier |
| Domain | ~$1 (amortized) |
| **Total** | **< $20/month** |

### Per-Test Variable

| Component | Cost |
|-----------|------|
| OpenRouter API | $5-50 (model dependent) |
| Compute time | ~$0.10-0.50 |

---

## Related Documents

- [Deployment Vision](./decision-deployment-vision.md) — Overall deployment strategy
- [Pricing Model](./core-pricing-model.md) — Financial model
- [Question Security](./core-question-security.md) — Question protection

