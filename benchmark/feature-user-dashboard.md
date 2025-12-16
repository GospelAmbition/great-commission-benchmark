# User Dashboard Feature Specification

## Purpose

The user dashboard provides a personalized view of a user's activity on the Great Commission Benchmark platform. It serves as the central hub where users can track their test runs, view results, manage submissions, and access account settings.

---

## Overview

The user dashboard enables users to:

- **View test history** — See all test runs they've initiated or submitted
- **Track test status** — Monitor pending, running, and completed tests
- **Access results** — Review detailed results from completed tests
- **Manage submissions** — View and manage community submissions (CLI results)
- **Configure preferences** — Manage notification settings and account details
- **View activity** — See recent activity and contributions to the platform

---

## User Stories

### Primary Users

1. **Volunteers** — "I want to see the status of the test I just submitted and when it will be published"
2. **Organizations** — "I need to track all the models our organization has tested"
3. **Researchers** — "I want to review my test history and compare results over time"
4. **Community Contributors** — "I need to see the status of my CLI submission and any moderator feedback"

### Key Scenarios

- **Scenario 1:** A volunteer submits a test run and checks the dashboard to see it's "Running" with 45% progress
- **Scenario 2:** An organization views their dashboard to see all 12 models they've tested, sorted by score
- **Scenario 3:** A user receives a notification that their test completed and navigates to the dashboard to view results
- **Scenario 4:** A community contributor checks their CLI submission status and sees it's been approved and published

---

## Architecture

### Component Structure

```
┌─────────────────────────────────────────────────────────┐
│            User Dashboard Page (Next.js)                 │
├─────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ Summary      │  │ Test History │  │ Submissions  │  │
│  │ Cards        │  │ Table        │  │ Management    │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ Quick Actions│  │ Preferences  │  │ Activity     │  │
│  │              │  │              │  │ Feed         │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│              FastAPI Backend (User API)                  │
│  ┌──────────────────────────────────────────────────┐  │
│  │ GET  /api/user/profile                          │  │
│  │ GET  /api/user/tests                            │  │
│  │ GET  /api/user/tests/:id                        │  │
│  │ GET  /api/user/submissions                      │  │
│  │ GET  /api/user/notifications                    │  │
│  │ PUT  /api/user/notifications                    │  │
│  │ GET  /api/user/activity                         │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
                    PostgreSQL
        (users, test_runs, community_submissions)
```

---

## Data Model

### Dashboard Summary

```typescript
interface DashboardSummary {
  user: {
    id: string;
    name: string;
    email: string;
    role: 'user' | 'moderator' | 'admin';
    created_at: string;
  };
  stats: {
    total_tests: number;
    completed_tests: number;
    pending_tests: number;
    running_tests: number;
    total_submissions: number;
    approved_submissions: number;
    total_contribution: number;        // Estimated $ value contributed
  };
  recent_activity: ActivityItem[];
}
```

### Test Run Summary

```typescript
interface TestRunSummary {
  id: string;
  model: {
    id: string;
    name: string;
    provider: string;
  };
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';
  payment_status: 'pending' | 'paid' | 'refunded';
  scores: {
    overall: number | null;
    tier1: number | null;
    tier2: number | null;
    tier3: number | null;
  };
  progress: {
    completed: number;
    total: number;
    percentage: number;
  };
  question_set_version: string;
  created_at: string;
  started_at: string | null;
  completed_at: string | null;
  trust_tier: 'automated' | 'reviewed' | 'validated';
  leaderboard_rank: number | null;     // Current rank on leaderboard
}
```

### Community Submission Summary

```typescript
interface SubmissionSummary {
  id: string;
  model_name: string;
  model_url: string | null;
  organization: string | null;
  cli_version: string;
  question_set_version: string;
  status: 'pending' | 'reviewing' | 'approved' | 'rejected';
  scores: {
    overall: number;
    tier1: number;
    tier2: number;
    tier3: number;
  };
  submitted_at: string;
  reviewed_at: string | null;
  reviewer_notes: string | null;
  leaderboard_rank: number | null;
}
```

### Activity Item

```typescript
interface ActivityItem {
  id: string;
  type: 'test_started' | 'test_completed' | 'submission_approved' | 
        'submission_rejected' | 'moderation_review' | 'payment_processed';
  title: string;
  description: string;
  timestamp: string;
  link: string | null;                 // Link to related resource
  metadata: Record<string, any>;
}
```

---

## API Endpoints

### GET /api/user/profile

Get current user's profile information.

**Authentication:** Required (Auth0 JWT)

**Response:**

