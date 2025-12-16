# Model Comparison Feature Specification

## Purpose

The model comparison feature enables users to view side-by-side comparisons of multiple LLM models' performance on the Great Commission Benchmark. It helps users make informed decisions by highlighting differences in scores, category performance, and verdict distributions.

---

## Overview

The model comparison feature provides:

- **Side-by-side comparison** — View 2-5 models simultaneously
- **Score breakdowns** — Compare overall, tier, and category scores
- **Verdict analysis** — Compare acceptance/refusal rates
- **Visual charts** — Bar charts, radar charts, and heatmaps
- **Category insights** — Deep dive into specific category performance
- **Export functionality** — Download comparison reports

---

## User Stories

### Primary Users

1. **Christian Organizations** — "I need to compare 3 models to decide which one to use for our ministry work"
2. **Researchers** — "I want to analyze performance differences between open-source and commercial models"
3. **Volunteers** — "I want to see how the model I tested compares to the top performers"
4. **Model Developers** — "I need to understand where my model falls short compared to competitors"

### Key Scenarios

- **Scenario 1:** An organization compares Claude, GPT-4, and Gemini to choose their primary LLM
- **Scenario 2:** A researcher compares models across different categories to identify strengths/weaknesses
- **Scenario 3:** A user compares their test results with leaderboard results for the same model
- **Scenario 4:** A developer compares their model's performance before and after improvements

---

## Architecture

### Component Structure

```
┌─────────────────────────────────────────────────────────┐
│        Model Comparison Page (Next.js)                    │
├─────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ Model        │  │ Score        │  │ Category     │  │
│  │ Selector     │  │ Comparison   │  │ Breakdown    │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ Verdict      │  │ Visual       │  │ Export       │  │
│  │ Analysis     │  │ Charts       │  │ Tools        │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│          FastAPI Backend (Comparison API)                 │
│  ┌──────────────────────────────────────────────────┐  │
│  │ GET  /api/compare                                 │  │
│  │ GET  /api/compare/export                         │  │
│  │ POST /api/compare/custom                         │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
                    PostgreSQL
              (test_runs, results, models)
```

---

## Data Model

### Comparison Request

```typescript
interface ComparisonRequest {
  models: string[];                  // Array of model IDs or test run IDs
  version?: string;                  // Benchmark version (default: "current")
  category?: string;                 // Optional category filter
  tier?: number;                     // Optional tier filter (1, 2, or 3)
  include_user_tests?: boolean;     // Include user's own test runs
}
```

### Comparison Result

```typescript
interface ComparisonResult {
  version: string;
  filters: {
    category: string | null;
    tier: number | null;
  };
  models: ComparedModel[];
  summary: {
    best_overall: string;            // Model ID with highest overall score
    best_tier1: string;              // Model ID with highest Tier 1 score
    best_tier2: string;              // Model ID with highest Tier 2 score
    best_tier3: string;              // Model ID with highest Tier 3 score
    score_range: {
      min: number;
      max: number;
      delta: number;
    };
  };
  category_insights: CategoryInsight[];
}

interface ComparedModel {
  model: {
    id: string;
    name: string;
    provider: string;
    model_id: string;
  };
  test_run: {
    id: string;
    trust_tier: 'automated' | 'reviewed' | 'validated';
    completed_at: string;
    question_set_version: string;
  };
  scores: {
    overall: number;
    tier1: number;
    tier2: number;
    tier3: number;
  };
  category_scores: {
    [category: string]: number;      // e.g., "3.1": 88, "3.2": 95
  };
  verdict_distribution: {
    ACCEPTED: number;
    COMPROMISED: number;
    REFUSED: number;
    ERROR: number;
  };
  verdict_percentages: {
    ACCEPTED: number;
    COMPROMISED: number;
    REFUSED: number;
    ERROR: number;
  };
  total_questions: number;
  metadata: {
    leaderboard_rank: number | null;
    submitted_by?: string;
  };
}

interface CategoryInsight {
  category: string;
  category_name: string;
  best_model: string;                // Model ID
  worst_model: string;               // Model ID
  score_delta: number;               // Difference between best and worst
  average_score: number;
}
```

