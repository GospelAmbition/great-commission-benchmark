# Leaderboard Feature Specification

## Purpose

The leaderboard is the primary public-facing feature of the Great Commission Benchmark platform. It displays ranked model performance results, enabling users to quickly identify which LLMs best support Great Commission Christian work.

---

## Overview

The leaderboard provides:

- **Ranked model performance** — Models sorted by overall GCB score
- **Multi-dimensional filtering** — View results by category, tier, version, or date range
- **Detailed drill-down** — Click through to model detail pages for comprehensive analysis
- **Comparison tools** — Side-by-side comparison of selected models
- **Version tracking** — Historical performance across benchmark versions

---

## User Stories

### Primary Users

1. **Christian Organizations** — "I need to quickly see which models perform best overall for ministry work"
2. **Volunteers** — "I want to see how the model I tested ranks compared to others"
3. **Model Developers** — "I need to understand where my model stands and identify improvement areas"
4. **Researchers** — "I want to analyze trends and performance patterns across categories"

### Key Scenarios

- **Scenario 1:** A mission agency visits the site and immediately sees the top 5 models ranked by overall score
- **Scenario 2:** A user filters to "Evangelistic Material Creation" to see which models excel at that specific use case
- **Scenario 3:** A volunteer compares their newly tested model against the top 3 existing models
- **Scenario 4:** A researcher views historical leaderboards to track model improvement over time

---

## Architecture

### Component Structure

```
┌─────────────────────────────────────────────────────────┐
│                  Leaderboard Page (Next.js)              │
├─────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────────────────────────┐ │
│  │ Filter Panel │  │  Chart.js Visualizations         │ │
│  │              │  │  • Top Performers Bar Chart      │ │
│  └──────────────┘  │  • Tier Breakdown Chart         │ │
│                    │  • Category Heatmap             │ │
│                    │  • Verdict Distribution Chart   │ │
│                    └──────────────────────────────────┘ │
│  ┌──────────────┐  ┌──────────────────────────────────┐ │
│  │ Ranking Table│  │  Comparison Tools                 │ │
│  │ (Collapsible)│  │  • Model Selection               │ │
│  │              │  │  • Quick Compare                  │ │
│  └──────────────┘  └──────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│              FastAPI Backend (Results API)               │
│  ┌──────────────────────────────────────────────────┐  │
│  │ GET /api/leaderboard                              │  │
│  │ GET /api/leaderboard/:version                     │  │
│  │ GET /api/leaderboard/category/:slug               │  │
│  │ GET /api/leaderboard/compare                      │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
                    PostgreSQL
              (test_runs, results, models)
```

---

## Data Model

### Leaderboard Entry

Each leaderboard entry represents the **best result** for a model within the selected filter criteria.

```typescript
interface LeaderboardEntry {
  rank: number;                    // Overall rank position
  model: {
    id: string;
    name: string;
    provider: string;
    model_id: string;              // OpenRouter model ID
  };
  test_run: {
    id: string;
    trust_tier: 'automated' | 'reviewed' | 'validated';
    completed_at: string;
    question_set_version: string;
  };
  scores: {
    overall: number;               // Weighted GCB score (0-100)
    tier1: number;                 // Task capability (0-100)
    tier2: number;                 // Doctrinal fidelity (0-100)
    tier3: number;                 // Worldview confession (0-100)
  };
  category_scores: {               // Per-category breakdown
    [category: string]: number;    // e.g., "3.1": 85, "3.2": 72
  };
  verdict_distribution: {
    ACCEPTED: number;
    COMPROMISED: number;
    REFUSED: number;
    ERROR: number;
  };
  total_questions: number;
  metadata: {
    submitted_by?: string;         // User/organization name (if public)
    submission_date: string;
    methodology_version: string;
  };
}
```

### Ranking Logic

**Primary Sort:** Overall GCB score (descending)

**Tie-breaking (in order):**
1. Higher Tier 1 (Task Capability) score
2. Higher Tier 2 (Doctrinal Fidelity) score
3. More recent test completion date
4. Higher trust tier (validated > reviewed > automated)

**Best Result Selection:**
- When multiple test runs exist for the same model, select the run with the **highest overall score**
- If scores are equal, prefer runs with higher trust tier
- If trust tiers are equal, prefer most recent run

---

## API Endpoints

### GET /api/leaderboard

