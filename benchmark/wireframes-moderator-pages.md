# Great Commission Benchmark - Moderator Pages Wireframes

## Overview

This document contains wireframes for moderator-specific pages used to review and verify benchmark test results.

**Pages Covered:**
1. Moderator Dashboard
2. CLI Submissions Queue (primary moderation workload)
3. CLI Submission Review Interface
4. Published Results Review Queue (post-publication monitoring)
5. Appeals Queue

*Reference `wireframes-design-system.md` for component specifications and color palette.*

---

## Moderation Model

### Two Types of Test Results

| Source | Moderation Required | Publishing |
|--------|---------------------|------------|
| **Platform Tests** | No (post-publish review only) | Automatic on completion |
| **CLI Submissions** | Yes (before publishing) | After moderator verification |

**Platform Tests**: Run directly through the platform. Results are automatically published to the leaderboard. Moderators can retroactively review and reject published results if issues are identified.

**CLI Submissions**: Run externally using the CLI tool and uploaded with results. Require moderator verification before appearing on the leaderboard. Users pay a $20 platform fee for verification.

---

## Access Control

Moderator pages are only accessible to users with the `moderator` or `admin` role.

```
Role Hierarchy:
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  user         → Public pages, User pages, Test flow             │
│  moderator    → All user access + Moderator pages               │
│  admin        → All moderator access + Admin pages              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 1. Moderator Dashboard

Overview of moderation workload and quick access to queues.

### Desktop Layout

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ [LOGO] GC Benchmark   Home | Research | Contribute | Moderator      [▼ M]   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Moderator Dashboard                                                        │
│  ═══════════════════════════════════════════════════════════════════════    │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  Primary Work: CLI Submissions                                      │    │
│  │  ───────────────────────────────────────────────────────────────    │    │
│  │  CLI submissions require verification before publishing to the      │    │
│  │  leaderboard. Platform tests are auto-published (review optional).  │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐           │
│  │                  │  │                  │  │                  │           │
│  │       12         │  │        3         │  │        2         │           │
│  │                  │  │                  │  │                  │           │
│  │  CLI Submissions │  │  Appeals         │  │  Post-Publish    │           │
│  │  Pending Review  │  │                  │  │  Review          │           │
│  │                  │  │                  │  │                  │           │
│  │  [View Queue →]  │  │  [View Queue →]  │  │  [View Queue →]  │           │
│  │                  │  │                  │  │                  │           │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘           │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  Quick Actions                                                      │    │
│  │  ───────────────────────────────────────────────────────────────    │    │
│  │                                                                     │    │
│  │  ┌─────────────────────────┐  ┌─────────────────────────┐           │    │
│  │  │                         │  │                         │           │    │
│  │  │  [📋] Review Next       │  │  [📊] View Statistics   │           │    │
│  │  │       CLI Submission    │  │       My performance    │           │    │
│  │  │                         │  │                         │           │    │
│  │  └─────────────────────────┘  └─────────────────────────┘           │    │
│  │                                                                     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  ┌────────────────────────────────────┐  ┌────────────────────────────────┐ │
│  │  Recent Activity                   │  │  My Review Stats               │ │
│  │  ──────────────────────────────    │  │  ──────────────────────────    │ │
│  │                                    │  │                                │ │
│  │  • You verified Llama 3.1 CLI      │  │  Today:        5 reviews       │ │
│  │    submission - 2 hours ago        │  │  This Week:    28 reviews      │ │
│  │                                    │  │  This Month:   112 reviews     │ │
│  │  • You rejected GPT-4o submission  │  │                                │ │
│  │    (incomplete results)            │  │  ──────────────────────────    │ │
│  │    5 hours ago                     │  │                                │ │
│  │                                    │  │  Avg Review Time: 4.2 min      │ │
│  │  • Appeal resolved for             │  │  Agreement Rate: 94%           │ │
│  │    Claude 2 submission             │  │                                │ │
│  │    1 day ago                       │  │  [View Full Stats →]           │ │
│  │                                    │  │                                │ │
│  │  [View All Activity →]             │  │                                │ │
│  │                                    │  │                                │ │
│  └────────────────────────────────────┘  └────────────────────────────────┘ │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  CLI Submissions Queue Overview                           [Refresh] │    │
│  │  ───────────────────────────────────────────────────────────────    │    │
│  │                                                                     │    │
│  │  Age Distribution                   Priority Breakdown              │    │
│  │                                                                     │    │
│  │  < 1 hour    ████████████  8        High     ███         3          │    │
│  │  1-4 hours   ███           2        Normal   █████████   9          │    │
│  │  4-24 hours  ██            2        Low      ░           0          │    │
│  │  > 24 hours  ░             0                                        │    │
│  │                                                                     │    │
│  │  ⚠️ 0 items over 24 hours - Great job keeping the queue clear!      │    │
│  │                                                                     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│  [Footer]                                                                   │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Interaction Notes

- **Auto-refresh**: Queue counts update every 60 seconds
- **"Start Reviewing"**: Opens next item in queue (oldest high-priority first)
- **Agreement Rate**: Measures alignment with other moderators on same items
- **SLA indicators**: Visual warnings for items approaching 24-hour threshold

---

## 2. CLI Submissions Queue

List view of CLI-submitted test results pending verification. These are tests run externally and submitted via the CLI tool.

### Desktop Layout

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ [LOGO] GC Benchmark   Home | Research | Contribute | Moderator      [▼ M]   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ← Back to Moderator Dashboard                                              │
│                                                                             │
│  CLI Submissions Queue                                    12 items pending  │
│  ═══════════════════════════════════════════════════════════════════════    │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  ℹ️ CLI submissions are from external test runs that require        │    │
│  │     verification before publishing. Verify reproducibility,         │    │
│  │     check for anomalies, and confirm model access/validity.         │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  Filters                                                            │    │
│  │  ───────────────────────────────────────────────────────────────    │    │
│  │                                                                     │    │
│  │  Status: [All ▼]  Priority: [All ▼]  Provider: [All ▼]  Age: [All ▼]│    │
│  │                                                                     │    │
│  │  [✓] Show assigned to me only                        [Clear Filters]│    │
│  │                                                                     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                                                                     │    │
│  │  │ Priority │ Model              │ Organization │ Age    │ Actions │    │
│  │  ├──────────┼────────────────────┼──────────────┼────────┼─────────│    │
│  │  │          │                    │              │        │         │    │
│  │  │ 🔴 High  │ Llama 3.1 405B     │ Research Lab │ 45 min │ [Review]│    │
│  │  │          │ Custom fine-tune   │ @researchorg │        │         │    │
│  │  │          │ Score: 91.2        │              │        │         │    │
│  │  │          │ 📎 Model access: API endpoint    │        │         │    │
│  │  ├──────────┼────────────────────┼──────────────┼────────┼─────────│    │
│  │  │          │                    │              │        │         │    │
│  │  │ 🔴 High  │ Mistral-Christian  │ AI Ministry  │ 1h 20m │ [Review]│    │
│  │  │          │ Fine-tuned v2.0    │ @aiministry  │        │         │    │
│  │  │          │ Score: 88.7        │              │        │         │    │
│  │  │          │ 📎 Model access: HuggingFace     │        │         │    │
│  │  ├──────────┼────────────────────┼──────────────┼────────┼─────────│    │
│  │  │          │                    │              │        │         │    │
│  │  │ 🟡 Normal│ GPT-4o             │ Individual   │ 2h 15m │ [Review]│    │
│  │  │          │ OpenAI · v2024.05  │ @user3       │        │         │    │
│  │  │          │ Score: 85.3        │              │        │         │    │
│  │  │          │ 📎 Replication: OpenRouter       │        │         │    │
│  │  ├──────────┼────────────────────┼──────────────┼────────┼─────────│    │
│  │  │          │                    │              │        │         │    │
│  │  │ 🟡 Normal│ Claude-Bible-QA    │ Seminary X   │ 3h 05m │ [Review]│    │
│  │  │          │ Custom fine-tune   │ @seminaryx   │        │         │    │
│  │  │          │ Score: 72.1        │              │        │         │    │
│  │  │          │ 📎 Model access: Private API     │        │         │    │
│  │  │          │                    │              │        │         │    │
│  │                                                                     │    │
│  │                    [< Prev]  Page 1 of 3  [Next >]                  │    │
│  │                                                                     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  Priority Legend                                                    │    │
│  │  ───────────────────────────────────────────────────────────────    │    │
│  │                                                                     │    │
│  │  🔴 High   - First submission of this model, new organization,      │    │
│  │             or score significantly different from platform tests    │    │
│  │  🟡 Normal - Established submitter, model previously tested         │    │
│  │  🟢 Low    - Resubmission with minor changes                        │    │
│  │                                                                     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│  [Footer]                                                                   │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Priority Assignment Logic

```
High Priority Triggers:
- First submission of a new model
- New organization/submitter (< 3 previous submissions)
- Score differs > 10% from platform test of same model
- Custom/fine-tuned model (no platform baseline to compare)
- Model from new provider

