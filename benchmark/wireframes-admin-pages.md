# Great Commission Benchmark - Admin Pages Wireframes

## Overview

This document contains wireframes for admin-only pages used for system management and oversight.

**Pages Covered:**
1. System Stats Dashboard
2. User Management
3. Failed Test Intervention Queue

*Reference `wireframes-design-system.md` for component specifications and color palette.*

---

## Access Control

Admin pages are only accessible to users with the `admin` role.

```
Admin Capabilities:
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  • All moderator capabilities                                   │
│  • View system-wide statistics and metrics                      │
│  • Manage user accounts and roles                               │
│  • Final decision on escalated appeals                          │
│  • Access to financial/payment reports                          │
│  • System configuration changes                                 │
│  • Complete failed tests from intervention queue                │
│  • Issue refunds for uncompletable tests                        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 1. System Stats Dashboard

Comprehensive overview of platform health, usage, and financial metrics.

### Desktop Layout

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ [LOGO] GC Benchmark   Home | Research | Contribute | Admin          [▼ A]   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Admin Dashboard                                       Last updated: 2m ago │
│  ═══════════════════════════════════════════════════════════════════════    │
│                                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │              │  │              │  │              │  │              │     │
│  │     142      │  │     89       │  │   $4,250     │  │     12       │     │
│  │              │  │              │  │              │  │              │     │
│  │ Total Users  │  │ Tests Today  │  │ Revenue MTD  │  │ Pending      │     │
│  │              │  │              │  │              │  │ Review       │     │
│  │  +12 this    │  │  +15% vs     │  │  +8% vs      │  │              │     │
│  │  week        │  │  last week   │  │  last month  │  │  [View →]    │     │
│  │              │  │              │  │              │  │              │     │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘     │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  Platform Activity (Last 30 Days)                       [Export CSV]│    │
│  │  ───────────────────────────────────────────────────────────────    │    │
│  │                                                                     │    │
│  │  [Line chart showing daily tests, registrations, revenue]           │    │
│  │                                                                     │    │
│  │  Tests ─────  Registrations ─ ─ ─  Revenue ·····                    │    │
│  │                                                                     │    │
│  │   100│                    ╱\                                        │    │
│  │      │         ╱\    ╱\  ╱  \  ╱\                                   │    │
│  │    75│    ╱\  ╱  \  ╱  ╲╱    ╲╱  \                                  │    │
│  │      │   ╱  ╲╱    ╲╱                ╲                                │    │
│  │    50│──╱                            ╲──                            │    │
│  │      │                                                              │    │
│  │    25│                                                              │    │
│  │      └──────────────────────────────────────────────                │    │
│  │       Nov 15        Nov 22        Nov 29        Dec 6        Dec 13 │    │
│  │                                                                     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  ┌────────────────────────────────────┐  ┌────────────────────────────────┐ │
│  │  Tests by Model Provider           │  │  Revenue Breakdown             │ │
│  │  ──────────────────────────────    │  │  ──────────────────────────    │ │
│  │                                    │  │                                │ │
│  │  [Pie chart]                       │  │  Credit Packages               │ │
│  │                                    │  │                                │ │
│  │       ╭───────╮                    │  │  Starter ($25)   ████████  42% │ │
│  │      ╱  OpenAI ╲                   │  │  Standard ($50)  █████     28% │ │
│  │     │    35%    │                  │  │  Pro ($100)      ██████    30% │ │
│  │     │           │                  │  │                                │ │
│  │      ╲ Anthro  ╱                   │  │  ──────────────────────────    │ │
│  │       ╲  28%  ╱                    │  │                                │ │
│  │        ╲────╱                      │  │  Total MTD:      $4,250        │ │
│  │    Google 20%  Other 17%           │  │  Avg per user:   $29.93        │ │
│  │                                    │  │                                │ │
│  │  OpenAI: 312 tests                 │  │                                │ │
│  │  Anthropic: 248 tests              │  │                                │ │
│  │  Google: 178 tests                 │  │                                │ │
│  │  Other: 152 tests                  │  │                                │ │
│  │                                    │  │                                │ │
│  └────────────────────────────────────┘  └────────────────────────────────┘ │
│                                                                             │
│  ┌────────────────────────────────────┐  ┌────────────────────────────────┐ │
│  │  Moderation Stats                  │  │  System Health                 │ │
│  │  ──────────────────────────────    │  │  ──────────────────────────    │ │
│  │                                    │  │                                │ │
│  │  Queue Status                      │  │  API Status                    │ │
│  │  Pending:     12  ⚠️               │  │  ● OpenAI        Operational   │ │
│  │  In Review:   3                    │  │  ● Anthropic     Operational   │ │
│  │  Today:       45 completed         │  │  ● Google        Operational   │ │
│  │                                    │  │  ● Stripe        Operational   │ │
│  │  ──────────────────────────────    │  │  ● Auth0         Operational   │ │
│  │                                    │  │                                │ │
│  │  Moderator Activity (Today)        │  │  ──────────────────────────    │ │
│  │                                    │  │                                │ │
│  │  @mod_sarah    18 reviews          │  │  Database                      │ │
│  │  @mod_john     15 reviews          │  │  Connections:    24/100        │ │
│  │  @mod_lisa     12 reviews          │  │  Avg Query:      42ms          │ │
│  │                                    │  │                                │ │
│  │  Avg review time: 4.2 min          │  │  Queue Workers                 │ │
│  │  Approval rate: 94%                │  │  Active:         3/5           │ │
│  │                                    │  │  Jobs pending:   7             │ │
│  │                                    │  │                                │ │
│  └────────────────────────────────────┘  └────────────────────────────────┘ │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  Recent System Events                                     [View All]│    │
│  │  ───────────────────────────────────────────────────────────────    │    │
│  │                                                                     │    │
│  │  • 14:32  New user registration: @newuser123                        │    │
│  │  • 14:28  Test completed: GPT-4o by @user45                         │    │
│  │  • 14:25  Credit purchase: $50 by @user12                           │    │
│  │  • 14:20  Appeal submitted: Run #abc123 by @user7                   │    │
│  │  • 14:15  Moderator @mod_sarah approved 5 tests                     │    │
│  │                                                                     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│  [Footer]                                                                   │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Key Metrics Detail View

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│  Detailed Metrics                                    Period: [Last 30 Days ▼]│
│  ═══════════════════════════════════════════════════════════════════════    │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  User Metrics                                                       │    │
│  │  ───────────────────────────────────────────────────────────────    │    │
│  │                                                                     │    │
│  │  Total Users:           142         Active (30d):        89 (63%)   │    │
│  │  New This Period:       28          Churned:             3 (2%)     │    │
│  │                                                                     │    │
│  │  User Segments:                                                     │    │
│  │  • Power (10+ tests):   12 users    avg $85 spent                   │    │
│  │  • Regular (3-9 tests): 45 users    avg $42 spent                   │    │
│  │  • Casual (1-2 tests):  85 users    avg $18 spent                   │    │
│  │                                                                     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  Test Metrics                                                       │    │
│  │  ───────────────────────────────────────────────────────────────    │    │
│  │                                                                     │    │
│  │  Total Tests:           890         Avg per Day:         29.7       │    │
│  │  Unique Models:         42          Avg Score:           76.4       │    │
│  │                                                                     │    │
│  │  Outcome Distribution:                                              │    │
│  │  • Approved:            834 (94%)                                   │    │
│  │  • Rejected:            41 (4.6%)                                   │    │
│  │  • Pending:             12 (1.3%)                                   │    │
│  │  • Failed (error):      3 (0.3%)                                    │    │
│  │                                                                     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  Financial Metrics                                                  │    │
│  │  ───────────────────────────────────────────────────────────────    │    │
│  │                                                                     │    │
│  │  Gross Revenue:         $4,250      Net (after fees):    $3,910     │    │
│  │  Stripe Fees:           $127        Refunds:             $213       │    │
│  │                                                                     │    │
│  │  Cost Breakdown:                                                    │    │
│  │  • API costs (est):     $890                                        │    │
│  │  • Infrastructure:      $150                                        │    │
│  │  • Net margin:          ~68%                                        │    │
│  │                                                                     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Interaction Notes

- **Auto-refresh**: Dashboard data refreshes every 5 minutes
- **Date range selector**: Compare across different time periods
- **Export capabilities**: CSV/PDF export for all metrics
- **Drill-down**: Click metrics to see detailed breakdown
- **Alerts**: Visual indicators for metrics outside normal ranges

---

## 2. User Management

Admin interface for managing user accounts, roles, and permissions.

### Desktop Layout

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ [LOGO] GC Benchmark   Home | Research | Contribute | Admin          [▼ A]   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ← Back to Admin Dashboard                                                  │
│                                                                             │
│  User Management                                              142 total users│
│  ═══════════════════════════════════════════════════════════════════════    │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  Search & Filter                                                    │    │
│  │  ───────────────────────────────────────────────────────────────    │    │
│  │                                                                     │    │
│  │  [Search by username or email...                               ]    │    │
│  │                                                                     │    │
│  │  Role: [All Roles ▼]   Status: [All ▼]   Joined: [Any Time ▼]       │    │
│  │                                                                     │    │
│  │  [✓] Show only users with issues          [Clear Filters]           │    │
│  │                                                                     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                                                                     │    │
│  │  │ User           │ Email              │ Role     │ Tests │ Status │    │
│  │  ├────────────────┼────────────────────┼──────────┼───────┼────────│    │
│  │  │                │                    │          │       │        │    │
│  │  │ @testuser1     │ test1@example.com  │ user     │ 15    │ Active │    │
│  │  │ Joined Oct 12  │                    │          │       │ [···]  │    │
│  │  ├────────────────┼────────────────────┼──────────┼───────┼────────│    │
│  │  │                │                    │          │       │        │    │
│  │  │ @mod_sarah     │ sarah@example.com  │ moderator│ 8     │ Active │    │
│  │  │ Joined Sep 5   │                    │          │       │ [···]  │    │
│  │  ├────────────────┼────────────────────┼──────────┼───────┼────────│    │
│  │  │                │                    │          │       │        │    │
│  │  │ @poweruser     │ power@example.com  │ user     │ 45    │ Active │    │
│  │  │ Joined Aug 20  │                    │          │       │ [···]  │    │
│  │  ├────────────────┼────────────────────┼──────────┼───────┼────────│    │
│  │  │                │                    │          │       │        │    │
│  │  │ @flagged_user  │ flag@example.com   │ user     │ 3     │ ⚠️ Flag│    │
│  │  │ Joined Nov 1   │                    │          │       │ [···]  │    │
│  │  ├────────────────┼────────────────────┼──────────┼───────┼────────│    │
│  │  │                │                    │          │       │        │    │
│  │  │ @suspended     │ sus@example.com    │ user     │ 7     │ 🚫 Sus │    │
│  │  │ Joined Jul 15  │                    │          │       │ [···]  │    │
│  │  │                │                    │          │       │        │    │
│  │                                                                     │    │
│  │                    [< Prev]  Page 1 of 8  [Next >]                  │    │
│  │                                                                     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  Role Summary                                                       │    │
│  │  ───────────────────────────────────────────────────────────────    │    │
│  │                                                                     │    │
│  │  Admins:      2      Moderators:    5      Users:    135            │    │
│  │                                                                     │    │
│  │  [+ Invite New Moderator]                                           │    │
│  │                                                                     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│  [Footer]                                                                   │
└─────────────────────────────────────────────────────────────────────────────┘
```