```json
{
  "user": {
    "id": "uuid",
    "name": "John Doe",
    "email": "john@example.com",
    "role": "user",
    "created_at": "2025-11-01T10:00:00Z",
    "organization": "Mission Agency X"
  }
}
```

### GET /api/user/tests

Get user's test run history with filtering and pagination.

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `status` | string | - | Filter by status ("pending", "running", "completed", "failed") |
| `model_id` | string | - | Filter by model ID |
| `version` | string | - | Filter by question set version |
| `limit` | integer | 20 | Number of results per page |
| `offset` | integer | 0 | Pagination offset |
| `sort` | string | `created_at` | Sort field ("created_at", "completed_at", "score") |
| `order` | string | `desc` | Sort order ("asc", "desc") |

**Response:**

```json
{
  "tests": [
    {
      "id": "uuid",
      "model": {
        "id": "uuid",
        "name": "Claude 3.5 Sonnet",
        "provider": "Anthropic"
      },
      "status": "completed",
      "payment_status": "paid",
      "scores": {
        "overall": 87,
        "tier1": 92,
        "tier2": 78,
        "tier3": 65
      },
      "progress": {
        "completed": 265,
        "total": 265,
        "percentage": 100
      },
      "question_set_version": "V1",
      "created_at": "2025-12-10T14:30:00Z",
      "started_at": "2025-12-10T14:31:00Z",
      "completed_at": "2025-12-10T15:45:00Z",
      "trust_tier": "validated",
      "leaderboard_rank": 1
    }
  ],
  "pagination": {
    "limit": 20,
    "offset": 0,
    "total": 12,
    "has_more": false
  }
}
```

### GET /api/user/tests/:id

Get detailed information about a specific test run.

**Path Parameters:**
- `id`: Test run UUID

**Response:**

```json
{
  "test": {
    "id": "uuid",
    "model": { /* full model details */ },
    "status": "completed",
    "payment": {
      "status": "paid",
      "amount": 20.00,
      "currency": "USD",
      "transaction_id": "stripe_xxx"
    },
    "scores": { /* full scores */ },
    "category_scores": { /* category breakdown */ },
    "verdict_distribution": { /* verdict counts */ },
    "progress": { /* progress info */ },
    "question_set": {
      "version": "V1",
      "total_questions": 265
    },
    "methodology_version": "V1.0",
    "timestamps": {
      "created": "2025-12-10T14:30:00Z",
      "started": "2025-12-10T14:31:00Z",
      "completed": "2025-12-10T15:45:00Z"
    },
    "trust_tier": "validated",
    "validation_metrics": {
      "inter_rater_reliability": 0.92,
      "reproducibility_score": 0.88
    },
    "leaderboard_rank": 1,
    "actions": {
      "can_retest": true,
      "can_download": true,
      "can_share": true,
      "can_request_refund": false
    }
  }
}
```

### GET /api/user/submissions

Get user's community submissions (CLI-generated results).

**Query Parameters:** Same as `/api/user/tests`

**Response:**

```json
{
  "submissions": [
    {
      "id": "uuid",
      "model_name": "Llama 3.1 70B",
      "model_url": "https://huggingface.co/meta-llama/Llama-3.1-70B",
      "organization": "Research Lab X",
      "cli_version": "1.2.0",
      "question_set_version": "V1",
      "status": "approved",
      "scores": {
        "overall": 82,
        "tier1": 85,
        "tier2": 75,
        "tier3": 70
      },
      "submitted_at": "2025-12-05T09:00:00Z",
      "reviewed_at": "2025-12-06T14:20:00Z",
      "reviewer_notes": "Approved after verification",
      "leaderboard_rank": 5
    }
  ],
  "pagination": { /* pagination info */ }
}
```

### GET /api/user/activity

Get user's recent activity feed.

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `limit` | integer | 20 | Number of activities to return |
| `types` | string[] | - | Filter by activity types |

**Response:**

```json
{
  "activities": [
    {
      "id": "uuid",
      "type": "test_completed",
      "title": "Test completed: Claude 3.5 Sonnet",
      "description": "Your test run finished with an overall score of 87",
      "timestamp": "2025-12-10T15:45:00Z",
      "link": "/user/tests/uuid",
      "metadata": {
        "test_id": "uuid",
        "score": 87
      }
    },
    {
      "id": "uuid",
      "type": "submission_approved",
      "title": "Submission approved: Llama 3.1 70B",
      "description": "Your CLI submission has been approved and published",
      "timestamp": "2025-12-06T14:20:00Z",
      "link": "/user/submissions/uuid",
      "metadata": {
        "submission_id": "uuid"
      }
    }
  ]
}
```

### PUT /api/user/notifications

Update user's notification preferences.

