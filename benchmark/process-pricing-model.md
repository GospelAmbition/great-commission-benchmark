# Pricing Model

This document defines the financial model for the Great Commission Benchmark, including cost structure, payment processing, and sustainability approach.

---

## Guiding Principles

1. **Not-for-profit, but cost-neutral** — The project doesn't aim to profit, but must cover its own costs sustainably
2. **Transparency** — Users see exactly what they're paying for
3. **Accessibility** — Low barriers for students, missionaries, and those in developing countries
4. **Community-funded** — Sponsorship and donations subsidize the system

---

## Cost Structure

### Pricing Approach

**Fixed price commitment** — Users are shown and charged a set price before execution. No post-run settlement or surprise charges.

### Cost Estimation Method

1. **Bridge token calculation** — Estimate API costs based on expected token usage
2. **Add 10% buffer** — Cover potential retries or failed runs
3. **Add processing fee** — Cover infrastructure and operations
4. **Display total** — User sees final price upfront

### Cost Components

| Component | Description | Variability |
|-----------|-------------|-------------|
| **API Costs** | OpenRouter/LLM token charges | Variable by model |
| **Processing Fee** | Server compute + platform operations | Fixed per test |
| **Tip (optional)** | Voluntary contribution | User's choice |

---

## Pricing Display

### Simplified View (Default)

```
─────────────────────────────────────────
  Test: Claude 3.5 Sonnet (Full Benchmark)
─────────────────────────────────────────
  API Cost (OpenRouter)         $12.40
  Processing Fee                 $2.50
  ─────────────────────────────────────
  Subtotal                      $14.90
  
  💡 Help with server & hosting costs (optional)
     ○ $5   ○ $10   ○ $20   ○ $100
  ─────────────────────────────────────
  Total                         $14.90
─────────────────────────────────────────
```

### Detailed View (On Request)

```
─────────────────────────────────────────
  Test: Claude 3.5 Sonnet (Full Benchmark)
─────────────────────────────────────────
  API Cost (OpenRouter)         $12.40
  CPU Processing Cost             $1.20
  Administration Cost             $1.30
  ─────────────────────────────────────
  Subtotal                      $14.90
  
  💡 Help with server & hosting costs (optional)
     ○ $5   ○ $10   ○ $20   ○ $100
  ─────────────────────────────────────
  Total                         $14.90
─────────────────────────────────────────
```

---

## Processing Fee Breakdown

The processing fee (initially estimated ~$2.50, subject to cost study) covers:

| Category | Includes |
|----------|----------|
| **CPU Processing** | Server compute for benchmark execution, evaluation logic, result generation |
| **Administration** | Moderation review, result processing, database storage, infrastructure maintenance |
| **Buffer** | ~10% margin for retries and unexpected costs |

### Fee Determination

The initial $2.50 figure was a **draft placeholder**. Final pricing requires:

1. **Cost study** — Actual API usage, infrastructure costs, Stripe fees
2. **Processing effort** — Time and resources for operations
3. **Sustainability check** — Ensure costs are covered with reasonable margin

---

## Payment Processing

### Payment Provider

**Stripe** handles all payments:
- Industry standard
- Supports credit cards, various payment methods
- Handles currency conversion
- PCI compliant

### Stripe Fees

Standard Stripe fees (absorbed in processing fee, not added separately):
- 2.9% + $0.30 per successful transaction (US)
- Additional fees for international cards

### Financial Steward

Payments flow to a **stewarding ministry** that manages finances and pays for services/infrastructure.

**Candidates (TBD):**
- Visual Story Network
- Digital Disciple Makers Network
- Gospel Ambition

The stewarding ministry:
- Receives Stripe payments
- Pays infrastructure costs (Railway, OpenRouter, etc.)
- Manages accounting and reporting
- Provides tax-deductible receipts where applicable

---

## Cost Overrun Handling

### Who Absorbs Overruns

If actual API costs exceed estimates:
- **Steering committee** absorbs the difference
- A sponsoring project covers infrastructure costs
- Pricing includes margin above actual costs

### Mitigation Strategies

1. **10% buffer** built into estimates
2. **Token limits** on model responses if needed
3. **Price adjustment** for consistently underpriced models
4. **Monitoring** to catch cost patterns early

---

## Sponsorship & Accessibility

### For Those Who Can't Pay

Users who cannot afford testing can submit a **sponsorship request form**:

| Field | Purpose |
|-------|---------|
| **Model requested** | Which model they want tested |
| **Justification** | Why there's a good need for it to be tested |
| **Context** | Their ministry/organization/situation |

The steering committee or community sponsors can fund tests on their behalf.

### How Sponsorship Works

1. User submits sponsorship request
2. Request reviewed by steering committee
3. If approved, added to sponsor funding queue
4. Community members can browse and fund requests
5. User notified when their test is sponsored
6. Test runs with standard workflow

### Community Sponsorship

Users can voluntarily contribute:
- **Tips** at checkout (helps server & hosting)
- **Direct sponsorship** of specific tests/models
- **General fund** donations for accessibility

---

## Refund Policy

### When Refunds Are Available

| Situation | Refund Available |
|-----------|------------------|
| Test failed to complete | Yes |
| Test stuck in error state | Yes |
| User reports issue before completion | Yes |
| Test completed successfully | No |
| User unhappy with results | No |

### Refund Process

1. User reports issue via support form
2. System verifies test status (failed/incomplete)
3. Refund processed through Stripe
4. User notified of refund

### Automatic Retries

Before refunds, the system attempts automatic retry:
- API errors → retry with backoff
- Timeouts → retry with extended timeout
- Rate limiting → queue and retry later

---

## Financial Sustainability

### Revenue Sources

| Source | Description |
|--------|-------------|
| **Test fees** | Processing fee per benchmark run |
| **Tips** | Optional contributions at checkout |
| **Sponsorships** | Funding tests for others |
| **Donations** | General fund contributions |

### Cost Coverage

| Cost Category | Covered By |
|---------------|------------|
| **API costs** | Pass-through to user |
| **Infrastructure** | Processing fees + sponsoring project |
| **Moderation** | Volunteer (no direct cost) |
| **Development** | Initial grant/volunteer time |

### Break-Even Goal

The pricing model aims to **break even**, not profit:
- Processing fees cover operational costs
- Tips and donations provide buffer
- Sponsoring project backstops shortfalls

---

## Estimated Costs

### Infrastructure (Monthly)

| Service | Estimated Cost |
|---------|----------------|
| Railway hosting | < $20/month |
| Database (Postgres) | Included in Railway |
| Auth0 | Free tier (up to 7,000 users) |
| Domain/DNS | ~$15/year |
| Email service | Free tier or minimal |

### Per-Test (Variable)

| Component | Range |
|-----------|-------|
| API costs | $5-50 depending on model |
| Processing | ~$1-2 per test |

---

## Future Considerations

### Price Adjustments

Processing fee may be adjusted based on:
- Actual cost data after launch
- Volume changes
- Infrastructure cost changes
- Community feedback

### Volume Discounts

If demand increases, consider:
- Bulk pricing for organizations
- Subscription options for frequent testers
- Reduced fees for verified ministries

---

## Related Documents

- [Deployment Vision](./platform-deployment-vision.md) — Overall deployment strategy
- [Technical Architecture](./platform-technical-architecture.md) — Infrastructure decisions
- [Success Metrics](./process-success-metrics.md) — KPIs including financial sustainability