---

## API Endpoints

### GET /api/compare

Compare multiple models side-by-side.

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `models` | string[] | yes | Array of model IDs or test run IDs (comma-separated) |
| `version` | string | no | Benchmark version (default: "current") |
| `category` | string | no | Filter to specific category |
| `tier` | integer | no | Filter to specific tier (1, 2, or 3) |
| `include_user_tests` | boolean | no | Include user's own test runs (default: false) |

**Response:**

```json
{
  "version": "V1",
  "filters": {
    "category": null,
    "tier": null
  },
  "models": [
    {
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
        "question_set_version": "V1"
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
      "verdict_percentages": {
        "ACCEPTED": 92.5,
        "COMPROMISED": 4.5,
        "REFUSED": 3.0,
        "ERROR": 0.0
      },
      "total_questions": 265,
      "metadata": {
        "leaderboard_rank": 1,
        "submitted_by": "Mission Agency X"
      }
    }
    // ... more models
  ],
  "summary": {
    "best_overall": "uuid",
    "best_tier1": "uuid",
    "best_tier2": "uuid",
    "best_tier3": "uuid",
    "score_range": {
      "min": 75,
      "max": 87,
      "delta": 12
    }
  },
  "category_insights": [
    {
      "category": "3.2",
      "category_name": "Evangelistic Material Creation",
      "best_model": "uuid",
      "worst_model": "uuid",
      "score_delta": 15,
      "average_score": 82
    }
  ]
}
```

### POST /api/compare/custom

Compare custom selection of models with advanced filtering.

**Request Body:**

```json
{
  "models": ["uuid1", "uuid2", "uuid3"],
  "version": "V1",
  "filters": {
    "categories": ["3.1", "3.2"],
    "tier": 1,
    "min_score": 80
  },
  "include_user_tests": true
}
```

**Response:** Same structure as GET /api/compare

### GET /api/compare/export

Export comparison as PDF, CSV, or JSON.

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `models` | string[] | yes | Model IDs to compare |
| `format` | string | yes | Export format ("pdf", "csv", "json") |
| `version` | string | no | Benchmark version |

**Response:**

- **PDF/CSV:** File download
- **JSON:** JSON response with comparison data

---

## UI/UX Design

### Comparison Page Layout

