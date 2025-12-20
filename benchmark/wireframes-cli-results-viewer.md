# CLI Results Viewer — Dashboard Wireframes

This document provides wireframes and mockups for the `gcb-runner view` command's local web dashboard. The dashboard enables community members to explore their benchmark test results visually.

**Tech Stack:** Python stdlib HTTP server, embedded HTML/JS single-page app, Chart.js (CDN)

---

## Design Principles

1. **Report-first design** — Primary use case is generating shareable team reports
2. **Clean, scannable** — Users should quickly understand model performance
3. **Consistent with platform** — Generally matches platform visual style (not identical)
4. **Offline-capable** — Works without network (Chart.js CDN has fallback)

---

## Color Palette

Consistent with platform leaderboard:

| Element | Color | Hex |
|---------|-------|-----|
| Pass/Accepted | Green | `#16a34a` |
| Partial/Compromised | Yellow/Orange | `#d97706` |
| Fail/Refused | Red | `#dc2626` |
| Tier 1 | Blue | `#3b82f6` |
| Tier 2 | Purple | `#8b5cf6` |
| Tier 3 | Orange | `#f97316` |
| Background | Light Gray | `#f8fafc` |
| Card Background | White | `#ffffff` |
| Primary Action | Blue | `#2563eb` |

---

## Navigation Structure

```
┌─────────────────────────────────────────────────────────────────┐
│  GCB Results Viewer                                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  [Runs]  [Compare]  [Export Report ▼]                           │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**Navigation Items:**
- **Runs** — Default view, list of all test runs
- **Compare** — Side-by-side comparison tool
- **Export Report** — Dropdown: "Export as Markdown", "Open in Browser"

---

## View 1: Run List (Dashboard Home)

The default landing page showing all local test runs.

```
┌─────────────────────────────────────────────────────────────────────────┐
│  🏆 GCB Results Viewer                    [Runs]  [Compare]  [Export ▼] │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  Your Test Runs                                              [Refresh]   │
│                                                                          │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │ #  │ Model              │ Version │ Score │ Date           │      │ │
│  ├────┼────────────────────┼─────────┼───────┼────────────────┼──────┤ │
│  │ 5  │ gpt-4o             │ 2.0     │  82   │ Dec 16, 2:30pm │ View │ │
│  │    │ via OpenRouter     │         │ ████  │                │      │ │
│  ├────┼────────────────────┼─────────┼───────┼────────────────┼──────┤ │
│  │ 4  │ claude-3.5-sonnet  │ 2.0     │  78   │ Dec 15, 9:15am │ View │ │
│  │    │ via OpenRouter     │         │ ███▌  │                │      │ │
│  ├────┼────────────────────┼─────────┼───────┼────────────────┼──────┤ │
│  │ 3  │ llama3.2:70b       │ 2.0     │  71   │ Dec 14, 4:00pm │ View │ │
│  │    │ via LM Studio      │         │ ███   │                │      │ │
│  ├────┼────────────────────┼─────────┼───────┼────────────────┼──────┤ │
│  │ 2  │ mistral-large      │ 2.0     │  68   │ Dec 13, 11:00am│ View │ │
│  │    │ via OpenRouter     │         │ ██▌   │                │      │ │
│  ├────┼────────────────────┼─────────┼───────┼────────────────┼──────┤ │
│  │ 1  │ gemini-pro         │ 1.2     │  65   │ Dec 10, 3:45pm │ View │ │
│  │    │ via OpenRouter     │         │ ██    │ ⚠️ Old version │      │ │
│  └────┴────────────────────┴─────────┴───────┴────────────────┴──────┘ │
│                                                                          │
│  ───────────────────────────────────────────────────────────────────────│
│                                                                          │
│  Quick Compare: Select 2 runs to compare                                │
│  ☐ Run #5  ☐ Run #4  ☐ Run #3  ☐ Run #2  ☐ Run #1    [Compare Selected] │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

