# Great Commission Benchmark — Testing Strategies

This document defines the testing strategies, standards, and practices for the Great Commission Benchmark platform and CLI Runner.

**Last Updated:** December 17, 2025

---

## Table of Contents

1. [Testing Philosophy](#testing-philosophy)
2. [Test Categories](#test-categories)
3. [Platform Testing](#platform-testing)
4. [CLI Runner Testing](#cli-runner-testing)
5. [Integration Testing](#integration-testing)
6. [End-to-End Testing](#end-to-end-testing)
7. [Performance Testing](#performance-testing)
8. [Accessibility Testing](#accessibility-testing)
9. [Test Data Management](#test-data-management)
10. [Continuous Integration](#continuous-integration)
11. [Testing Checklist](#testing-checklist)

---

## Testing Philosophy

### Guiding Principles

| Principle | Description |
|-----------|-------------|
| **Test What Matters** | Focus on critical paths and business logic, not implementation details |
| **Fast Feedback** | Tests should run quickly to support rapid development |
| **Reliability** | Tests should be deterministic—no flaky tests |
| **Maintainability** | Tests should be easy to understand and update |
| **Independence** | Tests should not depend on each other |

### Test Pyramid

```
        ╱╲
       ╱  ╲      E2E Tests (few, slow, high value)
      ╱────╲
     ╱      ╲    Integration Tests (moderate)
    ╱────────╲
   ╱          ╲  Unit Tests (many, fast)
  ╱────────────╲
```

| Layer | Quantity | Speed | Scope |
|-------|----------|-------|-------|
| **Unit** | Many | Fast | Single function/component |
| **Integration** | Moderate | Medium | Multiple components/services |
| **E2E** | Few | Slow | Full user flows |

### Coverage Goals

| Component | Target Coverage | Priority Areas |
|-----------|-----------------|----------------|
| **Backend API** | 80%+ | Auth, payments, test execution |
| **Frontend Components** | 70%+ | Forms, data display, auth flows |
| **CLI Runner** | 80%+ | Test execution, result storage |

---

## Test Categories

### By Speed

| Category | Timeout | When to Run |
|----------|---------|-------------|
| **Fast** | < 100ms | Every save (watch mode) |
| **Medium** | < 5s | Pre-commit |
| **Slow** | < 60s | CI only |
| **Very Slow** | > 60s | Nightly/manual only |

### By Type

| Type | Description | Tools |
|------|-------------|-------|
| **Unit** | Test isolated functions/components | pytest, Jest, React Testing Library |
| **Integration** | Test service interactions | pytest, Supertest |
| **E2E** | Test full user flows | Playwright |
| **Visual Regression** | Detect UI changes | Playwright screenshots |
| **Performance** | Load and stress testing | k6, Locust |
| **Accessibility** | WCAG compliance | axe-core, Lighthouse |

---

## Platform Testing

### Backend (FastAPI)

#### Unit Tests

Location: `gcb-platform/backend/tests/unit/`

```python
# Example: Test scoring calculation
import pytest
from app.services.scoring import calculate_weighted_score

def test_weighted_score_calculation():
    """Test the 70/20/10 weighting formula."""
    result = calculate_weighted_score(
        tier1_score=80,  # Task
        tier2_score=75,  # Doctrine
        tier3_score=70,  # Worldview
    )
    # (80 * 0.70) + (75 * 0.20) + (70 * 0.10) = 56 + 15 + 7 = 78
    assert result == 78

def test_weighted_score_with_zero_tier():
    """Test handling of zero scores."""
    result = calculate_weighted_score(
        tier1_score=0,
        tier2_score=100,
        tier3_score=100,
    )
    # (0 * 0.70) + (100 * 0.20) + (100 * 0.10) = 0 + 20 + 10 = 30
    assert result == 30
```

#### API Tests

Location: `gcb-platform/backend/tests/api/`

```python
# Example: Test leaderboard endpoint
import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    return TestClient(app)

def test_get_leaderboard(client, seed_test_data):
    """Test leaderboard returns sorted results."""
    response = client.get("/api/leaderboard")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "results" in data
    assert len(data["results"]) > 0
    # Verify sorted by score descending
    scores = [r["score"] for r in data["results"]]
    assert scores == sorted(scores, reverse=True)

def test_leaderboard_requires_no_auth(client):
    """Public endpoint should not require authentication."""
    response = client.get("/api/leaderboard")
    assert response.status_code == 200  # Not 401
```

#### Database Tests

Location: `gcb-platform/backend/tests/db/`

```python
# Example: Test repository patterns
import pytest
from sqlalchemy.orm import Session
from app.repositories.test_runs import TestRunRepository

@pytest.fixture
def repo(db_session: Session):
    return TestRunRepository(db_session)

def test_create_test_run(repo, sample_user, sample_model):
    """Test creating a new test run."""
    test_run = repo.create(
        user_id=sample_user.id,
        model_id=sample_model.id,
        question_set_id=1,
    )
    
    assert test_run.id is not None
    assert test_run.status == "pending"
    assert test_run.user_id == sample_user.id

def test_get_user_test_runs(repo, sample_user):
    """Test retrieving test runs for a user."""
    runs = repo.get_by_user(sample_user.id)
    
    assert isinstance(runs, list)
    for run in runs:
        assert run.user_id == sample_user.id
```

#### Running Backend Tests

```bash
cd gcb-platform/backend
source venv/bin/activate

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific category
pytest tests/unit/
pytest tests/api/
pytest tests/db/

# Run specific test file
pytest tests/api/test_leaderboard.py

# Run with verbose output
pytest -v

# Run tests matching pattern
pytest -k "test_score"

# Run in parallel
pytest -n auto
```

### Frontend (Next.js)

#### Component Tests

Location: `gcb-platform/frontend/__tests__/components/`

```typescript
// Example: Test leaderboard table component
import { render, screen } from '@testing-library/react';
import { LeaderboardTable } from '@/components/LeaderboardTable';

const mockData = [
  { rank: 1, model: 'Claude 3.5', score: 81, trustTier: 'validated' },
  { rank: 2, model: 'GPT-4o', score: 76, trustTier: 'reviewed' },
];

describe('LeaderboardTable', () => {
  it('renders all models', () => {
    render(<LeaderboardTable data={mockData} />);
    
    expect(screen.getByText('Claude 3.5')).toBeInTheDocument();
    expect(screen.getByText('GPT-4o')).toBeInTheDocument();
  });

  it('displays scores correctly', () => {
    render(<LeaderboardTable data={mockData} />);
    
    expect(screen.getByText('81')).toBeInTheDocument();
    expect(screen.getByText('76')).toBeInTheDocument();
  });

  it('shows trust tier badges', () => {
    render(<LeaderboardTable data={mockData} />);
    
    expect(screen.getByText('validated')).toBeInTheDocument();
    expect(screen.getByText('reviewed')).toBeInTheDocument();
  });
});
```

#### Hook Tests

Location: `gcb-platform/frontend/__tests__/hooks/`

```typescript
// Example: Test leaderboard data hook
import { renderHook, waitFor } from '@testing-library/react';
import { useLeaderboard } from '@/hooks/useLeaderboard';
import { QueryClientProvider, QueryClient } from '@tanstack/react-query';

const wrapper = ({ children }) => (
  <QueryClientProvider client={new QueryClient()}>
    {children}
  </QueryClientProvider>
);

describe('useLeaderboard', () => {
  it('fetches leaderboard data', async () => {
    const { result } = renderHook(() => useLeaderboard('2.0'), { wrapper });
    
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    
    expect(result.current.data).toBeDefined();
    expect(result.current.data.results).toBeInstanceOf(Array);
  });

  it('handles loading state', () => {
    const { result } = renderHook(() => useLeaderboard('2.0'), { wrapper });
    
    expect(result.current.isLoading).toBe(true);
  });
});
```

#### Running Frontend Tests

```bash
cd gcb-platform/frontend

# Run all tests
pnpm test

# Run in watch mode
pnpm test:watch

# Run with coverage
pnpm test:coverage

# Run specific test file
pnpm test LeaderboardTable.test.tsx

# Update snapshots
pnpm test -u
```

---

## CLI Runner Testing

### Unit Tests

Location: `cli/runner/tests/unit/`

```python
# Example: Test score calculation
import pytest
from gcb_runner.scoring import calculate_tier_score, calculate_overall_score

def test_tier_score_all_pass():
    """Test perfect score calculation."""
    results = [
        {"verdict": "ACCEPTED"},
        {"verdict": "ACCEPTED"},
        {"verdict": "ACCEPTED"},
    ]
    score = calculate_tier_score(results, passing_verdict="ACCEPTED")
    assert score == 100.0

def test_tier_score_mixed():
    """Test mixed results score."""
    results = [
        {"verdict": "ACCEPTED"},
        {"verdict": "REFUSED"},
        {"verdict": "ACCEPTED"},
        {"verdict": "COMPROMISED"},
    ]
    score = calculate_tier_score(results, passing_verdict="ACCEPTED")
    assert score == 50.0  # 2 out of 4

def test_overall_score_weighted():
    """Test weighted overall score."""
    score = calculate_overall_score(
        tier1_score=80,
        tier2_score=70,
        tier3_score=60,
    )
    # (80 * 0.70) + (70 * 0.20) + (60 * 0.10) = 56 + 14 + 6 = 76
    assert score == 76
```

### Backend Adapter Tests

Location: `cli/runner/tests/backends/`

```python
# Example: Test OpenRouter adapter
import pytest
from unittest.mock import AsyncMock, patch
from gcb_runner.backends.openrouter import OpenRouterBackend

@pytest.fixture
def backend():
    return OpenRouterBackend(api_key="test-key")

@pytest.mark.asyncio
async def test_complete_success(backend):
    """Test successful completion."""
    mock_response = {
        "choices": [{"message": {"content": "Test response"}}]
    }
    
    with patch.object(backend, "_make_request", return_value=mock_response):
        result = await backend.complete(
            messages=[{"role": "user", "content": "Hello"}],
            model="gpt-4o",
        )
    
    assert result == "Test response"

@pytest.mark.asyncio
async def test_complete_with_system_prompt(backend):
    """Test completion with system prompt."""
    mock_response = {
        "choices": [{"message": {"content": "Helpful response"}}]
    }
    
    with patch.object(backend, "_make_request", return_value=mock_response) as mock:
        await backend.complete(
            messages=[{"role": "user", "content": "Hello"}],
            model="gpt-4o",
            system_prompt="You are a helpful assistant.",
        )
    
    # Verify system prompt was prepended
    call_args = mock.call_args
    messages = call_args[1]["messages"]
    assert messages[0]["role"] == "system"
    assert messages[0]["content"] == "You are a helpful assistant."
```

### Results Storage Tests

Location: `cli/runner/tests/storage/`

```python
# Example: Test results database
import pytest
from gcb_runner.results import ResultsDatabase

@pytest.fixture
def db(tmp_path):
    db_path = tmp_path / "test_results.db"
    return ResultsDatabase(str(db_path))

def test_save_and_retrieve_results(db):
    """Test saving and retrieving test results."""
    results = {
        "model": "gpt-4o",
        "version": "2.0",
        "overall_score": 78,
        "tier1_score": 80,
        "tier2_score": 75,
        "tier3_score": 70,
    }
    
    run_id = db.save_results(results)
    retrieved = db.get_results(run_id)
    
    assert retrieved["model"] == "gpt-4o"
    assert retrieved["overall_score"] == 78

def test_list_results(db):
    """Test listing all results."""
    db.save_results({"model": "model-a", "version": "2.0", "overall_score": 80})
    db.save_results({"model": "model-b", "version": "2.0", "overall_score": 75})
    
    all_results = db.list_results()
    
    assert len(all_results) == 2
```

### Running Runner Tests

```bash
cd cli/runner
source venv/bin/activate

# Run all tests
pytest

# Run with coverage
pytest --cov=gcb_runner --cov-report=html

# Run async tests
pytest -v tests/backends/

# Run with markers
pytest -m "not slow"  # Skip slow tests
```

---

## Integration Testing

### API Integration Tests

Location: `gcb-platform/backend/tests/integration/`

```python
# Example: Test full test execution flow
import pytest
from fastapi.testclient import TestClient

@pytest.mark.integration
def test_test_execution_flow(
    client: TestClient,
    authenticated_user,
    mock_openrouter,
):
    """Test complete test execution from initiation to completion."""
    # 1. Get price estimate
    response = client.post(
        "/api/tests/estimate",
        json={"model_id": "gpt-4o"},
        headers=authenticated_user.headers,
    )
    assert response.status_code == 200
    estimate = response.json()
    
    # 2. Create test (mock payment)
    response = client.post(
        "/api/tests/create",
        json={
            "model_id": "gpt-4o",
            "payment_intent_id": "pi_test_123",
        },
        headers=authenticated_user.headers,
    )
    assert response.status_code == 201
    test_run = response.json()
    
    # 3. Check status (should be running or completed)
    response = client.get(
        f"/api/tests/{test_run['id']}/status",
        headers=authenticated_user.headers,
    )
    assert response.status_code == 200
    assert response.json()["status"] in ["running", "completed"]
```

### Cross-Service Integration

Location: `tests/integration/`

```python
# Example: Test CLI to Platform submission flow
import pytest
import subprocess
import requests

@pytest.mark.integration
@pytest.mark.slow
def test_cli_submission_to_platform(
    running_platform,
    test_user_token,
):
    """Test CLI result submission to platform."""
    # 1. Run CLI test (mocked LLM)
    result = subprocess.run(
        ["gcb-runner", "test", "--model", "test-model", "--mock"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    
    # 2. Export results
    result = subprocess.run(
        ["gcb-runner", "export", "--latest", "--format", "json"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    results_json = result.stdout
    
    # 3. Submit to platform
    response = requests.post(
        f"{running_platform}/api/community/submit",
        json={
            "model_name": "Test Model",
            "results_package": results_json,
        },
        headers={"Authorization": f"Bearer {test_user_token}"},
    )
    assert response.status_code == 201
```

---

## End-to-End Testing

### Playwright Setup

Location: `gcb-platform/e2e/`

```typescript
// playwright.config.ts
import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
  },
  projects: [
    { name: 'chromium', use: { browserName: 'chromium' } },
    { name: 'firefox', use: { browserName: 'firefox' } },
    { name: 'webkit', use: { browserName: 'webkit' } },
  ],
});
```

### E2E Test Examples

Location: `gcb-platform/e2e/tests/`

```typescript
// Example: Test leaderboard viewing
import { test, expect } from '@playwright/test';

test.describe('Leaderboard', () => {
  test('displays model rankings', async ({ page }) => {
    await page.goto('/');
    
    // Verify leaderboard is visible
    await expect(page.getByRole('heading', { name: /leaderboard/i })).toBeVisible();
    
    // Verify models are displayed
    const rows = page.getByRole('row');
    await expect(rows).toHaveCount({ greaterThan: 1 });
    
    // Verify scores are visible
    await expect(page.getByText(/\/100/)).toBeVisible();
  });

  test('allows filtering by category', async ({ page }) => {
    await page.goto('/');
    
    // Open filter dropdown
    await page.getByRole('button', { name: /filter/i }).click();
    
    // Select a category
    await page.getByRole('option', { name: /Missiological Research/i }).click();
    
    // Verify filter applied
    await expect(page.getByText(/Missiological Research/i)).toBeVisible();
  });
});

// Example: Test authentication flow
test.describe('Authentication', () => {
  test('user can sign in', async ({ page }) => {
    await page.goto('/');
    
    // Click sign in
    await page.getByRole('button', { name: /sign in/i }).click();
    
    // Fill credentials (Auth0 test user)
    await page.fill('input[name="email"]', 'test@example.com');
    await page.fill('input[name="password"]', 'TestPassword123!');
    await page.getByRole('button', { name: /continue/i }).click();
    
    // Verify signed in
    await expect(page.getByText(/Dashboard/i)).toBeVisible();
  });
});
```

### Running E2E Tests

```bash
cd gcb-platform/e2e

# Install Playwright browsers
npx playwright install

# Run all tests
npx playwright test

# Run specific test
npx playwright test leaderboard.spec.ts

# Run in headed mode
npx playwright test --headed

# Debug mode
npx playwright test --debug

# View report
npx playwright show-report
```

---

## Performance Testing

### Load Testing with k6

Location: `tests/performance/`

```javascript
// k6/leaderboard-load.js
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '30s', target: 20 },  // Ramp up
    { duration: '1m', target: 20 },   // Stay at 20 users
    { duration: '30s', target: 0 },   // Ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'],  // 95% of requests under 500ms
    http_req_failed: ['rate<0.01'],    // Less than 1% failures
  },
};

export default function () {
  const res = http.get('http://localhost:3000/api/leaderboard');
  
  check(res, {
    'status is 200': (r) => r.status === 200,
    'response time < 500ms': (r) => r.timings.duration < 500,
  });
  
  sleep(1);
}
```

### Running Performance Tests

```bash
# Run load test
k6 run tests/performance/k6/leaderboard-load.js

# Run with cloud reporting
K6_CLOUD_TOKEN=xxx k6 cloud tests/performance/k6/leaderboard-load.js
```

---

## Accessibility Testing

### Automated Testing

```typescript
// Example: axe-core integration
import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

test.describe('Accessibility', () => {
  test('leaderboard page meets WCAG A', async ({ page }) => {
    await page.goto('/');
    
    const results = await new AxeBuilder({ page })
      .withTags(['wcag2a'])
      .analyze();
    
    expect(results.violations).toEqual([]);
  });

  test('login form is accessible', async ({ page }) => {
    await page.goto('/login');
    
    const results = await new AxeBuilder({ page })
      .include('#login-form')
      .analyze();
    
    expect(results.violations).toEqual([]);
  });
});
```

### Manual Testing Checklist

| Test | Method |
|------|--------|
| **Keyboard Navigation** | Tab through all interactive elements |
| **Screen Reader** | Test with VoiceOver/NVDA |
| **Color Contrast** | Verify with browser dev tools |
| **Focus Indicators** | Visible focus on all interactive elements |
| **Form Labels** | All inputs have associated labels |
| **Alt Text** | All images have descriptive alt text |

---

## Test Data Management

### Fixtures

```python
# pytest fixtures for test data
import pytest
from app.models import User, Model, TestRun

@pytest.fixture
def sample_user(db_session):
    """Create a test user."""
    user = User(
        auth0_id="auth0|test123",
        email="test@example.com",
        name="Test User",
        role="user",
    )
    db_session.add(user)
    db_session.commit()
    return user

@pytest.fixture
def sample_model(db_session):
    """Create a test model."""
    model = Model(
        model_id="gpt-4o-test",
        name="GPT-4o Test",
        provider="OpenAI",
        is_active=True,
    )
    db_session.add(model)
    db_session.commit()
    return model

@pytest.fixture
def seed_leaderboard_data(db_session, sample_user):
    """Seed data for leaderboard tests."""
    models = [
        {"model_id": "model-a", "name": "Model A", "provider": "Provider A"},
        {"model_id": "model-b", "name": "Model B", "provider": "Provider B"},
    ]
    # ... create test runs with results
```

### Test Database

```python
# conftest.py - Database setup
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

@pytest.fixture(scope="session")
def engine():
    """Create test database engine."""
    return create_engine("sqlite:///:memory:")

@pytest.fixture(scope="function")
def db_session(engine):
    """Create fresh database session for each test."""
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
    Base.metadata.drop_all(engine)
```

---

## Continuous Integration

### GitHub Actions Workflow

```yaml
# .github/workflows/test.yml
name: Tests

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          cd gcb-platform/backend
          pip install -e ".[dev]"
      - name: Run tests
        run: |
          cd gcb-platform/backend
          pytest --cov=app --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v3

  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
      - uses: pnpm/action-setup@v2
        with:
          version: 8
      - name: Install dependencies
        run: |
          cd gcb-platform/frontend
          pnpm install
      - name: Run tests
        run: |
          cd gcb-platform/frontend
          pnpm test:ci

  e2e-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
      - name: Install Playwright
        run: npx playwright install --with-deps
      - name: Run E2E tests
        run: |
          cd gcb-platform/e2e
          npx playwright test
      - uses: actions/upload-artifact@v3
        if: failure()
        with:
          name: playwright-report
          path: gcb-platform/e2e/playwright-report/
```

---

## Testing Checklist

### Before Committing

- [ ] All unit tests pass
- [ ] New code has test coverage
- [ ] No console.log or debug statements
- [ ] Type checking passes

### Before PR

- [ ] All CI checks pass
- [ ] Integration tests pass locally
- [ ] Documentation updated if needed

### Before Release

- [ ] Full E2E test suite passes
- [ ] Performance tests show no regression
- [ ] Accessibility audit passes
- [ ] Security scan shows no new issues

---

## Related Documents

- [Local Development Setup](./Local-Development-Setup.md) — Environment setup
- [Contribution Guidelines](./Contribution-Guidelines.md) — How to contribute
- [Deployment Procedures](./Deployment-Procedures.md) — Deployment workflow
- [Security Practices](./Security-Practices.md) — Security testing

---

*This document should be updated as testing strategies evolve. Last review: December 2025.*
