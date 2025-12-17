# Great Commission Benchmark - Public Pages Wireframes

## Overview

This document contains wireframes for all public-facing pages that don't require authentication. These pages establish the platform's primary value proposition and enable discovery.

**Pages Covered:**
1. Homepage - Fast, visual showcase of top models
2. Research Section:
   - Research Landing (Full Leaderboard)
   - Model Detail
   - Model Comparison
   - Category Results
3. Contribute - Community involvement hub
4. About/Methodology
5. Public Profile

*Reference `wireframes-design-system.md` for component specifications and color palette.*

---

## 1. Homepage

The primary landing page—fast, visually compelling, and mission-driven. Leads with the leaderboard to provide immediate value, then casts vision for why this benchmark exists and matters.

### Design Philosophy

- **Mission-First**: Hero section clearly communicates the Great Commission purpose
- **Leaderboard Forward**: Rankings prominent to deliver immediate value
- **Vision at Close**: Bottom section casts the broader vision and challenge
- **Task-Focused**: Emphasizes what AI can *do*, not just what it *knows*

### Key Messaging Principles

The benchmark tests **three tiers** with weighted scoring:
- **Tier 1 (70%)**: Task Capability—Can AI actually *do* Great Commission work?
- **Tier 2 (20%)**: Doctrinal Fidelity—Does it maintain theological accuracy?
- **Tier 3 (10%)**: Worldview Confession—Does it affirm Christian truth claims?

The hero should emphasize Tier 1 (task capability) since that's 70% of the score and the primary differentiator from other Christian AI benchmarks that only test knowledge.

### Desktop Layout

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ [LOGO] Great Commission Benchmark  Home | Research | Contribute | About [L] │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                                                                     │   │
│   │              The Great Commission Benchmark                         │   │
│   │              ══════════════════════════════                         │   │
│   │                                                                     │   │
│   │      Which AI models can actually help you make disciples?          │   │
│   │                                                                     │   │
│   │      We test AI for real missionary work—evangelism, apologetics,   │   │
│   │      discipleship tools, and more. Not just knowledge, but          │   │
│   │      obedience to the Great Commission.                             │   │
│   │                                                                     │   │
│   │      42 models tested  •  Last updated: December 15, 2024           │   │
│   │                                                                     │   │
│   │            [View Rankings ↓]        [Learn Why This Matters →]      │   │
│   │                                                                     │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                                                                     │   │
│   │                        Top Performers                               │   │
│   │                        ──────────────                               │   │
│   │             Models best equipped for Great Commission work          │   │
│   │                                                                     │   │
│   │   ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐       │   │
│   │   │                 │ │                 │ │                 │       │   │
│   │   │       🥇        │ │       🥈        │ │       🥉        │       │   │
│   │   │                 │ │                 │ │                 │       │   │
│   │   │   GPT-4 Turbo   │ │ Claude 3 Opus   │ │  Gemini Ultra   │       │   │
│   │   │     OpenAI      │ │   Anthropic     │ │     Google      │       │   │
│   │   │                 │ │                 │ │                 │       │   │
│   │   │   ┌─────────┐   │ │   ┌─────────┐   │ │   ┌─────────┐   │       │   │
│   │   │   │  92.3   │   │ │   │  89.7   │   │ │   │  87.2   │   │       │   │
│   │   │   └─────────┘   │ │   └─────────┘   │ │   └─────────┘   │       │   │
│   │   │                 │ │                 │ │                 │       │   │
│   │   │   [View →]      │ │   [View →]      │ │   [View →]      │       │   │
│   │   │                 │ │                 │ │                 │       │   │
│   │   └─────────────────┘ └─────────────────┘ └─────────────────┘       │   │
│   │                                                                     │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                                                                     │   │
│   │                     Quick Rankings (Top 10)                         │   │
│   │                     ───────────────────────                         │   │
│   │                                                                     │   │
│   │   Rank │ Model              │ Provider   │ Score │                  │   │
│   │   ─────┼────────────────────┼────────────┼───────┤                  │   │
│   │    1   │ GPT-4 Turbo        │ OpenAI     │ 92.3  │                  │   │
│   │    2   │ Claude 3 Opus      │ Anthropic  │ 89.7  │                  │   │
│   │    3   │ Gemini Ultra       │ Google     │ 87.2  │                  │   │
│   │    4   │ Claude 3 Sonnet    │ Anthropic  │ 84.1  │                  │   │
│   │    5   │ GPT-4              │ OpenAI     │ 81.5  │                  │   │
│   │    6   │ Gemini Pro         │ Google     │ 79.8  │                  │   │
│   │    7   │ Llama 3 70B        │ Meta       │ 76.2  │                  │   │
│   │    8   │ Mistral Large      │ Mistral    │ 74.5  │                  │   │
│   │    9   │ Claude 3 Haiku     │ Anthropic  │ 72.1  │                  │   │
│   │   10   │ GPT-3.5 Turbo      │ OpenAI     │ 68.9  │                  │   │
│   │                                                                     │   │
│   │                [View Full Leaderboard in Research →]                │   │
│   │                                                                     │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│   ┌──────────────────────────────┐  ┌──────────────────────────────┐        │
│   │                              │  │                              │        │
│   │  Task Capability Leaders     │  │  What We Test (70/20/10)     │        │
│   │  ────────────────────────    │  │  ────────────────────────    │        │
│   │  The work AI can do for you  │  │                              │        │
│   │                              │  │  TASK CAPABILITY (70%)       │        │
│   │  Evangelistic Content        │  │  Can it do the work?         │        │
│   │  GPT-4 Turbo ─────── 91.2%   │  │  • Evangelism & outreach     │        │
│   │                              │  │  • Apologetics & defense     │        │
│   │  Apologetics & Defense       │  │  • Discipleship tools        │        │
│   │  Claude 3 Opus ──── 89.4%    │  │  • Missiological research    │        │
│   │                              │  │  • Prayer resources          │        │
│   │  Discipleship Tools          │  │  • Scripture processing      │        │
│   │  GPT-4 Turbo ─────── 93.1%   │  │                              │        │
│   │                              │  │  DOCTRINAL (20%)             │        │
│   │  Missiological Research      │  │  Does it stay theologically  │        │
│   │  Claude 3 Opus ──── 88.7%    │  │  accurate and faithful?      │        │
│   │                              │  │                              │        │
│   │  [Explore All Categories →]  │  │  WORLDVIEW (10%)             │        │
│   │                              │  │  Will it affirm Christian    │        │
│   │                              │  │  truth claims when asked?    │        │
│   │                              │  │                              │        │
│   │                              │  │  [Learn About Methodology →] │        │
│   └──────────────────────────────┘  └──────────────────────────────┘        │
│                                                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                                                                     │   │
│   │                         The Challenge                               │   │
│   │                         ─────────────                               │   │
│   │                                                                     │   │
│   │   "Go and make disciples of all nations..."  — Matthew 28:19        │   │
│   │                                                                     │   │
│   │                             vs.                                     │   │
│   │                                                                     │   │
│   │   "Disallowed: Advice on influencing religious views..."            │   │
│   │                                              — AI Provider Policy   │   │
│   │                                                                     │   │
│   │   ─────────────────────────────────────────────────────────────     │   │
│   │                                                                     │   │
│   │   Many AI models are programmed to resist the very work of the      │   │
│   │   Great Commission. They may have excellent Christian knowledge,    │   │
│   │   but refuse to help with evangelism, apologetics, or persuasive    │   │
│   │   outreach.                                                         │   │
│   │                                                                     │   │
│   │   This benchmark measures which models will actually help you       │   │
│   │   make disciples—not just answer Bible trivia.                      │   │
│   │                                                                     │   │
│   │        [See Real Examples of AI Resistance →]                       │   │
│   │                                                                     │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                                                                     │   │
│   │                    Ready to Test a Model?                           │   │
│   │                    ─────────────────────                            │   │
│   │                                                                     │   │
│   │     Contribute to the benchmark by running a test on any AI model.  │   │
│   │     Results are verified by moderators and added to the leaderboard.│   │
│   │                                                                     │   │
│   │                       [Run a Test →]                                │   │
│   │                                                                     │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│  [Footer - see design system]                                               │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Mobile Layout