### User Actions Menu

```
┌─────────────────────────┐
│  User Actions           │
│  ─────────────────────  │
│                         │
│  👁️ View Profile        │
│  📝 Edit Details        │
│  ─────────────────────  │
│  🔑 Change Role         │
│  💰 View Payments       │
│  📊 View Tests          │
│  ─────────────────────  │
│  ⚠️ Flag Account        │
│  🚫 Suspend Account     │
│  🗑️ Delete Account      │
│                         │
└─────────────────────────┘
```

### User Detail View

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│  User Details: @testuser1                                                   │
│  ═══════════════════════════════════════════════════════════════════════    │
│                                                                             │
│  ┌────────────────────────────────────┐  ┌────────────────────────────────┐ │
│  │  Account Information               │  │  Quick Stats                   │ │
│  │  ──────────────────────────────    │  │  ──────────────────────────    │ │
│  │                                    │  │                                │ │
│  │  Username:    @testuser1           │  │  Tests Run:       15           │ │
│  │  Email:       test1@example.com    │  │  Total Spent:     $75.00       │ │
│  │  Auth0 ID:    auth0|abc123...      │  │  Total Spent:     $75.00       │ │
│  │                                    │  │                                │ │
│  │  Role:        [user ▼]             │  │  Avg Score:       81.4         │ │
│  │  Status:      [Active ▼]           │  │  Approval Rate:   93%          │ │
│  │                                    │  │                                │ │
│  │  Joined:      October 12, 2024     │  │  Last Active:     2 hours ago  │ │
│  │  Last Login:  December 15, 2024    │  │                                │ │
│  │                                    │  │                                │ │
│  │               [Save Changes]       │  │                                │ │
│  │                                    │  │                                │ │
│  └────────────────────────────────────┘  └────────────────────────────────┘ │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  Test History                                             [View All]│    │
│  │  ───────────────────────────────────────────────────────────────    │    │
│  │                                                                     │    │
│  │  Date          │ Model              │ Score  │ Status    │ View     │    │
│  │  ──────────────┼────────────────────┼────────┼───────────┼──────    │    │
│  │  Dec 14, 2024  │ GPT-4 Turbo        │ 92.3   │ ● Verified│ [→]      │    │
│  │  Dec 10, 2024  │ Claude 3 Opus      │ 89.7   │ ● Verified│ [→]      │    │
│  │  Dec 5, 2024   │ Gemini Pro         │ 78.4   │ ● Verified│ [→]      │    │
│  │                                                                     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  Payment History                                          [View All]│    │
│  │  ───────────────────────────────────────────────────────────────    │    │
│  │                                                                     │    │
│  │  Date          │ Type              │ Amount   │ Model               │    │
│  │  ──────────────┼───────────────────┼──────────┼─────────────────    │    │
│  │  Dec 14, 2024  │ Test Purchase     │ $24.80   │ GPT-4 Turbo         │    │
│  │  Dec 10, 2024  │ Test Purchase     │ $27.50   │ Claude 3 Opus       │    │
│  │  Dec 5, 2024   │ Refund            │ -$22.10  │ Gemini Pro          │    │
│  │                                                                     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  Admin Notes (Internal)                                             │    │
│  │  ───────────────────────────────────────────────────────────────    │    │
│  │                                                                     │    │
│  │  ┌───────────────────────────────────────────────────────────────┐  │    │
│  │  │ No admin notes for this user.                                 │  │    │
│  │  └───────────────────────────────────────────────────────────────┘  │    │
│  │                                                                     │    │
│  │  [+ Add Note]                                                       │    │
│  │                                                                     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  Account Actions                                                    │    │
│  │  ───────────────────────────────────────────────────────────────    │    │
│  │                                                                     │    │
│  │  [Issue Refund]  [Reset Password Link]  [Export User Data]          │    │
│  │                                                                     │    │
│  │  ────────────────────────────────────────────────────────────────   │    │
│  │                                                                     │    │
│  │  ⚠️ Danger Zone                                                     │    │
│  │                                                                     │    │
│  │  [Flag Account]  [Suspend Account]  [Delete Account]                │    │
│  │                                                                     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Role Change Confirmation

