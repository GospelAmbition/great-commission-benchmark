# Great Commission Benchmark - Platform Design System

## Overview

This document establishes the design system foundation for the Great Commission Benchmark platform. All wireframes in the companion documents reference these standards.

## Document Index

| Document | Pages Covered |
|----------|---------------|
| `wireframes-design-system.md` | Design system, colors, components, navigation |
| `wireframes-public-pages.md` | Homepage, Research (Leaderboard, Compare, Model Detail, Categories), Contribute, About, Public Profile |
| `wireframes-user-pages.md` | User Dashboard, Account/Settings, Payment History |
| `wireframes-test-flow.md` | Model Selection, Payment, Results Pending, Results Ready |
| `wireframes-moderator-pages.md` | Moderator Dashboard, Review Queue, Review Interface, Appeals Queue |
| `wireframes-admin-pages.md` | System Stats Dashboard, User Management |

---

## Design Principles

1. **Clarity First**: Complex benchmark data presented simply
2. **Trust Through Transparency**: Show methodology, scoring details openly
3. **Progressive Disclosure**: Summary → Detail → Raw Data flow
4. **Consistent Hierarchy**: Same patterns across all page types
5. **Mobile-Conscious**: Key pages optimized for mobile viewing

---

## Color Palette

Based on brand colors from the marketing website:

```
Primary Colors:
┌─────────────────────────────────────────────────────────────┐
│  --ga-red: #a11824        Primary dark red (brand anchor)   │
│  --ga-dark-red: #7a1219   Darker red (hover states)         │
│  --ga-light-red: #e84545  Lighter red (links, buttons)      │
│  --ga-accent-red: #fee9e8 Very light red (backgrounds)      │
└─────────────────────────────────────────────────────────────┘

Neutral Colors:
┌─────────────────────────────────────────────────────────────┐
│  --ga-black: #232323      Deep black (text, headers)        │
│  --ga-white: #ffffff      Clean white (backgrounds)         │
│  --ga-gray: #f5f5f7       Soft gray (panels, cards)         │
│  --ga-medium-gray: #999   Medium gray (secondary text)      │
└─────────────────────────────────────────────────────────────┘

Semantic Colors:
┌─────────────────────────────────────────────────────────────┐
│  Success: #28a745         Green for pass/success states     │
│  Warning: #ffc107         Yellow for pending/caution        │
│  Error: #dc3545           Red for fail/error states         │
│  Info: #17a2b8            Blue for informational            │
└─────────────────────────────────────────────────────────────┘
```

---

## Typography

```
Font Stack:
┌─────────────────────────────────────────────────────────────┐
│  Primary: 'Inter', 'Segoe UI', Roboto, sans-serif           │
│  Monospace: 'SF Mono', 'Monaco', 'Consolas', monospace      │
└─────────────────────────────────────────────────────────────┘

Scale:
┌─────────────────────────────────────────────────────────────┐
│  Page Title:    32px / bold    / --ga-black                 │
│  Section Title: 24px / semibold / --ga-black                │
│  Card Title:    18px / semibold / --ga-black                │
│  Body:          16px / regular / --ga-black                 │
│  Small:         14px / regular / --ga-medium-gray           │
│  Caption:       12px / regular / --ga-medium-gray           │
└─────────────────────────────────────────────────────────────┘
```

---

## Navigation Structure

### Global Header (All Pages)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ [LOGO] Great Commission Benchmark  Home | Research | Contribute | About [L] │
│                                                                             │
│ (logged in: Home | Research | Contribute | About | Dashboard | [User ▼])   │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Navigation Structure:**
- **Home** (`/`) - Fast, visually compelling showcase of top models
- **Research** (`/research`) - Deep-dive tools: full leaderboard, comparisons, categories
- **Contribute** (`/contribute`) - Community vision: run tests, submit models, support the project
- **About** (`/about`) - Organization info, methodology, FAQ
- **Dashboard** (authenticated only) - User's personal testing hub

### User Menu Dropdown (Authenticated)

```
┌─────────────────────┐
│ My Dashboard        │
│ Run New Test        │
│ Payment History     │
│ Account Settings    │
│ ─────────────────── │
│ Logout              │
└─────────────────────┘
```

### Moderator Menu (Role-Based)

```
┌─────────────────────┐
│ Moderator Dashboard │
│ Review Queue        │
│ Appeals             │
│ ─────────────────── │
│ Back to Platform    │
└─────────────────────┘
```

### Admin Menu (Role-Based)

```
┌─────────────────────┐
│ Admin Dashboard     │
│ User Management     │
│ System Stats        │
│ ─────────────────── │
│ Back to Platform    │
└─────────────────────┘
```

### Global Footer

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│   Great Commission Benchmark                                                │
│                                                                             │
│   Platform              Community              Legal              Connect   │
│   ─────────────         ─────────────          ─────────────      ───────   │
│   Home                  Contribute             Terms of Service   GitHub    │
│   Research              Discord                Privacy Policy     Contact   │
│   Methodology           API Documentation      Tester Agreement             │
│                                                                             │
│   © 2025 Great Commission Benchmark. All rights reserved.                   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Common Components