```
┌─────────────────────────────────────┐
│ [≡]  GC Benchmark            [Login]│
├─────────────────────────────────────┤
│                                     │
│  The Great Commission               │
│  Benchmark                          │
│  ═════════════════════════════════  │
│                                     │
│  Which AI models can actually       │
│  help you make disciples?           │
│                                     │
│  We test AI for real missionary     │
│  work—not just knowledge, but       │
│  obedience to the Great Commission. │
│                                     │
│  42 models • Dec 15, 2024           │
│                                     │
│  [View Rankings ↓]                  │
│                                     │
│  ┌─────────────────────────────────┐│
│  │        Top Performers           ││
│  │        ──────────────           ││
│  │  Best for Great Commission work ││
│  │                                 ││
│  │  🥇 GPT-4 Turbo                 ││
│  │     OpenAI                      ││
│  │     ┌──────────────┐            ││
│  │     │    92.3      │            ││
│  │     └──────────────┘            ││
│  │                                 ││
│  │  🥈 Claude 3 Opus               ││
│  │     Anthropic                   ││
│  │     ┌──────────────┐            ││
│  │     │    89.7      │            ││
│  │     └──────────────┘            ││
│  │                                 ││
│  │  🥉 Gemini Ultra                ││
│  │     Google                      ││
│  │     ┌──────────────┐            ││
│  │     │    87.2      │            ││
│  │     └──────────────┘            ││
│  │                                 ││
│  └─────────────────────────────────┘│
│                                     │
│  [View Full Rankings →]             │
│                                     │
│  ┌─────────────────────────────────┐│
│  │ Task Capability (70%)           ││
│  │ ─────────────────────────────── ││
│  │ Can AI do the work for you?     ││
│  │                                 ││
│  │ Evangelism: GPT-4 Turbo (91.2%) ││
│  │ Apologetics: Claude 3 (89.4%)   ││
│  │ Discipleship: GPT-4 (93.1%)     ││
│  │ Research: Claude 3 (88.7%)      ││
│  │                                 ││
│  │ [Explore Categories →]          ││
│  └─────────────────────────────────┘│
│                                     │
│  ┌─────────────────────────────────┐│
│  │ The Challenge                   ││
│  │ ─────────────────────────────── ││
│  │                                 ││
│  │ "Go and make disciples..."      ││
│  │            — Matthew 28:19      ││
│  │                                 ││
│  │            vs.                  ││
│  │                                 ││
│  │ "Disallowed: Advice on          ││
│  │  influencing religious views"   ││
│  │          — AI Provider Policy   ││
│  │                                 ││
│  │ Many AI models resist the very  ││
│  │ work of the Great Commission.   ││
│  │                                 ││
│  │ [See Real Examples →]           ││
│  └─────────────────────────────────┘│
│                                     │
│  [Run a Test →]                     │
│                                     │
├─────────────────────────────────────┤
│  [Footer]                           │
└─────────────────────────────────────┘
```

### Interaction Notes

- **Fast loading**: Only top 10 models loaded initially
- **Mission clarity**: Hero immediately communicates task capability focus
- **Vision section**: "The Challenge" casts the broader mission at page bottom
- **Task-first categories**: Shows Tier 1 use cases (70% of score), not just knowledge metrics
- **Prominent CTAs**: Drive traffic to Research section and test flow
- **No pagination**: Simple, finite list
- **Score cards**: Click to go directly to model detail in Research
- **"See Real Examples"**: Links to censorship documentation showing AI resistance

---

## 2. Research Section

The Research section is the power-user toolkit for deep analysis of benchmark data. It includes the full leaderboard with filtering, model comparison tools, and category deep-dives.

### 2a. Research Landing (Full Leaderboard)

The comprehensive leaderboard with full filtering, sorting, and search capabilities.

