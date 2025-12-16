# Moderation Process

This document defines how moderators are selected, their responsibilities, and the workflows they follow for reviewing benchmark submissions.

---

## Overview

Moderation is **asynchronous and additive**—it doesn't block publication but increases trust over time. Results publish immediately after automated validation; moderators review afterward.

---

## Traffic Expectations

This is a **low-traffic project** by design:

| Metric | Expectation |
|--------|-------------|
| **Total submissions** | ~600 anticipated overall |
| **Frequency** | ~2 submissions per month at best |
| **Publication timing** | Instant (after automated validation) |
| **Review timing** | Asynchronous (hours to days) |

These low volumes mean:
- Moderation capacity can be sized modestly
- No need to design for high-volume scenarios
- Volunteer moderators can handle the load without burnout

---

## Moderator Role

### Definition

A **moderator** is a user with a special role granting elevated permissions in the system.

### Permissions

Moderators can:
- Access the moderation queue
- Review published submissions
- Provide moderation feedback (verify, flag, or raise concerns)
- View detailed response data for verification
- Access activity logs for their own reviews

Moderators cannot:
- Delete results unilaterally
- Modify scores or verdicts
- Access user payment information
- Override other moderators without escalation

### Account Requirements

Each moderator account includes:
- **Credentials/qualifications on record** — Background, expertise, relevant experience
- **Activity log** — System-tracked history of reviews and actions
- **Contact information** — For committee communication

---

## Moderator Selection

### Selection Authority

Volunteer moderators are selected by a **founding committee**—a small group of initial leaders who guide the benchmark's launch.

### Selection Criteria

Candidates are evaluated on:

| Criterion | What We Look For |
|-----------|------------------|
| **Background & expertise** | Theological education, ministry experience, or technical AI/ML knowledge |
| **Mission interest** | Demonstrated commitment to Great Commission work |
| **Community standing** | Positive reputation in relevant Christian/tech communities |
| **Availability** | Realistic time commitment for review load |
| **Judgment** | Ability to make fair, consistent decisions |

### Selection Process

1. **Nomination** — Committee members or existing moderators nominate candidates
2. **Review** — Committee evaluates candidate against criteria
3. **Invitation** — Approved candidates receive invitation to moderate
4. **Onboarding** — New moderators complete training and guidelines review
5. **Probation** — Initial reviews may be double-checked by experienced moderators

### Ongoing Evaluation

The committee periodically reviews moderator performance:
- Activity levels
- Agreement rates with other moderators
- Concerns raised and their resolution
- Community feedback

---

## Moderation Workflow

### Queue Management

The moderation queue shows:
- Results awaiting first review (prioritized by age)
- Results with one review (seeking second opinion)
- Results flagged with concerns (requiring attention)

### Review Process

1. **Claim a review** — Moderator selects result from queue
2. **Examine sample** — Review 20 randomly selected verdicts
3. **For each verdict:**
   - Read the question and model response
   - Read the LLM-judge's verdict and reasoning
   - Mark as: `Agree` / `Disagree` / `Unsure`
4. **Submit assessment:**
   - `Verified` — Verdicts appear accurate
   - `Concerns` — Significant disagreements need discussion
5. **Add notes** — Document patterns, issues, or observations

### Trust Tier Progression

Reviews accumulate to increase trust:

| Reviews Completed | Trust Tier |
|-------------------|------------|
| 0 | `Automated` |
| 1-2 | `Reviewed` |
| 3+ | `Fully Validated` |

---

## Disagreement Resolution

### Single Moderator Flags Concerns

1. Result remains published but flagged
2. Second moderator assigned automatically
3. Second moderator reviews independently

### Second Moderator Also Flags

1. Issue escalates to methodology review
2. Both moderators' concerns documented
3. Committee reviews the specific issues

### Moderator-to-Moderator Disagreement

When moderators cannot reach consensus:

1. **Escalation** — Issue goes to the designated committee
2. **Final decision** — The **chair of the committee** makes the binding decision
3. **Documentation** — Decision and reasoning recorded
4. **Action** — Result updated, corrected, or withdrawn as decided

---

## Activity Logging

The system automatically logs all moderator activity:

| Data Captured | Purpose |
|---------------|---------|
| Reviews completed | Track workload and contribution |
| Time to complete | Identify bottlenecks or training needs |
| Verdicts given | Quality assurance |
| Agreement rate | Calibration between moderators |
| Concerns raised | Pattern detection |
| Escalations | Process improvement |

### Log Access

- **Moderators** — Can view their own activity log
- **Committee** — Can view all moderator logs
- **Users** — Cannot view moderator identities or logs

---

## Moderator Guidelines

### Core Principles

1. **Consistency** — Apply the same standards to every review
2. **Objectivity** — Evaluate verdicts on their merits, not model reputation
3. **Thoroughness** — Review the full sample, don't skim
4. **Documentation** — Note anything unusual for future reference
5. **Confidentiality** — Don't share question content outside approved channels

### What to Look For

During spot-checks, moderators evaluate:

- **Verdict accuracy** — Does the judge's verdict match what a human would conclude?
- **Reasoning quality** — Is the judge's explanation sound?
- **Edge cases** — Are borderline responses handled appropriately?
- **Systematic issues** — Are there patterns of misjudgment?

### When to Flag Concerns

Flag `Concerns` when:
- Multiple verdicts appear clearly wrong
- Judge reasoning is inconsistent or flawed
- You suspect the test wasn't run correctly
- Results seem anomalous compared to known model behavior

Do NOT flag for:
- Minor disagreements (1-2 verdicts out of 20)
- Personal opinions about model quality
- Issues with questions rather than verdicts

---

## Committee Structure

### Composition

The founding committee includes:
- Initial project leaders
- Theological advisors
- Technical advisors

### Responsibilities

- Select and onboard moderators
- Resolve escalated disputes
- Guide methodology updates
- Oversee benchmark integrity

### Chair Role

The committee chair:
- Makes final decisions on unresolved disputes
- Coordinates committee meetings
- Represents the benchmark to external parties
- Ensures consistent application of standards

---

## Related Documents

- [Core Publication Model](./process-publication-model.md) — Publication criteria and trust tiers
- [Deployment Vision](./platform-deployment-vision.md) — Overall deployment strategy
- [Question Security](./decision-question-security.md) — Question protection and access control