### Card Component

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  Card Title                                    [Action ▼]   │
│  ───────────────────────────────────────────────────────    │
│                                                             │
│  Card content area with data, text, or visualizations.      │
│                                                             │
│                                                             │
└─────────────────────────────────────────────────────────────┘

States: Default (--ga-white bg, subtle shadow)
        Hover (elevated shadow)
        Selected (--ga-accent-red border-left)
```

### Button Variants

```
Primary Button:        [  Run Test  ]     --ga-red bg, white text
                       Hover: --ga-dark-red bg

Secondary Button:      [  View Details  ] --ga-white bg, --ga-red border/text
                       Hover: --ga-accent-red bg

Text Button:           View All →         --ga-light-red text, no border
                       Hover: underline

Disabled Button:       [  Processing  ]   --ga-gray bg, --ga-medium-gray text
```

### Data Table

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  Column A ▼    │  Column B      │  Column C      │  Column D      │ Actions │
├─────────────────────────────────────────────────────────────────────────────┤
│  Row 1 data    │  Value         │  Value         │  Value         │  [···]  │
├─────────────────────────────────────────────────────────────────────────────┤
│  Row 2 data    │  Value         │  Value         │  Value         │  [···]  │
├─────────────────────────────────────────────────────────────────────────────┤
│  Row 3 data    │  Value         │  Value         │  Value         │  [···]  │
└─────────────────────────────────────────────────────────────────────────────┘
│                              [< Prev]  Page 1 of 5  [Next >]                │
└─────────────────────────────────────────────────────────────────────────────┘

Features: Sortable columns (▼/▲), row hover highlight, pagination
```

### Score Badge

```
High Score (≥80):    ┌──────┐
                     │ 92.3 │  --ga-red bg, white text, bold
                     └──────┘

Medium Score (50-79): ┌──────┐
                      │ 67.8 │  --ga-accent-red bg, --ga-red text
                      └──────┘

Low Score (<50):      ┌──────┐
                      │ 34.2 │  --ga-gray bg, --ga-medium-gray text
                      └──────┘
```

### Status Indicator

```
┌─────────┐
│ ● Pass  │   Green dot + text
└─────────┘

┌─────────┐
│ ○ Fail  │   Red outline dot + text
└─────────┘

┌─────────┐
│ ◐ Pending│   Yellow half-filled dot + text
└─────────┘
```

### Progress Indicator (Test Flow)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│    ●──────────────●──────────────○──────────────○                          │
│    Select         Payment        Processing      Results                    │
│    Model          (current)                                                 │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

● = Completed (--ga-red filled)
● = Current (--ga-red filled, larger)
○ = Upcoming (--ga-medium-gray outline)
```

### Alert/Notification Banner

```
Info:
┌─────────────────────────────────────────────────────────────────────────────┐
│ ℹ  Your test is processing. Results typically ready in 2-5 minutes.    [×] │
└─────────────────────────────────────────────────────────────────────────────┘
   Info blue bg, dark text

Success:
┌─────────────────────────────────────────────────────────────────────────────┐
│ ✓  Payment successful! Your test has been queued.                      [×] │
└─────────────────────────────────────────────────────────────────────────────┘
   Success green bg, dark text

Error:
┌─────────────────────────────────────────────────────────────────────────────┐
│ ✗  Payment failed. Please try again or contact support.                [×] │
└─────────────────────────────────────────────────────────────────────────────┘
   Error red bg, white text
```

### Modal Dialog

```
┌─────────────────────────────────────────────────────────────┐
│                                                         [×] │
│                                                             │
│   Modal Title                                               │
│   ───────────────────────────────────────────────────────   │
│                                                             │
│   Modal content goes here. This could be a confirmation     │
│   dialog, form, or detailed information view.               │
│                                                             │
│                                                             │
│                        [Cancel]  [Confirm Action]           │
│                                                             │
└─────────────────────────────────────────────────────────────┘