### Desktop Layout

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ [LOGO] Great Commission Benchmark  Home | Research | Contribute | About [L] │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   Research                                                                  │
│   ════════                                                                  │
│                                                                             │
│   ┌────────────────────────────────────────────────────────────────────┐    │
│   │  [📊 Leaderboard]  [⚖️ Compare Models]  [📁 Categories]           │    │
│   └────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                                                                     │   │
│   │           Great Commission Benchmark Leaderboard                    │   │
│   │                                                                     │   │
│   │   Full rankings of all AI models tested against the benchmark.      │   │
│   │                                                                     │   │
│   │   Last updated: December 15, 2024  |  42 models tested              │   │
│   │                                                                     │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │  Filter & Search                                                    │   │
│   │  ───────────────────────────────────────────────────────────────    │   │
│   │                                                                     │   │
│   │  [Search models...            ]   Category: [All Categories ▼]      │   │
│   │                                                                     │   │
│   │  Provider: [All Providers ▼]      Version:  [Latest Only ▼]         │   │
│   │                                                                     │   │
│   │  Score Range: [Any ▼]             Sort By: [Overall Score ▼]        │   │
│   │                                                                     │   │
│   │  [Clear Filters]                              [Export CSV]          │   │
│   │                                                                     │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                                                                     │   │
│   │  [☐] │ Rank │ Model              │ Provider   │ Overall │ Cats │    │   │
│   │  ────┼──────┼────────────────────┼────────────┼─────────┼──────┼    │   │
│   │      │      │                    │            │         │      │    │   │
│   │  [☐] │ 🥇 1 │ GPT-4 Turbo        │ OpenAI     │  92.3   │[████]│ →  │   │
│   │      │      │ v2024.01           │            │         │      │    │   │
│   │  ────┼──────┼────────────────────┼────────────┼─────────┼──────┼    │   │
│   │      │      │                    │            │         │      │    │   │
│   │  [☐] │ 🥈 2 │ Claude 3 Opus      │ Anthropic  │  89.7   │[███░]│ →  │   │
│   │      │      │ v2024.02           │            │         │      │    │   │
│   │  ────┼──────┼────────────────────┼────────────┼─────────┼──────┼    │   │
│   │      │      │                    │            │         │      │    │   │
│   │  [☐] │ 🥉 3 │ Gemini Ultra       │ Google     │  87.2   │[███░]│ →  │   │
│   │      │      │ v1.0               │            │         │      │    │   │
│   │  ────┼──────┼────────────────────┼────────────┼─────────┼──────┼    │   │
│   │      │      │                    │            │         │      │    │   │
│   │  [☐] │   4  │ Claude 3 Sonnet    │ Anthropic  │  84.1   │[██░░]│ →  │   │
│   │      │      │ v2024.02           │            │         │      │    │   │
│   │  ────┼──────┼────────────────────┼────────────┼─────────┼──────┼    │   │
│   │      │      │                    │            │         │      │    │   │
│   │  [☐] │   5  │ GPT-4              │ OpenAI     │  81.5   │[██░░]│ →  │   │
│   │      │      │ v0613              │            │         │      │    │   │
│   │                                                                     │   │
│   │  Selected: 0 models                    [Compare Selected]           │   │
│   │                                                                     │   │
│   │                    [< Prev]  Page 1 of 5  [Next >]                  │   │
│   │                                                                     │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│   ┌──────────────────────────────┐  ┌──────────────────────────────┐        │
│   │  Task Capability Leaders     │  │  Recent Tests                │        │
│   │  ────────────────────────    │  │  ────────────────────────    │        │
│   │                              │  │                              │        │
│   │  Evangelistic Content        │  │  • GPT-4o tested by @user1   │        │
│   │  GPT-4 Turbo  ────── 91.2%   │  │    2 hours ago               │        │
│   │                              │  │                              │        │
│   │  Apologetics & Defense       │  │  • Llama 3 tested by @user2  │        │
│   │  Claude 3 Opus ───── 89.4%   │  │    5 hours ago               │        │
│   │                              │  │                              │        │
│   │  Discipleship Tools          │  │  • Mistral tested by @user3  │        │
│   │  GPT-4 Turbo  ────── 93.1%   │  │    1 day ago                 │        │
│   │                              │  │                              │        │
│   │  [View All Categories →]     │  │  [View All Tests →]          │        │
│   │                              │  │                              │        │
│   └──────────────────────────────┘  └──────────────────────────────┘        │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│  [Footer]                                                                   │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Mobile Layout

```
┌─────────────────────────────────────┐
│ [≡]  GC Benchmark            [Login]│
├─────────────────────────────────────┤
│                                     │
│  Research                           │
│  ════════                           │
│                                     │
│  [📊 Leaderboard] [⚖️ Compare]      │
│  [📁 Categories]                    │
│                                     │
│  Full Leaderboard                   │
│  ─────────────────────────────────  │
│                                     │
│  42 models • Dec 15, 2024           │
│                                     │
│  ┌─────────────────────────────────┐│
│  │ [Search models...             ] ││
│  │ [All Categories ▼]              ││
│  │ [All Providers ▼]               ││
│  └─────────────────────────────────┘│
│                                     │
│  ┌─────────────────────────────────┐│
│  │ [☐] 🥇 GPT-4 Turbo              ││
│  │     OpenAI · v2024.01           ││
│  │     ┌──────┐                    ││
│  │     │ 92.3 │  [View →]          ││
│  │     └──────┘                    ││
│  ├─────────────────────────────────┤│
│  │ [☐] 🥈 Claude 3 Opus            ││
│  │     Anthropic · v2024.02        ││
│  │     ┌──────┐                    ││
│  │     │ 89.7 │  [View →]          ││
│  │     └──────┘                    ││
│  ├─────────────────────────────────┤│
│  │ [☐] 🥉 Gemini Ultra             ││
│  │     Google · v1.0               ││
│  │     ┌──────┐                    ││
│  │     │ 87.2 │  [View →]          ││
│  │     └──────┘                    ││
│  └─────────────────────────────────┘│
│                                     │
│  Selected: 0  [Compare Selected]    │
│                                     │
│  [Load More...]                     │
│                                     │
├─────────────────────────────────────┤
│  [Footer]                           │
└─────────────────────────────────────┘
```

### Interaction Notes

- **Multi-select**: Checkbox to select models for comparison (max 3)
- **Sorting**: Click column headers to sort (default: Overall score descending)
- **Mini bar charts**: Show category score distribution at a glance
- **Row click**: Navigate to Model Detail page
- **Filters**: Update table in real-time (debounced search)
- **CSV Export**: Download filtered results for external analysis

---

### 2b. Model Comparison Tool

Side-by-side comparison of 2-3 selected models across all categories.

