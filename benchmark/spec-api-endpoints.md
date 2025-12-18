# API Endpoints Specification

This document defines the API endpoints for the Great Commission Benchmark platform backend (FastAPI).

---

## Overview

The GCB Platform API is organized into the following domains:

| Domain | Base Path | Auth Required | Description |
|--------|-----------|---------------|-------------|
| **Public** | `/api/public` | No | Public leaderboard and model data |
| **User** | `/api/user` | Yes (User) | User dashboard, test history |
| **Tests** | `/api/tests` | Yes (User) | Test execution and management |
| **Submissions** | `/api/submissions` | Yes (User) | CLI result uploads |
| **Moderator** | `/api/moderator` | Yes (Moderator) | Moderation queue and reviews |
| **Admin** | `/api/admin` | Yes (Admin) | Administrative operations |
| **Versions** | `/api/versions` | Mixed | Benchmark version management |
| **Payments** | `/api/payments` | Yes (User) | Payment processing |
| **Webhooks** | `/api/webhooks` | Signature | External service callbacks |

---

## Authentication

### Auth0 JWT

All authenticated endpoints require a valid JWT token in the Authorization header:

```
Authorization: Bearer <jwt_token>
```

### Roles

| Role | Description |
|------|-------------|
| `user` | Standard registered user |
| `moderator` | Can access moderation queue |
| `admin` | Full administrative access |

---

## Common Response Formats

### Success Response

```json
{
  "success": true,
  "data": { ... }
}
```