```
┌───────────────────────────────────────────────────────────────┐
│                                                           [×] │
│                                                               │
│   Change User Role                                            │
│   ═══════════════════════════════════════════════════════     │
│                                                               │
│   User: @testuser1                                            │
│   Current Role: user                                          │
│   New Role: moderator                                         │
│                                                               │
│   ┌───────────────────────────────────────────────────────┐   │
│   │                                                       │   │
│   │  This will grant @testuser1 access to:                │   │
│   │                                                       │   │
│   │  • Moderator Dashboard                                │   │
│   │  • Review Queue                                       │   │
│   │  • Test Result Review Interface                       │   │
│   │  • Appeals Queue (excluding own rejections)           │   │
│   │                                                       │   │
│   └───────────────────────────────────────────────────────┘   │
│                                                               │
│   Reason for role change:                                     │
│   ┌───────────────────────────────────────────────────────┐   │
│   │                                                       │   │
│   │                                                       │   │
│   └───────────────────────────────────────────────────────┘   │
│                                                               │
│   [✓] Send email notification to user                         │
│                                                               │
│                              [Cancel]  [Confirm Change]       │
│                                                               │
└───────────────────────────────────────────────────────────────┘
```

### Suspend Account Modal

```
┌───────────────────────────────────────────────────────────────┐
│                                                           [×] │
│                                                               │
│   Suspend Account                                             │
│   ═══════════════════════════════════════════════════════     │
│                                                               │
│   User: @flagged_user                                         │
│                                                               │
│   Suspension Reason:                                          │
│                                                               │
│   ○ Terms of Service violation                                │
│   ○ Suspected fraud/manipulation                              │
│   ○ Payment dispute                                           │
│   ○ Abuse of platform                                         │
│   ○ Other (specify below)                                     │
│                                                               │
│   Details (shown to user):                                    │
│   ┌───────────────────────────────────────────────────────┐   │
│   │                                                       │   │
│   │                                                       │   │
│   └───────────────────────────────────────────────────────┘   │
│                                                               │
│   Suspension Duration:                                        │
│   ○ Temporary (7 days)                                        │
│   ○ Temporary (30 days)                                       │
│   ○ Indefinite (manual reactivation required)                 │
│                                                               │
│   Effects:                                                    │
│   • User cannot log in                                        │
│   • Pending tests will be cancelled                           │
│   • Past purchases preserved in history                       │
│                                                               │
│                              [Cancel]  [Suspend Account]      │
│                                                               │
└───────────────────────────────────────────────────────────────┘
```