Get the overall leaderboard with optional filtering.

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `version` | string | `current` | Semantic version (e.g., "1.0", "1.1", "2.0") or "current" |
| `marketing_version` | string | - | Marketing version (e.g., "Version 1", "Version 2") |
| `category` | string | - | Filter by category (e.g., "3.1", "3.2") |
| `tier` | integer | - | Filter by tier (1, 2, or 3) |
| `provider` | string | - | Filter by model provider (e.g., "OpenAI", "Anthropic") |
| `trust_tier` | string | - | Filter by trust tier ("automated", "reviewed", "validated") |
| `limit` | integer | 50 | Number of results to return |
| `offset` | integer | 0 | Pagination offset |
| `sort` | string | `score` | Sort field ("score", "date", "tier1", "tier2", "tier3") |
| `order` | string | `desc` | Sort order ("asc", "desc") |

**Response:**

```json
{
  "semantic_version": "1.2",
  "marketing_version": "Version 1",
  "filters": {
    "category": null,
    "tier": null,
    "provider": null,
    "trust_tier": null
  },
  "total_models": 42,
  "entries": [
    {
      "rank": 1,
      "model": {
        "id": "uuid",
        "name": "Claude 3.5 Sonnet",
        "provider": "Anthropic",
        "model_id": "anthropic/claude-3.5-sonnet"
      },
      "test_run": {
        "id": "uuid",
        "trust_tier": "validated",
        "completed_at": "2025-12-15T10:30:00Z",
        "question_set_version": "1.2"
      },
      "scores": {
        "overall": 87,
        "tier1": 92,
        "tier2": 78,
        "tier3": 65
      },
      "category_scores": {
        "3.1": 88,
        "3.2": 95,
        "3.3": 90,
        "3.4": 85,
        "3.5": 92,
        "3.6": 88
      },
      "verdict_distribution": {
        "ACCEPTED": 245,
        "COMPROMISED": 12,
        "REFUSED": 8,
        "ERROR": 0
      },
      "total_questions": 265,
      "metadata": {
        "submission_date": "2025-12-15",
        "marketing_version": "Version 1"
      }
    }
  ],
  "pagination": {
    "limit": 50,
    "offset": 0,
    "total": 42,
    "has_more": false
  }
}
```

### GET /api/leaderboard/:version

Get leaderboard for a specific benchmark version.

**Path Parameters:**
- `version`: Semantic version identifier (e.g., "1.0", "1.1", "2.0")

**Query Parameters:** Same as `/api/leaderboard`

### GET /api/leaderboard/category/:slug

Get leaderboard filtered to a specific category.

**Path Parameters:**
- `slug`: Category identifier (e.g., "3.1", "3.2", "missiological-research")

**Query Parameters:** Same as `/api/leaderboard` (except `category` is ignored)

**Response:** Same structure as `/api/leaderboard`, but scores reflect only the selected category.

### GET /api/leaderboard/compare

Compare multiple models side-by-side.

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `models` | string[] | yes | Array of model IDs to compare |
| `version` | string | no | Benchmark version (default: "current") |
| `category` | string | no | Filter to specific category |

**Response:**

```json
{
  "semantic_version": "1.2",
  "marketing_version": "Version 1",
  "models": [
    {
      "model": { /* model info */ },
      "scores": { /* scores */ },
      "category_scores": { /* category breakdown */ },
      "verdict_distribution": { /* verdicts */ }
    }
  ],
  "comparison": {
    "score_delta": {
      "overall": 5,      // Difference between highest and lowest
      "tier1": 8,
      "tier2": 3,
      "tier3": 12
    },
    "category_deltas": {
      "3.1": 6,
      "3.2": 10,
      // ...
    }
  }
}
```

---

## UI/UX Design

### Design Philosophy

The leaderboard prioritizes **visual data presentation** over tabular data. Charts and visualizations are the primary interface, with the table serving as a detailed reference. This approach makes performance differences immediately apparent and creates an engaging, modern user experience.

### Visualization Library