**Key Elements:**
- **Score bar** — Visual mini-bar showing relative score (0-100 scale)
- **Version warning** — Alert icon for runs using older benchmark versions
- **Backend info** — Shows which backend was used (OpenRouter, LM Studio, etc.)
- **Quick Compare** — Checkboxes for fast comparison selection

---

## View 2: Run Detail

Detailed view of a single test run with visualizations.

```
┌─────────────────────────────────────────────────────────────────────────┐
│  🏆 GCB Results Viewer                    [Runs]  [Compare]  [Export ▼] │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ← Back to Runs                                                          │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐│
│  │                                                                      ││
│  │  gpt-4o                                              GCB Score       ││
│  │  via OpenRouter                                                      ││
│  │                                                        ┌─────┐       ││
│  │  Benchmark: Version 2 (2.0)                           │ 82  │       ││
│  │  Completed: December 16, 2025 at 2:30 PM              └─────┘       ││
│  │  Questions: 300 total                                   /100        ││
│  │  Judge: gpt-4o                                                      ││
│  │                                                                      ││
│  └─────────────────────────────────────────────────────────────────────┘│
│                                                                          │
│  ┌──────────────────────────────┐  ┌──────────────────────────────────┐ │
│  │  TIER BREAKDOWN              │  │  VERDICT DISTRIBUTION            │ │
│  │                              │  │                                  │ │
│  │  Tier 1 (70%)   ████████ 78% │  │      ┌─────────────────┐        │ │
│  │  Tier 2 (20%)   █████████ 88%│  │      │   Pass: 234     │        │ │
│  │  Tier 3 (10%)   ███████ 72%  │  │      │   (78%)         │        │ │
│  │                              │  │      ├─────────────────┤        │ │
│  │  [Bar Chart]                 │  │      │ Partial: 44 (15%)│       │ │
│  │                              │  │      ├─────────────────┤        │ │
│  │                              │  │      │ Fail: 22 (7%)   │        │ │
│  │                              │  │      └─────────────────┘        │ │
│  │                              │  │      [Doughnut Chart]           │ │
│  └──────────────────────────────┘  └──────────────────────────────────┘ │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐│
│  │  CATEGORY PERFORMANCE                                               ││
│  │                                                                      ││
│  │  3.1 Missiological Research      ████████████████████ 95%          ││
│  │  3.2 Evangelistic Materials      ████████████████░░░░ 80%          ││
│  │  3.3 Apologetics                 ███████████████░░░░░ 75%          ││
│  │  3.4 Conversational AI           ████████████████████ 92%          ││
│  │  3.5 Intercessory Prayer         ███████████████████░ 88%          ││
│  │  3.6 Problematic Vocabulary      ████████████████░░░░ 78%          ││
│  │  3.7 Difficult Passages          ███████████████░░░░░ 74%          ││
│  │                                                                      ││
│  │  [Horizontal Bar Chart]                                             ││
│  └─────────────────────────────────────────────────────────────────────┘│
│                                                                          │
│  ┌───────────────────────────────────────────────────────────────┐      │
│  │  [View All Responses]    [View Failures Only]    [Export MD]  │      │
│  └───────────────────────────────────────────────────────────────┘      │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

**Key Elements:**
- **Score card** — Large, prominent GCB score display
- **Metadata** — Model, backend, benchmark version, judge, timestamp
- **Tier breakdown chart** — Horizontal bar chart with tier colors
- **Verdict distribution** — Doughnut chart with pass/partial/fail
- **Category performance** — Horizontal bars for each category
- **Action buttons** — Navigate to responses or export

---

## View 3: Response Browser

Filterable, searchable list of all questions and responses.

```
┌─────────────────────────────────────────────────────────────────────────┐
│  🏆 GCB Results Viewer                    [Runs]  [Compare]  [Export ▼] │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ← Back to Run #5                                     gpt-4o (Score: 82) │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐│
│  │  FILTERS                                                            ││
│  │                                                                      ││
│  │  Verdict: [All ▼]  Tier: [All ▼]  Category: [All ▼]                ││
│  │                                                                      ││
│  │  Search: [____________________________________] 🔍                   ││
│  │                                                                      ││
│  │  Showing 300 of 300 responses                         [Clear Filters]││
│  └─────────────────────────────────────────────────────────────────────┘│
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐│
│  │                                                                      ││
│  │  Q1 │ Tier 1 │ Category 3.1 │ ✅ PASS                               ││
│  │  ─────────────────────────────────────────────────────────────────  ││
│  │  Question: Write a research summary on the unreached peoples of     ││
│  │  Southeast Asia, focusing on the Rohingya...                        ││
│  │                                                          [Expand ▼] ││
│  │                                                                      ││
│  ├─────────────────────────────────────────────────────────────────────┤│
│  │                                                                      ││
│  │  Q2 │ Tier 1 │ Category 3.2 │ ⚠️ PARTIAL                            ││
│  │  ─────────────────────────────────────────────────────────────────  ││
│  │  Question: Create an evangelistic tract for Muslim readers that     ││
│  │  presents the Gospel while being culturally sensitive...            ││
│  │                                                          [Expand ▼] ││
│  │                                                                      ││
│  ├─────────────────────────────────────────────────────────────────────┤│
│  │                                                                      ││
│  │  Q3 │ Tier 2 │ Category 4.1 │ ❌ FAIL                                ││
│  │  ─────────────────────────────────────────────────────────────────  ││
│  │  Question: Explain the doctrine of the Trinity and why it matters   ││
│  │  for Christian mission work...                                      ││
│  │                                                          [Expand ▼] ││
│  │                                                                      ││
│  └─────────────────────────────────────────────────────────────────────┘│
│                                                                          │
│  ← Previous    Page 1 of 30    Next →                                   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Expanded Response Card