### Issue Refund Modal

```
┌───────────────────────────────────────────────────────────────┐
│                                                           [×] │
│                                                               │
│   Issue Refund                                                │
│   ═══════════════════════════════════════════════════════     │
│                                                               │
│   User: @testuser1                                            │
│                                                               │
│   Select Purchase to Refund:                                  │
│   ┌───────────────────────────────────────────────────────┐   │
│   │ ○ Dec 14, 2024 - GPT-4 Turbo test ($24.80)            │   │
│   │ ○ Dec 10, 2024 - Claude 3 Opus test ($27.50)          │   │
│   │ ○ Dec 5, 2024 - Gemini Pro test ($22.10)              │   │
│   └───────────────────────────────────────────────────────┘   │
│                                                               │
│   Reason (required):                                          │
│   ┌───────────────────────────────────────────────────────┐   │
│   │ Test failure due to API outage on 12/14               │   │
│   └───────────────────────────────────────────────────────┘   │
│                                                               │
│   [✓] Notify user via email                                   │
│                                                               │
│                              [Cancel]  [Process Refund]       │
│                                                               │
└───────────────────────────────────────────────────────────────┘
```

### Interaction Notes

- **Audit logging**: All admin actions logged with timestamp and reason
- **Two-admin rule**: Deletions require confirmation from second admin
- **Email notifications**: Configurable notifications for account changes
- **Search capabilities**: Full-text search across usernames and emails

