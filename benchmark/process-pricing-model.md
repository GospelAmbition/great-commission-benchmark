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

1. **Input token cost** — Calculate based on question token count × model input cost per token
2. **Output token cost** — Estimate average output token count × model output cost per token, plus 10% margin for variability
3. **Benchmark hosting contribution** — Fixed $20 contribution to cover benchmark hosting and infrastructure
4. **Optional round-up** — User can optionally round up to support the initiative
5. **Display total** — User sees final price upfront

### Cost Components

| Component | Description | Variability |
|-----------|-------------|-------------|
| **Input Token Costs** | Question token count × model input cost per token | Variable by model and question length |
| **Output Token Costs** | Estimated output tokens × model output cost per token + 10% margin | Variable by model |
| **Benchmark Hosting** | Fixed contribution for infrastructure and operations | Fixed $20 per test |
| **Round-up (optional)** | Optional contribution to support the initiative | User's choice |

---

## Pricing Display

### Simplified View (Default)

```
─────────────────────────────────────────
  Test: Claude 3.5 Sonnet (Full Benchmark)
─────────────────────────────────────────
  Input Tokens (12,500 × $0.003)  $37.50
  Output Tokens (est. 8,000)      $24.00
  ─────────────────────────────────────
  API Cost Subtotal               $61.50
  Benchmark Hosting Contribution  $20.00
  ─────────────────────────────────────
  Subtotal                        $81.50
  
  💡 Round up to support the initiative (optional)
     ○ Round to $85   ○ Round to $90   ○ Round to $100
  ─────────────────────────────────────
  Total                           $81.50
─────────────────────────────────────────
```

### Detailed View (On Request)

```
─────────────────────────────────────────
  Test: Claude 3.5 Sonnet (Full Benchmark)
─────────────────────────────────────────
  Input Tokens (12,500 × $0.003)  $37.50
  Output Tokens (est. 8,000)      $24.00
  Output Margin (10%)              $2.40
  ─────────────────────────────────────
  API Cost Subtotal               $63.90
  Benchmark Hosting Contribution  $20.00
  ─────────────────────────────────────
  Subtotal                        $83.90
  
  💡 Round up to support the initiative (optional)
     ○ Round to $85   ○ Round to $90   ○ Round to $100
  ─────────────────────────────────────
  Total                           $83.90
─────────────────────────────────────────
```

---

## Benchmark Hosting Contribution

The $20 benchmark hosting contribution covers:

| Category | Includes |
|----------|----------|
| **Infrastructure** | Server compute, database storage, hosting platform costs |
| **Operations** | Moderation review, result processing, system maintenance |
| **Platform Services** | Payment processing fees, authentication, email services |

### Contribution Determination

**Starting Cost:** $20 is confirmed as the beginning cost for the benchmark hosting contribution. This amount may be adjusted later based on operational needs, but $20 is the starting cost.

The fixed $20 contribution is based on:

1. **Infrastructure costs** — Estimated monthly hosting and platform service costs
2. **Operational overhead** — Time and resources for moderation and processing
3. **Sustainability** — Ensures benchmark platform remains cost-neutral

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

1. **10% margin** built into output token estimates
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
- **Round-up contributions** at checkout (supports the initiative)
- **Direct sponsorship** of specific tests/models
- **General fund** donations for accessibility

---

## Refund Policy

### When Refunds Are Available

| Situation | Refund Available | Notes |
|-----------|------------------|-------|
| Test failed after 3 auto-retry attempts | Yes (user choice) | User can choose refund OR wait for admin completion |
| User chooses refund over admin completion | Yes | Full refund, partial results discarded |
| Admin unable to complete test | Yes | Full refund after admin review |
| Test stuck in error state | Yes | After investigation |
| User reports issue before completion | Yes | Case-by-case basis |
| Test completed successfully | No | — |
| User unhappy with results | No | — |

### Refund Process

**Automatic Refund Path (User-Initiated):**
1. After 3 failed retry attempts, user is given choice
2. If user selects "Request refund now"
3. Refund processed automatically through Stripe
4. User notified via email
5. Partial results marked as "refunded" (not published)

**Manual Refund Path (Admin-Initiated):**
1. User chooses to wait for admin completion
2. Admin investigates and attempts completion
3. If admin cannot complete, admin initiates refund
4. Refund processed through Stripe
5. User notified with explanation

### Automatic Recovery System

The system includes a robust checkpoint and recovery mechanism that handles errors transparently:

**Checkpoint System:**
- Progress saved after each question (responses, verdicts, metadata)
- On any error, system resumes from last checkpoint—NOT from the beginning
- Users are not re-charged for completed work

**Automatic Retry (Transparent to User):**
- API errors → retry with exponential backoff (30s → 60s → 120s)
- Timeouts → retry with extended timeout
- Rate limiting → queue and retry later
- Up to **3 retry attempts** before escalating

**Admin Escalation (After 3 Failed Attempts):**
When automatic recovery fails 3 times:
1. System notifies administrator(s) immediately
2. User is presented with two options:
   - **Wait for admin completion**: An administrator manually completes the remaining portion of the test (typical resolution: 24-48 hours)
   - **Request immediate refund**: Full refund processed, partial results discarded

**Admin Completion Process:**
- Admin reviews the failure cause
- Admin manually runs remaining questions (possibly with different API configuration)
- Results are merged with previously completed portion
- User notified when complete, results enter normal moderation queue

---

## Financial Sustainability

### Revenue Sources

| Source | Description |
|--------|-------------|
| **Test fees** | Benchmark hosting contribution per benchmark run |
| **Round-up contributions** | Optional contributions at checkout |
| **Sponsorships** | Funding tests for others |
| **Donations** | General fund contributions |

### Cost Coverage

| Cost Category | Covered By |
|---------------|------------|
| **API costs** | Pass-through to user (input + output tokens) |
| **Infrastructure** | Benchmark hosting contribution + sponsoring project |
| **Moderation** | Volunteer (no direct cost) |
| **Development** | Initial grant/volunteer time |

### Break-Even Goal

The pricing model aims to **break even**, not profit:
- Benchmark hosting contribution covers operational costs
- Round-up contributions and donations provide buffer
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
| API costs (input + output tokens) | $5-50 depending on model and question length |
| Benchmark hosting contribution | $20 per test (fixed) |

---

## Future Considerations

### Price Adjustments

Benchmark hosting contribution may be adjusted based on:
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

