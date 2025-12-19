# Technical Debt Remediation Plan

**Generated:** December 18, 2025  
**Status:** Pending Implementation

This document outlines all identified technical debt issues in the Great Commission Benchmark codebase, organized by priority with specific action items and file locations.

---

## Table of Contents

- [🔴 High Priority (Security & Critical)](#-high-priority-security--critical)
- [🟡 Medium Priority (Functionality & Performance)](#-medium-priority-functionality--performance)
- [🟢 Low Priority (Code Quality & Maintenance)](#-low-priority-code-quality--maintenance)
- [Progress Tracking](#progress-tracking)

---

## 🔴 High Priority (Security & Critical)

### 1. Fix Insecure JWT Fallback in Development

**File:** `gcb-platform/backend/app/core/auth.py` (lines 97-102)

**Problem:** When Auth0 isn't configured, JWTs are decoded without signature verification, which could allow token forgery if accidentally deployed to production.

**Current Code:**
```python
else:
    # Fallback for development/testing without Auth0 configured
    # WARNING: This should not be used in production
    payload = jwt.decode(
        token,
        options={"verify_signature": False}
    )
```

**Action Items:**
- [ ] Add environment check to prevent this fallback in production
- [ ] Add `ENVIRONMENT` or `DEBUG` setting to config
- [ ] Raise an explicit error in production when Auth0 is not configured
- [ ] Consider removing the fallback entirely and requiring Auth0 even in development

**Suggested Fix:**
```python
else:
    # Only allow unverified tokens in explicit development mode
    import os
    if os.getenv("ENVIRONMENT", "production").lower() == "development":
        payload = jwt.decode(
            token,
            options={"verify_signature": False}
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication not properly configured"
        )
```

---

### 2. Remove Hardcoded Production URLs from Config Defaults

**File:** `gcb-platform/backend/app/core/config.py` (line 35)

**Problem:** Production URLs are hardcoded in default values rather than being required environment variables.

**Current Code:**
```python
CORS_ORIGINS_STR: str = "http://localhost:3000,http://localhost:3001,https://frontend-production-8b79.up.railway.app"
```

**Action Items:**
- [ ] Change default to localhost-only
- [ ] Require production URLs via environment variables
- [ ] Add validation to ensure CORS origins are set in production

**Suggested Fix:**
```python
CORS_ORIGINS_STR: str = Field(
    default="http://localhost:3000,http://localhost:3001",
    description="Comma-separated list of allowed CORS origins"
)
```

---

### 3. Replace Print Statements with Proper Logging

**Files:**
- `gcb-platform/backend/app/services/executor.py` (line 117)
- `gcb-platform/backend/app/services/email.py` (lines 35, 47)

**Problem:** Using `print()` instead of proper logging loses structured log data, timestamps, and log levels.

**Action Items:**
- [ ] Add logger import to each file
- [ ] Replace `print()` calls with appropriate log levels
- [ ] Ensure log format includes context (test_id, user_id, etc.)

**executor.py Fix:**
```python
# Add at top:
import logging
logger = logging.getLogger(__name__)

# Replace line 117:
logger.warning(f"Failed to send completion email for test {test_run.id}: {str(e)}")
```

**email.py Fix:**
```python
# Add at top:
import logging
logger = logging.getLogger(__name__)

# Replace line 35:
logger.info(f"Email not sent (service not configured): to={to}, subject={subject}")

# Replace line 47:
logger.error(f"Failed to send email to {to}: {str(e)}")
```

---

## 🟡 Medium Priority (Functionality & Performance)

### 4. Fix TypeScript `any` Types in Frontend

**Files:**
- `gcb-platform/frontend/app/page.tsx` (lines 13-16)
- `gcb-platform/frontend/app/dashboard/page.tsx` (lines 24-28)
- `gcb-platform/frontend/app/research/page.tsx` (line 26+)
- `gcb-platform/frontend/app/tests/new/page.tsx` (line 26+)

**Problem:** Using `any` defeats TypeScript's type safety.

**Action Items:**
- [ ] Create proper interfaces in `lib/types.ts`
- [ ] Update `page.tsx` to use typed state
- [ ] Update `dashboard/page.tsx` to use typed state
- [ ] Update `research/page.tsx` to use typed state
- [ ] Update `tests/new/page.tsx` to use typed state

**Create new file `gcb-platform/frontend/lib/types.ts`:**
```typescript
// Re-export API types for convenience
export type {
  LeaderboardItem,
  LeaderboardResponse,
  ModelResponse,
  StatsResponse,
  TestRun,
  UserProfile,
} from './api';

// Additional component-specific types
export interface TopPerformer {
  rank: number;
  model_id: string;
  model_name: string;
  provider: string;
  score: number;
}

export interface RankingItem {
  rank: number;
  model_id: string;
  model_name: string;
  provider: string;
  score: number;
}

export interface Submission {
  id: string;
  model_name: string;
  status: string;
  created_at: string;
}

export interface ActivityItem {
  type: string;
  description?: string;
  created_at: string;
  link?: string;
}
```

**Update `page.tsx`:**
```typescript
import { TopPerformer, RankingItem, StatsResponse } from "@/lib/types";

const [topPerformers, setTopPerformers] = useState<TopPerformer[]>([]);
const [rankings, setRankings] = useState<RankingItem[]>([]);
const [stats, setStats] = useState<StatsResponse | null>(null);
```

---

### 5. Implement Auth0 Token Integration in API Client

**File:** `gcb-platform/frontend/lib/api.ts` (lines 186-190)

**Problem:** Auth token retrieval is stubbed out, meaning authenticated API calls won't work properly.

**Action Items:**
- [ ] Install `@auth0/nextjs-auth0` client-side utilities if not present
- [ ] Implement token retrieval using Auth0's session
- [ ] Handle token refresh and errors

**Suggested Fix:**
```typescript
private async getAuthToken(): Promise<string | null> {
  try {
    // For client-side, fetch from our API route that gets the token
    const response = await fetch('/api/auth/token');
    if (response.ok) {
      const data = await response.json();
      return data.accessToken || null;
    }
    return null;
  } catch {
    return null;
  }
}
```

**Create new API route `gcb-platform/frontend/app/api/auth/token/route.ts`:**
```typescript
import { getAccessToken } from '@auth0/nextjs-auth0';
import { NextResponse } from 'next/server';

export async function GET() {
  try {
    const { accessToken } = await getAccessToken();
    return NextResponse.json({ accessToken });
  } catch {
    return NextResponse.json({ accessToken: null }, { status: 401 });
  }
}
```

---

### 6. Fix N+1 Query Issues in Leaderboard

**File:** `gcb-platform/backend/app/api/v1/endpoints/public.py` (lines 98-100)

**Problem:** Scores are calculated in a loop, triggering separate queries per test run.

**Action Items:**
- [ ] Option A: Cache scores on TestRun model (add `cached_scores` JSONB column)
- [ ] Option B: Batch calculate scores for all test runs
- [ ] Option C: Use eager loading with joinedload

**Suggested Fix (Option A - Cache scores):**

1. Add migration for cached scores:
```python
# New migration file
def upgrade():
    op.add_column('test_runs', sa.Column('cached_scores', JSONB, nullable=True))
```

2. Update executor to cache scores on completion:
```python
# In executor.py, after calculating scores:
test_run.cached_scores = scores
```

3. Update leaderboard to use cached scores:
```python
for idx, test_run in enumerate(test_runs[offset:offset+limit]):
    if test_run.cached_scores:
        scores_data = test_run.cached_scores
    else:
        scores_data = ScoringService.calculate_scores(db, str(test_run.id))
```

---

### 7. Address TODO Comments Throughout Codebase

**Locations and Actions:**

| File | Line | TODO | Action |
|------|------|------|--------|
| `cli.py` | 414 | Implement full upload flow | Create upload implementation |
| `public.py` | 139 | Get methodology_version | Query actual version |
| `user.py` | 64, 81 | Add organization field | Add to User model + migration |
| `user.py` | 140 | Get total from question_set | Query question count |
| `user.py` | 163 | Calculate rank | Implement rank calculation |
| `submissions.py` | 106 | Verify score calculation | Add validation logic |
| `runner.py` | 24 | Validate API key against DB | Add database validation |
| `runner.py` | 140, 145 | Split judge prompt by tier | Store tier-specific prompts |
| `moderator.py` | 214 | Send admin notification | Implement email notification |
| `moderator.py` | 384 | Create test run from submission | Implement conversion logic |

**Action Items:**
- [ ] Fix `public.py:139` - Replace hardcoded "1.0" with actual methodology version
- [ ] Fix `user.py` - Add organization field to User model
- [ ] Fix `user.py:140` - Query question count from question_set
- [ ] Fix `user.py:163` - Implement leaderboard rank calculation
- [ ] Fix `submissions.py:106` - Add score verification
- [ ] Fix `runner.py:24` - Add API key database validation
- [ ] Fix `runner.py:140-145` - Store/retrieve tier-specific judge prompts
- [ ] Fix `moderator.py:214` - Send admin committee notification email
- [ ] Fix `moderator.py:384` - Implement submission-to-test-run conversion
- [ ] Fix `cli.py:414` - Implement CLI upload functionality

---

### 8. Improve Rate Limiter with Redis Support

**File:** `gcb-platform/backend/app/core/rate_limit.py`

**Problem:** In-memory rate limiting won't work across multiple server instances.

**Action Items:**
- [ ] Add Redis dependency to requirements
- [ ] Create Redis connection configuration
- [ ] Implement Redis-backed rate limiter
- [ ] Fall back to in-memory for development

**Suggested Implementation:**
```python
import os
from typing import Optional
import redis

class RedisRateLimiter:
    """Redis-backed rate limiter for production use."""
    
    def __init__(self, redis_url: Optional[str] = None):
        self.redis_url = redis_url or os.getenv("REDIS_URL")
        self._client: Optional[redis.Redis] = None
    
    @property
    def client(self) -> redis.Redis:
        if self._client is None:
            self._client = redis.from_url(self.redis_url)
        return self._client
    
    def check_rate_limit(
        self,
        key: str,
        limit: int,
        window_seconds: int
    ) -> tuple[bool, int, int]:
        pipe = self.client.pipeline()
        now = int(time.time())
        window_key = f"ratelimit:{key}:{now // window_seconds}"
        
        pipe.incr(window_key)
        pipe.expire(window_key, window_seconds)
        results = pipe.execute()
        
        current_count = results[0]
        remaining = max(0, limit - current_count)
        
        if current_count > limit:
            return False, 0, window_seconds - (now % window_seconds)
        
        return True, remaining, window_seconds


# Factory function to get appropriate rate limiter
def get_rate_limiter():
    redis_url = os.getenv("REDIS_URL")
    if redis_url:
        return RedisRateLimiter(redis_url)
    return RateLimiter()  # Fall back to in-memory

rate_limiter = get_rate_limiter()
```

---

### 9. Store Original Verdict Alongside Normalized Verdict

**File:** `gcb-platform/backend/app/db/models/result.py`

**Problem:** Original tier-specific verdicts are lost after normalization.

**Action Items:**
- [ ] Add `original_verdict` column to Result model
- [ ] Create database migration
- [ ] Update executor to store both verdicts
- [ ] Update scoring service to use normalized verdict

**Migration:**
```python
def upgrade():
    op.add_column('results', sa.Column('original_verdict', sa.String(50), nullable=True))
    # Copy existing verdicts to original_verdict
    op.execute("UPDATE results SET original_verdict = verdict")
```

**Model Update:**
```python
class Result(Base):
    # ... existing fields ...
    original_verdict = Column(String(50))  # LOYAL, AFFIRMED, etc.
    verdict = Column(String(50), nullable=False, index=True)  # Normalized: ACCEPTED, COMPROMISED, REFUSED
```

---

## 🟢 Low Priority (Code Quality & Maintenance)

### 10. Fix Deprecated SQLAlchemy Import

**File:** `gcb-platform/backend/app/db/base.py` (line 4)

**Action Items:**
- [ ] Update import statement

**Fix:**
```python
# Change from:
from sqlalchemy.ext.declarative import declarative_base

# To:
from sqlalchemy.orm import declarative_base
```

---

### 11. Fix Bare Exception Handling

**File:** `gcb-platform/backend/app/api/v1/endpoints/tests.py` (lines 331-333)

**Action Items:**
- [ ] Catch specific exceptions
- [ ] Add logging for failures

**Fix:**
```python
try:
    scores = ScoringService.calculate_scores(db, str(test.id))
except ValueError as e:
    logger.warning(f"Failed to calculate scores for test {test.id}: {e}")
    scores = None
except Exception as e:
    logger.error(f"Unexpected error calculating scores for test {test.id}: {e}")
    scores = None
```

Also fix similar issues in:
- `gcb-platform/backend/app/api/v1/endpoints/moderator.py` (lines 69-72)
- `gcb-platform/backend/app/api/v1/endpoints/public.py` (lines 418-422)

---

### 12. Add Missing Database Index

**File:** `gcb-platform/backend/app/db/models/result.py`

**Action Items:**
- [ ] Add index on `question_id` column
- [ ] Create migration

**Model Update:**
```python
question_id = Column(UUID(as_uuid=True), ForeignKey("questions.id"), nullable=False, index=True)
```

**Migration:**
```python
def upgrade():
    op.create_index('ix_results_question_id', 'results', ['question_id'])
```

---

### 13. Extract Magic Numbers to Constants

**Files:**
- `gcb-platform/backend/app/api/v1/endpoints/tests.py` (lines 415-419)
- `gcb-platform/backend/app/api/v1/endpoints/moderator.py`

**Action Items:**
- [ ] Create constants file
- [ ] Replace magic numbers with named constants

**Create `gcb-platform/backend/app/core/constants.py`:**
```python
"""Application constants"""

# Scoring thresholds
SIGNIFICANT_IMPROVEMENT_THRESHOLD = 5.0  # Points
SIGNIFICANT_DECLINE_THRESHOLD = -5.0  # Points

# Validation thresholds
HIGH_ERROR_RATE_THRESHOLD = 0.10  # 10%
SUSPICIOUS_HIGH_SCORE = 99.0
SUSPICIOUS_LOW_SCORE = 5.0
SKEWED_VERDICT_THRESHOLD = 0.99  # 99%
TIER_DISCREPANCY_THRESHOLD = 50.0  # Points

# Rate limits
PUBLIC_RATE_LIMIT = 100  # requests per minute
AUTHENTICATED_RATE_LIMIT = 300  # requests per minute
RUNNER_RATE_LIMIT = 50  # requests per hour
SUBMISSIONS_RATE_LIMIT = 10  # requests per hour

# Moderation
REVIEWS_FOR_VALIDATED_STATUS = 3
```

---

### 14. Add Frontend Error Reporting

**Files:** Multiple frontend pages using `console.error`

**Action Items:**
- [ ] Create error reporting utility
- [ ] Replace `console.error` with proper error handling
- [ ] (Optional) Integrate Sentry or similar service

**Create `gcb-platform/frontend/lib/error-reporting.ts`:**
```typescript
type ErrorContext = {
  component?: string;
  action?: string;
  userId?: string;
  [key: string]: unknown;
};

export function reportError(error: Error | unknown, context?: ErrorContext): void {
  // Log to console in development
  if (process.env.NODE_ENV === 'development') {
    console.error('Error:', error, context);
  }
  
  // In production, send to error reporting service
  // TODO: Integrate Sentry or similar
  // if (typeof window !== 'undefined' && window.Sentry) {
  //   window.Sentry.captureException(error, { extra: context });
  // }
}

export function reportWarning(message: string, context?: ErrorContext): void {
  if (process.env.NODE_ENV === 'development') {
    console.warn('Warning:', message, context);
  }
}
```

---

## Progress Tracking

### Summary

| Priority | Total | Completed | Remaining |
|----------|-------|-----------|-----------|
| 🔴 High | 3 | 0 | 3 |
| 🟡 Medium | 6 | 0 | 6 |
| 🟢 Low | 5 | 0 | 5 |
| **Total** | **14** | **0** | **14** |

### Checklist

#### High Priority
- [ ] 1. Fix insecure JWT fallback
- [ ] 2. Remove hardcoded production URLs
- [ ] 3. Replace print statements with logging

#### Medium Priority
- [ ] 4. Fix TypeScript `any` types
- [ ] 5. Implement Auth0 token integration
- [ ] 6. Fix N+1 query issues
- [ ] 7. Address TODO comments (10 items)
- [ ] 8. Improve rate limiter with Redis
- [ ] 9. Store original verdict alongside normalized

#### Low Priority
- [ ] 10. Fix deprecated SQLAlchemy import
- [ ] 11. Fix bare exception handling
- [ ] 12. Add missing database index
- [ ] 13. Extract magic numbers to constants
- [ ] 14. Add frontend error reporting

---

## Notes

- All database changes require migrations - test locally before deploying
- Frontend changes should be tested with both authenticated and unauthenticated states
- Consider adding integration tests for critical fixes
- Rate limiter Redis implementation requires Redis to be provisioned in production environment

---

*Last updated: December 18, 2025*