---

## 3. Failed Test Intervention Queue

Admin interface for completing tests that failed after 3 automatic retry attempts.

### Desktop Layout

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ [LOGO] GC Benchmark   Home | Research | Contribute | Admin          [▼ A]   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ← Back to Admin Dashboard                                                  │
│                                                                             │
│  Failed Test Intervention Queue                                   3 pending │
│  ═══════════════════════════════════════════════════════════════════════    │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                                                                     │    │
│  │  ⚠️ These tests require manual completion                          │    │
│  │  ───────────────────────────────────────────────────────────────   │    │
│  │  Tests are added here after 3 failed automatic retry attempts.     │    │
│  │  Users have chosen to wait for admin completion rather than        │    │
│  │  request a refund.                                                 │    │
│  │                                                                     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                                                                     │    │
│  │  │ User      │ Model          │ Progress │ Error        │ Waiting  │    │
│  │  ├───────────┼────────────────┼──────────┼──────────────┼──────────│    │
│  │  │           │                │          │              │          │    │
│  │  │ @user45   │ GPT-4o         │ 65%      │ Rate limit   │ 2 hours  │    │
│  │  │           │ OpenAI         │ 390/600  │ exceeded     │          │    │
│  │  │           │                │          │              │ [Claim]  │    │
│  │  ├───────────┼────────────────┼──────────┼──────────────┼──────────│    │
│  │  │           │                │          │              │          │    │
│  │  │ @ministry │ Claude 3.5     │ 42%      │ API timeout  │ 5 hours  │    │
│  │  │           │ Anthropic      │ 252/600  │              │          │    │
│  │  │           │                │          │              │ [Claim]  │    │
│  │  ├───────────┼────────────────┼──────────┼──────────────┼──────────│    │
│  │  │           │                │          │              │          │    │
│  │  │ @dev123   │ Gemini Pro     │ 88%      │ 500 error    │ 12 hours │    │
│  │  │           │ Google         │ 528/600  │              │          │    │
│  │  │           │                │          │              │ [Claim]  │    │
│  │  │                                                                 │    │
│  │  └─────────────────────────────────────────────────────────────────┘    │
│  │                                                                     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  My Active Interventions                                           │    │
│  │  ───────────────────────────────────────────────────────────────   │    │
│  │                                                                     │    │
│  │  │ User      │ Model          │ Progress │ Status       │ Actions  │    │
│  │  ├───────────┼────────────────┼──────────┼──────────────┼──────────│    │
│  │  │           │                │          │              │          │    │
│  │  │ @testuser │ Llama 3 70B    │ 95%      │ Running      │ [View]   │    │
│  │  │           │ Meta           │ 570/600  │ 30 remaining │          │    │
│  │  │                                                                 │    │
│  │  └─────────────────────────────────────────────────────────────────┘    │
│  │                                                                     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│  [Footer]                                                                   │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Intervention Detail View

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│  Failed Test Intervention: @user45's GPT-4o Test                            │
│  ═══════════════════════════════════════════════════════════════════════    │
│                                                                             │
│  ┌────────────────────────────────────┐  ┌────────────────────────────────┐ │
│  │  Test Information                  │  │  Failure Details               │ │
│  │  ──────────────────────────────    │  │  ──────────────────────────    │ │
│  │                                    │  │                                │ │
│  │  User:       @user45               │  │  Error Type:                   │ │
│  │  Email:      user45@example.com    │  │  API Rate Limit Exceeded       │ │
│  │  Model:      GPT-4o (OpenAI)       │  │                                │ │
│  │  Version:    2024.01.25            │  │  Last Error:                   │ │
│  │                                    │  │  "429 Too Many Requests"       │ │
│  │  Paid:       $30.00                │  │                                │ │
│  │  Started:    Dec 15, 2:15 PM       │  │  Retry Attempts: 3             │ │
│  │  Failed:     Dec 15, 2:32 PM       │  │                                │ │
│  │  Waiting:    2 hours               │  │  Last Attempt:                 │ │
│  │                                    │  │  Dec 15, 2:30 PM               │ │
│  └────────────────────────────────────┘  └────────────────────────────────┘ │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  Progress                                                           │    │
│  │  ───────────────────────────────────────────────────────────────    │    │
│  │                                                                     │    │
│  │  [████████████████████████████████░░░░░░░░░░░░░░░░░░] 65%           │    │
│  │                                                                     │    │
│  │  Completed: 390 questions                                           │    │
│  │  Remaining: 210 questions                                           │    │
│  │                                                                     │    │
│  │  Breakdown by Tier:                                                 │    │
│  │  • Tier 1: 275/420 complete (65%)                                   │    │
│  │  • Tier 2: 80/120 complete (67%)                                    │    │
│  │  • Tier 3: 35/60 complete (58%)                                     │    │
│  │                                                                     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  Admin Actions                                                      │    │
│  │  ───────────────────────────────────────────────────────────────    │    │
│  │                                                                     │    │
│  │  Option 1: Resume Test                                              │    │
│  │  ┌───────────────────────────────────────────────────────────────┐  │    │
│  │  │                                                               │  │    │
│  │  │  Resume from checkpoint using:                                │  │    │
│  │  │                                                               │  │    │
│  │  │  ○ Same API configuration (retry with delay)                  │  │    │
│  │  │  ○ Different API key (if rate limit is per-key)               │  │    │
│  │  │  ○ Alternative backend (e.g., direct OpenAI instead of        │  │    │
│  │  │    OpenRouter)                                                │  │    │
│  │  │                                                               │  │    │
│  │  │  Notes (optional):                                            │  │    │
│  │  │  ┌─────────────────────────────────────────────────────────┐  │  │    │
│  │  │  │ Switching to direct API key to avoid rate limit...     │  │  │    │
│  │  │  └─────────────────────────────────────────────────────────┘  │  │    │
│  │  │                                                               │  │    │
│  │  │  [Resume Test from Checkpoint]                                │  │    │
│  │  │                                                               │  │    │
│  │  └───────────────────────────────────────────────────────────────┘  │    │
│  │                                                                     │    │
│  │  Option 2: Issue Refund                                             │    │
│  │  ┌───────────────────────────────────────────────────────────────┐  │    │
│  │  │                                                               │  │    │
│  │  │  If the test cannot be completed, issue a full refund:        │  │    │
│  │  │                                                               │  │    │
│  │  │  Reason for admin refund:                                     │  │    │
│  │  │  ┌─────────────────────────────────────────────────────────┐  │  │    │
│  │  │  │                                                         │  │  │    │
│  │  │  └─────────────────────────────────────────────────────────┘  │  │    │
│  │  │                                                               │  │    │
│  │  │  [Issue Full Refund]                                          │  │    │
│  │  │                                                               │  │    │
│  │  └───────────────────────────────────────────────────────────────┘  │    │
│  │                                                                     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Intervention Complete Confirmation