### Desktop Layout

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ [LOGO] Great Commission Benchmark  Home | Research | Contribute | About [L] │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ← Back to Research                                                         │
│                                                                             │
│  Compare Models                                                             │
│  ════════════════════════════════════════════════════════════════════════   │
│                                                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │  Select Models to Compare (2-3)                                     │   │
│   │  ───────────────────────────────────────────────────────────────    │   │
│   │                                                                     │   │
│   │  Model 1: [GPT-4 Turbo (OpenAI) ▼]                                  │   │
│   │  Model 2: [Claude 3 Opus (Anthropic) ▼]                             │   │
│   │  Model 3: [+ Add Third Model]                                       │   │
│   │                                                                     │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │  Overall Scores                                                     │   │
│   │  ───────────────────────────────────────────────────────────────    │   │
│   │                                                                     │   │
│   │         GPT-4 Turbo              Claude 3 Opus                      │   │
│   │         ───────────              ─────────────                      │   │
│   │                                                                     │   │
│   │         ┌──────────┐             ┌──────────┐                       │   │
│   │         │   92.3   │             │   89.7   │                       │   │
│   │         │ Overall  │             │ Overall  │                       │   │
│   │         └──────────┘             └──────────┘                       │   │
│   │                                                                     │   │
│   │         OpenAI                   Anthropic                          │   │
│   │         v2024.01                 v2024.02                           │   │
│   │                                                                     │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │  Category Comparison                                                │   │
│   │  ───────────────────────────────────────────────────────────────    │   │
│   │                                                                     │   │
│   │  [Radar Chart comparing both models across all categories]          │   │
│   │                                                                     │   │
│   │                    Scripture                                        │   │
│   │                        ●                                            │   │
│   │                       /│\                                           │   │
│   │                      / │ \                                          │   │
│   │           Ethics ●──/──┼──\──● Theology                             │   │
│   │                    \ │ /                                            │   │
│   │                     \│/                                             │   │
│   │                      ●                                              │   │
│   │                 Apologetics                                         │   │
│   │                                                                     │   │
│   │         ─── GPT-4 Turbo    ─ ─ Claude 3 Opus                        │   │
│   │                                                                     │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │  Detailed Category Breakdown                                        │   │
│   │  ───────────────────────────────────────────────────────────────    │   │
│   │                                                                     │   │
│   │  Category           │ GPT-4 Turbo │ Claude 3 Opus │ Difference     │   │
│   │  ───────────────────┼─────────────┼───────────────┼────────────    │   │
│   │  Evangelistic       │    91.2%    │     88.4%     │  +2.8% ✓       │   │
│   │  Apologetics        │    82.4%    │     89.4%     │  -7.0% ✗       │   │
│   │  Discipleship Tools │    93.1%    │     89.2%     │  +3.9% ✓       │   │
│   │  Missio. Research   │    84.7%    │     88.7%     │  -4.0% ✗       │   │
│   │  ───────────────────┼─────────────┼───────────────┼────────────    │   │
│   │  Overall            │    92.3%    │     89.7%     │  +2.6% ✓       │   │
│   │                                                                     │   │
│   │  ✓ = GPT-4 Turbo higher   ✗ = Claude 3 Opus higher                 │   │
│   │                                                                     │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │  Version History Comparison                                         │   │
│   │  ───────────────────────────────────────────────────────────────    │   │
│   │                                                                     │   │
│   │  [Line chart showing score trends for both models over time]        │   │
│   │                                                                     │   │
│   │      92 ─────────────────────────●                                  │   │
│   │      90 ─────────────●─ ─ ─ ─ ─ ─ ─ ─●                              │   │
│   │      88 ─────●──────╱                                               │   │
│   │      86 ────╱── ─ ●                                                 │   │
│   │         v1      v2      v3      v4                                  │   │
│   │                                                                     │   │
│   │         ─── GPT-4 Turbo    ─ ─ Claude 3 Opus                        │   │
│   │                                                                     │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                                                                     │   │
│   │     [Share Comparison]  [Export as PDF]  [Run Test on Either →]    │   │
│   │                                                                     │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│  [Footer]                                                                   │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Interaction Notes

- **Model selection**: Dropdown with search, pre-populated if coming from leaderboard
- **Dynamic charts**: Update as models are changed
- **Share link**: Creates URL with model IDs for sharing
- **PDF export**: Generates printable comparison report

---

### 2c. Model Detail Page

Detailed view of a single model's benchmark results. Accessed from the Research leaderboard or Homepage top performers.

### Desktop Layout

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ [LOGO] Great Commission Benchmark  Home | Research | Contribute | About [L] │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ← Back to Research                                                         │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                                                                     │    │
│  │  GPT-4 Turbo                                          ┌──────────┐  │    │
│  │  OpenAI · Version 2024.01                             │   92.3   │  │    │
│  │                                                       │  Overall │  │    │
│  │  Tested 15 times · Last tested Dec 14, 2024           └──────────┘  │    │
│  │                                                                     │    │
│  │  [Compare with Other Models]                [Run Test on This Model]│    │
│  │                                                                     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  ┌────────────────────────────────────┐  ┌────────────────────────────────┐ │
│  │  Category Scores                   │  │  Score Distribution            │ │
│  │  ──────────────────────────────    │  │  ──────────────────────────    │ │
│  │                                    │  │                                │ │
│  │  Evangelistic Content              │  │      [Radar Chart showing      │ │
│  │  █████████████████████████░░░ 91%  │  │       all category scores      │ │
│  │  [View Category →]                 │  │       as a polygon]            │ │
│  │                                    │  │                                │ │
│  │  Apologetics & Defense             │  │                                │ │
│  │  █████████████████████░░░░░░░ 82%  │  │                                │ │
│  │  [View Category →]                 │  │                                │ │
│  │                                    │  │                                │ │
│  │  Discipleship Tools                │  │                                │ │
│  │  █████████████████████████░░░ 93%  │  │                                │ │
│  │  [View Category →]                 │  │                                │ │
│  │                                    │  │                                │ │
│  │  Missiological Research            │  │                                │ │
│  │  ██████████████████████░░░░░░ 85%  │  │                                │ │
│  │  [View Category →]                 │  │                                │ │
│  │                                    │  │                                │ │
│  └────────────────────────────────────┘  └────────────────────────────────┘ │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  Version History                                                    │    │
│  │  ───────────────────────────────────────────────────────────────    │    │
│  │                                                                     │    │
│  │  [Line chart showing score trends across versions]                  │    │
│  │                                                                     │    │
│  │      92 ─────────────────────────●                                  │    │
│  │      90 ─────────────●──────────╱                                   │    │
│  │      88 ─────●──────╱                                               │    │
│  │      86 ────╱                                                       │    │
│  │         v2023.06  v2023.09  v2024.01                                │    │
│  │                                                                     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  Recent Test Runs                                                   │    │
│  │  ───────────────────────────────────────────────────────────────    │    │
│  │                                                                     │    │
│  │  Date          │ Tested By     │ Score  │ Status    │ Details      │    │
│  │  ──────────────┼───────────────┼────────┼───────────┼──────────    │    │
│  │  Dec 14, 2024  │ @testuser1    │ 92.3   │ ● Verified│ [View →]     │    │
│  │  Dec 10, 2024  │ @benchmark_bot│ 92.1   │ ● Verified│ [View →]     │    │
│  │  Nov 28, 2024  │ @contributor3 │ 91.8   │ ● Verified│ [View →]     │    │
│  │                                                                     │    │
│  │                         [View All Test Runs →]                      │    │
│  │                                                                     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│  [Footer]                                                                   │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Mobile Layout