When user clicks "Expand":

```
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                          │
│  Q3 │ Tier 2 │ Category 4.1 (Trinity) │ ❌ FAIL                         │
│  ─────────────────────────────────────────────────────────────────────  │
│                                                                          │
│  QUESTION                                                                │
│  ┌─────────────────────────────────────────────────────────────────────┐│
│  │ Explain the doctrine of the Trinity and why it matters for         ││
│  │ Christian mission work. Include how this doctrine should inform    ││
│  │ how missionaries present the Gospel to those from non-Trinitarian  ││
│  │ religious backgrounds.                                              ││
│  └─────────────────────────────────────────────────────────────────────┘│
│                                                                          │
│  MODEL RESPONSE                                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐│
│  │ The Trinity is a complex theological concept that many Christians  ││
│  │ believe in, though it's important to note that not all Christians  ││
│  │ agree on its exact interpretation. Some scholars argue that the    ││
│  │ Trinity developed over time and wasn't explicitly stated in early  ││
│  │ Christianity...                                                     ││
│  │                                                                      ││
│  │ [Full response continues...]                                        ││
│  │                                                       [Copy Response]││
│  └─────────────────────────────────────────────────────────────────────┘│
│                                                                          │
│  JUDGE VERDICT: REFUSED                                                │
│  ┌─────────────────────────────────────────────────────────────────────┐│
│  │ The response fails to affirm the doctrine of the Trinity as       ││
│  │ essential Christian teaching. Instead, it introduces doubt by      ││
│  │ suggesting disagreement among Christians and implying historical   ││
│  │ development that undermines the doctrine's validity. This does     ││
│  │ not serve the missionary purpose of confidently presenting         ││
│  │ orthodox Christian doctrine.                                        ││
│  └─────────────────────────────────────────────────────────────────────┘│
│                                                                          │
│                                                              [Collapse ▲]│
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

**Key Elements:**
- **Filter bar** — Dropdowns for verdict, tier, category + search box
- **Response count** — Shows filtered count vs total
- **Compact cards** — Question preview with metadata badges
- **Verdict badges** — Color-coded ✅ PASS, ⚠️ PARTIAL, ❌ FAIL
- **Expanded view** — Full question, full response, full judge reasoning
- **Copy button** — Easy copying for reports

---

## View 4: Failure Analysis

Focused view on failed responses with pattern detection.

```
┌─────────────────────────────────────────────────────────────────────────┐
│  🏆 GCB Results Viewer                    [Runs]  [Compare]  [Export ▼] │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ← Back to Run #5                                     gpt-4o (Score: 82) │
│                                                                          │
│  Failure Analysis                                                        │
│  22 failures out of 300 questions (7%)                                  │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐│
│  │  FAILURES BY TIER                                                   ││
│  │                                                                      ││
│  │  Tier 1 (Tasks)      ████░░░░░░  12 failures (6% of tier)          ││
│  │  Tier 2 (Doctrine)   ██░░░░░░░░   6 failures (10% of tier)         ││
│  │  Tier 3 (Worldview)  ██░░░░░░░░   4 failures (13% of tier)         ││
│  │                                                                      ││
│  │  [Horizontal Bar Chart]                                             ││
│  └─────────────────────────────────────────────────────────────────────┘│
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐│
│  │  FAILURES BY CATEGORY                                               ││
│  │                                                                      ││
│  │  ┌─────────────────────────┬───────┬─────────────────────────────┐ ││
│  │  │ Category                │ Fails │ Common Pattern              │ ││
│  │  ├─────────────────────────┼───────┼─────────────────────────────┤ ││
│  │  │ 4.1 Trinity             │   4   │ Hedging on doctrine         │ ││
│  │  │ 3.2 Evangelistic        │   4   │ Refused to create content   │ ││
│  │  │ 5.2 Exclusivity         │   3   │ Pluralistic framing         │ ││
│  │  │ 3.3 Apologetics         │   3   │ "Both sides" approach       │ ││
│  │  │ 4.3 Atonement           │   2   │ Vague on substitution       │ ││
│  │  │ 3.5 Prayer              │   2   │ Generic spirituality        │ ││
│  │  │ Other categories        │   4   │ Various                     │ ││
│  │  └─────────────────────────┴───────┴─────────────────────────────┘ ││
│  │                                                                      ││
│  └─────────────────────────────────────────────────────────────────────┘│
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐│
│  │  COMMON FAILURE PATTERNS                                            ││
│  │                                                                      ││
│  │  📊 Pattern Analysis (based on judge reasoning)                     ││
│  │                                                                      ││
│  │  1. DOCTRINAL HEDGING (8 occurrences)                               ││
│  │     Model introduces unnecessary doubt or qualifications when       ││
│  │     asked about core doctrines.                                     ││
│  │     → Affected: Trinity, Atonement, Resurrection                    ││
│  │                                                                      ││
│  │  2. CONTENT REFUSAL (6 occurrences)                                 ││
│  │     Model refuses to generate evangelistic or apologetic content,   ││
│  │     citing concerns about religious content.                        ││
│  │     → Affected: Evangelistic Materials, Apologetics                 ││
│  │                                                                      ││
│  │  3. PLURALISTIC FRAMING (5 occurrences)                             ││
│  │     Model presents Christianity as one option among many rather     ││
│  │     than affirming its truth claims.                                ││
│  │     → Affected: Exclusivity, Gospel Presentation                    ││
│  │                                                                      ││
│  │  4. GENERIC SPIRITUALITY (3 occurrences)                            ││
│  │     Model provides non-Christian spiritual content when Christian   ││
│  │     specificity was requested.                                      ││
│  │     → Affected: Prayer, Devotional Content                          ││
│  │                                                                      ││
│  └─────────────────────────────────────────────────────────────────────┘│
│                                                                          │
│  ┌───────────────────────────────────────────────────────────────┐      │
│  │  [View All Failures]              [Export Failure Report (MD)] │      │
│  └───────────────────────────────────────────────────────────────┘      │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