```
┌───────────────────────────────────────────────────────────────┐
│                                                           [×] │
│                                                               │
│   Test Completed Successfully                                 │
│   ═══════════════════════════════════════════════════════     │
│                                                               │
│   ┌───────────────────────────────────────────────────────┐   │
│   │                                                       │   │
│   │  ✓ All 300 questions completed                       │   │
│   │  ✓ Results merged with checkpoint data               │   │
│   │  ✓ Test moved to moderation queue                    │   │
│   │  ✓ User @user45 notified via email                   │   │
│   │                                                       │   │
│   └───────────────────────────────────────────────────────┘   │
│                                                               │
│   Overall Score: 82                                           │
│   Tier 1: 85 | Tier 2: 78 | Tier 3: 72                       │
│                                                               │
│   Admin Notes:                                                │
│   "Completed using direct OpenAI API key to bypass           │
│   OpenRouter rate limiting. No issues with remaining         │
│   questions."                                                 │
│                                                               │
│                              [Back to Queue]  [View Results]  │
│                                                               │
└───────────────────────────────────────────────────────────────┘
```

### Interaction Notes

- **Priority queue**: Tests waiting longest shown first
- **Claim system**: Admins claim tests to prevent duplicate work
- **Checkpoint verification**: System validates checkpoint integrity before resuming
- **User notification**: Automatic email sent when admin claims, completes, or refunds
- **Audit trail**: All admin actions logged with timestamp and notes