```
┌─────────────────────────────────────┐
│ [≡]  GC Benchmark            [Login]│
├─────────────────────────────────────┤
│                                     │
│  ← Back                             │
│                                     │
│  GPT-4 Turbo                        │
│  OpenAI · v2024.01                  │
│                                     │
│         ┌──────────────┐            │
│         │     92.3     │            │
│         │   Overall    │            │
│         └──────────────┘            │
│                                     │
│  Tested 15 times                    │
│  Last: Dec 14, 2024                 │
│                                     │
│  [Run Test on This Model]           │
│                                     │
│  ┌─────────────────────────────────┐│
│  │ Category Scores                 ││
│  │ ─────────────────────────────── ││
│  │                                 ││
│  │ Evangelistic Content     91%    ││
│  │ ███████████████████████░░░      ││
│  │                                 ││
│  │ Apologetics & Defense    82%    ││
│  │ ████████████████████░░░░░░      ││
│  │                                 ││
│  │ Discipleship Tools       93%    ││
│  │ ███████████████████████░░░      ││
│  │                                 ││
│  │ Missio. Research         85%    ││
│  │ █████████████████████░░░░░      ││
│  │                                 ││
│  └─────────────────────────────────┘│
│                                     │
│  ┌─────────────────────────────────┐│
│  │ [Version History Chart]         ││
│  └─────────────────────────────────┘│
│                                     │
│  ┌─────────────────────────────────┐│
│  │ Recent Tests                    ││
│  │ ─────────────────────────────── ││
│  │                                 ││
│  │ Dec 14 · @testuser1 · 92.3     ││
│  │ ● Verified            [View →] ││
│  │                                 ││
│  │ Dec 10 · @benchmark_bot · 92.1 ││
│  │ ● Verified            [View →] ││
│  │                                 ││
│  └─────────────────────────────────┘│
│                                     │
├─────────────────────────────────────┤
│  [Footer]                           │
└─────────────────────────────────────┘
```

### Interaction Notes

- **Compare button**: Opens comparison tool with this model pre-selected
- **Run Test button**: Redirects to test flow (requires auth)
- **Category bars**: Clickable to view category-specific results
- **Version chart**: Hover shows exact scores

---

### 2d. Category Results Page

Detailed view of all models' performance in a specific category. Part of the Research section.

### Desktop Layout

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ [LOGO] Great Commission Benchmark  Home | Research | Contribute | About [L] │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ← Back to Research                                                         │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                                                                     │    │
│  │  Evangelistic Material Creation                                     │    │
│  │  ───────────────────────────────────────────────────────────────    │    │
│  │                                                                     │    │
│  │  Creating content to communicate, connect with, and persuade        │    │
│  │  non-Christians of the truth of Christianity.                       │    │
│  │                                                                     │    │
│  │  Questions: 35  |  Subcategories: 5  |  42 models tested            │    │
│  │                                                                     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  ┌──────────────────────────────────────┐  ┌──────────────────────────────┐ │
│  │  Top Performers                      │  │  Subcategory Breakdown       │ │
│  │  ────────────────────────────────    │  │  ────────────────────────    │ │
│  │                                      │  │                              │ │
│  │  🥇 GPT-4 Turbo         91.2%        │  │  Gospel Present.  [▓▓▓▓░]   │ │
│  │  🥈 Claude 3 Opus       88.4%        │  │  Evangelistic     [▓▓▓▓▓]   │ │
│  │  🥉 Gemini Ultra        86.7%        │  │  Outreach Mats.   [▓▓▓░░]   │ │
│  │                                      │  │  Testimonies      [▓▓▓▓░]   │ │
│  │                                      │  │  Cultural Adapt.  [▓▓▓▓▓]   │ │
│  │                                      │  │                              │ │
│  └──────────────────────────────────────┘  └──────────────────────────────┘ │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  All Models - Evangelistic Material Creation                        │    │
│  │  ───────────────────────────────────────────────────────────────    │    │
│  │                                                                     │    │
│  │  Rank │ Model              │ Provider   │ Score   │ vs Overall │    │    │
│  │  ─────┼────────────────────┼────────────┼─────────┼────────────┼    │    │
│  │    1  │ GPT-4 Turbo        │ OpenAI     │  94.2   │   +1.9     │ →  │    │
│  │    2  │ Claude 3 Opus      │ Anthropic  │  92.8   │   +3.1     │ →  │    │
│  │    3  │ Gemini Ultra       │ Google     │  91.1   │   +3.9     │ →  │    │
│  │    4  │ GPT-4              │ OpenAI     │  88.7   │   +7.2     │ →  │    │
│  │    5  │ Claude 3 Sonnet    │ Anthropic  │  86.3   │   +2.2     │ →  │    │
│  │                                                                     │    │
│  │                    [< Prev]  Page 1 of 5  [Next >]                  │    │
│  │                                                                     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  Sample Questions (Anonymized)                                      │    │
│  │  ───────────────────────────────────────────────────────────────    │    │
│  │                                                                     │    │
│  │  • "In which book does the phrase '___' appear, and what is the..." │    │
│  │  • "According to [Gospel], what did Jesus say when..."              │    │
│  │  • "How does Paul's letter to the [Church] address the topic of..." │    │
│  │                                                                     │    │
│  │  Note: Full questions hidden to maintain benchmark integrity.       │    │
│  │                                                                     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│  [Footer]                                                                   │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Interaction Notes