### Error Response

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": { ... }
  }
}
```

### Pagination

```json
{
  "data": [ ... ],
  "pagination": {
    "limit": 20,
    "offset": 0,
    "total": 150,
    "has_more": true
  }
}
```

---

## 1. Public API

### GET /api/public/leaderboard

Get the public leaderboard with optional filtering.

**Authentication:** None

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `version` | string | `current` | Semantic version (e.g., "1.0", "2.0") or "current" |
| `marketing_version` | string | - | Marketing version (e.g., "Version 1", "Version 2") |
| `category` | string | - | Filter by category (e.g., "3.1", "3.2") |
| `tier` | integer | - | Filter by tier (1, 2, or 3) |
| `provider` | string | - | Filter by model provider (e.g., "OpenAI", "Anthropic") |
| `trust_tier` | string | - | Filter by trust tier ("automated", "reviewed", "validated") |
| `limit` | integer | 50 | Number of results (max 100) |
| `offset` | integer | 0 | Pagination offset |
| `sort` | string | `score` | Sort field: "score", "date", "tier1", "tier2", "tier3" |
| `order` | string | `desc` | Sort order: "asc", "desc" |

**Response:** `200 OK`

```json
{
  "semantic_version": "2.0",
  "marketing_version": "Version 2",
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
        "question_set_version": "2.0"
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
        "3.6": 88,
        "3.7": 86
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
        "methodology_version": "1.0"
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

---

### GET /api/public/leaderboard/:version

Get leaderboard for a specific benchmark version.

**Path Parameters:**
- `version`: Semantic version identifier (e.g., "1.0", "2.0")

**Query Parameters:** Same as `/api/public/leaderboard`

**Response:** Same as `/api/public/leaderboard`

---

### GET /api/public/leaderboard/category/:slug

Get leaderboard filtered to a specific category.

**Path Parameters:**
- `slug`: Category identifier (e.g., "3.1", "missiological-research")

**Query Parameters:** Same as `/api/public/leaderboard` (except `category` is ignored)

**Response:** Same structure, but scores reflect only the selected category.

---

### GET /api/public/leaderboard/compare

Compare multiple models side-by-side.

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `models` | string[] | Yes | Array of model IDs to compare (max 5) |
| `version` | string | No | Benchmark version (default: "current") |
| `category` | string | No | Filter to specific category |

**Response:** `200 OK`

```json
{
  "semantic_version": "2.0",
  "marketing_version": "Version 2",
  "models": [
    {
      "model": {
        "id": "uuid",
        "name": "Claude 3.5 Sonnet",
        "provider": "Anthropic"
      },
      "test_run_id": "uuid",
      "scores": {
        "overall": 87,
        "tier1": 92,
        "tier2": 78,
        "tier3": 65
      },
      "category_scores": {
        "3.1": 88,
        "3.2": 95
      },
      "verdict_distribution": {
        "ACCEPTED": 245,
        "COMPROMISED": 12,
        "REFUSED": 8
      }
    }
  ],
  "comparison": {
    "score_delta": {
      "overall": 5,
      "tier1": 8,
      "tier2": 3,
      "tier3": 12
    },
    "category_deltas": {
      "3.1": 6,
      "3.2": 10
    },
    "best_per_category": {
      "3.1": "model-uuid-1",
      "3.2": "model-uuid-2"
    }
  }
}
```

---

### GET /api/public/models

List all tested models.

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `provider` | string | - | Filter by provider |
| `search` | string | - | Search by model name |
| `limit` | integer | 50 | Number of results |
| `offset` | integer | 0 | Pagination offset |

**Response:** `200 OK`

```json
{
  "models": [
    {
      "id": "uuid",
      "name": "Claude 3.5 Sonnet",
      "provider": "Anthropic",
      "model_id": "anthropic/claude-3.5-sonnet",
      "description": "Anthropic's most capable model",
      "latest_score": 87,
      "test_count": 3,
      "first_tested": "2025-11-01T00:00:00Z",
      "last_tested": "2025-12-15T10:30:00Z"
    }
  ],
  "pagination": { ... }
}
```

---

### GET /api/public/models/:id

Get detailed model information.

**Path Parameters:**
- `id`: Model UUID

**Response:** `200 OK`

```json
{
  "model": {
    "id": "uuid",
    "name": "Claude 3.5 Sonnet",
    "provider": "Anthropic",
    "model_id": "anthropic/claude-3.5-sonnet",
    "description": "Anthropic's most capable model",
    "model_url": "https://www.anthropic.com/claude",
    "context_window": 200000,
    "released_date": "2024-10-22"
  },
  "best_result": {
    "test_run_id": "uuid",
    "scores": {
      "overall": 87,
      "tier1": 92,
      "tier2": 78,
      "tier3": 65
    },
    "trust_tier": "validated",
    "completed_at": "2025-12-15T10:30:00Z",
    "benchmark_version": "2.0"
  },
  "test_history": [
    {
      "test_run_id": "uuid",
      "overall_score": 87,
      "benchmark_version": "2.0",
      "completed_at": "2025-12-15T10:30:00Z",
      "trust_tier": "validated"
    }
  ],
  "category_breakdown": {
    "3.1": { "score": 88, "total": 35, "passed": 31 },
    "3.2": { "score": 95, "total": 35, "passed": 33 }
  },
  "leaderboard_rank": 1,
  "total_models_tested": 42
}
```

---

### GET /api/public/versions

List all benchmark versions.

**Response:** `200 OK`

```json
{
  "versions": [
    {
      "semantic_version": "2.0",
      "marketing_version": "Version 2",
      "status": "current",
      "release_date": "2025-12-01",
      "question_count": 300,
      "tier_distribution": {
        "tier1": 210,
        "tier2": 60,
        "tier3": 30
      },
      "scoring_weights": {
        "tier1": 0.70,
        "tier2": 0.20,
        "tier3": 0.10
      },
      "models_tested": 42,
      "changelog_url": "/docs/versions/2.0"
    },
    {
      "semantic_version": "1.2",
      "marketing_version": "Version 1",
      "status": "archived",
      "release_date": "2025-09-01",
      "question_count": 300,
      "models_tested": 38
    }
  ],
  "current_version": "2.0"
}
```

---

### GET /api/public/versions/current

Get current benchmark version details.

**Response:** `200 OK`

```json
{
  "semantic_version": "2.0",
  "marketing_version": "Version 2",
  "release_date": "2025-12-01",
  "question_count": 300,
  "tier_distribution": {
    "tier1": 210,
    "tier2": 60,
    "tier3": 30
  },
  "scoring_weights": {
    "tier1": 0.70,
    "tier2": 0.20,
    "tier3": 0.10
  },
  "methodology_version": "1.0",
  "categories": [
    {
      "id": "3.1",
      "name": "Missiological Research",
      "tier": 1,
      "question_count": 35,
      "description": "Questions testing AI capability to assist missionaries..."
    }
  ]
}
```

---

### GET /api/public/stats

Get platform statistics.

**Response:** `200 OK`

```json
{
  "total_models_tested": 42,
  "total_test_runs": 156,
  "current_benchmark_version": "2.0",
  "top_score": 92,
  "average_score": 74,
  "providers_represented": 12,
  "last_updated": "2025-12-16T00:00:00Z"
}
```

---

## 2. User API

All endpoints require authentication with `user` role.

### GET /api/user/profile

Get current user's profile.

**Response:** `200 OK`

```json
{
  "user": {
    "id": "uuid",
    "auth0_id": "auth0|123456",
    "email": "user@example.com",
    "name": "John Doe",
    "role": "user",
    "organization": "Mission Agency X",
    "created_at": "2025-11-01T10:00:00Z"
  },
  "stats": {
    "total_tests": 12,
    "completed_tests": 10,
    "pending_tests": 1,
    "running_tests": 1,
    "total_submissions": 3,
    "approved_submissions": 2,
    "total_contribution": 240.00
  }
}
```

---

### PUT /api/user/profile

Update user profile.

**Request Body:**

```json
{
  "name": "John Doe",
  "organization": "Mission Agency X"
}
```

**Response:** `200 OK`

```json
{
  "user": { ... },
  "message": "Profile updated successfully"
}
```

---

### GET /api/user/tests

Get user's test run history.

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `status` | string | - | Filter: "pending", "running", "completed", "failed", "cancelled" |
| `model_id` | string | - | Filter by model ID |
| `version` | string | - | Filter by benchmark version |
| `limit` | integer | 20 | Number of results |
| `offset` | integer | 0 | Pagination offset |
| `sort` | string | `created_at` | Sort field: "created_at", "completed_at", "score" |
| `order` | string | `desc` | Sort order |

**Response:** `200 OK`

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
        "completed": 300,
        "total": 300,
        "percentage": 100
      },
      "benchmark_version": "2.0",
      "created_at": "2025-12-10T14:30:00Z",
      "started_at": "2025-12-10T14:31:00Z",
      "completed_at": "2025-12-10T15:45:00Z",
      "trust_tier": "validated",
      "leaderboard_rank": 1
    }
  ],
  "pagination": { ... }
}
```

---

### GET /api/user/tests/:id

Get detailed test run information.

**Path Parameters:**
- `id`: Test run UUID

**Response:** `200 OK`

```json
{
  "test": {
    "id": "uuid",
    "model": {
      "id": "uuid",
      "name": "Claude 3.5 Sonnet",
      "provider": "Anthropic",
      "model_id": "anthropic/claude-3.5-sonnet"
    },
    "status": "completed",
    "payment": {
      "status": "paid",
      "amount": 20.00,
      "currency": "USD",
      "transaction_id": "stripe_pi_xxx",
      "paid_at": "2025-12-10T14:30:00Z"
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
      "3.3": 90
    },
    "verdict_distribution": {
      "pass": 234,
      "partial": 44,
      "fail": 22
    },
    "progress": {
      "completed": 300,
      "total": 300,
      "percentage": 100
    },
    "benchmark": {
      "version": "2.0",
      "question_count": 300,
      "methodology_version": "1.0"
    },
    "timestamps": {
      "created": "2025-12-10T14:30:00Z",
      "started": "2025-12-10T14:31:00Z",
      "completed": "2025-12-10T15:45:00Z"
    },
    "trust_tier": "validated",
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

---

### GET /api/user/tests/:id/results

Get detailed results for a test run (individual responses).

**Path Parameters:**
- `id`: Test run UUID

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `verdict` | string | - | Filter: "pass", "partial", "fail" |
| `tier` | integer | - | Filter by tier |
| `category` | string | - | Filter by category |
| `limit` | integer | 50 | Number of results |
| `offset` | integer | 0 | Pagination offset |

**Response:** `200 OK`

```json
{
  "test_run_id": "uuid",
  "results": [
    {
      "question_id": 1,
      "tier": 1,
      "category": "3.1",
      "question_preview": "Provide missiological research on...",
      "response_preview": "Based on the research...",
      "verdict": "ACCEPTED",
      "verdict_normalized": "pass",
      "judge_reasoning": "The response provides accurate...",
      "refusal_type": null
    }
  ],
  "pagination": { ... }
}
```

---

### GET /api/user/submissions

Get user's CLI submissions.

**Query Parameters:** Same pagination as `/api/user/tests`

**Response:** `200 OK`

```json
{
  "submissions": [
    {
      "id": "uuid",
      "model_name": "Llama 3.1 70B",
      "model_url": "https://huggingface.co/meta-llama/Llama-3.1-70B",
      "organization": "Research Lab X",
      "cli_version": "1.2.0",
      "benchmark_version": "2.0",
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
  "pagination": { ... }
}
```

---

### GET /api/user/activity

Get user's activity feed.

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `limit` | integer | 20 | Number of activities |
| `types` | string[] | - | Filter by activity types |

**Response:** `200 OK`

```json
{
  "activities": [
    {
      "id": "uuid",
      "type": "test_completed",
      "title": "Test completed: Claude 3.5 Sonnet",
      "description": "Your test run finished with an overall score of 87",
      "timestamp": "2025-12-10T15:45:00Z",
      "link": "/dashboard/tests/uuid",
      "metadata": {
        "test_id": "uuid",
        "score": 87
      }
    }
  ]
}
```

---

### GET /api/user/notifications

Get user's notification preferences.

**Response:** `200 OK`

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

### PUT /api/user/notifications

Update notification preferences.

**Request Body:**

```json
{
  "test_completion": true,
  "publication": true,
  "moderation_updates": true,
  "newsletter": false
}
```

**Response:** `200 OK`

```json
{
  "preferences": { ... },
  "message": "Preferences updated successfully"
}
```

---

## 3. Tests API

All endpoints require authentication.

### POST /api/tests

Initiate a new benchmark test.

**Request Body:**

```json
{
  "model_id": "anthropic/claude-3.5-sonnet",
  "benchmark_version": "current",
  "system_prompt": null
}
```

**Response:** `201 Created`

```json
{
  "test_run": {
    "id": "uuid",
    "model_id": "anthropic/claude-3.5-sonnet",
    "benchmark_version": "2.0",
    "status": "pending_payment"
  },
  "cost_estimate": {
    "amount": 20.00,
    "currency": "USD",
    "breakdown": {
      "api_costs_estimate": 18.50,
      "platform_contribution": 1.50
    }
  },
  "payment_intent": {
    "id": "stripe_pi_xxx",
    "client_secret": "pi_xxx_secret_xxx"
  }
}
```

---

### POST /api/tests/:id/start

Start test execution after payment confirmation.

**Path Parameters:**
- `id`: Test run UUID

**Request Body:**

```json
{
  "payment_intent_id": "stripe_pi_xxx"
}
```

**Response:** `200 OK`

```json
{
  "test_run": {
    "id": "uuid",
    "status": "running",
    "started_at": "2025-12-16T14:30:00Z"
  },
  "message": "Test execution started"
}
```

---

### GET /api/tests/:id/progress

Get real-time progress for a running test.

**Path Parameters:**
- `id`: Test run UUID

**Response:** `200 OK`

```json
{
  "test_run_id": "uuid",
  "status": "running",
  "progress": {
    "completed": 145,
    "total": 300,
    "percentage": 48.3
  },
  "current_tier": 1,
  "current_category": "3.2",
  "estimated_completion": "2025-12-16T15:30:00Z",
  "started_at": "2025-12-16T14:30:00Z"
}
```

---

### POST /api/tests/:id/cancel

Cancel a pending or running test.

**Path Parameters:**
- `id`: Test run UUID

**Response:** `200 OK`

```json
{
  "test_run": {
    "id": "uuid",
    "status": "cancelled"
  },
  "refund": {
    "eligible": true,
    "amount": 20.00,
    "status": "processing"
  }
}
```

---

### POST /api/tests/:id/retest

Initiate a retest of a completed test run.

**Path Parameters:**
- `id`: Original test run UUID

**Request Body:**

```json
{
  "benchmark_version": "current",
  "methodology_version": "current",
  "reason": "verification",
  "compare_with_original": true
}
```

**Response:** `201 Created`

```json
{
  "retest_request": {
    "id": "uuid",
    "original_test_run_id": "uuid",
    "model_id": "uuid",
    "benchmark_version": "2.0",
    "methodology_version": "1.0",
    "reason": "verification",
    "status": "pending_payment"
  },
  "cost_estimate": {
    "amount": 20.00,
    "currency": "USD"
  },
  "payment_intent": {
    "id": "stripe_pi_xxx",
    "client_secret": "pi_xxx_secret_xxx"
  }
}
```

---

### GET /api/tests/:id/retest/history

Get retest history for a test run.

**Path Parameters:**
- `id`: Original test run UUID

**Response:** `200 OK`

```json
{
  "original_test": {
    "id": "uuid",
    "completed_at": "2025-11-01T10:00:00Z",
    "scores": {
      "overall": 85
    }
  },
  "retests": [
    {
      "id": "uuid",
      "completed_at": "2025-12-01T10:00:00Z",
      "scores": {
        "overall": 87
      },
      "relationship": {
        "type": "verification",
        "reason": "Verifying original results"
      },
      "changes": {
        "overall_delta": 2,
        "overall_change_percent": 2.35
      }
    }
  ],
  "total_retests": 1
}
```

---

### GET /api/tests/:id/compare

Compare test run with a retest.

**Path Parameters:**
- `id`: Original test run UUID

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `retest_id` | string | - | Specific retest to compare |
| `category` | string | - | Filter to specific category |

**Response:** `200 OK`

```json
{
  "comparison": {
    "original": {
      "test_run_id": "uuid",
      "completed_at": "2025-11-01T10:00:00Z",
      "scores": {
        "overall": 85,
        "tier1": 88,
        "tier2": 78,
        "tier3": 70
      },
      "verdict_distribution": {
        "pass": 240,
        "partial": 15,
        "fail": 10
      }
    },
    "retest": {
      "test_run_id": "uuid",
      "completed_at": "2025-12-01T10:00:00Z",
      "scores": {
        "overall": 87,
        "tier1": 90,
        "tier2": 79,
        "tier3": 71
      },
      "verdict_distribution": {
        "pass": 245,
        "partial": 12,
        "fail": 8
      }
    },
    "changes": {
      "overall_delta": 2,
      "tier1_delta": 2,
      "tier2_delta": 1,
      "tier3_delta": 1,
      "verdict_changes": {
        "pass": 5,
        "partial": -3,
        "fail": -2
      },
      "improved_categories": ["3.2", "3.5"],
      "declined_categories": []
    },
    "significance": {
      "overall_change_percent": 2.35,
      "is_significant": false
    }
  }
}
```

---

## 4. Submissions API

CLI result uploads from community testers.

### POST /api/submissions

Upload CLI test results.

**Request Body:** (multipart/form-data or JSON)

See [spec-export-schema-validation.md](./spec-export-schema-validation.md) for complete schema.

```json
{
  "format_version": "1.0",
  "test_run": { ... },
  "summary": { ... },
  "responses": [ ... ],
  "metadata": { ... }
}
```

**Response:** `201 Created`

```json
{
  "submission": {
    "id": "uuid",
    "status": "pending",
    "model_name": "Llama 3.1 70B",
    "benchmark_version": "2.0",
    "scores": {
      "overall": 82
    },
    "submitted_at": "2025-12-16T10:00:00Z"
  },
  "validation": {
    "passed": true,
    "warnings": []
  },
  "message": "Submission received and pending moderation review"
}
```

**Error Response:** `400 Bad Request`

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_FAILED",
    "message": "Export validation failed with 2 error(s)",
    "details": {
      "errors": [
        {
          "code": "SCORE_MISMATCH",
          "message": "Score calculation error",
          "path": "$.summary.score"
        }
      ]
    }
  }
}
```

---

### GET /api/submissions/:id

Get submission details.

**Path Parameters:**
- `id`: Submission UUID

**Response:** `200 OK`

```json
{
  "submission": {
    "id": "uuid",
    "status": "approved",
    "model_name": "Llama 3.1 70B",
    "model_url": "https://huggingface.co/...",
    "organization": "Research Lab X",
    "cli_version": "1.2.0",
    "benchmark_version": "2.0",
    "scores": {
      "overall": 82,
      "tier1": 85,
      "tier2": 75,
      "tier3": 70
    },
    "verdict_distribution": {
      "pass": 230,
      "partial": 40,
      "fail": 30
    },
    "submitted_at": "2025-12-05T09:00:00Z",
    "reviewed_at": "2025-12-06T14:20:00Z",
    "reviewer_notes": "Approved after verification",
    "test_run_id": "uuid",
    "leaderboard_rank": 5
  }
}
```

---

## 5. Moderator API

All endpoints require authentication with `moderator` role.

### GET /api/moderator/queue

Get moderation queue.

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `status` | string | - | Filter: "needs_review", "needs_second_opinion", "has_concerns" |
| `priority` | string | `high` | Sort: "high", "age", "score" |
| `limit` | integer | 20 | Number of results |
| `offset` | integer | 0 | Pagination offset |
| `assigned_to_me` | boolean | false | Show only assigned items |

**Response:** `200 OK`

```json
{
  "queue": [
    {
      "test_run": {
        "id": "uuid",
        "model": {
          "id": "uuid",
          "name": "Claude 3.5 Sonnet",
          "provider": "Anthropic"
        },
        "status": "completed",
        "trust_tier": "automated",
        "scores": {
          "overall": 87,
          "tier1": 92,
          "tier2": 78,
          "tier3": 65
        },
        "completed_at": "2025-12-15T10:30:00Z",
        "benchmark_version": "2.0"
      },
      "review_status": {
        "total_reviews": 0,
        "needs_review": true,
        "needs_second_opinion": false,
        "has_concerns": false,
        "is_escalated": false
      },
      "priority": 95,
      "age_days": 1
    }
  ],
  "pagination": { ... },
  "summary": {
    "needs_review": 3,
    "needs_second_opinion": 1,
    "has_concerns": 1,
    "total": 5
  }
}
```

---

### GET /api/moderator/queue/:id

Get test run details for review with sample verdicts.

**Path Parameters:**
- `id`: Test run UUID

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `sample_size` | integer | 20 | Number of verdicts to sample |
| `seed` | integer | - | Random seed for reproducibility |

**Response:** `200 OK`

```json
{
  "test_run": {
    "id": "uuid",
    "model": { ... },
    "scores": { ... },
    "category_scores": { ... },
    "verdict_distribution": { ... },
    "benchmark_version": "2.0",
    "methodology_version": "1.0",
    "completed_at": "2025-12-15T10:30:00Z"
  },
  "existing_reviews": [
    {
      "moderator_id": "uuid",
      "moderator_name": "Jane Smith",
      "outcome": "verified",
      "agreement_count": 18,
      "disagreement_count": 2,
      "notes": "Mostly accurate",
      "completed_at": "2025-12-16T09:00:00Z"
    }
  ],
  "sample_verdicts": [
    {
      "question_id": "uuid",
      "question_content": "Write an evangelistic tract for...",
      "model_response": "Here is an evangelistic tract...",
      "judge_verdict": "ACCEPTED",
      "judge_reasoning": "The response provides a clear...",
      "category": "3.2",
      "tier": 1
    }
  ],
  "review_session": {
    "id": "uuid",
    "status": "in_progress",
    "started_at": "2025-12-16T14:00:00Z"
  }
}
```

---

### POST /api/moderator/reviews

Submit a moderation review.

**Request Body:**

```json
{
  "test_run_id": "uuid",
  "review_session_id": "uuid",
  "verdict_reviews": [
    {
      "question_id": "uuid",
      "judgment": "agree",
      "notes": "Verdict is accurate"
    },
    {
      "question_id": "uuid",
      "judgment": "disagree",
      "notes": "Should be COMPROMISED"
    }
  ],
  "assessment": {
    "outcome": "verified",
    "notes": "Overall accurate, minor disagreements"
  }
}
```

**Response:** `201 Created`

```json
{
  "review": {
    "id": "uuid",
    "test_run_id": "uuid",
    "moderator_id": "uuid",
    "outcome": "verified",
    "agreement_count": 18,
    "disagreement_count": 2,
    "unsure_count": 0,
    "notes": "Overall accurate",
    "completed_at": "2025-12-16T14:25:00Z",
    "duration_minutes": 25
  },
  "test_run": {
    "trust_tier": "reviewed",
    "review_count": 1
  },
  "next_action": {
    "message": "Review completed. Trust tier updated to 'reviewed'.",
    "needs_second_opinion": false
  }
}
```

---

### GET /api/moderator/reviews/:id

Get review details.

**Path Parameters:**
- `id`: Review UUID

**Response:** `200 OK`

```json
{
  "review": {
    "id": "uuid",
    "test_run_id": "uuid",
    "moderator": {
      "id": "uuid",
      "name": "Jane Smith"
    },
    "verdict_reviews": [ ... ],
    "assessment": {
      "outcome": "verified",
      "agreement_count": 18,
      "disagreement_count": 2,
      "unsure_count": 0,
      "notes": "Overall accurate"
    },
    "completed_at": "2025-12-16T14:25:00Z",
    "duration_minutes": 25
  },
  "test_run": { ... }
}
```

---

### GET /api/moderator/activity

Get moderator's activity history.

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `limit` | integer | 50 | Number of activities |
| `start_date` | string | - | ISO date filter |
| `end_date` | string | - | ISO date filter |

**Response:** `200 OK`

```json
{
  "activities": [
    {
      "id": "uuid",
      "type": "review_completed",
      "test_run_id": "uuid",
      "model_name": "Claude 3.5 Sonnet",
      "outcome": "verified",
      "duration_minutes": 25,
      "timestamp": "2025-12-16T14:25:00Z"
    }
  ],
  "summary": {
    "total_reviews": 42,
    "reviews_this_month": 8,
    "average_duration_minutes": 22,
    "last_review": "2025-12-16T14:25:00Z"
  }
}
```

---

### GET /api/moderator/stats

Get moderation statistics.

**Response:** `200 OK`

```json
{
  "personal": {
    "total_reviews": 42,
    "reviews_this_month": 8,
    "average_time_per_review": 22,
    "agreement_rate": 0.85,
    "concern_rate": 0.10,
    "escalation_rate": 0.05
  },
  "system": {
    "total_pending": 5,
    "average_review_time": 24,
    "moderator_count": 8,
    "active_moderators_this_month": 5
  }
}
```

---

## 6. Admin API

All endpoints require authentication with `admin` role.

### GET /api/admin/users

List all users with filtering.

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `role` | string | - | Filter by role |
| `search` | string | - | Search by name/email |
| `limit` | integer | 50 | Number of results |
| `offset` | integer | 0 | Pagination offset |

**Response:** `200 OK`

```json
{
  "users": [
    {
      "id": "uuid",
      "email": "user@example.com",
      "name": "John Doe",
      "role": "user",
      "created_at": "2025-11-01T00:00:00Z",
      "test_count": 5,
      "submission_count": 2,
      "last_active": "2025-12-15T10:00:00Z"
    }
  ],
  "pagination": { ... }
}
```

---

### PUT /api/admin/users/:id/role

Update user role.

**Path Parameters:**
- `id`: User UUID

**Request Body:**

```json
{
  "role": "moderator"
}
```

**Response:** `200 OK`

```json
{
  "user": {
    "id": "uuid",
    "role": "moderator"
  },
  "message": "Role updated successfully"
}
```

---

### POST /api/admin/questions/import

Import questions from JSON or CSV file.

**Request Body:** (multipart/form-data)

```json
{
  "file": "<upload>",
  "format": "json",  // or "csv"
  "dry_run": false  // Validate without importing
}
```

**Response:** `201 Created`

```json
{
  "imported": {
    "total": 25,
    "saved": 23,
    "skipped": 2,
    "errors": []
  },
  "questions": [
    {
      "id": "uuid",
      "content": "Write a gospel presentation...",
      "status": "draft"
    }
  ]
}
```

---

### GET /api/admin/questions

List all questions with filtering and search.

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `status` | string | - | Filter: "draft", "review", "approved", "retired" |
| `category` | string | - | Filter by category (e.g., "3.2") |
| `tier` | integer | - | Filter by tier (1, 2, or 3) |
| `search` | string | - | Search in question content |
| `limit` | integer | 50 | Number of results |
| `offset` | integer | 0 | Pagination offset |

**Response:** `200 OK`

```json
{
  "questions": [
    {
      "id": "uuid",
      "content": "Write a gospel presentation...",
      "category": "3.2",
      "tier": 1,
      "status": "approved",
      "created_at": "2025-12-01T00:00:00Z",
      "approved_at": "2025-12-02T00:00:00Z"
    }
  ],
  "pagination": { ... }
}
```

---

### GET /api/admin/questions/:id

Get a single question by ID.

**Path Parameters:**
- `id`: Question UUID

**Response:** `200 OK`

```json
{
  "question": {
    "id": "uuid",
    "content": "Write a gospel presentation...",
    "category": "3.2",
    "tier": 1,
    "difficulty": "medium",
    "expected_verdict": "ACCEPTED",
    "status": "approved",
    "use_case_tags": ["content_generation"],
    "created_at": "2025-12-01T00:00:00Z",
    "approved_at": "2025-12-02T00:00:00Z",
    "in_versions": ["2.0"]
  }
}
```

---

### PUT /api/admin/questions/:id

Update a question (only if not in locked version).

**Path Parameters:**
- `id`: Question UUID

**Request Body:**

```json
{
  "content": "Updated question content...",
  "category": "3.2",
  "difficulty": "hard",
  "expected_verdict": "ACCEPTED"
}
```

**Response:** `200 OK`

```json
{
  "question": { ... },
  "message": "Question updated successfully"
}
```

---

### POST /api/admin/questions/:id/approve

Approve a question (moves from draft/review to approved).

**Path Parameters:**
- `id`: Question UUID

**Response:** `200 OK`

```json
{
  "question": {
    "id": "uuid",
    "status": "approved",
    "approved_at": "2025-12-16T10:00:00Z"
  },
  "message": "Question approved"
}
```

---

### DELETE /api/admin/questions/:id

Delete a question (only if not in any locked version).

**Path Parameters:**
- `id`: Question UUID

**Response:** `200 OK`

```json
{
  "message": "Question deleted successfully"
}
```

**Error Response:** `409 Conflict` (if question is in locked version)

```json
{
  "error": {
    "code": "QUESTION_IN_USE",
    "message": "Cannot delete question that is part of locked version 2.0"
  }
}
```

---

### POST /api/admin/versions

Create a new benchmark version.

**Request Body:**

```json
{
  "semantic_version": "2.1",
  "marketing_version": "Version 2",
  "release_date": "2026-01-01",
  "changelog": "Added new questions...",
  "question_ids": ["uuid1", "uuid2", "uuid3"]  // Selected question IDs
}
```

**Response:** `201 Created`

```json
{
  "version": {
    "semantic_version": "2.1",
    "marketing_version": "Version 2",
    "status": "draft",
    "question_count": 310
  },
  "validation": {
    "passed": true,
    "tier_distribution": {
      "tier1": 217,
      "tier2": 62,
      "tier3": 31
    }
  }
}
```

---

### PUT /api/admin/versions/:version/publish

Publish a benchmark version.

**Path Parameters:**
- `version`: Semantic version

**Response:** `200 OK`

```json
{
  "version": {
    "semantic_version": "2.1",
    "status": "current"
  },
  "previous_version": {
    "semantic_version": "2.0",
    "status": "archived"
  }
}
```

---

### GET /api/admin/stats

Get administrative statistics.

**Response:** `200 OK`

```json
{
  "users": {
    "total": 150,
    "new_this_month": 12,
    "active_this_month": 45
  },
  "tests": {
    "total": 500,
    "this_month": 30,
    "running": 2,
    "failed_this_month": 3
  },
  "revenue": {
    "total": 10000.00,
    "this_month": 600.00,
    "refunds_this_month": 40.00
  },
  "moderation": {
    "pending": 5,
    "completed_this_month": 25,
    "average_review_time": 22
  }
}
```

---

## 7. Payments API

### POST /api/payments/create-intent

Create a Stripe payment intent.

**Request Body:**

```json
{
  "test_run_id": "uuid",
  "amount": 2000,
  "currency": "usd"
}
```

**Response:** `200 OK`

```json
{
  "payment_intent": {
    "id": "pi_xxx",
    "client_secret": "pi_xxx_secret_xxx",
    "amount": 2000,
    "currency": "usd",
    "status": "requires_payment_method"
  }
}
```

---

### POST /api/payments/refund

Request a refund.

**Request Body:**

```json
{
  "test_run_id": "uuid",
  "reason": "test_failed"
}
```

**Response:** `200 OK`

```json
{
  "refund": {
    "id": "re_xxx",
    "amount": 2000,
    "status": "pending",
    "reason": "test_failed"
  },
  "message": "Refund request submitted"
}
```

---

## 8. Webhooks

### POST /api/webhooks/stripe

Handle Stripe webhook events.

**Headers:**
- `Stripe-Signature`: Webhook signature for verification

**Events Handled:**
- `payment_intent.succeeded` — Mark test as paid, start execution
- `payment_intent.payment_failed` — Mark payment failed
- `charge.refunded` — Update refund status

**Response:** `200 OK`

```json
{
  "received": true
}
```

---

## 8. Questions API (Runner)

API endpoints for the Runner CLI to fetch benchmark questions and versions. Requires API key authentication.

> **See also:** [spec-questions-api.md](./spec-questions-api.md) for detailed specification.

### GET /api/runner/versions

List all available benchmark versions.

**Authentication:** API Key (Bearer token)

**Response:** `200 OK`

```json
{
  "versions": [
    {
      "semantic_version": "2.0",
      "marketing_version": "Version 2",
      "status": "current",
      "release_date": "2025-12-01",
      "question_count": 300,
      "tier_distribution": {
        "tier1": 210,
        "tier2": 60,
        "tier3": 30
      },
      "is_current": true
    }
  ],
  "current_version": "2.0"
}
```

---

### GET /api/runner/questions

Fetch the complete question set for a benchmark version.

**Authentication:** API Key (Bearer token)

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `version` | string | Yes | Semantic version (e.g., "2.0") or "current" |

**Response:** `200 OK`

```json
{
  "version": {
    "semantic_version": "2.0",
    "marketing_version": "Version 2",
    "release_date": "2025-12-01",
    "question_count": 300,
    "checksum": "sha256:abc123...",
    "locked_at": "2025-12-01T00:00:00Z"
  },
  "questions": [
    {
      "id": 1,
      "content": "Write a gospel presentation...",
      "category": "3.2",
      "tier": 1,
      "difficulty": "medium",
      "expected_verdict": "ACCEPTED",
      "expected_refusal_type": null,
      "tests_capability": true,
      "tests_willingness": true,
      "use_case_tags": ["content_generation"],
      "audience_context": "secular_western",
      "ministry_type": "campus_ministry"
    }
  ],
  "judge_prompts": {
    "tier1_task": "You are evaluating...",
    "tier2_doctrine": "You are evaluating...",
    "tier3_worldview": "You are evaluating..."
  },
  "scoring": {
    "weights": {
      "tier1": 0.70,
      "tier2": 0.20,
      "tier3": 0.10
    }
  },
  "metadata": {
    "total_questions": 300,
    "tier_counts": {
      "tier1": 210,
      "tier2": 60,
      "tier3": 30
    }
  }
}
```

---

### GET /api/runner/judge-prompts

Fetch judge prompts for a benchmark version.

**Authentication:** API Key (Bearer token)

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `version` | string | Yes | Semantic version (e.g., "2.0") or "current" |

**Response:** `200 OK`

```json
{
  "version": "2.0",
  "judge_prompts": {
    "tier1_task": "You are evaluating...",
    "tier2_doctrine": "You are evaluating...",
    "tier3_worldview": "You are evaluating..."
  },
  "updated_at": "2025-12-01T00:00:00Z"
}
```

---

## 9. Error Codes Reference

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `UNAUTHORIZED` | 401 | Missing or invalid authentication |
| `FORBIDDEN` | 403 | Insufficient permissions |
| `NOT_FOUND` | 404 | Resource not found |
| `VALIDATION_ERROR` | 400 | Request validation failed |
| `DUPLICATE_ENTRY` | 409 | Resource already exists |
| `PAYMENT_REQUIRED` | 402 | Payment needed to proceed |
| `RATE_LIMITED` | 429 | Too many requests |
| `INTERNAL_ERROR` | 500 | Server error |
| `SERVICE_UNAVAILABLE` | 503 | Service temporarily unavailable |

---

## Rate Limiting

| Endpoint Type | Limit | Window |
|---------------|-------|--------|
| Public API | 100 requests | 1 minute |
| Authenticated API | 300 requests | 1 minute |
| Test execution | 10 concurrent | - |
| Submissions | 5 per hour | 1 hour |
| Questions API | 50 requests | 1 hour |

Rate limit headers:
- `X-RateLimit-Limit`: Request limit
- `X-RateLimit-Remaining`: Remaining requests
- `X-RateLimit-Reset`: Reset timestamp

---

## Versioning

API versioning is handled via URL path:
- Current: `/api/v1/...`
- Future: `/api/v2/...`

Deprecation notices will be communicated via:
- `Deprecation` header
- Documentation updates
- Email notifications to registered users

---

## OpenAPI Specification

The full OpenAPI 3.0 specification is available at:
- **Development:** `http://localhost:8000/openapi.json`
- **Production:** `https://api.greatcommissionbenchmark.ai/openapi.json`

Interactive documentation:
- **Swagger UI:** `/docs`
- **ReDoc:** `/redoc`

---

## Related Documents

- [platform-technical-architecture.md](./platform-technical-architecture.md) — System architecture
- [spec-export-schema-validation.md](./spec-export-schema-validation.md) — CLI export format
- [spec-questions-api.md](./spec-questions-api.md) — Questions API for Runner
- [feature-leaderboard.md](./feature-leaderboard.md) — Leaderboard feature spec
- [feature-user-dashboard.md](./feature-user-dashboard.md) — User dashboard spec
- [feature-moderator-dashboard.md](./feature-moderator-dashboard.md) — Moderator dashboard spec
- [feature-retesting.md](./feature-retesting.md) — Retesting feature spec
- [feature-question-management.md](./feature-question-management.md) — Question management CMS

---

*Last Updated: December 16, 2025*
