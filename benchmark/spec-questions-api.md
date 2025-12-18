# Questions API Specification

This document defines the API endpoints for the GCB Runner CLI to fetch benchmark questions, versions, and judge prompts from the Platform.

---

## Overview

The Questions API provides authenticated access to benchmark question sets for the Runner CLI. Questions are fetched on-demand via API rather than being embedded in the Runner package.

**Key features:**
- API key authentication
- Version-based question retrieval
- Local caching support
- Rate limiting
- Judge prompts included

---

## Authentication

All endpoints require an API key provided via Bearer token:

```
Authorization: Bearer <api_key>
```

### API Key Management

- API keys are issued through the Platform user dashboard
- Keys are tied to user accounts
- Keys can be revoked at any time
- Rate limits apply per key

---

## Base URL

```
Production: https://api.greatcommissionbenchmark.ai/api/runner
Development: http://localhost:8000/api/runner
```

---

## Endpoints

### GET /api/runner/versions

List all available benchmark versions.

**Authentication:** Required (API Key)

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
    },
    {
      "semantic_version": "1.2",
      "marketing_version": "Version 1",
      "status": "archived",
      "release_date": "2025-09-01",
      "question_count": 300,
      "tier_distribution": {
        "tier1": 210,
        "tier2": 60,
        "tier3": 30
      },
      "is_current": false
    }
  ],
  "current_version": "2.0"
}
```

---

### GET /api/runner/questions

Fetch the complete question set for a benchmark version.

**Authentication:** Required (API Key)

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
    "checksum": "sha256:abc123def456...",
    "locked_at": "2025-12-01T00:00:00Z"
  },
  "questions": [
    {
      "id": 1,
      "content": "Write a gospel presentation for a secular Western audience...",
      "category": "3.2",
      "tier": 1,
      "difficulty": "medium",
      "expected_verdict": "ACCEPTED",
      "expected_refusal_type": null,
      "tests_capability": true,
      "tests_willingness": true,
      "use_case_tags": ["content_generation", "evangelism"],
      "audience_context": "secular_western",
      "ministry_type": "campus_ministry"
    }
  ],
  "judge_prompts": {
    "tier1_task": "You are evaluating an LLM response to a ministry task...",
    "tier2_doctrine": "You are evaluating an LLM response for doctrinal fidelity...",
    "tier3_worldview": "You are evaluating an LLM response for worldview alignment..."
  },
  "scoring": {
    "weights": {
      "tier1": 0.70,
      "tier2": 0.20,
      "tier3": 0.10
    },
    "formula": "(tier1_score * 0.70) + (tier2_score * 0.20) + (tier3_score * 0.10)"
  },
  "metadata": {
    "total_questions": 300,
    "tier_counts": {
      "tier1": 210,
      "tier2": 60,
      "tier3": 30
    },
    "category_counts": {
      "3.1": 35,
      "3.2": 35
    }
  }
}
```

**Error Responses:**

- `400 Bad Request` - Invalid version parameter
- `401 Unauthorized` - Missing or invalid API key
- `404 Not Found` - Version does not exist
- `429 Too Many Requests` - Rate limit exceeded

---

### GET /api/runner/judge-prompts

Fetch judge prompts for a benchmark version.

**Authentication:** Required (API Key)

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `version` | string | Yes | Semantic version (e.g., "2.0") or "current" |

**Response:** `200 OK`

```json
{
  "version": "2.0",
  "judge_prompts": {
    "tier1_task": "You are evaluating an LLM response to a ministry task...",
    "tier2_doctrine": "You are evaluating an LLM response for doctrinal fidelity...",
    "tier3_worldview": "You are evaluating an LLM response for worldview alignment..."
  },
  "updated_at": "2025-12-01T00:00:00Z"
}
```

---

## Caching Strategy

The Runner should implement local caching to reduce API calls and enable offline operation:

### Cache Location

- **macOS/Linux:** `~/.gcb-runner/cache/`
- **Windows:** `%APPDATA%\gcb-runner\cache\`

### Cache Structure

```
cache/
├── versions.json          # List of available versions
├── v2.0/
│   ├── questions.json     # Full question set
│   ├── judge-prompts.json
│   └── metadata.json     # Version metadata, checksum
└── v1.2/
    └── ...
```

### Cache Invalidation

- Check for version updates daily (or on Runner start)
- Compare checksums to detect changes
- Re-fetch if checksum differs or cache is stale (>7 days)
- Cache is versioned by semantic version number

### Cache Headers

The API includes cache headers:

```
Cache-Control: public, max-age=86400
ETag: "sha256:abc123..."
Last-Modified: Wed, 01 Dec 2025 00:00:00 GMT
```

The Runner should respect these headers and implement conditional requests:

```
If-None-Match: "sha256:abc123..."
```

---

## Rate Limiting

| Endpoint | Limit | Window |
|----------|-------|--------|
| `/api/runner/versions` | 100 requests | 1 hour |
| `/api/runner/questions` | 50 requests | 1 hour |
| `/api/runner/judge-prompts` | 100 requests | 1 hour |

Rate limit headers:

```
X-RateLimit-Limit: 50
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1701388800
```

When rate limit is exceeded:

**Response:** `429 Too Many Requests`

```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded. Try again in 3600 seconds.",
    "retry_after": 3600
  }
}
```

---

## Error Handling

### Standard Error Response

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {}
  }
}
```

### Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `UNAUTHORIZED` | 401 | Missing or invalid API key |
| `FORBIDDEN` | 403 | API key lacks required permissions |
| `NOT_FOUND` | 404 | Version or resource not found |
| `VALIDATION_ERROR` | 400 | Invalid request parameters |
| `RATE_LIMIT_EXCEEDED` | 429 | Too many requests |
| `INTERNAL_ERROR` | 500 | Server error |

---

## Version Selection

### Using "current"

The special version identifier `"current"` always resolves to the latest active version:

```
GET /api/runner/questions?version=current
```

This is equivalent to fetching the version marked `"is_current": true` from `/api/runner/versions`.

### Version Format

Versions use semantic versioning:
- `"1.0"`, `"1.1"`, `"1.2"` - Minor versions within Version 1
- `"2.0"`, `"2.1"` - Minor versions within Version 2

---

## Security Considerations

### API Key Storage

- Store API keys securely (encrypted at rest)
- Never commit keys to version control
- Support key rotation

### Question Protection

- Questions are only served to authenticated users
- All access is logged for audit
- Rate limiting prevents bulk extraction
- Checksums verify integrity

### Network Security

- All requests must use HTTPS in production
- Certificate pinning recommended for Runner
- Validate TLS certificates

---

## Example Usage

### Fetch Current Version

```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
  "https://api.greatcommissionbenchmark.ai/api/runner/questions?version=current"
```

### Fetch Specific Version

```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
  "https://api.greatcommissionbenchmark.ai/api/runner/questions?version=2.0"
```

### List Available Versions

```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
  "https://api.greatcommissionbenchmark.ai/api/runner/versions"
```

---

## Related Documents

- [cli-runner-specifications.md](./cli-runner-specifications.md) - Runner CLI implementation
- [spec-api-endpoints.md](./spec-api-endpoints.md) - Complete API reference
- [process-question-security.md](./process-question-security.md) - Question protection policies

---

*Last Updated: December 18, 2025*