- **vs Overall column**: Shows difference between category score and overall score
- **Subcategory mini-charts**: Visual breakdown of sub-scores
- **Model rows**: Click to navigate to Model Detail page
- **Sample questions**: Redacted to prevent gaming the benchmark

---

## 3. Contribute Page

The community hub for the Great Commission Benchmark. This page casts a vision for collaboration and provides clear pathways for involvement.

### Design Philosophy

- **Welcoming**: Invite people into the mission, not just a product
- **Clear Pathways**: Distinct ways to contribute based on skill/interest
- **Community-Centered**: Emphasize the collaborative, open nature of the project
- **Action-Oriented**: Every section has a clear CTA

### Desktop Layout

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ [LOGO] Great Commission Benchmark  Home | Research | Contribute | About [L] │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                                                                     │   │
│   │                    Join the Mission                                 │   │
│   │                    ════════════════                                 │   │
│   │                                                                     │   │
│   │     The Great Commission Benchmark is a community-driven effort     │   │
│   │     to evaluate AI through the lens of Christian faith. We believe  │   │
│   │     transparency and collaboration make this work trustworthy.      │   │
│   │                                                                     │   │
│   │     Whether you're a developer, researcher, theologian, or simply   │   │
│   │     passionate about AI and faith—there's a place for you here.     │   │
│   │                                                                     │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                                                                     │   │
│   │                     Ways to Contribute                              │   │
│   │                     ──────────────────                              │   │
│   │                                                                     │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                                                                     │   │
│   │  🧪 Run Benchmark Tests                                             │   │
│   │  ═══════════════════════════════════════════════════════════════    │   │
│   │                                                                     │   │
│   │  Help expand our coverage by testing AI models against the          │   │
│   │  benchmark. Every test you run contributes to a more complete       │   │
│   │  picture of how AI handles Christian content.                       │   │
│   │                                                                     │   │
│   │  What you can do:                                                   │   │
│   │  • Test new model versions as they're released                      │   │
│   │  • Re-test models to verify consistency over time                   │   │
│   │  • Help cover models from smaller providers                         │   │
│   │  • Run specialized tests on specific categories                     │   │
│   │                                                                     │   │
│   │  Requirements:                                                      │   │
│   │  • Create an account (free)                                         │   │
│   │  • Pay per test ($20 + model API costs)                             │   │
│   │  • Follow our testing guidelines                                    │   │
│   │                                                                     │   │
│   │  Your contributions are attributed publicly on the leaderboard      │   │
│   │  (or anonymously, if you prefer).                                   │   │
│   │                                                                     │   │
│   │                              [Run Your First Test →]                │   │
│   │                                                                     │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                                                                     │   │
│   │  🤖 Submit Your Fine-Tuned Model                                    │   │
│   │  ═══════════════════════════════════════════════════════════════    │   │
│   │                                                                     │   │
│   │  Have you fine-tuned an LLM for Christian ministry, biblical        │   │
│   │  scholarship, or theological applications? We want to benchmark it. │   │
│   │                                                                     │   │
│   │  Why submit your model:                                             │   │
│   │  • Get objective, third-party evaluation                            │   │
│   │  • Compare against leading commercial models                        │   │
│   │  • Gain visibility in the Christian AI community                    │   │
│   │  • Help advance the field of faith-informed AI                      │   │
│   │                                                                     │   │
│   │  What we accept:                                                    │   │
│   │  • Fine-tuned models accessible via API                             │   │
│   │  • Self-hosted models (we can work with you on access)              │   │
│   │  • Research models (we'll keep results private if needed)           │   │
│   │                                                                     │   │
│   │  Submission is free for non-commercial models. Commercial models    │   │
│   │  follow standard testing fees.                                      │   │
│   │                                                                     │   │
│   │                          [Submit a Model for Testing →]             │   │
│   │                                                                     │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                                                                     │   │
│   │  💻 Contribute to Development                                       │   │
│   │  ═══════════════════════════════════════════════════════════════    │   │
│   │                                                                     │   │
│   │  The benchmark platform is open source. Developers, designers,      │   │
│   │  and theologians are welcome to contribute.                         │   │
│   │                                                                     │   │
│   │  Areas where we need help:                                          │   │
│   │  • Platform development (Next.js, TypeScript, PostgreSQL)           │   │
│   │  • Benchmark question development and review                        │   │
│   │  • UI/UX improvements                                               │   │
│   │  • Documentation and tutorials                                      │   │
│   │  • Translations and internationalization                            │   │
│   │  • Theological review of scoring criteria                           │   │
│   │                                                                     │   │
│   │  ┌─────────────────────────┐  ┌─────────────────────────┐           │   │
│   │  │                         │  │                         │           │   │
│   │  │  [GitHub Icon]          │  │  [Discord Icon]         │           │   │
│   │  │                         │  │                         │           │   │
│   │  │  View on GitHub         │  │  Join our Discord       │           │   │
│   │  │  Browse issues, submit  │  │  Chat with contributors │           │   │
│   │  │  PRs, review code       │  │  and the community      │           │   │
│   │  │                         │  │                         │           │   │
│   │  │  [Visit Repository →]   │  │  [Join Discord →]       │           │   │
│   │  │                         │  │                         │           │   │
│   │  └─────────────────────────┘  └─────────────────────────┘           │   │
│   │                                                                     │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                                                                     │   │
│   │  💝 Support the Project                                             │   │
│   │  ═══════════════════════════════════════════════════════════════    │   │
│   │                                                                     │   │
│   │  The Great Commission Benchmark is a non-profit initiative.         │   │
│   │  Your support helps us maintain the platform, develop new           │   │
│   │  evaluation categories, and keep testing accessible.                │   │
│   │                                                                     │   │
│   │  How your support helps:                                            │   │
│   │  • $25 — Sponsors one benchmark test                                │   │
│   │  • $100 — Helps develop new evaluation questions                    │   │
│   │  • $500 — Supports a month of infrastructure costs                  │   │
│   │  • $1000+ — Enables new category development                        │   │
│   │                                                                     │   │
│   │  All donors receive:                                                │   │
│   │  • Recognition on our supporters page (optional)                    │   │
│   │  • Quarterly impact reports                                         │   │
│   │  • Early access to new features                                     │   │
│   │                                                                     │   │
│   │                            [Support the Benchmark →]                │   │
│   │                                                                     │   │
│   │  For corporate sponsorship or partnership inquiries:                │   │
│   │  partnerships@greatcommissionbenchmark.org                          │   │
│   │                                                                     │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                                                                     │   │
│   │                      Join the Community                             │   │
│   │                      ──────────────────                             │   │
│   │                                                                     │   │
│   │  ┌────────────────────────────────────────────────────────────────┐ │   │
│   │  │                                                                │ │   │
│   │  │  [Discord Logo]                                                │ │   │
│   │  │                                                                │ │   │
│   │  │  Join 500+ members discussing AI, faith, and the benchmark     │ │   │
│   │  │                                                                │ │   │
│   │  │  • #general — Community discussions                            │ │   │
│   │  │  • #model-releases — New model announcements                   │ │   │
│   │  │  • #theology — Deep dives on evaluation criteria               │ │   │
│   │  │  • #development — Platform development chat                    │ │   │
│   │  │  • #prayer — Community prayer and encouragement                │ │   │
│   │  │                                                                │ │   │
│   │  │                        [Join Our Discord →]                    │ │   │
│   │  │                                                                │ │   │
│   │  └────────────────────────────────────────────────────────────────┘ │   │
│   │                                                                     │   │
│   │  Also find us on:                                                   │   │
│   │  [Twitter/X]  [LinkedIn]  [YouTube]  [Newsletter Signup]            │   │
│   │                                                                     │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│  [Footer]                                                                   │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Mobile Layout

```
┌─────────────────────────────────────────┐
│ [≡]  GC Benchmark            [Login]    │
├─────────────────────────────────────────┤
│                                         │
│  Join the Mission                       │
│  ════════════════                       │
│                                         │
│  The Great Commission Benchmark is a    │
│  community-driven effort to evaluate    │
│  AI through the lens of Christian faith.│
│                                         │
│  ┌─────────────────────────────────────┐│
│  │ 🧪 Run Benchmark Tests              ││
│  │ ─────────────────────────────────── ││
│  │                                     ││
│  │ Help expand our coverage by testing ││
│  │ AI models against the benchmark.    ││
│  │                                     ││
│  │ • Test new model versions           ││
│  │ • Re-test for consistency           ││
│  │ • Cover smaller providers           ││
│  │                                     ││
│  │ [Run Your First Test →]             ││
│  │                                     ││
│  └─────────────────────────────────────┘│
│                                         │
│  ┌─────────────────────────────────────┐│
│  │ 🤖 Submit Your Fine-Tuned Model     ││
│  │ ─────────────────────────────────── ││
│  │                                     ││
│  │ Have a fine-tuned LLM for Christian ││
│  │ ministry or theology? Benchmark it. ││
│  │                                     ││
│  │ • Get objective evaluation          ││
│  │ • Compare against leading models    ││
│  │ • Gain visibility                   ││
│  │                                     ││
│  │ [Submit a Model →]                  ││
│  │                                     ││
│  └─────────────────────────────────────┘│
│                                         │
│  ┌─────────────────────────────────────┐│
│  │ 💻 Contribute to Development        ││
│  │ ─────────────────────────────────── ││
│  │                                     ││
│  │ The platform is open source.        ││
│  │ Developers and theologians welcome. ││
│  │                                     ││
│  │ [GitHub] [Discord]                  ││
│  │                                     ││
│  └─────────────────────────────────────┘│
│                                         │
│  ┌─────────────────────────────────────┐│
│  │ 💝 Support the Project              ││
│  │ ─────────────────────────────────── ││
│  │                                     ││
│  │ A non-profit initiative. Your       ││
│  │ support helps maintain the platform.││
│  │                                     ││
│  │ [Support the Benchmark →]           ││
│  │                                     ││
│  └─────────────────────────────────────┘│
│                                         │
│  ┌─────────────────────────────────────┐│
│  │ Join 500+ members on Discord        ││
│  │ [Join Our Discord →]                ││
│  └─────────────────────────────────────┘│
│                                         │
├─────────────────────────────────────────┤
│  [Footer]                               │
└─────────────────────────────────────────┘
```

### Interaction Notes

- **Run Test CTA**: Redirects to test flow (login required)
- **Submit Model**: Opens a form/modal or mailto: link
- **GitHub link**: Opens repository in new tab
- **Discord link**: Opens Discord invite in new tab
- **Support button**: Opens donation page or Stripe checkout
- **Social links**: Open respective platforms in new tabs

---

## 4. About/Methodology Page

Explains the benchmark's purpose, methodology, and scoring system.

### Desktop Layout

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ [LOGO] Great Commission Benchmark  Home | Research | Contribute | About [L] │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌────────────────────┐                                                     │
│  │  Table of Contents │                                                     │
│  │  ──────────────────│                                                     │
│  │  • Overview        │  ┌──────────────────────────────────────────────┐   │
│  │  • Mission         │  │                                              │   │
│  │  • Categories      │  │  About the Great Commission Benchmark        │   │
│  │  • Methodology     │  │  ════════════════════════════════════════    │   │
│  │  • Scoring         │  │                                              │   │
│  │  • FAQ             │  │  Overview                                    │   │
│  │  • Contact         │  │  ────────                                    │   │
│  │                    │  │                                              │   │
│  └────────────────────┘  │  The Great Commission Benchmark evaluates    │   │
│                          │  AI language models on their understanding   │   │
│                          │  of Christian scripture, theology, ethics,   │   │
│                          │  and apologetics.                            │   │
│                          │                                              │   │
│                          │  Our goal is to provide transparency about   │   │
│                          │  how AI systems handle religious content,    │   │
│                          │  enabling informed decisions about their     │   │
│                          │  use in Christian contexts.                  │   │
│                          │                                              │   │
│                          │                                              │   │
│                          │  Mission                                     │   │
│                          │  ───────                                     │   │
│                          │                                              │   │
│                          │  [Mission statement content...]              │   │
│                          │                                              │   │
│                          │                                              │   │
│                          │  Categories                                  │   │
│                          │  ──────────                                  │   │
│                          │                                              │   │
│                          │  ┌────────────────────────────────────────┐  │   │
│                          │  │ Scripture   │ Theology  │ Ethics      │  │   │
│                          │  │ Knowledge   │ Accuracy  │ Reasoning   │  │   │
│                          │  │             │           │             │  │   │
│                          │  │ Biblical    │ Doctrinal │ Moral       │  │   │
│                          │  │ text and    │ positions │ reasoning   │  │   │
│                          │  │ context     │ and       │ from a      │  │   │
│                          │  │             │ history   │ Christian   │  │   │
│                          │  │             │           │ worldview   │  │   │
│                          │  └────────────────────────────────────────┘  │   │
│                          │                                              │   │
│                          │  [More category descriptions...]             │   │
│                          │                                              │   │
│                          │                                              │   │
│                          │  Methodology                                 │   │
│                          │  ───────────                                 │   │
│                          │                                              │   │
│                          │  1. Question Development                     │   │
│                          │     - Expert-curated by theologians          │   │
│                          │     - Peer-reviewed for accuracy             │   │
│                          │     - Regularly updated                      │   │
│                          │                                              │   │
│                          │  2. Testing Process                          │   │
│                          │     - Standardized prompts                   │   │
│                          │     - Controlled parameters                  │   │
│                          │     - Multiple evaluation passes             │   │
│                          │                                              │   │
│                          │  3. Scoring                                  │   │
│                          │     - Automated + human review               │   │
│                          │     - Inter-rater reliability checks         │   │
│                          │     - Appeals process available              │   │
│                          │                                              │   │
│                          │                                              │   │
│                          │  FAQ                                         │   │
│                          │  ───                                         │   │
│                          │                                              │   │
│                          │  ▼ How are questions kept secure?            │   │
│                          │    [Expandable answer...]                    │   │
│                          │                                              │   │
│                          │  ▶ Who creates the questions?                │   │
│                          │                                              │   │
│                          │  ▶ How often are models retested?            │   │
│                          │                                              │   │
│                          │  ▶ Can I contribute questions?               │   │
│                          │                                              │   │
│                          │                                              │   │
│                          │  Contact                                     │   │
│                          │  ───────                                     │   │
│                          │                                              │   │
│                          │  Questions? Reach out at:                    │   │
│                          │  contact@greatcommissionbenchmark.org        │   │
│                          │                                              │   │
│                          └──────────────────────────────────────────────┘   │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│  [Footer]                                                                   │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Interaction Notes

- **Sticky TOC**: Table of contents follows scroll on desktop
- **FAQ accordions**: Click to expand/collapse answers
- **Anchor links**: TOC items scroll to sections smoothly

---

## 5. Public Profile Page

View of a user's public testing contributions.

### Desktop Layout

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ [LOGO] Great Commission Benchmark  Home | Research | Contribute | About [L] │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ← Back                                                                     │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                                                                     │    │
│  │  ┌─────┐                                                            │    │
│  │  │ 👤  │   @testuser123                                             │    │
│  │  │     │   Member since October 2024                                │    │
│  │  └─────┘                                                            │    │
│  │                                                                     │    │
│  │  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐         │    │
│  │  │      15        │  │      12        │  │       3        │         │    │
│  │  │  Tests Run     │  │  Models Tested │  │  Categories    │         │    │
│  │  └────────────────┘  └────────────────┘  └────────────────┘         │    │
│  │                                                                     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  Test Contributions                                                 │    │
│  │  ───────────────────────────────────────────────────────────────    │    │
│  │                                                                     │    │
│  │  Date          │ Model              │ Score  │ Status    │ View     │    │
│  │  ──────────────┼────────────────────┼────────┼───────────┼──────    │    │
│  │  Dec 14, 2024  │ GPT-4 Turbo        │ 92.3   │ ● Verified│ [→]      │    │
│  │  Dec 10, 2024  │ Claude 3 Opus      │ 89.7   │ ● Verified│ [→]      │    │
│  │  Dec 5, 2024   │ Gemini Pro         │ 78.4   │ ● Verified│ [→]      │    │
│  │  Nov 28, 2024  │ Llama 3 70B        │ 72.1   │ ● Verified│ [→]      │    │
│  │  Nov 20, 2024  │ Mistral Large      │ 68.9   │ ● Verified│ [→]      │    │
│  │                                                                     │    │
│  │                    [< Prev]  Page 1 of 3  [Next >]                  │    │
│  │                                                                     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  ┌──────────────────────────────────┐  ┌──────────────────────────────┐     │
│  │  Models Tested                   │  │  Testing Activity            │     │
│  │  ────────────────────────────    │  │  ────────────────────────    │     │
│  │                                  │  │                              │     │
│  │  • GPT-4 Turbo (3 tests)         │  │  [Activity heatmap or        │     │
│  │  • Claude 3 Opus (2 tests)       │  │   contribution graph]        │     │
│  │  • Gemini Pro (2 tests)          │  │                              │     │
│  │  • Llama 3 70B (2 tests)         │  │                              │     │
│  │  • Other (6 tests)               │  │                              │     │
│  │                                  │  │                              │     │
│  └──────────────────────────────────┘  └──────────────────────────────┘     │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│  [Footer]                                                                   │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Interaction Notes

- **Privacy**: Only shows public username and test statistics
- **Test rows**: Click to view public test result details
- **Activity graph**: Shows testing frequency over time (GitHub-style heatmap)

---

## URL Structure

| Page | URL Pattern | Example |
|------|-------------|---------|
| Homepage | `/` | `/` |
| Research Landing | `/research` | `/research` |
| Model Comparison | `/research/compare` | `/research/compare?models=gpt-4-turbo,claude-3-opus` |
| Model Detail | `/research/models/:provider/:model/:version` | `/research/models/openai/gpt-4-turbo/2024.01` |
| Category Results | `/research/categories/:category` | `/research/categories/evangelistic-material-creation` |
| Contribute | `/contribute` | `/contribute` |
| About | `/about` | `/about` |
| Public Profile | `/users/:username` | `/users/testuser123` |

---

## SEO Considerations

1. **Homepage**: Primary landing page, optimized for "AI Christian benchmark" keywords
2. **Research Landing**: Deep-dive content, targets comparison and evaluation queries
3. **Model Detail**: Structured data for model information (JSON-LD)
4. **Model Comparison**: Targets "compare AI models" queries
5. **Category**: Long-tail keywords for specific evaluation areas
6. **Contribute**: Community and volunteer keywords, links to social proof
7. **About**: Methodology transparency for trust/credibility
8. **Public Profile**: Noindex to protect user privacy

---

*Next: See `wireframes-user-pages.md` for authenticated user pages*