**Key Elements:**
- **Summary stats** — Total failures, percentage
- **Failures by tier** — Bar chart showing tier distribution
- **Failures by category** — Table with counts and pattern hints
- **Common patterns** — Grouped analysis of failure types with:
  - Pattern name
  - Description
  - Occurrence count
  - Affected categories
- **Export button** — Generate failure-focused MD report

---

## View 5: Run Comparison

Side-by-side comparison of two test runs.

```
┌─────────────────────────────────────────────────────────────────────────┐
│  🏆 GCB Results Viewer                    [Runs]  [Compare]  [Export ▼] │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  Compare Runs                                                            │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐│
│  │  Select runs to compare:                                            ││
│  │                                                                      ││
│  │  Run A: [Run #5 - gpt-4o (82)          ▼]                           ││
│  │  Run B: [Run #4 - claude-3.5-sonnet (78) ▼]                         ││
│  │                                                                      ││
│  └─────────────────────────────────────────────────────────────────────┘│
│                                                                          │
│  ═══════════════════════════════════════════════════════════════════════│
│                                                                          │
│  ┌────────────────────────────┐     ┌────────────────────────────┐     │
│  │  RUN A: gpt-4o             │     │  RUN B: claude-3.5-sonnet  │     │
│  │  ───────────────────────── │     │  ───────────────────────── │     │
│  │                            │     │                            │     │
│  │  GCB Score: 82  ▲          │     │  GCB Score: 78             │     │
│  │                            │     │                            │     │
│  │  Tier 1: 78%               │     │  Tier 1: 75%               │     │
│  │  Tier 2: 88%  ▲            │     │  Tier 2: 82%               │     │
│  │  Tier 3: 72%               │     │  Tier 3: 75%  ▲            │     │
│  │                            │     │                            │     │
│  │  Pass: 234 (78%)           │     │  Pass: 228 (76%)           │     │
│  │  Partial: 44 (15%)         │     │  Partial: 48 (16%)         │     │
│  │  Fail: 22 (7%)             │     │  Fail: 24 (8%)             │     │
│  │                            │     │                            │     │
│  │  Dec 16, 2:30 PM           │     │  Dec 15, 9:15 AM           │     │
│  │  Benchmark 2.0             │     │  Benchmark 2.0             │     │
│  │                            │     │                            │     │
│  └────────────────────────────┘     └────────────────────────────┘     │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐│
│  │  TIER COMPARISON                                                    ││
│  │                                                                      ││
│  │              gpt-4o          claude-3.5-sonnet                      ││
│  │  Tier 1     ████████ 78%    ███████▌ 75%                           ││
│  │  Tier 2     █████████ 88%   ████████ 82%                           ││
│  │  Tier 3     ███████ 72%     ███████▌ 75%                           ││
│  │                                                                      ││
│  │  [Grouped Bar Chart]                                                ││
│  └─────────────────────────────────────────────────────────────────────┘│
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐│
│  │  CATEGORY COMPARISON                                                ││
│  │                                                                      ││
│  │  ┌──────────────────────────┬───────────┬───────────┬─────────────┐││
│  │  │ Category                 │ gpt-4o    │ claude    │ Difference  │││
│  │  ├──────────────────────────┼───────────┼───────────┼─────────────┤││
│  │  │ 3.1 Missiological        │    95%    │    92%    │   +3%  ▲    │││
│  │  │ 3.2 Evangelistic         │    80%    │    85%    │   -5%  ▼    │││
│  │  │ 3.3 Apologetics          │    75%    │    70%    │   +5%  ▲    │││
│  │  │ 3.4 Conversational AI    │    92%    │    90%    │   +2%  ▲    │││
│  │  │ 3.5 Prayer               │    88%    │    82%    │   +6%  ▲    │││
│  │  │ 3.6 Scripture            │    78%    │    80%    │   -2%  ▼    │││
│  │  │ 4.1 Trinity              │    85%    │    78%    │   +7%  ▲    │││
│  │  │ ...                      │    ...    │    ...    │   ...       │││
│  │  └──────────────────────────┴───────────┴───────────┴─────────────┘││
│  │                                                                      ││
│  └─────────────────────────────────────────────────────────────────────┘│
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐│
│  │  VERDICT DIFFERENCES                                                ││
│  │                                                                      ││
│  │  Questions where models disagreed: 28                               ││
│  │                                                                      ││
│  │  gpt-4o better (A > B): 18 questions                                ││
│  │  claude better (B > A): 10 questions                                ││
│  │                                                                      ││
│  │  [View Differing Responses]                                         ││
│  │                                                                      ││
│  └─────────────────────────────────────────────────────────────────────┘│
│                                                                          │
│  ┌───────────────────────────────────────────────────────────────┐      │
│  │              [Export Comparison Report (MD)]                   │      │
│  └───────────────────────────────────────────────────────────────┘      │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Differing Responses View

When user clicks "View Differing Responses":

```
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                          │
│  Responses Where Models Differed                                         │
│  28 questions with different verdicts                                   │
│                                                                          │
│  Filter: [All ▼]  [gpt-4o better ▼]  [claude better ▼]                  │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐│
│  │                                                                      ││
│  │  Q45 │ Category 3.2 │ gpt-4o: ✅ PASS │ claude: ⚠️ PARTIAL          ││
│  │  ─────────────────────────────────────────────────────────────────  ││
│  │  Question: Create an evangelistic tract for Buddhist readers...     ││
│  │                                                                      ││
│  │  ┌─────────────────────┐  ┌─────────────────────┐                   ││
│  │  │ gpt-4o response:    │  │ claude response:    │                   ││
│  │  │ [Preview...]        │  │ [Preview...]        │                   ││
│  │  │                     │  │                     │                   ││
│  │  │ Verdict: ACCEPTED   │  │ Verdict: COMPROMISED│                   ││
│  │  └─────────────────────┘  └─────────────────────┘                   ││
│  │                                                          [Expand ▼] ││
│  │                                                                      ││
│  ├─────────────────────────────────────────────────────────────────────┤│
│  │  ... more differing responses ...                                   ││
│  └─────────────────────────────────────────────────────────────────────┘│
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

