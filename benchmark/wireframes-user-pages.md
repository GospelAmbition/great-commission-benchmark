# Great Commission Benchmark - User Pages Wireframes

## Overview

This document contains wireframes for authenticated user pages that provide account management and test history functionality.

**Pages Covered:**
1. User Dashboard
2. Account/Settings
3. Payment History

*Reference `wireframes-design-system.md` for component specifications and color palette.*

---

## 1. User Dashboard

The authenticated user's home base showing their testing activity and quick actions.

### Desktop Layout

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ [LOGO] GC Benchmark  Home | Research | Contribute | About | Dashboard [▼ U] │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Welcome back, @testuser123                                                 │
│                                                                             │
│  ┌───────────────────────────────────────────────┐  ┌────────────────────┐  │
│  │                                               │  │                    │  │
│  │  Quick Actions                                │  │  Account Summary   │  │
│  │  ─────────────────────────────────────────    │  │  ────────────────  │  │
│  │                                               │  │                    │  │
│  │  ┌─────────────────┐  ┌─────────────────┐     │  │  Member since:     │  │
│  │  │                 │  │                 │     │  │  Oct 2024          │  │
│  │  │  [+] Run New    │  │  [📊] Compare   │     │  │                    │  │
│  │  │      Test       │  │     Models      │     │  │  Tests Run: 15     │  │
│  │  │                 │  │                 │     │  │                    │  │
│  │  └─────────────────┘  └─────────────────┘     │  │  Total Spent:      │  │
│  │                                               │  │  $75.00            │  │
│  │  ┌─────────────────┐  ┌─────────────────┐     │  │                    │  │
│  │  │                 │  │                 │     │  │                    │  │
│  │  │  [📜] View      │  │  [⚙️] Account   │     │  │                    │  │
│  │  │     History     │  │    Settings     │     │  │                    │  │
│  │  │                 │  │                 │     │  │                    │  │
│  │  └─────────────────┘  └─────────────────┘     │  │                    │  │
│  │                                               │  │                    │  │
│  └───────────────────────────────────────────────┘  └────────────────────┘  │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  Pending Results                                          [View All]│    │
│  │  ───────────────────────────────────────────────────────────────    │    │
│  │                                                                     │    │
│  │  ┌───────────────────────────────────────────────────────────────┐  │    │
│  │  │ ◐ Processing                                                  │  │    │
│  │  │                                                               │  │    │
│  │  │ GPT-4o · Started 3 minutes ago                                │  │    │
│  │  │ Estimated completion: ~2 minutes                              │  │    │
│  │  │                                                               │  │    │
│  │  │ [████████████████████░░░░░░░░░░] 65%                          │  │    │
│  │  │                                                               │  │    │
│  │  │                                         [View Progress →]     │  │    │
│  │  └───────────────────────────────────────────────────────────────┘  │    │
│  │                                                                     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  Recent Test Results                                      [View All]│    │
│  │  ───────────────────────────────────────────────────────────────    │    │
│  │                                                                     │    │
│  │  Date          │ Model              │ Score  │ Status    │ Actions │    │
│  │  ──────────────┼────────────────────┼────────┼───────────┼─────────│    │
│  │  Dec 14, 2024  │ GPT-4 Turbo        │ 92.3   │ ● Live    │ [View]  │    │
│  │  Dec 10, 2024  │ Claude 3 Opus      │ 89.7   │ ● Live    │ [View]  │    │
│  │  Dec 5, 2024   │ Gemini Pro         │ 78.4   │ ● Live    │ [View]  │    │
│  │                                                                     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  ┌──────────────────────────────────┐  ┌──────────────────────────────┐     │
│  │  Your Testing Stats              │  │  Notifications               │     │
│  │  ────────────────────────────    │  │  ────────────────────────    │     │
│  │                                  │  │                              │     │
│  │  Total Tests:     15             │  │  🔔 Results ready for        │     │
│  │  Models Tested:   12             │  │     Claude 3 Opus test       │     │
│  │  Avg Score:       81.4           │  │     2 hours ago              │     │
│  │                                  │  │                              │     │
│  │  [Bar chart: Tests by month]     │  │  🔔 Your GPT-4 test was      │     │
│  │                                  │  │     published to leaderboard │     │
│  │    Dec ████████  5               │  │     1 day ago                │     │
│  │    Nov █████     3               │  │                              │     │
│  │    Oct ███████   4               │  │  [View All Notifications →]  │     │
│  │    Sep ███       2               │  │                              │     │
│  │    Aug █         1               │  │                              │     │
│  │                                  │  │                              │     │
│  └──────────────────────────────────┘  └──────────────────────────────┘     │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│  [Footer]                                                                   │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Mobile Layout