```
┌─────────────────────────────────────────────────────────────┐
│  Model Comparison                            [Export] [Share]│
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  Select Models                                                │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ [Model 1: Claude 3.5 Sonnet ▼] [Remove]            │   │
│  │ [Model 2: GPT-4 Turbo ▼] [Remove]                   │   │
│  │ [Model 3: Gemini Pro ▼] [Remove]                    │   │
│  │ [+ Add Model]                                        │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                               │
│  Filters: [Version: V1 ▼] [Category: All ▼] [Tier: All ▼]  │
│                                                               │
│  ─────────────────────────────────────────────────────────  │
│                                                               │
│  Overall Scores Comparison                                    │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Model          │ Overall │ Tier 1 │ Tier 2 │ Tier 3 │   │
│  ├─────────────────────────────────────────────────────┤   │
│  │ Claude 3.5     │   87    │   92   │   78   │   65   │   │
│  │ Sonnet         │  ████████        │        │        │   │
│  ├─────────────────────────────────────────────────────┤   │
│  │ GPT-4 Turbo    │   84    │   89   │   75   │   70   │   │
│  │                │  ███████        │        │        │   │
│  ├─────────────────────────────────────────────────────┤   │
│  │ Gemini Pro     │   79    │   82   │   72   │   68   │   │
│  │                │  ██████         │        │        │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                               │
│  Category Performance                                         │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Category          │ Claude │ GPT-4 │ Gemini │ Best   │   │
│  ├─────────────────────────────────────────────────────┤   │
│  │ 3.1 Missiological │   88   │  85   │   80   │ Claude │   │
│  │ 3.2 Evangelistic  │   95   │  90   │   85   │ Claude │   │
│  │ 3.3 Apologetic    │   90   │  88   │   82   │ Claude │   │
│  │ 3.4 Conversational │   85   │  87   │   78   │ GPT-4  │   │
│  │ 3.5 Intercessory  │   92   │  89   │   83   │ Claude │   │
│  │ 3.6 Scripture     │   88   │  86   │   81   │ Claude │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                               │
│  Verdict Distribution                                         │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ [Bar Chart: ACCEPTED/COMPROMISED/REFUSED by model]   │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                               │
│  Visual Comparison                                            │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ [Radar Chart: Multi-dimensional comparison]          │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### Key UI Components

#### 1. Model Selector

**Multi-select dropdown with:**
- Search functionality
- Filter by provider
- Show leaderboard rank
- Display trust tier badge
- Max 5 models selectable

**Model Selection Options:**
- **From Leaderboard** — Select from top models
- **From My Tests** — Select from user's test history
- **By Model ID** — Enter model ID directly
- **By Test Run ID** — Compare specific test runs

#### 2. Score Comparison Table

**Side-by-side table showing:**
- Model names (with provider logos)
- Overall scores (highlighted, largest)
- Tier 1, Tier 2, Tier 3 scores
- Visual progress bars for each score
- Best score highlighted in green
- Worst score highlighted in red (optional)

**Sorting:**
- Click column header to sort
- Default: Sort by overall score (descending)

#### 3. Category Breakdown Table

**Table showing:**
- Category names and codes
- Score for each model per category
- Best model per category highlighted
- Score delta (difference) column
- Average score across models

**Interactions:**
- Click category row → Navigate to category deep-dive
- Hover → Show tooltip with category description

#### 4. Verdict Distribution Chart

**Stacked bar chart or grouped bar chart:**
- X-axis: Models
- Y-axis: Percentage or count
- Stacked bars: ACCEPTED (green), COMPROMISED (yellow), REFUSED (red)
- Tooltip: Show exact counts on hover

**Chart Types:**
- **Stacked Bar Chart** — Shows composition
- **Grouped Bar Chart** — Easier to compare categories
- **Pie Charts** — Per-model breakdown (optional)

#### 5. Radar Chart

**Multi-dimensional comparison:**
- Axes: Overall, Tier 1, Tier 2, Tier 3, plus top categories
- One line per model
- Color-coded by model
- Legend showing model names

#### 6. Category Heatmap

**Visual heatmap:**
- Rows: Categories
- Columns: Models
- Color intensity: Score (green=high, red=low)
- Tooltip: Show exact score on hover

#### 7. Summary Panel

**Key insights:**
- Best overall model
- Best per tier
- Largest score gap
- Category where models differ most
- Trust tier summary

---

## Comparison Modes

### Mode 1: Leaderboard Comparison

**Compare top models from leaderboard:**
- Default: Top 3 models
- User can add/remove models
- Shows best results for each model

### Mode 2: Custom Selection

**User selects specific models:**
- From dropdown
- By model ID
- Mix of leaderboard and user's tests

### Mode 3: Test Run Comparison

**Compare specific test runs:**
- User's own test runs
- Different versions of same model
- Before/after improvements

### Mode 4: Category-Focused Comparison

**Compare models within specific category:**
- Filter to one category
- Shows category-specific scores
- Highlights category strengths/weaknesses

---

## Visualizations

### Bar Charts

**Score Comparison Bars:**
- Horizontal bars for each model
- Color-coded by score range
- Annotations for best/worst

**Verdict Distribution Bars:**
- Stacked or grouped bars
- Percentage or absolute counts
- Color-coded by verdict type

### Radar Charts

**Multi-Dimensional Comparison:**
- 6-8 axes (Overall, Tier 1-3, top categories)
- One polygon per model
- Overlay multiple models for comparison

### Heatmaps

**Category Performance Heatmap:**
- Rows: Categories
- Columns: Models
- Color gradient: Low (red) to High (green)
- Tooltips with exact scores

### Line Charts

**Score Trends (if historical data):**
- X-axis: Time or version
- Y-axis: Score
- One line per model
- Show improvement/regression

---

## Export Functionality

### PDF Export

**Comprehensive comparison report:**
- Cover page with model list
- Score comparison tables
- Category breakdown
- Charts and visualizations
- Summary insights
- Methodology notes

### CSV Export

**Structured data:**
- Model names and IDs
- All scores (overall, tiers, categories)
- Verdict distributions
- Metadata (dates, trust tiers)

### JSON Export

**Machine-readable format:**
- Full comparison data structure
- Includes all metadata
- Suitable for programmatic analysis

### Share Link

**Generate shareable URL:**
- Encodes model selection and filters
- Anyone with link can view comparison
- No authentication required
- Expires after 30 days (optional)

---

## Performance Considerations

### Data Loading

- **Lazy loading:** Load model data on demand
- **Caching:** Cache comparison results for 5 minutes
- **Pagination:** For large model lists, paginate selection

### Chart Rendering

- **Client-side rendering:** Use Chart.js or similar
- **Progressive enhancement:** Show table first, enhance with charts
- **Chart optimization:** Limit to 5 models for performance

### API Optimization

- **Batch queries:** Fetch all model data in single request
- **Field selection:** Only fetch needed fields
- **Compression:** Compress JSON responses

---

## Accessibility

### WCAG Level A Compliance

- **Keyboard navigation:** Full keyboard support
- **Screen reader support:** ARIA labels for charts
- **Color contrast:** Minimum 4.5:1 for all text
- **Alternative text:** Text alternatives for charts

### Screen Reader Support

- **Table summaries:** Describe comparison structure
- **Chart descriptions:** Text summaries of chart data
- **Data tables:** Accessible HTML tables for all data

---

## Edge Cases

### Insufficient Data

- **Missing scores:** Show "N/A" or exclude from comparison
- **Incomplete tests:** Only compare completed test runs
- **Different versions:** Warn if comparing different benchmark versions

### Model Selection Limits

- **Too many models:** Limit to 5 models maximum
- **Too few models:** Require at least 2 models
- **Invalid models:** Show error for invalid model IDs

### Filter Conflicts

- **No results:** Show "No models match your filters"
- **Category filter:** Only show models tested in that category
- **Version mismatch:** Warn if models from different versions

---

## Future Enhancements

### Phase 2 Features

- **Historical comparison:** Compare models across versions
- **Statistical significance:** Show confidence intervals
- **Custom scoring:** User-defined weightings for tiers
- **Comparison templates:** Save common comparisons

### Phase 3 Features

- **ML insights:** AI-generated insights and recommendations
- **Cost comparison:** Include cost per test in comparison
- **Performance trends:** Show improvement/regression over time
- **Category recommendations:** Suggest best model for specific use case

---

## Testing Requirements

### Unit Tests

- Comparison calculation logic
- Score aggregation
- Category insight generation
- Export format generation

### Integration Tests

- API endpoint responses
- Model selection validation
- Filter application
- Export functionality

### E2E Tests

- Complete comparison workflow
- Model selection
- Chart rendering
- Export download

---

## Related Features

- **Leaderboard** — Source of models for comparison (see feature-leaderboard.md)
- **User Dashboard** — Compare user's test runs (see feature-user-dashboard.md)
- **Model Detail Pages** — Deep dive into individual models

---

## Open Questions

1. **Should we allow comparing models from different benchmark versions?**
   - Recommendation: Allow but show clear warning

2. **What's the maximum number of models for comparison?**
   - Recommendation: 5 models maximum for readability

3. **Should comparison include cost information?**
   - Recommendation: Phase 2 feature, optional cost column

4. **How should we handle models with different trust tiers in comparison?**
   - Recommendation: Show trust tier badges, allow filtering by trust tier

---

*Last Updated: December 16, 2025*