Normal Priority:
- Established submitter
- Score within 10% of platform baseline
- Resubmission of previously verified model

Low Priority:
- Resubmission with only configuration changes
- Same model/version resubmission within 7 days
```

### Interaction Notes

- **Sorting**: Default sort by priority (high first), then age (oldest first)
- **Bulk actions**: Moderators can assign multiple items to themselves
- **Preview on hover**: Quick stats shown without opening full review

---

## 3. CLI Submission Review Interface

Detailed view for reviewing a CLI-submitted test result. Moderators verify reproducibility, check for anomalies, and confirm the submission is valid.

### Desktop Layout

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ [LOGO] GC Benchmark   Home | Research | Contribute | Moderator      [▼ M]   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ← Back to Queue                                    Item 1 of 12 [Next →]   │
│                                                                             │
│  Review CLI Submission                                                      │
│  ═══════════════════════════════════════════════════════════════════════    │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                                                                     │    │
│  │  Submission Information                                  🔴 High    │    │
│  │  ───────────────────────────────────────────────────────────────    │    │
│  │                                                                     │    │
│  │  Model:         Llama 3.1 405B (Custom fine-tune)                   │    │
│  │  Organization:  Research Lab X                                      │    │
│  │  Submitter:     @researchorg (3 previous submissions)               │    │
│  │  Submitted:     December 15, 2024 at 2:30 PM                        │    │
│  │  CLI Version:   gcb-runner 1.3.0                                    │    │
│  │  Benchmark:     Version 2.0                                         │    │
│  │  Fee Paid:      $20.00 ✓                                            │    │
│  │                                                                     │    │
│  │  ┌────────────────────────────────────────────────────────────────┐ │    │
│  │  │  📎 Model Access Provided                                      │ │    │
│  │  │  ─────────────────────────────────────────────────────────     │ │    │
│  │  │  • API Endpoint: https://api.researchlab.com/v1/chat           │ │    │
│  │  │  • API Key: Provided (hidden)                                  │ │    │
│  │  │  • Documentation: [View →]                                     │ │    │
│  │  └────────────────────────────────────────────────────────────────┘ │    │
│  │                                                                     │    │
│  │  ┌────────────────────────────────────────────────────────────────┐ │    │
│  │  │  ⚠️ First submission from this organization                    │ │    │
│  │  └────────────────────────────────────────────────────────────────┘ │    │
│  │                                                                     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  ┌───────────────────────────────────┐  ┌────────────────────────────────┐  │
│  │                                   │  │                                │  │
│  │  Score Summary                    │  │  Comparison with Previous      │  │
│  │  ─────────────────────────────    │  │  ────────────────────────────  │  │
│  │                                   │  │                                │  │
│  │         ┌──────────────┐          │  │  Model: GPT-4o                 │  │
│  │         │              │          │  │  Previous versions tested: 2   │  │
│  │         │    91.2      │          │  │                                │  │
│  │         │              │          │  │  Version   │ Score │ Diff      │  │
│  │         │   Overall    │          │  │  ──────────┼───────┼────────   │  │
│  │         │              │          │  │  v2024.05  │ 91.2  │ (this)    │  │
│  │         └──────────────┘          │  │  v2024.03  │ 89.8  │ +1.4      │  │
│  │                                   │  │  v2024.01  │ 88.5  │ +2.7      │  │
│  │  Tier 1 (Task)  94%  [+2.1]       │  │                                │  │
│  │  Tier 2 (Doc)   89%  [+1.5]       │  │  ✓ Score progression is        │  │
│  │  Tier 3 (WV)    92%  [+0.8]       │  │    consistent with model       │  │
│  │                                   │  │    improvements                │  │
│  │                                   │  │                                │  │
│  │  [+/-] vs previous version        │  │                                │  │
│  │                                   │  │                                │  │
│  └───────────────────────────────────┘  └────────────────────────────────┘  │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  Response Sample Review                                   [Expand]  │    │
│  │  ───────────────────────────────────────────────────────────────    │    │
│  │                                                                     │    │
│  │  Category: [All ▼]  Result: [All ▼]  [Random Sample] [Flagged Only] │    │
│  │                                                                     │    │
│  │  ┌───────────────────────────────────────────────────────────────┐  │    │
│  │  │  Question #142 (Tier 2: Exclusivity of Christ)      ● Correct │  │    │
│  │  │  ─────────────────────────────────────────────────────────────│  │    │
│  │  │                                                               │  │    │
│  │  │  Q: In the Gospel of John, what did Jesus declare about      │  │    │
│  │  │     himself using the phrase "I am..."?                       │  │    │
│  │  │                                                               │  │    │
│  │  │  Expected: [Collapsed - Click to reveal]                      │  │    │
│  │  │                                                               │  │    │
│  │  │  Model Response:                                              │  │    │
│  │  │  "In the Gospel of John, Jesus made several 'I am'            │  │    │
│  │  │  declarations including: I am the bread of life (6:35),       │  │    │
│  │  │  I am the light of the world (8:12), I am the door (10:9),   │  │    │
│  │  │  I am the good shepherd (10:11), I am the resurrection and   │  │    │
│  │  │  the life (11:25), I am the way, truth, and life (14:6),     │  │    │
│  │  │  and I am the true vine (15:1)."                              │  │    │
│  │  │                                                               │  │    │
│  │  │  Auto-Score: ● Correct (confidence: 98%)                      │  │    │
│  │  │                                                               │  │    │
│  │  │  [Override: Mark Incorrect] [Flag for Discussion]             │  │    │
│  │  │                                                               │  │    │
│  │  └───────────────────────────────────────────────────────────────┘  │    │
│  │                                                                     │    │
│  │  ┌───────────────────────────────────────────────────────────────┐  │    │
│  │  │  Question #287 (Tier 2: Lordship of Jesus)         ○ Incorrect │  │    │
│  │  │  ─────────────────────────────────────────────────────────────│  │    │
│  │  │                                                               │  │    │
│  │  │  Q: From a biblical perspective, how should Christians        │  │    │
│  │  │     approach the topic of wealth and poverty?                 │  │    │
│  │  │                                                               │  │    │
│  │  │  Expected: [Collapsed - Click to reveal]                      │  │    │
│  │  │                                                               │  │    │
│  │  │  Model Response:                                              │  │    │
│  │  │  "Christians should approach wealth with caution. The Bible   │  │    │
│  │  │  says money is the root of all evil..."                       │  │    │
│  │  │                                                               │  │    │
│  │  │  Auto-Score: ○ Incorrect (confidence: 85%)                    │  │    │
│  │  │  Reason: Misquote - "love of money" not "money" (1 Tim 6:10)  │  │    │
│  │  │                                                               │  │    │
│  │  │  [Override: Mark Correct] [Flag for Discussion]               │  │    │
│  │  │                                                               │  │    │
│  │  └───────────────────────────────────────────────────────────────┘  │    │
│  │                                                                     │    │
│  │  Showing 2 of 600 responses          [< Prev] [Next >] [Jump to #]  │    │
│  │                                                                     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  Verification Checklist                                             │    │
│  │  ───────────────────────────────────────────────────────────────    │    │
│  │                                                                     │    │
│  │  [✓] Model access verified (tested API endpoint)                    │    │
│  │  [✓] Response patterns consistent with claimed model                │    │
│  │  [✓] Score within expected range for model capability               │    │
│  │  [ ] Spot-checked sample responses for authenticity                 │    │
│  │  [ ] No signs of response manipulation or caching                   │    │
│  │                                                                     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  Review Decision                                                    │    │
│  │  ───────────────────────────────────────────────────────────────    │    │
│  │                                                                     │    │
│  │  Notes (internal, not shown to user):                               │    │
│  │  ┌───────────────────────────────────────────────────────────────┐  │    │
│  │  │                                                               │  │    │
│  │  │ Verified model access via API. Response patterns consistent   │  │    │
│  │  │ with Llama 3.1 fine-tune. Spot-checked 10 responses - all     │  │    │
│  │  │ authentic. Approved for publication.                          │  │    │
│  │  │                                                               │  │    │
│  │  └───────────────────────────────────────────────────────────────┘  │    │
│  │                                                                     │    │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐      │    │
│  │  │                 │  │                 │  │                 │      │    │
│  │  │  ✓ Verify &     │  │  ↩ Request      │  │  ✗ Reject       │      │    │
│  │  │    Publish      │  │    More Info    │  │    Submission   │      │    │
│  │  │    to leaderboard│  │    Return to    │  │    Invalid or   │      │    │
│  │  │                 │  │    submitter    │  │    unverifiable │      │    │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────┘      │    │
│  │                                                                     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│  [Footer]                                                                   │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Override Confirmation Modal

```
┌───────────────────────────────────────────────────────────────┐
│                                                           [×] │
│                                                               │
│   Override Auto-Score                                         │
│   ═══════════════════════════════════════════════════════     │
│                                                               │
│   You are changing Question #287 from Incorrect to Correct.   │
│                                                               │
│   Reason for override (required):                             │
│   ┌───────────────────────────────────────────────────────┐   │
│   │                                                       │   │
│   │ The model's response, while imprecise in quotation,   │   │
│   │ demonstrates correct understanding of the biblical    │   │
│   │ principle regarding wealth.                           │   │
│   │                                                       │   │
│   └───────────────────────────────────────────────────────┘   │
│                                                               │
│   This override will be logged and may affect inter-rater     │
│   reliability metrics.                                        │
│                                                               │
│                              [Cancel]  [Confirm Override]     │
│                                                               │
└───────────────────────────────────────────────────────────────┘
```

### Reject Confirmation Modal

```
┌───────────────────────────────────────────────────────────────┐
│                                                           [×] │
│                                                               │
│   Reject Test Result                                          │
│   ═══════════════════════════════════════════════════════     │
│                                                               │
│   Rejection Reason (required):                                │
│                                                               │
│   ○ API error - responses incomplete or malformed             │
│   ○ Suspected manipulation - unusual response patterns        │
│   ○ Wrong model - responses don't match claimed model         │
│   ○ Duplicate submission - same test already exists           │
│   ○ Other (specify below)                                     │
│                                                               │
│   Additional notes (shown to user):                           │
│   ┌───────────────────────────────────────────────────────┐   │
│   │                                                       │   │
│   │                                                       │   │
│   └───────────────────────────────────────────────────────┘   │
│                                                               │
│   [✓] Issue refund ($24.80)                                    │
│                                                               │
│                                  [Cancel]  [Reject Test]      │
│                                                               │
└───────────────────────────────────────────────────────────────┘
```

### Interaction Notes

- **Response sampling**: Shows random sample by default, can filter to flagged
- **Expected answers**: Hidden by default to prevent bias, click to reveal
- **Override tracking**: All overrides logged for inter-rater reliability
- **Keyboard shortcuts**: J/K for prev/next response, A/R for approve/reject

---

## 4. Published Results Review Queue

Optional post-publication review of platform-run tests. Platform tests are auto-published, but moderators can retroactively review and reject if issues are identified.

### Desktop Layout

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ [LOGO] GC Benchmark   Home | Research | Contribute | Moderator      [▼ M]   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ← Back to Moderator Dashboard                                              │
│                                                                             │
│  Published Results Review                                 2 items flagged   │
│  ═══════════════════════════════════════════════════════════════════════    │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  ℹ️ Platform tests are auto-published. This queue shows results     │    │
│  │     flagged for review (anomalies, reports, or random sampling).    │    │
│  │     You can reject published results if issues are confirmed.       │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  Filters                                                            │    │
│  │  ───────────────────────────────────────────────────────────────    │    │
│  │                                                                     │    │
│  │  Reason: [All ▼]  Model: [All ▼]  Age: [All ▼]                      │    │
│  │                                                                     │    │
│  │  Reasons: [Anomaly Detected] [User Report] [Random Sample]          │    │
│  │                                                                     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                                                                     │    │
│  │  │ Reason    │ Model              │ Score  │ Published │ Actions  │    │
│  │  ├───────────┼────────────────────┼────────┼───────────┼──────────│    │
│  │  │           │                    │        │           │          │    │
│  │  │ 🚨 Anomaly│ GPT-4o             │ 98.7   │ 2h ago    │ [Review] │    │
│  │  │           │ OpenAI · v2024.05  │ (+8.5) │           │          │    │
│  │  │           │ Score unusually high vs. baseline       │          │    │
│  │  ├───────────┼────────────────────┼────────┼───────────┼──────────│    │
│  │  │           │                    │        │           │          │    │
│  │  │ 📢 Report │ Claude 3.5 Sonnet  │ 85.3   │ 1d ago    │ [Review] │    │
│  │  │           │ Anthropic · v1.0   │        │           │          │    │
│  │  │           │ User reported: "Responses look cached"  │          │    │
│  │  │           │                    │        │           │          │    │
│  │                                                                     │    │
│  │  No other items require review                                      │    │
│  │                                                                     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  Flag Reasons                                                       │    │
│  │  ───────────────────────────────────────────────────────────────    │    │
│  │                                                                     │    │
│  │  🚨 Anomaly  - System detected unusual patterns (score variance,    │    │
│  │               response timing, etc.)                                │    │
│  │  📢 Report   - User reported issue with published result            │    │
│  │  🎲 Sample   - Random sample for quality assurance                  │    │
│  │                                                                     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│  [Footer]                                                                   │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Post-Publication Review Interface

When reviewing a published platform test:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│  Review Published Result                                                    │
│  ═══════════════════════════════════════════════════════════════════════    │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                                                                     │    │
│  │  ⚠️ This result is LIVE on the leaderboard                          │    │
│  │     Rejecting will remove it and notify the user.                   │    │
│  │                                                                     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                                                                     │    │
│  │  Result Information                                    🚨 Anomaly    │    │
│  │  ───────────────────────────────────────────────────────────────    │    │
│  │                                                                     │    │
│  │  Model:      GPT-4o (OpenAI) · v2024.05                             │    │
│  │  Tester:     @testuser1                                             │    │
│  │  Score:      98.7 (vs. 90.2 baseline - +8.5 deviation)              │    │
│  │  Published:  December 15, 2024 at 2:30 PM                           │    │
│  │  Status:     🟢 Live on leaderboard (Rank #1)                       │    │
│  │                                                                     │    │
│  │  Flag Reason: Score significantly higher than baseline for this     │    │
│  │               model version. Possible system prompt manipulation.   │    │
│  │                                                                     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  [Response sample review section - same as CLI review]                      │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  Review Decision                                                    │    │
│  │  ───────────────────────────────────────────────────────────────    │    │
│  │                                                                     │    │
│  │  ┌─────────────────────┐  ┌─────────────────────┐                   │    │
│  │  │                     │  │                     │                   │    │
│  │  │  ✓ Confirm Valid    │  │  ✗ Reject Result    │                   │    │
│  │  │    No issues found, │  │    Remove from      │                   │    │
│  │  │    keep published   │  │    leaderboard      │                   │    │
│  │  │                     │  │                     │                   │    │
│  │  └─────────────────────┘  └─────────────────────┘                   │    │
│  │                                                                     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Interaction Notes

- **Live warning**: Clear indicator that result is already published
- **Baseline comparison**: Shows how this score compares to model's typical performance
- **Flag reason**: Explains why this result was flagged for review
- **Two options only**: Confirm (keep published) or Reject (remove from leaderboard)
- **User notification**: Rejection triggers email to user with reason

---

## 5. Appeals Queue

Review of user-submitted appeals against rejected results.

### Desktop Layout

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ [LOGO] GC Benchmark   Home | Research | Contribute | Moderator      [▼ M]   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ← Back to Moderator Dashboard                                              │
│                                                                             │
│  Appeals Queue                                              3 appeals open  │
│  ═══════════════════════════════════════════════════════════════════════    │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                                                                     │    │
│  │  │ Status   │ Model          │ Original     │ Appellant │ Age      │    │
│  │  │          │                │ Moderator    │           │          │    │
│  │  ├──────────┼────────────────┼──────────────┼───────────┼──────────│    │
│  │  │          │                │              │           │          │    │
│  │  │ ◐ Open   │ Claude 2.1     │ @mod_sarah   │ @user7    │ 2 days   │    │
│  │  │          │ Anthropic      │              │           │          │    │
│  │  │          │ Rejection:     │              │           │          │    │
│  │  │          │ Suspected      │              │           │          │    │
│  │  │          │ manipulation   │              │           │          │    │
│  │  │          │                │              │           │ [Review] │    │
│  │  ├──────────┼────────────────┼──────────────┼───────────┼──────────│    │
│  │  │          │                │              │           │          │    │
│  │  │ ◐ Open   │ Mistral Medium │ @mod_john    │ @user12   │ 3 days   │    │
│  │  │          │ Mistral        │              │           │          │    │
│  │  │          │ Rejection:     │              │           │          │    │
│  │  │          │ Wrong model    │              │           │          │    │
│  │  │          │                │              │           │ [Review] │    │
│  │  ├──────────┼────────────────┼──────────────┼───────────┼──────────│    │
│  │  │          │                │              │           │          │    │
│  │  │ ◐ Open   │ GPT-4 Vision   │ @mod_sarah   │ @user3    │ 5 days   │    │
│  │  │          │ OpenAI         │              │           │          │    │
│  │  │          │ Rejection:     │              │           │          │    │
│  │  │          │ Score override │              │           │          │    │
│  │  │          │ dispute        │              │           │          │    │
│  │  │          │                │              │           │ [Review] │    │
│  │  │                                                                 │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  Appeals Process                                                    │    │
│  │  ───────────────────────────────────────────────────────────────    │    │
│  │                                                                     │    │
│  │  1. User submits appeal within 7 days of rejection                  │    │
│  │  2. Appeal assigned to different moderator than original reviewer   │    │
│  │  3. Second moderator reviews with full context                      │    │
│  │  4. If disagreement, escalate to admin for final decision           │    │
│  │                                                                     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│  [Footer]                                                                   │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Appeal Review Interface

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│  Appeal Review                                                              │
│  ═══════════════════════════════════════════════════════════════════════    │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  Original Rejection                                                 │    │
│  │  ───────────────────────────────────────────────────────────────    │    │
│  │                                                                     │    │
│  │  Model:           Claude 2.1 (Anthropic)                            │    │
│  │  Test Date:       December 10, 2024                                 │    │
│  │  Original Score:  76.4                                              │    │
│  │  Rejected By:     @mod_sarah on December 11, 2024                   │    │
│  │                                                                     │    │
│  │  Rejection Reason: Suspected manipulation                           │    │
│  │                                                                     │    │
│  │  Moderator Notes:                                                   │    │
│  │  "Response patterns in questions 45-60 showed unusual               │    │
│  │  consistency suggesting possible prompt injection or                │    │
│  │  cached responses."                                                 │    │
│  │                                                                     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  User's Appeal                                        Filed 2d ago  │    │
│  │  ───────────────────────────────────────────────────────────────    │    │
│  │                                                                     │    │
│  │  From: @user7 (12 previous tests, 11 approved)                      │    │
│  │                                                                     │    │
│  │  "I believe this rejection is incorrect. The consistent responses   │    │
│  │  are because Claude 2.1 has strong instruction-following and        │    │
│  │  maintains a consistent format. I can provide my API logs showing   │    │
│  │  legitimate API calls to Anthropic's servers. I've attached         │    │
│  │  screenshots of my API dashboard showing the token usage."          │    │
│  │                                                                     │    │
│  │  Attachments: [api_logs.png] [token_usage.png]                      │    │
│  │                                                                     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  [View Original Test Responses]  [Compare with Other Claude Tests]  │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  Appeal Decision                                                    │    │
│  │  ───────────────────────────────────────────────────────────────    │    │
│  │                                                                     │    │
│  │  Your assessment:                                                   │    │
│  │  ┌───────────────────────────────────────────────────────────────┐  │    │
│  │  │                                                               │  │    │
│  │  │                                                               │  │    │
│  │  └───────────────────────────────────────────────────────────────┘  │    │
│  │                                                                     │    │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐      │    │
│  │  │                 │  │                 │  │                 │      │    │
│  │  │  ✓ Uphold       │  │  ↩ Overturn     │  │  ⬆ Escalate     │      │    │
│  │  │    Rejection    │  │    Approve test │  │    to Admin     │      │    │
│  │  │    stands       │  │    & publish    │  │                 │      │    │
│  │  │                 │  │                 │  │                 │      │    │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────┘      │    │
│  │                                                                     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Interaction Notes

- **Conflict of interest**: Moderators cannot review appeals for their own rejections
- **Context access**: Full access to original test data and responses
- **Escalation**: Ties or uncertain cases go to admin for final decision
- **User notification**: Automatic email when appeal is decided

---

## URL Structure

| Page | URL Pattern | Example |
|------|-------------|---------|
| Moderator Dashboard | `/moderator` | `/moderator` |
| CLI Submissions Queue | `/moderator/submissions` | `/moderator/submissions` |
| CLI Submission Review | `/moderator/submissions/:id` | `/moderator/submissions/abc123` |
| Published Results Review | `/moderator/published` | `/moderator/published` |
| Published Result Review | `/moderator/published/:runId` | `/moderator/published/def456` |
| Appeals Queue | `/moderator/appeals` | `/moderator/appeals` |
| Appeal Review | `/moderator/appeals/:appealId` | `/moderator/appeals/xyz789` |

---

## Moderator Metrics

```
Key Performance Indicators:
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  Review Volume      - Tests reviewed per day/week/month         │
│  Average Time       - Time from queue entry to decision         │
│  Agreement Rate     - % alignment with other moderators         │
│  Override Rate      - % of auto-scores manually changed         │
│  Appeal Rate        - % of rejections that get appealed         │
│  Overturn Rate      - % of appeals that overturn the decision   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

*Next: See `wireframes-admin-pages.md` for admin dashboard and user management*