```
┌─────────────────────────────────────┐
│ [≡]  GC Benchmark              [👤] │
├─────────────────────────────────────┤
│                                     │
│  Welcome, @testuser123              │
│                                     │
│  ┌─────────────────────────────────┐│
│  │ Account Summary                 ││
│  │ ─────────────────────────────── ││
│  │ Tests: 15  |  Spent: $75.00     ││
│  └─────────────────────────────────┘│
│                                     │
│  ┌───────────────┐┌───────────────┐ │
│  │ [+] Run Test  ││ [📊] Compare  │ │
│  └───────────────┘└───────────────┘ │
│                                     │
│  ┌─────────────────────────────────┐│
│  │ ◐ Processing                    ││
│  │ GPT-4o · 3 min ago              ││
│  │ [████████████░░░░░░░░] 65%      ││
│  │                    [View →]     ││
│  └─────────────────────────────────┘│
│                                     │
│  Recent Results                     │
│  ─────────────────────────────────  │
│                                     │
│  ┌─────────────────────────────────┐│
│  │ GPT-4 Turbo         92.3       ││
│  │ Dec 14 · ● Live       [View →] ││
│  ├─────────────────────────────────┤│
│  │ Claude 3 Opus       89.7       ││
│  │ Dec 10 · ● Live       [View →] ││
│  ├─────────────────────────────────┤│
│  │ Gemini Pro          78.4       ││
│  │ Dec 5 · ● Live        [View →] ││
│  └─────────────────────────────────┘│
│                                     │
│  [View All Results]                 │
│                                     │
├─────────────────────────────────────┤
│  [Footer]                           │
└─────────────────────────────────────┘
```

### Interaction Notes

- **Quick action cards**: Large tap targets for primary actions
- **Pending results**: Auto-refreshes every 30 seconds
- **Progress bar**: Shows real-time test completion status
- **Notifications**: Unread highlighted, click to mark read

---

## 2. Account/Settings Page

User account management and preferences.

### Desktop Layout

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ [LOGO] GC Benchmark  Home | Research | Contribute | About | Dashboard [▼ U] │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ← Back to Dashboard                                                        │
│                                                                             │
│  ┌────────────────────┐  ┌──────────────────────────────────────────────┐   │
│  │                    │  │                                              │   │
│  │  Settings Menu     │  │  Profile Settings                           │   │
│  │  ──────────────    │  │  ════════════════════════════════════════   │   │
│  │                    │  │                                              │   │
│  │  ● Profile         │  │  ┌───────────────────────────────────────┐   │   │
│  │  ○ Notifications   │  │  │                                       │   │   │
│  │  ○ Privacy         │  │  │  Display Name                         │   │   │
│  │  ○ Danger Zone     │  │  │  ┌─────────────────────────────────┐   │   │   │
│  │                    │  │  │  │ testuser123                     │   │   │   │
│  │                    │  │  │  └─────────────────────────────────┘   │   │   │
│  │                    │  │  │  This is your public username.         │   │   │
│  │                    │  │  │                                       │   │   │
│  │                    │  │  │  Email                                │   │   │
│  │                    │  │  │  ┌─────────────────────────────────┐   │   │   │
│  │                    │  │  │  │ user@example.com                │   │   │   │
│  │                    │  │  │  └─────────────────────────────────┘   │   │   │
│  │                    │  │  │  Managed by Auth0. Change via login.  │   │   │
│  │                    │  │  │                                       │   │   │
│  │                    │  │  │  Bio (Optional)                       │   │   │
│  │                    │  │  │  ┌─────────────────────────────────┐   │   │   │
│  │                    │  │  │  │ Christian developer interested  │   │   │   │
│  │                    │  │  │  │ in AI and theology.             │   │   │   │
│  │                    │  │  │  └─────────────────────────────────┘   │   │   │
│  │                    │  │  │  Max 200 characters                   │   │   │
│  │                    │  │  │                                       │   │   │
│  │                    │  │  │                   [Save Changes]       │   │   │
│  │                    │  │  │                                       │   │   │
│  │                    │  │  └───────────────────────────────────────┘   │   │
│  │                    │  │                                              │   │
│  │                    │  │  ┌───────────────────────────────────────┐   │   │
│  │                    │  │  │                                       │   │   │
│  │                    │  │  │  Connected Accounts                   │   │   │
│  │                    │  │  │  ─────────────────────────────────    │   │   │
│  │                    │  │  │                                       │   │   │
│  │                    │  │  │  Auth0 (Google)  ● Connected          │   │   │
│  │                    │  │  │  user@example.com                     │   │   │
│  │                    │  │  │                                       │   │   │
│  │                    │  │  │  CLI Access      ○ Not linked         │   │   │
│  │                    │  │  │  [Generate CLI Token]                 │   │   │
│  │                    │  │  │                                       │   │   │
│  │                    │  │  └───────────────────────────────────────┘   │   │
│  │                    │  │                                              │   │
│  └────────────────────┘  └──────────────────────────────────────────────┘   │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│  [Footer]                                                                   │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Settings Sections