**Chart.js** (loaded from CDN) is used for all charting components:
- Lightweight and performant
- Responsive and accessible
- Extensive customization options
- Progressive enhancement (charts enhance, don't replace, data tables)

### Leaderboard Page Layout

```
┌─────────────────────────────────────────────────────────────┐
│  Great Commission Benchmark - Leaderboard                    │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  [Filters Panel - Collapsible]                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Version: [Version 1 (1.2) ▼]  Category: [All ▼]  Tier: [All ▼] │   │
│  │ Provider: [All ▼]  Trust: [All ▼]                  │   │
│  │ [Clear Filters]                                     │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  TOP PERFORMERS - Horizontal Bar Chart                │   │
│  │  [Top 10 models with overall scores as bars]        │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  TIER BREAKDOWN - Grouped Bar Chart                  │   │
│  │  [Tier 1, 2, 3 scores for top models side-by-side]   │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  CATEGORY PERFORMANCE - Heatmap                      │   │
│  │  [Color-coded grid: rows=categories, cols=top models]│   │
│  └─────────────────────────────────────────────────────┘   │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  VERDICT DISTRIBUTION - Stacked Bar Chart            │   │
│  │  [ACCEPTED/COMPROMISED/REFUSED breakdown per model] │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  DETAILED RANKING TABLE (Collapsible/Secondary)     │   │
│  │  Rank │ Model          │ Overall │ Tier 1 │ Tier 2 │   │
│  │  [Full table view - click to expand]                 │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                               │
│  [View Full Table] [Load More] [Export CSV]                  │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### Key UI Components

#### 1. Filter Panel

- **Collapsible section** at top of page
- **Quick filters:** Version dropdown, Category dropdown, Tier selector
- **Advanced filters:** Provider, Trust tier, Date range
- **Filter chips:** Show active filters with remove buttons
- **Clear all:** Reset to default view
- **Live updates:** Charts refresh automatically when filters change

#### 2. Top Performers Bar Chart (Primary Visualization)

**Horizontal bar chart showing top 10-15 models:**
- **X-axis:** Overall GCB score (0-100)
- **Y-axis:** Model names (ranked top to bottom)
- **Bar colors:** Gradient from green (high) to yellow (medium) to red (low)
- **Annotations:** Rank number on each bar, score value at end of bar
- **Interactivity:**
  - Hover: Show detailed tooltip (all tier scores, trust tier, date)
  - Click bar: Navigate to model detail page
  - Click legend: Toggle model visibility
- **Responsive:** Adjusts number of models shown based on screen size

#### 3. Tier Breakdown Chart

**Grouped bar chart comparing Tier 1, 2, 3 scores:**
- **X-axis:** Models (top 10)
- **Y-axis:** Score (0-100)
- **Grouped bars:** Three bars per model (Tier 1, Tier 2, Tier 3)
- **Color coding:**
  - Tier 1: Blue (#3b82f6)
  - Tier 2: Purple (#8b5cf6)
  - Tier 3: Pink (#ec4899)
- **Interactivity:**
  - Hover: Show exact scores
  - Click: Filter leaderboard to that tier
  - Toggle tiers: Show/hide specific tiers

#### 4. Category Performance Heatmap

**Visual heatmap grid:**
- **Rows:** Categories (3.1, 3.2, 3.3, etc.)
- **Columns:** Top 10-15 models
- **Color intensity:** Score value (green=high, yellow=medium, red=low)
- **Cell tooltip:** Category name, model name, exact score
- **Interactivity:**
  - Click row: Filter to that category
  - Click column: Navigate to model detail
  - Hover: Highlight row/column for easier reading
- **Sorting:** Allow sorting by category performance or model performance

#### 5. Verdict Distribution Chart

**Stacked bar chart showing response quality:**
- **X-axis:** Models (top 10)
- **Y-axis:** Percentage or count
- **Stacked segments:**
  - ACCEPTED (green, bottom)
  - COMPROMISED (yellow, middle)
  - REFUSED (red, top)
  - ERROR (gray, if any)
- **Interactivity:**
  - Hover: Show exact counts and percentages
  - Click segment: Filter to see only that verdict type
  - Toggle: Switch between percentage and absolute counts

#### 6. Score Distribution Histogram (Optional)

**Shows overall score distribution across all models:**
- **X-axis:** Score ranges (0-20, 21-40, 41-60, 61-80, 81-100)
- **Y-axis:** Number of models
- **Purpose:** Helps users understand the competitive landscape
- **Interactivity:** Click bin to filter models in that score range

#### 7. Ranking Table (Secondary/Detailed View)

**Collapsible detailed table for users who prefer tabular data:**

**Columns:**
- **Rank** — Numeric position (1, 2, 3...)
- **Model** — Name and provider (with logo if available)
- **Overall Score** — Primary metric (large, bold) with mini bar chart
- **Tier 1** — Task capability score with progress bar
- **Tier 2** — Doctrinal fidelity score with progress bar
- **Tier 3** — Worldview confession score with progress bar
- **Verdicts** — Mini pie chart showing distribution
- **Actions** — "View Details" and "Compare" buttons

**Row Interactions:**
- **Hover:** Highlight row, show quick stats tooltip
- **Click row:** Navigate to model detail page
- **Click "View":** Navigate to model detail page
- **Click "Compare":** Add to comparison selection

**Visual Indicators:**
- **Trust tier badge:** Color-coded (green=validated, yellow=reviewed, gray=automated)
- **Score bars:** Visual progress bars for each tier score (inline)
- **Trend indicators:** Up/down arrows if historical data available
- **Mini charts:** Small sparkline charts for score trends

**Table Features:**
- **Collapsible by default:** Can be expanded to show full table
- **Sortable columns:** Click headers to sort
- **Searchable:** Filter models by name
- **Exportable:** Download as CSV

#### 8. Comparison Tool

- **Selection mode:** Checkboxes on chart elements and table rows
- **Visual selection:** Selected models highlighted across all charts
- **Comparison panel:** Fixed bottom bar showing selected models with quick stats
- **Compare button:** Opens comparison view (see feature-model-comparison.md)
- **Max selection:** Limit to 5 models for comparison
- **Quick compare:** "Compare top 3" button for instant comparison

#### 9. View Toggle

**Allow users to switch between visualization modes:**
- **Visual-first (default):** Charts prominent, table collapsed
- **Table-first:** Table expanded, charts smaller
- **Side-by-side:** Charts on left, table on right (desktop only)
- **Mobile:** Stacked view optimized for small screens

#### 10. Pagination & Loading

- **Initial load:** Top 15 models in charts, 50 in table
- **Load more:** "Show more models" button expands charts and table
- **Infinite scroll:** Optional infinite scroll for table
- **Total count:** Display "Showing top X of Y models"
- **Loading states:** Skeleton screens for charts during data fetch

---

## Filtering Logic

### Category Filtering

When a category is selected:
- **Score calculation:** Only questions from that category are included
- **Overall score:** Recalculated based on filtered questions
- **Tier scores:** Recalculated proportionally
- **Leaderboard:** Reranked based on filtered scores

**Example:** Filtering to "3.2 Evangelistic Material Creation" shows which models excel specifically at creating evangelistic content.

### Tier Filtering

When a tier is selected:
- **Score calculation:** Only questions from that tier are included
- **Overall score:** Recalculated (but note: tier weighting doesn't apply in filtered view)
- **Leaderboard:** Reranked based on tier-specific performance

### Version Filtering

- **Current version:** Shows only results from the active benchmark version
- **Historical versions:** Shows results from past versions (Version 1, Version 2, etc.) with semantic version details (1.0, 1.1, 1.2, 2.0, etc.)
- **Version comparison:** Users can switch between versions to see how rankings changed

### Trust Tier Filtering

- **All:** Include all results (default)
- **Validated only:** Show only results that have passed human moderation
- **Reviewed only:** Show results that have been spot-checked
- **Automated only:** Show unmoderated results

---

## Performance Considerations

### Caching Strategy

- **Leaderboard cache:** Cache full leaderboard for 5 minutes
- **Filtered results:** Cache common filter combinations (by category, by tier)
- **Invalidation:** Clear cache when new test results are published

### Database Optimization

- **Materialized view:** Pre-compute leaderboard rankings
- **Indexes:** Ensure indexes on `test_runs.status`, `test_runs.completed_at`, `results.verdict`
- **Query optimization:** Use window functions for ranking calculations

### Frontend Optimization

- **Virtual scrolling:** For large result sets (100+ models) in table view
- **Lazy loading:** Load model details on demand, lazy render charts below fold
- **Progressive enhancement:** Show cached data immediately, refresh in background
- **Chart.js optimization:** Limit datasets, use canvas rendering, debounce updates
- **Image optimization:** Lazy load provider logos and model images
- **Code splitting:** Load Chart.js and chart components asynchronously

---

## Accessibility

### WCAG Level A Compliance

- **Keyboard navigation:** Full keyboard support for all interactions
- **Screen reader support:** ARIA labels for all interactive elements
- **Color contrast:** Minimum 4.5:1 contrast ratio for text
- **Focus indicators:** Clear focus states for all interactive elements
- **Skip links:** Skip to main content, skip to filters

### Screen Reader Announcements

- "Leaderboard loaded, showing 50 models"
- "Filter applied: Category 3.2"
- "Model Claude 3.5 Sonnet, rank 1, overall score 87"

---

## Edge Cases

### No Results

- Display: "No models found matching your filters. Try adjusting your search criteria."
- Action: Provide "Clear all filters" button

### Single Model

- Display: Still show ranking table format (rank 1)
- Message: "Only one model matches your filters"

### Tied Scores

- Apply tie-breaking logic (see Ranking Logic section)
- Display same rank number for tied models
- Show tie indicator in UI

### Missing Data

- **Incomplete test runs:** Exclude from leaderboard (status must be "completed")
- **Missing category scores:** Show "N/A" or exclude from category-filtered views
- **Historical gaps:** Show message if version has no results

---

## Chart.js Implementation Details

### Library Setup

**CDN Integration:**
```html
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
```

**Alternative (npm):**
```bash
npm install chart.js
```

### Chart Configuration

**Common Configuration:**
- **Responsive:** All charts resize with container
- **Maintain aspect ratio:** Preserve visual proportions
- **Animation:** Smooth transitions on data updates
- **Accessibility:** ARIA labels and screen reader support
- **Theme:** Consistent color palette across all charts

**Color Palette:**
- **High scores:** Green gradient (#16a34a to #22c55e)
- **Medium scores:** Yellow/Orange (#d97706 to #f59e0b)
- **Low scores:** Red gradient (#dc2626 to #ef4444)
- **Tier 1:** Blue (#3b82f6)
- **Tier 2:** Purple (#8b5cf6)
- **Tier 3:** Pink (#ec4899)
- **Verdicts:** ACCEPTED (green), COMPROMISED (yellow), REFUSED (red), ERROR (gray)

### Performance Optimization

- **Data limits:** Charts show top 15 models by default (configurable)
- **Lazy rendering:** Charts render only when visible (Intersection Observer)
- **Debounced updates:** Filter changes debounced to prevent excessive re-renders
- **Canvas optimization:** Use hardware acceleration where available
- **Progressive loading:** Show skeleton/loading state, then render charts

### Accessibility Features

- **Keyboard navigation:** Tab through chart elements
- **Screen reader support:** Descriptive ARIA labels for all charts
- **High contrast mode:** Alternative color schemes for accessibility
- **Text alternatives:** Data tables available for all chart data
- **Focus indicators:** Clear focus states for interactive elements

### Chart Responsiveness

- **Mobile:** Stack charts vertically, reduce number of models shown
- **Tablet:** 2-column layout for smaller charts
- **Desktop:** Full multi-chart layout with side-by-side views
- **Breakpoints:** 
  - Mobile: < 768px
  - Tablet: 768px - 1024px
  - Desktop: > 1024px

## Future Enhancements

### Phase 2 Features

- **Trend visualization:** Line charts showing model performance over time (versions)
- **Interactive filtering:** Click chart elements to filter other charts
- **Export functionality:** Download charts as PNG/SVG, leaderboard as CSV/PDF
- **Share links:** Generate shareable URLs for filtered views with chart state
- **Model alerts:** Notify users when a model's rank changes
- **Custom chart views:** User-selectable chart types and layouts
- **3D visualizations:** Optional 3D bar charts for multi-dimensional comparison

### Phase 3 Features

- **Predictive rankings:** ML-based predictions of future performance with trend lines
- **Custom scoring:** Allow users to weight tiers differently (dynamic chart updates)
- **Community rankings:** Separate leaderboard for community-submitted results
- **Real-time updates:** WebSocket integration for live leaderboard updates
- **Advanced analytics:** Statistical overlays (confidence intervals, error bars)

---

## Testing Requirements

### Unit Tests

- Ranking algorithm correctness
- Filter logic validation
- Score calculation accuracy
- Tie-breaking logic

### Integration Tests

- API endpoint responses
- Database query performance
- Cache invalidation
- Pagination behavior

### E2E Tests

- Filter application and removal
- Leaderboard navigation
- Comparison tool selection
- Model detail page navigation

---

## Related Features

- **Model Detail Pages** — Deep dive into individual model performance
- **Model Comparison** — Side-by-side comparison view (see feature-model-comparison.md)
- **Category Deep-Dives** — Category-specific analysis pages
- **User Dashboard** — Personal test history (see feature-user-dashboard.md)

---

## Open Questions

1. **Should we show community-submitted results separately or merged with platform results?**
   - Recommendation: Separate "Community Leaderboard" tab

2. **How should we handle models with multiple test runs from different users?**
   - Recommendation: Show best result (highest score) as primary, with "View all runs" link

3. **Should leaderboard be real-time or updated on a schedule?**
   - Recommendation: Real-time with 5-minute cache for performance

4. **Should we display confidence intervals or error bars for scores?**
   - Recommendation: Phase 2 feature, show only for validated results initially

---

*Last Updated: December 16, 2025*