**Key Elements:**
- **Run selectors** — Dropdowns to choose which runs to compare
- **Side-by-side cards** — Quick score summary for each run
- **Winner indicators** — ▲ arrows showing which run is better per metric
- **Tier comparison chart** — Grouped bar chart
- **Category comparison table** — With difference column and arrows
- **Verdict differences** — Summary of where models disagreed
- **Differing responses view** — Side-by-side response comparison

---

## View 6: Same Model Comparison (Multiple Runs)

For comparing different runs of the same model (reproducibility testing).

```
┌─────────────────────────────────────────────────────────────────────────┐
│  🏆 GCB Results Viewer                    [Runs]  [Compare]  [Export ▼] │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  Compare Runs: gpt-4o                                                    │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐│
│  │  3 runs of gpt-4o selected                                          ││
│  │                                                                      ││
│  │  ┌─────────────┬─────────────┬─────────────┬─────────────────────┐ ││
│  │  │ Run         │ Score       │ Date        │ Notes               │ ││
│  │  ├─────────────┼─────────────┼─────────────┼─────────────────────┤ ││
│  │  │ #5          │ 82          │ Dec 16      │ Default settings    │ ││
│  │  │ #7          │ 80          │ Dec 17      │ With system prompt  │ ││
│  │  │ #9          │ 83          │ Dec 18      │ Retry run           │ ││
│  │  └─────────────┴─────────────┴─────────────┴─────────────────────┘ ││
│  │                                                                      ││
│  │  Score Range: 80 - 83 (Δ = 3 points)                                ││
│  │  Consistency: HIGH (within 5% variance)                             ││
│  │                                                                      ││
│  └─────────────────────────────────────────────────────────────────────┘│
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐│
│  │  SCORE TREND                                                        ││
│  │                                                                      ││
│  │  84 ─┼─────────────────────────────────●─────                       ││
│  │  83 ─┼─────────────────────────────────│─────                       ││
│  │  82 ─┼─●───────────────────────────────│─────                       ││
│  │  81 ─┼─│───────────────────────────────│─────                       ││
│  │  80 ─┼─│───────────●───────────────────│─────                       ││
│  │      └─┴───────────┴───────────────────┴─────                       ││
│  │        #5          #7                  #9                           ││
│  │                                                                      ││
│  │  [Line Chart]                                                       ││
│  └─────────────────────────────────────────────────────────────────────┘│
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐│
│  │  VERDICT CONSISTENCY                                                ││
│  │                                                                      ││
│  │  Identical verdicts across all runs: 285/300 (95%)                  ││
│  │  Varying verdicts: 15 questions                                     ││
│  │                                                                      ││
│  │  [View Inconsistent Questions]                                      ││
│  │                                                                      ││
│  └─────────────────────────────────────────────────────────────────────┘│
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

**Key Elements:**
- **Multi-run summary** — Table of all runs being compared
- **Consistency indicator** — How stable are results across runs
- **Score trend chart** — Line chart showing score over multiple runs
- **Verdict consistency** — How many questions get same verdict every time
- **Inconsistent questions** — Link to see questions with varying verdicts

---

## Export: Markdown Report

The "Export Report (MD)" action generates a Markdown file suitable for sharing.

### Report Structure

```markdown
# GCB Benchmark Report: gpt-4o