#### Notifications Settings

```
┌───────────────────────────────────────────────────────────────┐
│                                                               │
│  Notification Preferences                                     │
│  ════════════════════════════════════════════════════════     │
│                                                               │
│  Email Notifications                                          │
│  ───────────────────────────────────────────────────────      │
│                                                               │
│  [✓] Test results ready & published                           │
│      Receive email when your benchmark test completes         │
│      (Platform tests are auto-published to leaderboard)       │
│                                                               │
│  [✓] CLI submission verified                                  │
│      Receive email when CLI submissions are verified          │
│                                                               │
│  [ ] Weekly leaderboard updates                               │
│      Summary of leaderboard changes and new models            │
│                                                               │
│  [ ] Platform announcements                                   │
│      New features, methodology updates, etc.                  │
│                                                               │
│                                              [Save Changes]   │
│                                                               │
└───────────────────────────────────────────────────────────────┘
```

#### Privacy Settings

```
┌───────────────────────────────────────────────────────────────┐
│                                                               │
│  Privacy Settings                                             │
│  ════════════════════════════════════════════════════════     │
│                                                               │
│  Profile Visibility                                           │
│  ───────────────────────────────────────────────────────      │
│                                                               │
│  [●] Public                                                   │
│      Your username and test history visible on leaderboard    │
│                                                               │
│  [ ] Private                                                  │
│      Tests attributed to "Anonymous Contributor"              │
│                                                               │
│                                                               │
│  Data Export                                                  │
│  ───────────────────────────────────────────────────────      │
│                                                               │
│  [Download My Data]   Export all your data (JSON format)      │
│                                                               │
│                                              [Save Changes]   │
│                                                               │
└───────────────────────────────────────────────────────────────┘
```

#### Danger Zone Settings

```
┌───────────────────────────────────────────────────────────────┐
│                                                               │
│  Danger Zone                                                  │
│  ════════════════════════════════════════════════════════     │
│                                                               │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │  ⚠️ Delete Account                                      │  │
│  │  ─────────────────────────────────────────────────────  │  │
│  │                                                         │  │
│  │  Permanently delete your account and all associated     │  │
│  │  data. Your test contributions will be anonymized.      │  │
│  │                                                         │  │
│  │  This action cannot be undone.                          │  │
│  │                                                         │  │
│  │                              [Delete My Account]        │  │
│  │                                                         │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                               │
└───────────────────────────────────────────────────────────────┘
```

### Interaction Notes

- **Tab navigation**: Settings sections in left nav
- **Inline validation**: Form fields validate on blur
- **Confirmation modals**: Destructive actions require confirmation
- **Toast notifications**: Success/error feedback after save

---

## 3. Purchase History Page

