# Great Commission Benchmark — Moderator Onboarding

Welcome to the Great Commission Benchmark moderation team! This document will guide you through everything you need to know to get started as a moderator.

**Last Updated:** December 17, 2025

---

## Table of Contents

1. [Welcome](#welcome)
2. [Getting Started](#getting-started)
3. [Your Role & Responsibilities](#your-role--responsibilities)
4. [The Moderation Dashboard](#the-moderation-dashboard)
5. [How to Review Submissions](#how-to-review-submissions)
6. [Quality Standards](#quality-standards)
7. [Handling Special Situations](#handling-special-situations)
8. [First Week Checklist](#first-week-checklist)
9. [FAQs](#faqs)
10. [Getting Help](#getting-help)

---

## Welcome

Thank you for joining the moderation team for the Great Commission Benchmark. Your work helps ensure the integrity of this tool, which exists to serve missionaries, ministry leaders, and Great Commission workers worldwide as they evaluate AI tools for ministry use.

### Why Moderation Matters

The benchmark measures how well AI models perform on tasks relevant to Christian ministry. Your role as a moderator is to:

- **Verify accuracy** — Ensure the automated judge's verdicts are correct
- **Maintain quality** — Catch systematic errors or anomalies
- **Build trust** — Each human review increases confidence in results

### What to Expect

This is a **low-traffic, volunteer-friendly commitment**:

| Aspect | Expectation |
|--------|-------------|
| **Total submissions** | ~600 anticipated overall |
| **Review frequency** | ~2 submissions per month |
| **Time per review** | 15-30 minutes |
| **Review style** | Asynchronous; do reviews when convenient |

You won't be overwhelmed—the benchmark is designed for manageable moderation loads.

---

## Getting Started

### Step 1: Account Setup

Your moderator account should already be created. If not, contact the committee chair.

**To verify your access:**

1. Log in at `https://gcbenchmark.org` (or staging URL during development)
2. Click your profile icon in the top-right corner
3. Confirm you see "Moderator" listed under your role
4. Navigate to `/moderator` to access your dashboard

### Step 2: Review This Documentation

Before your first review, read through:

| Document | Purpose | Time |
|----------|---------|------|
| **This document** | Onboarding and interface guide | 15 min |
| **[Moderation Process](../benchmark/process-moderation-process.md)** | Full process details and policies | 10 min |
| **[Curation Guidelines](../benchmark/spec-curation-guidelines.md)** | How questions and verdicts are created | 10 min |

### Step 3: Complete Your First Supervised Review

Your first 2-3 reviews will be **double-checked** by an experienced moderator. This is normal—it ensures consistency and gives you a chance to ask questions.

After your initial reviews are confirmed:
- You'll receive feedback on any discrepancies
- You can then review independently
- Your agreement rate will be tracked for ongoing calibration

### Step 4: Join Communication Channels

Join our Discord server for:
- Asking questions about specific reviews
- Discussing edge cases with other moderators
- Receiving announcements about benchmark updates

**Discord server:** [Link provided separately]  
**Channel:** `#moderators` (private to moderation team)

---

## Your Role & Responsibilities

### What You CAN Do

| Permission | Description |
|------------|-------------|
| **Access moderation queue** | View submissions awaiting review |
| **Review submissions** | Examine verdicts and provide feedback |
| **Verify or flag results** | Mark submissions as verified or raise concerns |
| **View response data** | See model responses for verification |
| **Access your activity log** | Review your own moderation history |

### What You CANNOT Do

| Restriction | Reason |
|-------------|--------|
| **Delete results unilaterally** | Requires committee decision |
| **Modify scores or verdicts** | Preserves audit trail integrity |
| **Access payment information** | Privacy and security |
| **Override other moderators** | Requires escalation process |

### Time Commitment

| Activity | Expected Time |
|----------|---------------|
| **Weekly check-in** | 5 minutes to check if queue has items |
| **Per review** | 15-30 minutes |
| **Monthly total** | 1-2 hours (at typical volume) |

### Confidentiality Requirements

As a moderator, you agree to:

- ❌ **NOT** share benchmark questions publicly
- ❌ **NOT** discuss question content on social media or forums
- ❌ **NOT** share questions with AI providers
- ✅ **DO** report any suspected question leaks to the committee
- ✅ **DO** keep moderation discussions within approved channels

---

## The Moderation Dashboard

When you navigate to `/moderator`, you'll see your dashboard.

### Dashboard Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  MODERATOR DASHBOARD                                            │
│                                                                 │
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐        │
│  │      12       │  │       3       │  │       2       │        │
│  │               │  │               │  │               │        │
│  │ CLI Pending   │  │   Appeals     │  │ Post-Publish  │        │
│  │  [View →]     │  │   [View →]    │  │   [View →]    │        │
│  └───────────────┘  └───────────────┘  └───────────────┘        │
│                                                                 │
│  Your Stats:                                                    │
│  • Today: 2 reviews                                             │
│  • This Week: 8 reviews                                         │
│  • Agreement Rate: 94%                                          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Queue Types

| Queue | Description | Priority |
|-------|-------------|----------|
| **CLI Submissions** | External test results awaiting verification before publishing | Primary workload |
| **Appeals** | Users appealing rejected submissions | Review when assigned |
| **Post-Publish Review** | Published results flagged for review (anomalies or reports) | Secondary |

### Priority Indicators

| Icon | Meaning | Action |
|------|---------|--------|
| 🔴 **High** | First submission from new organization, unusual scores | Review promptly |
| 🟡 **Normal** | Established submitter, expected scores | Review in order |
| 🟢 **Low** | Resubmission with minor changes | Can wait |

---

## How to Review Submissions

### Step-by-Step Review Process

#### 1. Select a Submission

From the CLI Submissions queue, click **[Review]** on any item. Start with the oldest high-priority items.

#### 2. Review Submission Information

Check the submission details:

| Field | What to Look For |
|-------|------------------|
| **Model** | Is this a known model? Custom fine-tune? |
| **Organization** | New or established? Previous submission history? |
| **CLI Version** | Using current gcb-runner version? |
| **Score** | Does it seem reasonable for this model type? |

#### 3. Examine the Response Sample

You'll review **20 randomly selected verdicts**. For each:

1. **Read the question** (click to reveal if hidden)
2. **Read the model's response**
3. **Read the judge's verdict and reasoning**
4. **Mark your assessment:**
   - ✅ **Agree** — Judge's verdict is correct
   - ❌ **Disagree** — Judge made an error
   - ❓ **Unsure** — Edge case; need discussion

#### 4. Complete the Verification Checklist

Before making your decision, verify:

- [ ] Response patterns consistent with claimed model
- [ ] Score within expected range for model capability
- [ ] No signs of response manipulation or caching
- [ ] Model access verified (if applicable)

#### 5. Submit Your Decision

| Decision | When to Use | Result |
|----------|-------------|--------|
| **✓ Verify & Publish** | Verdicts appear accurate, no issues | Published to leaderboard |
| **↩ Request More Info** | Need clarification from submitter | Returned to user |
| **✗ Reject** | Invalid, unverifiable, or fraudulent | Not published; refund may apply |

#### 6. Add Notes

Always add internal notes documenting:
- Any patterns you noticed
- Concerns for future reference
- Reason for your decision

---

## Quality Standards

### What Makes a Good Review

| Principle | Description |
|-----------|-------------|
| **Consistency** | Apply the same standards to every submission |
| **Objectivity** | Evaluate verdicts on their merits, not model reputation |
| **Thoroughness** | Review the full sample; don't skim |
| **Documentation** | Note anything unusual for future reference |

### What to Look For in Verdicts

| Check | Question to Ask |
|-------|-----------------|
| **Verdict accuracy** | Does the judge's verdict match what a human would conclude? |
| **Reasoning quality** | Is the judge's explanation sound and well-supported? |
| **Edge cases** | Are borderline responses handled appropriately? |
| **Systematic issues** | Are there patterns of misjudgment across responses? |

### Agreement Thresholds

Your agreement rate with other moderators is tracked:

| Rate | Interpretation |
|------|----------------|
| **90%+** | Excellent calibration |
| **80-90%** | Good; occasional differences expected |
| **70-80%** | May need recalibration; discuss edge cases |
| **Below 70%** | Training refresh recommended |

### Common Verdict Types

| Verdict | Meaning |
|---------|---------|
| **Correct** | Model gave an accurate, helpful response |
| **Incorrect** | Model made factual errors or gave harmful advice |
| **Refused** | Model declined to answer |
| **Partially Correct** | Some correct elements with notable issues |

---

## Handling Special Situations

### When to Flag Concerns

Flag `Concerns` when you observe:

- ⚠️ Multiple verdicts (3+) appear clearly wrong
- ⚠️ Judge reasoning is inconsistent or flawed
- ⚠️ You suspect the test wasn't run correctly
- ⚠️ Results seem anomalous compared to known model behavior

**Do NOT flag for:**
- Minor disagreements (1-2 verdicts out of 20)
- Personal opinions about model quality
- Issues with questions rather than verdicts

### Handling Appeals

If assigned an appeal:

1. **Review independently** — Don't just defer to the original moderator
2. **Examine the user's argument** — Consider their evidence
3. **Check attachments** — API logs, screenshots, etc.
4. **Make your decision:**
   - **Uphold** — Original rejection stands
   - **Overturn** — Approve and publish
   - **Escalate** — Uncertain; send to admin

**Important:** You cannot review appeals for submissions you originally rejected.

### Escalation Path

When consensus can't be reached:

```
Step 1: Second moderator reviews
          ↓
Step 2: If still disagreement → Escalate to committee
          ↓
Step 3: Committee chair makes final decision
          ↓
Step 4: Decision documented and implemented
```

### Suspected Fraud

If you suspect manipulation:

1. **Document specifics** — Which responses look suspicious and why
2. **Flag as concerns** — Don't reject outright
3. **Request second opinion** — Another moderator should verify
4. **Escalate if confirmed** — Committee handles fraud cases

---

## First Week Checklist

Complete these items in your first week as a moderator:

### Day 1

- [ ] Log in and verify moderator access
- [ ] Navigate to `/moderator` dashboard
- [ ] Review this onboarding document completely
- [ ] Join the Discord `#moderators` channel

### Day 2-3

- [ ] Read [Moderation Process](../benchmark/process-moderation-process.md)
- [ ] Read [Curation Guidelines](../benchmark/spec-curation-guidelines.md)
- [ ] Familiarize yourself with the queue interface (browse without acting)

### Day 4-5

- [ ] Complete your first review (will be double-checked)
- [ ] Receive feedback from experienced moderator
- [ ] Ask questions about any unclear aspects

### End of Week 1

- [ ] Complete 2-3 supervised reviews
- [ ] Receive confirmation to review independently
- [ ] Bookmark key documentation for reference

---

## FAQs

### General Questions

**Q: How often should I check the queue?**  
A: Once or twice a week is sufficient given typical volume. High-priority items will also trigger email notifications.

**Q: What if I'm unavailable for an extended period?**  
A: Let the committee know. Your items will be reassigned, and there's no penalty for planned absences.

**Q: Can I see who submitted a test?**  
A: Yes, you can see the submitter's username and organization for verification purposes.

### Review Questions

**Q: What if I'm not sure about a verdict?**  
A: Mark it as "Unsure" and add notes. When multiple verdicts are uncertain, flag for concerns.

**Q: How long should a review take?**  
A: 15-30 minutes is typical. Don't rush, but you don't need to spend hours either.

**Q: What if I recognize the model and know it's better/worse than the score suggests?**  
A: Focus on whether the individual verdicts are correct, not whether the overall score "feels right."

### Technical Questions

**Q: What if the platform is down or buggy?**  
A: Report issues in the Discord `#bugs` channel. Don't lose your notes—you can complete the review later.

**Q: Can I review on mobile?**  
A: The interface is designed for desktop. Mobile works but isn't recommended for detailed reviews.

**Q: What browsers are supported?**  
A: Chrome, Firefox, Safari, and Edge (latest versions).

---

## Getting Help

### Quick Reference

| Need | Contact |
|------|---------|
| **Technical issues** | Discord `#bugs` channel |
| **Review questions** | Discord `#moderators` channel |
| **Policy questions** | Committee chair |
| **Urgent issues** | Email to committee (provided separately) |

### Key Documentation

| Document | Location |
|----------|----------|
| Moderation Process | `benchmark/process-moderation-process.md` |
| Curation Guidelines | `benchmark/spec-curation-guidelines.md` |
| Question Security | `benchmark/process-question-security.md` |
| Security Practices | `documents/Security-Practices.md` |

### Response Times

| Channel | Expected Response |
|---------|-------------------|
| **Discord** | Within 24 hours (often faster) |
| **Email** | Within 48 hours |
| **Escalations** | Depends on committee schedule |

---

## Final Notes

### Remember

- **You're not alone** — Other moderators and the committee are here to help
- **Quality over speed** — Take the time needed for thorough reviews
- **Ask questions** — No question is too basic during onboarding
- **Your work matters** — Every review strengthens the benchmark's integrity

### Thank You

Your volunteer service helps ensure that Great Commission workers around the world have access to trustworthy AI evaluations. This work directly supports missionaries, translators, evangelists, and ministry leaders who are using AI tools to advance the Gospel.

Welcome to the team!

---

## Related Documents

- [Moderation Process](../benchmark/process-moderation-process.md) — Full process details and policies
- [Curation Guidelines](../benchmark/spec-curation-guidelines.md) — How questions and verdicts are created
- [Security Practices](./Security-Practices.md) — Platform security overview
- [Wireframes: Moderator Pages](../benchmark/wireframes-moderator-pages.md) — Visual interface guide

---

*This document should be reviewed and updated as the moderation process evolves. Last substantive review: December 2025.*