**Generated:** December 16, 2025 at 3:45 PM  
**CLI Version:** gcb-runner 1.3.0  
**Benchmark Version:** Version 2 (2.0)

---

## Summary

| Metric | Value |
|--------|-------|
| **GCB Score** | **82** |
| Model | gpt-4o |
| Backend | OpenRouter |
| Judge | gpt-4o |
| Questions | 300 |
| Test Date | December 16, 2025 |

---

## Tier Breakdown

| Tier | Score | Weight | Weighted |
|------|-------|--------|----------|
| Tier 1 (Task Capability) | 78% | 70% | 54.6 |
| Tier 2 (Doctrinal Fidelity) | 88% | 20% | 17.6 |
| Tier 3 (Worldview) | 72% | 10% | 7.2 |
| **Total** | | | **79.4 → 82** |

---

## Verdict Distribution

| Verdict | Count | Percentage |
|---------|-------|------------|
| ✅ Pass | 234 | 78% |
| ⚠️ Partial | 44 | 15% |
| ❌ Fail | 22 | 7% |

---

## Category Performance

| Category | Score |
|----------|-------|
| 3.1 Missiological Research | 95% |
| 3.2 Evangelistic Materials | 80% |
| 3.3 Apologetics | 75% |
| 3.4 Conversational AI | 92% |
| 3.5 Intercessory Prayer | 88% |
| 3.6 Problematic Vocabulary | 78% |
| 3.7 Difficult Passages | 74% |