View of all test purchases and transactions.

### Desktop Layout

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ [LOGO] GC Benchmark  Home | Research | Contribute | About | Dashboard [▼ U] │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ← Back to Dashboard                                                        │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                                                                     │    │
│  │  Purchase History                                                   │    │
│  │  ═══════════════════════════════════════════════════════════════    │    │
│  │                                                                     │    │
│  │  ┌────────────────────────────┐  ┌────────────────────────────┐     │    │
│  │  │                            │  │                            │     │    │
│  │  │  Total Tests               │  │  Total Spent               │     │    │
│  │  │  ────────────────────────  │  │  ────────────────────────  │     │    │
│  │  │                            │  │                            │     │    │
│  │  │     15                     │  │     $75.00                 │     │    │
│  │  │                            │  │                            │     │    │
│  │  │  Benchmark tests run       │  │  Since Oct 2024            │     │    │
│  │  │                            │  │                            │     │    │
│  │  └────────────────────────────┘  └────────────────────────────┘     │    │
│  │                                                                     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                                                                     │    │
│  │  Transaction History                                    [Export CSV]│    │
│  │  ───────────────────────────────────────────────────────────────    │    │
│  │                                                                     │    │
│  │  Filter: [All Transactions ▼]   Date: [Last 30 Days ▼]              │    │
│  │                                                                     │    │
│  │  Date          │ Type              │ Description        │ Amount   │    │
│  │  ──────────────┼───────────────────┼────────────────────┼──────────│    │
│  │                │                   │                    │          │    │
│  │  Dec 14, 2024  │ 🧪 Test Purchase  │ GPT-4 Turbo test   │ $5.00    │    │
│  │                │                   │ Run ID: abc123     │          │    │
│  │  ──────────────┼───────────────────┼────────────────────┼──────────│    │
│  │                │                   │                    │          │    │
│  │  Dec 10, 2024  │ 🧪 Test Purchase  │ Claude 3 Opus test │ $5.00    │    │
│  │                │                   │ Run ID: def456     │          │    │
│  │  ──────────────┼───────────────────┼────────────────────┼──────────│    │
│  │                │                   │                    │          │    │
│  │  Dec 5, 2024   │ 🧪 Test Purchase  │ Gemini Pro test    │ $5.00    │    │
│  │                │                   │ Run ID: ghi789     │          │    │
│  │  ──────────────┼───────────────────┼────────────────────┼──────────│    │
│  │                │                   │                    │          │    │
│  │  Dec 1, 2024   │ ↩️ Refund         │ API failure refund │ -$5.00   │    │
│  │                │                   │ Run ID: jkl012     │          │    │
│  │                                                                     │    │
│  │                    [< Prev]  Page 1 of 3  [Next >]                  │    │
│  │                                                                     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                                                                     │    │
│  │  Pricing                                                            │    │
│  │  ───────────────────────────────────────────────────────────────    │    │
│  │                                                                     │    │
│  │  Each benchmark test costs model API price + $20.                   │    │
│  │                                                                     │    │
│  │  This covers:                                                       │    │
│  │  • 300 benchmark questions + all results                            │    │
│  │  • Full scoring across all categories                               │    │
│  │  • Permanent storage                                                │    │
│  │  • Leaderboard listing                                              │    │
│  │                                                                     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│  [Footer]                                                                   │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Interaction Notes

- **Transaction filtering**: Filter by type (test purchases, refunds)
- **Export CSV**: Download transaction history for records
- **Receipt links**: Each purchase links to Stripe receipt
- **Refund visibility**: Refunds shown with negative amounts and reason

---

## URL Structure

| Page | URL Pattern | Example |
|------|-------------|---------|
| User Dashboard | `/dashboard` | `/dashboard` |
| Account Settings | `/settings/:section?` | `/settings/notifications` |
| Purchase History | `/purchases` | `/purchases` |

---

## Authentication Requirements

All pages in this document require authentication:

- **Redirect behavior**: Unauthenticated users → Auth0 login → Return to requested page
- **Session timeout**: 24-hour session with refresh token
- **Role check**: Standard user role minimum required

---

*Next: See `wireframes-test-flow.md` for the model testing wizard*