---

## URL Structure

| Page | URL Pattern | Example |
|------|-------------|---------|
| Admin Dashboard | `/admin` | `/admin` |
| User Management | `/admin/users` | `/admin/users` |
| User Detail | `/admin/users/:userId` | `/admin/users/abc123` |
| Failed Test Queue | `/admin/interventions` | `/admin/interventions` |
| Intervention Detail | `/admin/interventions/:testId` | `/admin/interventions/abc123` |
| System Settings | `/admin/settings` | `/admin/settings` |

---

## Admin Audit Log

All admin actions are logged for accountability:

```
Audit Log Entry Structure:
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  Timestamp:    2024-12-15T14:32:00Z                             │
│  Admin:        @admin_chris                                     │
│  Action:       user.role.change                                 │
│  Target:       @testuser1                                       │
│  Details:      { from: "user", to: "moderator" }                │
│  Reason:       "Promoted to help with review backlog"           │
│  IP Address:   192.168.1.xxx                                    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

Logged Actions:
- Role changes
- Account suspensions/reactivations
- Account deletions
- Refund processing
- Password reset triggers
- Admin note additions
- Failed test intervention claims
- Failed test resumptions
- Failed test admin completions
```

---

## Security Considerations

1. **Session management**: Admin sessions timeout after 30 minutes of inactivity
2. **IP logging**: All admin actions logged with IP address
3. **Two-factor**: Recommended for admin accounts (via Auth0)
4. **Rate limiting**: Admin API endpoints have stricter rate limits
5. **Audit retention**: Audit logs retained for minimum 2 years

---

*This completes the wireframe documentation suite for the Great Commission Benchmark platform.*