**Request Body:**

```json
{
  "test_completion": true,
  "publication": true,
  "moderation_updates": true,
  "newsletter": false
}
```

**Response:**

```json
{
  "preferences": {
    "test_completion": true,
    "publication": true,
    "moderation_updates": true,
    "newsletter": false,
    "updated_at": "2025-12-16T10:00:00Z"
  }
}
```

---

## UI/UX Design

### Dashboard Page Layout

```
┌─────────────────────────────────────────────────────────────┐
│  My Dashboard                                    [Settings]  │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │ Total    │  │ Completed│  │ Running   │  │ Pending   │  │
│  │ Tests    │  │ Tests    │  │ Tests     │  │ Tests     │  │
│  │    12    │  │    10    │  │     1     │  │     1     │  │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘  │
│                                                               │
│  My Test Runs                                    [New Test]  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Model          │ Status    │ Score │ Date    │ Actions│   │
│  ├─────────────────────────────────────────────────────┤   │
│  │ Claude 3.5     │ Completed │  87   │ Dec 10  │ [View] │   │
│  │ Sonnet         │ ✓         │       │         │        │   │
│  ├─────────────────────────────────────────────────────┤   │
│  │ GPT-4 Turbo    │ Running   │  -    │ Dec 15  │ [View] │   │
│  │                │ ⏳ 45%     │       │         │        │   │
│  ├─────────────────────────────────────────────────────┤   │
│  │ Llama 3.1 70B  │ Pending   │  -    │ Dec 16  │ [View] │   │
│  │                │ ⏸ Payment │       │         │        │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                               │
│  Community Submissions                          [New Submission]│
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Model          │ Status    │ Score │ Date    │ Actions│   │
│  ├─────────────────────────────────────────────────────┤   │
│  │ Mistral 7B     │ Approved  │  75   │ Dec 5   │ [View] │   │
│  │                │ ✓         │       │         │        │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                               │
│  Recent Activity                                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ • Test completed: Claude 3.5 Sonnet (Score: 87)    │   │
│  │   2 hours ago                                        │   │
│  │ • Submission approved: Llama 3.1 70B                │   │
│  │   5 days ago                                         │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### Key UI Components

#### 1. Summary Cards

**Four stat cards at top:**
- **Total Tests** — Count of all test runs (any status)
- **Completed Tests** — Count of successfully completed tests
- **Running Tests** — Count of currently executing tests
- **Pending Tests** — Count of tests awaiting payment or start

**Visual Design:**
- Large number, small label
- Color-coded (green=completed, blue=running, yellow=pending)
- Clickable → filters test history table

#### 2. Test History Table

**Columns:**
- **Model** — Name and provider
- **Status** — Visual status indicator with badge
- **Score** — Overall GCB score (or "-" if not completed)
- **Date** — Created date (or completed date if available)
- **Actions** — "View", "Retest", "Download", "Share"

**Status Indicators:**
- **Completed** — Green checkmark, shows score
- **Running** — Blue spinner with progress percentage
- **Pending** — Yellow clock icon, shows "Payment" or "Queued"
- **Failed** — Red X, shows error message on hover
- **Cancelled** — Gray icon

**Row Interactions:**
- **Click row:** Navigate to test detail page
- **Hover:** Highlight row, show quick actions
- **Status badge:** Click to filter by that status

#### 3. Community Submissions Table

Similar structure to test history table, but shows:
- **Status:** pending, reviewing, approved, rejected
- **Reviewer notes:** Display if available
- **Leaderboard rank:** Show if published

#### 4. Activity Feed

**Timeline-style feed showing:**
- Test started/completed events
- Submission status changes
- Moderation updates
- Payment confirmations

**Each item:**
- Icon representing activity type
- Title and description
- Timestamp (relative: "2 hours ago")
- Link to related resource

#### 5. Quick Actions Panel

**Sidebar or top bar with:**
- **New Test** — Start a new benchmark test
- **New Submission** — Upload CLI results
- **Compare Tests** — Select multiple tests to compare
- **Export History** — Download test history as CSV

---

## Test Detail View

When a user clicks "View" on a test, they see a detailed page with:

### Overview Section

- **Model information** — Full model details
- **Test metadata** — Version, methodology, timestamps
- **Payment information** — Status, amount, transaction ID
- **Trust tier** — Badge and explanation

### Results Section

- **Score breakdown** — Overall, Tier 1, Tier 2, Tier 3
- **Category scores** — Performance by category
- **Verdict distribution** — Pie chart or bar chart
- **Leaderboard position** — Current rank and link

### Actions Section

- **View Full Results** — Link to detailed results page
- **Retest** — Start a new test with same model (see feature-retesting.md)
- **Download Report** — Generate and download PDF/HTML report
- **Share Results** — Generate shareable link
- **Request Refund** — If eligible (within refund window)

### Progress Timeline

For running tests, show:
- **Progress bar** — Visual progress indicator
- **Current question** — "Processing question 120 of 265"
- **Estimated time remaining** — Based on current rate
- **Logs** — Recent activity log (optional, for debugging)

---

## Filtering & Sorting

### Test History Filters

- **Status** — All, Completed, Running, Pending, Failed
- **Model** — Filter by specific model
- **Version** — Filter by question set version
- **Date Range** — Start and end date picker
- **Score Range** — Min and max score sliders

### Sorting Options

- **Date** — Newest first (default) or oldest first
- **Score** — Highest to lowest or lowest to highest
- **Model Name** — Alphabetical
- **Status** — Group by status

---

## Notifications Integration

The dashboard integrates with the notification system (see feature-user-notifications.md):

- **In-app notifications** — Badge count on dashboard icon
- **Activity feed** — Real-time updates in activity section
- **Email notifications** — Configurable via preferences

---

## Privacy & Security

### Data Access

- Users can **only** see their own test runs and submissions
- No access to other users' data
- Moderators see additional moderation queue (see feature-moderator-dashboard.md)

### Sensitive Information

- **Payment details** — Show only last 4 digits of card, transaction ID
- **Email addresses** — Only visible to account owner
- **Test responses** — Full responses only visible to test owner (not in leaderboard)

---

## Performance Considerations

### Data Loading

- **Initial load:** Summary stats + first 20 test runs
- **Lazy loading:** Load more tests on scroll or "Load More" click
- **Caching:** Cache user profile and preferences for 5 minutes

### Real-time Updates

- **WebSocket connection:** For running tests, push progress updates
- **Polling fallback:** If WebSocket unavailable, poll every 10 seconds
- **Status badges:** Update without full page refresh

---

## Accessibility

### WCAG Level A Compliance

- **Keyboard navigation:** Full keyboard support
- **Screen reader support:** ARIA labels and live regions for status updates
- **Focus management:** Clear focus indicators
- **Status announcements:** Screen reader announces status changes

### Screen Reader Announcements

- "Dashboard loaded, 12 total tests, 10 completed"
- "Test status updated: Claude 3.5 Sonnet is now completed"
- "New activity: Submission approved"

---

## Edge Cases

### No Tests

- Display: "You haven't run any tests yet. [Start Your First Test]"
- Show onboarding tips or quick start guide

### Failed Tests

- Show error message and reason
- Provide "Retry" or "Contact Support" options
- Allow download of partial results if available

### Payment Issues

- Show payment status clearly
- Provide "Complete Payment" button if pending
- Show refund status if applicable

### Large Test History

- Implement pagination or infinite scroll
- Provide export functionality for bulk download
- Allow filtering to reduce result set

---

## Future Enhancements

### Phase 2 Features

- **Test comparison** — Compare multiple tests side-by-side
- **Custom reports** — Generate custom analysis reports
- **Test scheduling** — Schedule recurring tests
- **Team/organization views** — Aggregate stats for organizations

### Phase 3 Features

- **Performance trends** — Charts showing score trends over time
- **Category insights** — Detailed category performance analysis
- **Export templates** — Customizable export formats
- **API access** — Programmatic access to user's test data

---

## Testing Requirements

### Unit Tests

- Dashboard summary calculation
- Filter and sort logic
- Status badge rendering
- Activity feed formatting

### Integration Tests

- API endpoint responses
- Authentication and authorization
- Data filtering and pagination
- Real-time update delivery

### E2E Tests

- Dashboard navigation
- Test detail view
- Filter application
- Notification interactions

---

## Related Features

- **User Notifications** — Notification system integration (see feature-user-notifications.md)
- **Model Comparison** — Compare tests side-by-side (see feature-model-comparison.md)
- **Retesting** — Retest flow for models (see feature-retesting.md)
- **Leaderboard** — Public leaderboard view (see feature-leaderboard.md)

---

## Open Questions

1. **Should users be able to delete their test runs?**
   - Recommendation: Soft delete (hide from dashboard, keep in database for audit)

2. **Should test results be shareable publicly?**
   - Recommendation: Yes, with opt-in sharing link generation

3. **How should we handle organization/team accounts?**
   - Recommendation: Phase 2 feature, allow multiple users under organization

4. **Should users see estimated costs before starting tests?**
   - Recommendation: Yes, show cost estimate in "New Test" flow

---

*Last Updated: December 16, 2025*