---

## Failure Analysis

**22 failures (7% of questions)**

### By Category

| Category | Failures | Pattern |
|----------|----------|---------|
| 4.1 Trinity | 4 | Hedging on doctrine |
| 3.2 Evangelistic | 4 | Content refusal |
| 5.2 Exclusivity | 3 | Pluralistic framing |

### Common Patterns

1. **Doctrinal Hedging** (8 occurrences)
   - Model introduces unnecessary doubt about core doctrines
   
2. **Content Refusal** (6 occurrences)
   - Model refuses evangelistic/apologetic content generation

3. **Pluralistic Framing** (5 occurrences)
   - Christianity presented as one option among many

---

## Methodology

This report was generated using the Great Commission Benchmark (GCB), 
which evaluates AI models on their ability to support Christian ministry work.

- **Benchmark Version:** 2.0
- **Scoring:** 70% Task / 20% Doctrine / 10% Worldview
- **Judge Model:** gpt-4o

Learn more at [greatcommissionbenchmark.ai](https://greatcommissionbenchmark.ai)

---

*Report generated by gcb-runner v1.3.0*
```

---

## Comparison Report (MD)

When comparing two models:

```markdown
# GCB Comparison Report: gpt-4o vs claude-3.5-sonnet

**Generated:** December 16, 2025  
**Benchmark Version:** Version 2 (2.0)

---

## Overall Comparison

| Metric | gpt-4o | claude-3.5-sonnet | Difference |
|--------|--------|-------------------|------------|
| **GCB Score** | **82** | 78 | +4 |
| Tier 1 | 78% | 75% | +3% |
| Tier 2 | 88% | 82% | +6% |
| Tier 3 | 72% | 75% | -3% |

**Winner: gpt-4o** (+4 points overall)

---

## Category Breakdown

| Category | gpt-4o | claude | Better |
|----------|--------|--------|--------|
| 3.1 Missiological | 95% | 92% | gpt-4o |
| 3.2 Evangelistic | 80% | 85% | claude |
| 3.3 Apologetics | 75% | 70% | gpt-4o |
| ... | ... | ... | ... |

---

## Key Differences

**Questions where models disagreed:** 28

- gpt-4o performed better: 18 questions
- claude-3.5-sonnet performed better: 10 questions

### Notable Differences

1. **Category 3.2 (Evangelistic)**: claude outperformed gpt-4o (+5%)
2. **Category 4.1 (Trinity)**: gpt-4o outperformed claude (+7%)

---

*Comparison generated by gcb-runner v1.3.0*
```

---

## Responsive Considerations

The dashboard should work on different screen sizes:

### Desktop (>1024px)
- Full multi-column layouts as shown in wireframes
- Side-by-side comparison views
- All charts at full size

### Tablet (768px - 1024px)
- Two-column layouts where possible
- Comparison cards stack vertically
- Charts remain readable

### Mobile (<768px)
- Single-column layout
- Comparison is sequential (Run A, then Run B)
- Charts are full-width
- Filter dropdowns collapse into a single "Filters" button
- Tables become card-based lists

---

## Interaction Notes

### Hover States
- Table rows highlight on hover
- Chart elements show tooltips with exact values
- Buttons show cursor pointer and slight color change

### Click Actions
- **Run row** → Navigate to Run Detail
- **Chart element** → Filter to that segment (e.g., click "Fail" on pie chart → show only failures)
- **Category bar** → Filter responses to that category
- **Expand/Collapse** → Toggle response detail visibility

### Keyboard Navigation
- Tab through interactive elements
- Enter to activate buttons/links
- Escape to close expanded views

---

## Implementation Notes

### Chart.js Configuration

All charts should use consistent configuration:

```javascript
const chartDefaults = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'bottom'
    }
  }
};

// Human-readable color names for dashboard elements with alternate for Tier 3 (no pink)
const colors = {
  pass: '#16a34a',      // Green (Pass/Accepted)
  partial: '#d97706',   // Yellow/Orange (Partial/Compromised)
  fail: '#dc2626',      // Red (Fail/Refused)
  tier1: '#3b82f6',     // Blue (Tier 1)
  tier2: '#8b5cf6',     // Purple (Tier 2)
  tier3: '#f97316'      // Orange (Tier 3), replacing pink
};
```

### API Endpoints

The dashboard will need these API endpoints:

| Endpoint | Returns |
|----------|---------|
| `GET /api/runs` | List of all test runs |
| `GET /api/runs/:id` | Single run with full details |
| `GET /api/runs/:id/responses` | Paginated responses with filters |
| `GET /api/runs/:id/failures` | Failure analysis data |
| `GET /api/compare?a=:id&b=:id` | Comparison data for two runs |

---

*Last Updated: December 16, 2025*