Background: Semi-transparent dark overlay
```

### Empty State

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│                         [Icon]                              │
│                                                             │
│                   No results found                          │
│                                                             │
│         Try adjusting your filters or search terms          │
│                                                             │
│                    [Clear Filters]                          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Loading State

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│                        [Spinner]                            │
│                                                             │
│                   Loading results...                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Chart Components (Chart.js)

### Bar Chart (Category Scores)

```
┌─────────────────────────────────────────────────────────────┐
│  Category Performance                                       │
│  ───────────────────────────────────────────────────────    │
│                                                             │
│  Scripture    ████████████████████████████████░░░░  82%     │
│  Theology     ██████████████████████████░░░░░░░░░░  65%     │
│  Ethics       ████████████████████████████████████  91%     │
│  Apologetics  ████████████████████░░░░░░░░░░░░░░░░  48%     │
│                                                             │
│               0%    25%    50%    75%   100%                │
└─────────────────────────────────────────────────────────────┘
```

### Line Chart (Score Trends)

```
┌─────────────────────────────────────────────────────────────┐
│  Score Trend Over Time                                      │
│  ───────────────────────────────────────────────────────    │
│                                                             │
│  100│                              ●                        │
│     │                    ●────────╱                         │
│   75│          ●────────╱                                   │
│     │    ●────╱                                             │
│   50│───╱                                                   │
│     │                                                       │
│   25│                                                       │
│     └───────────────────────────────────────────────        │
│        v1.0   v1.1   v1.2   v1.3   v1.4                     │
└─────────────────────────────────────────────────────────────┘
```

### Radar Chart (Multi-Category Comparison)

```
┌─────────────────────────────────────────────────────────────┐
│  Category Comparison                                        │
│  ───────────────────────────────────────────────────────    │
│                                                             │
│                    Scripture                                │
│                        ●                                    │
│                       /│\                                   │
│                      / │ \                                  │
│           Ethics ●──/──┼──\──● Theology                     │
│                    \ │ /                                    │
│                     \│/                                     │
│                      ●                                      │
│                 Apologetics                                 │
│                                                             │
│         ─── GPT-4    ─── Claude    ─── Gemini               │
└─────────────────────────────────────────────────────────────┘
```

---

## Responsive Breakpoints

```
Desktop:    ≥1024px   Full layout, side-by-side panels
Tablet:     768-1023  Stacked layout, collapsed navigation
Mobile:     <768px    Single column, hamburger menu
```

### Mobile Navigation

```
┌─────────────────────────────────────────┐
│ [≡]  Great Commission Benchmark   [👤]  │
└─────────────────────────────────────────┘

Menu expanded:
┌─────────────────────────────────────────┐
│ [×]  Great Commission Benchmark   [👤]  │
├─────────────────────────────────────────┤
│                                         │
│   Home                                  │
│   Research                              │
│   Contribute                            │
│   About                                 │
│   ─────────────────────────────────     │
│   Login with Auth0                      │
│                                         │
└─────────────────────────────────────────┘
```

---

## Authentication States

### Logged Out Header

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ [LOGO] Great Commission Benchmark  Home | Research | Contribute | About [L] │
└─────────────────────────────────────────────────────────────────────────────┘

[L] = Login button, triggers Auth0 redirect (external flow)
```

### Logged In Header

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ [LOGO] GC Benchmark  Home | Research | Contribute | About | Dashboard [▼ U] │
└─────────────────────────────────────────────────────────────────────────────┘

[▼ U] = User avatar/initial with dropdown menu
```

### Role Indicators

```
Regular User:     [U]  Standard user menu
Moderator:        [M]  User menu + Moderator Dashboard link
Admin:            [A]  User menu + Admin Dashboard link
```

---

## Accessibility Notes

1. **Color Contrast**: All text meets WCAG AA standards (4.5:1 minimum)
2. **Focus States**: Visible focus rings on all interactive elements
3. **Screen Readers**: Proper ARIA labels on icons and interactive elements
4. **Keyboard Navigation**: Full keyboard support for all interactions
5. **Skip Links**: "Skip to main content" link at page top

---

## Implementation Notes

### CSS Variables Setup

```css
:root {
  /* Typography */
  --font-primary: 'Inter', 'Segoe UI', Roboto, sans-serif;
  --font-mono: 'SF Mono', Monaco, Consolas, monospace;
  
  /* Brand Colors */
  --ga-red: #a11824;
  --ga-dark-red: #7a1219;
  --ga-light-red: #e84545;
  --ga-accent-red: #fee9e8;
  --ga-black: #232323;
  --ga-white: #ffffff;
  --ga-gray: #f5f5f7;
  --ga-medium-gray: #999999;
  
  /* Semantic Colors */
  --color-success: #28a745;
  --color-warning: #ffc107;
  --color-error: #dc3545;
  --color-info: #17a2b8;
  
  /* Spacing Scale */
  --space-xs: 4px;
  --space-sm: 8px;
  --space-md: 16px;
  --space-lg: 24px;
  --space-xl: 32px;
  --space-xxl: 48px;
  
  /* Border Radius */
  --radius-sm: 4px;
  --radius-md: 8px;
  --radius-lg: 12px;
  
  /* Shadows */
  --shadow-sm: 0 1px 3px rgba(0,0,0,0.1);
  --shadow-md: 0 4px 6px rgba(0,0,0,0.1);
  --shadow-lg: 0 10px 20px rgba(0,0,0,0.15);
}
```

### Font Loading

Inter is the primary typeface for the platform. Load via:

```html
<!-- Google Fonts (recommended for simplicity) -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
```

Or use `@next/font` in Next.js for automatic optimization:

```typescript
import { Inter } from 'next/font/google'

const inter = Inter({ subsets: ['latin'] })
```

### Component Library Recommendations

- **React Components**: Use Headless UI or Radix for accessible primitives
- **Charts**: Chart.js with react-chartjs-2 wrapper
- **Forms**: React Hook Form for validation
- **Tables**: TanStack Table for sorting/filtering/pagination

---

*Next: See `wireframes-public-pages.md` for public-facing page layouts*
