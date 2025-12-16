# Legal & Compliance Requirements

This document outlines the legal, accessibility, and internationalization requirements for the Great Commission Benchmark platform.

---

## Legal Documents

### Status

Legal documents are **planned but not yet drafted**. These must be completed before public launch.

### Required Documents

| Document | Purpose | Status |
|----------|---------|--------|
| **Terms of Service** | Define user rights and obligations | To be written |
| **Privacy Policy** | Explain data collection and use | To be written |
| **Liability Disclaimers** | Limit legal exposure | To be written |
| **Tester Agreement** | Question confidentiality terms | To be written |

---

## Terms of Service (ToS)

### Key Elements to Include

1. **Service Description**
   - What the benchmark is and isn't
   - Informational purposes statement
   - Not an endorsement of any model

2. **User Obligations**
   - Accurate information
   - Compliance with tester agreement
   - Acceptable use

3. **Payment Terms**
   - Pricing transparency
   - Refund policy (see [process-pricing-model.md](./process-pricing-model.md))
   - No guarantee of specific results

4. **Intellectual Property**
   - Benchmark methodology ownership
   - User-submitted data rights
   - Open source code licensing

5. **Limitation of Liability**
   - "As is" service provision
   - No warranty of fitness for purpose
   - Maximum liability caps

6. **Dispute Resolution**
   - Governing law (jurisdiction TBD)
   - Dispute process

### Key Disclaimers

The ToS should prominently include:

> "This benchmark is for **informational purposes only** and does not constitute an endorsement or recommendation of any AI model or service."

> "Results reflect performance on specific test questions at a point in time and may not predict performance on other tasks or future model versions."

> "The Great Commission Benchmark is an independent project and is not affiliated with any AI company or model provider."

---

## Privacy Policy

### Data Collection

| Data Type | Collected | Purpose |
|-----------|-----------|---------|
| Email address | Yes | Account, notifications |
| Name | Optional | Display on contributions |
| Payment info | Via Stripe | Process payments |
| Test results | Yes | Leaderboard publication |
| Model responses | Yes | Verification, research |

### Data Sharing

| Recipient | What's Shared | Purpose |
|-----------|---------------|---------|
| Public | Aggregate results | Leaderboard |
| Researchers | Anonymized data | On request |
| Model providers | Their model's results | Transparency |
| Moderators | Full test data | Verification |

### Data Retention

- **Test data:** Indefinite (see [core-deployment-vision.md](./core-deployment-vision.md))
- **User accounts:** Until deletion requested
- **Payment records:** As required by law

### User Rights

- Access their data
- Request deletion (except published results)
- Opt out of optional communications

---

## Liability Disclaimers

### Key Protections

1. **No Warranty**
   - Benchmark provided "as is"
   - No guarantee of accuracy
   - No guarantee of availability

2. **Results Disclaimer**
   - Results are informational
   - Not advice or recommendation
   - Users make own decisions

3. **Third-Party Services**
   - Not responsible for OpenRouter/model issues
   - Not responsible for Stripe issues
   - Links to external sites disclaimed

4. **Limitation of Damages**
   - Cap liability at fees paid
   - No consequential damages
   - No liability for model provider actions

---

## Tester Agreement

### Confidentiality Terms

Testers must agree to:

| Obligation | Description |
|------------|-------------|
| No public sharing | Cannot post questions online |
| No provider sharing | Cannot share with AI companies |
| No training use | Cannot use questions to train models |
| Report leaks | Must report suspected breaches |

### Enforcement

| Violation Level | Response |
|-----------------|----------|
| Minor/accidental | Warning, re-confirm agreement |
| Major/deliberate | Access revocation |
| Severe/malicious | Permanent ban, possible public disclosure |

---

## Accessibility

### Target Standard

**WCAG Level A compliance** (at best)

This is the minimum accessibility standard, not Level AA or AAA.

### Level A Requirements

| Requirement | Implementation |
|-------------|----------------|
| **Text alternatives** | Alt text for images |
| **Keyboard navigation** | All functions keyboard-accessible |
| **No seizure triggers** | No flashing content |
| **Page titles** | Descriptive titles |
| **Link purpose** | Clear link text |
| **Language** | Page language specified |

### What's NOT Guaranteed

Level A does not require:
- Full color contrast compliance (Level AA)
- Captions for live audio (Level AA)
- Extended audio descriptions (Level AAA)
- Sign language interpretation (Level AAA)

### Implementation Notes

- Use semantic HTML
- Include skip links
- Ensure form labels
- Test with screen reader (basic)
- Validate with automated tools (WAVE, Lighthouse)

---

## Internationalization (i18n)

### Current Status

**Multilingual is desired** but not immediate.

### Rationale

The benchmark serves a global Great Commission audience:
- Missionaries worldwide
- Non-English-speaking churches
- International ministries

### Planned Approach

| Phase | Scope |
|-------|-------|
| **Launch** | English only |
| **Future** | Add major languages based on demand |

### Implementation Considerations

1. **Question Sets**
   - May need translated versions
   - Or may keep English-only for consistency
   - Translation quality is critical

2. **UI/Website**
   - Build with i18n framework from start
   - Extract strings for translation
   - Support RTL languages if needed

3. **Results**
   - Language of test noted in results
   - Cross-language comparison considerations

### Priority Languages (TBD)

Based on Great Commission community needs:
- Spanish
- Portuguese
- French
- Chinese (Simplified/Traditional)
- Arabic
- Hindi

---

## Timeline

### Pre-Launch Requirements

| Item | Priority | Status |
|------|----------|--------|
| Terms of Service | Required | Not started |
| Privacy Policy | Required | Not started |
| Liability disclaimers | Required | Not started |
| Tester Agreement | Required | Not started |
| WCAG Level A | Required | Not started |

### Post-Launch

| Item | Priority | Status |
|------|----------|--------|
| Multilingual UI | Desired | Future |
| Multilingual questions | Desired | Future |
| WCAG Level AA | Nice to have | Future |

---

## Legal Review

### Recommendation

Before launch:
- Have ToS/Privacy Policy reviewed by legal counsel
- Ensure compliance with applicable laws
- Verify liability protections are adequate

### Jurisdiction Considerations

- **Service location:** TBD (likely US-based)
- **User location:** Global
- **Data storage:** US (Railway)
- **GDPR implications:** May apply to EU users

---

## Related Documents

- [Deployment Vision](./core-deployment-vision.md) — Overall deployment strategy
- [Pricing Model](./process-pricing-model.md) — Payment and refund policies
- [Question Security](./process-question-security.md) — Tester agreement details

