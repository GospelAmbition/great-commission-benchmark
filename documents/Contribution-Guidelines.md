# Great Commission Benchmark — Contribution Guidelines

This document outlines how to contribute to the Great Commission Benchmark project, including code standards, pull request processes, and community expectations.

**Last Updated:** December 17, 2025

---

## Table of Contents

1. [Welcome Contributors](#welcome-contributors)
2. [Ways to Contribute](#ways-to-contribute)
3. [Getting Started](#getting-started)
4. [Development Workflow](#development-workflow)
5. [Code Standards](#code-standards)
6. [Pull Request Process](#pull-request-process)
7. [Code Review Guidelines](#code-review-guidelines)
8. [Issue Guidelines](#issue-guidelines)
9. [Community Standards](#community-standards)
10. [Recognition](#recognition)

---

## Welcome Contributors

Thank you for your interest in contributing to the Great Commission Benchmark! This project exists to serve missionaries, ministry leaders, and Great Commission workers worldwide by providing trustworthy AI evaluations.

### Our Mission

We're building tools that help Christian organizations make informed decisions about AI technologies. Every contribution—whether code, documentation, testing, or feedback—helps advance this mission.

### Who Can Contribute

| Contributor Type | Typical Contributions |
|------------------|----------------------|
| **Developers** | Code, bug fixes, new features, tests |
| **Technical Writers** | Documentation, guides, translations |
| **Testers** | Bug reports, test case creation, QA |
| **Domain Experts** | Theological review, ministry context, use cases |
| **Community Members** | Feedback, discussions, evangelism |

---

## Ways to Contribute

### Code Contributions

| Area | Description | Difficulty |
|------|-------------|------------|
| **Bug Fixes** | Fix reported issues | Beginner-friendly |
| **Documentation** | Improve code comments, READMEs | Beginner-friendly |
| **Tests** | Add test coverage | Intermediate |
| **Features** | Implement new functionality | Intermediate-Advanced |
| **Architecture** | Design improvements, refactoring | Advanced |

### Non-Code Contributions

| Area | Description |
|------|-------------|
| **Bug Reports** | Report issues with clear reproduction steps |
| **Feature Requests** | Suggest improvements with use cases |
| **Documentation Review** | Identify unclear or outdated docs |
| **Translation** | Help translate for multilingual support |
| **Accessibility Testing** | Verify WCAG compliance |

---

## Getting Started

### 1. Set Up Your Environment

Follow the [Local Development Setup](./Local-Development-Setup.md) guide to configure your development environment.

### 2. Find an Issue to Work On

| Label | Meaning |
|-------|---------|
| `good first issue` | Suitable for new contributors |
| `help wanted` | We're actively seeking contributions |
| `bug` | Something isn't working |
| `enhancement` | New feature or improvement |
| `documentation` | Documentation improvements |

### 3. Claim the Issue

Comment on the issue to let others know you're working on it:

```
I'd like to work on this issue. I plan to [brief approach description].
```

### 4. Create a Branch

```bash
# Sync with main
git checkout main
git pull origin main

# Create feature branch
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

### Branch Naming Conventions

| Prefix | Usage | Example |
|--------|-------|---------|
| `feature/` | New features | `feature/leaderboard-filtering` |
| `fix/` | Bug fixes | `fix/payment-webhook-timeout` |
| `docs/` | Documentation | `docs/api-endpoint-guide` |
| `refactor/` | Code refactoring | `refactor/database-queries` |
| `test/` | Test additions | `test/runner-cli-coverage` |

---

## Development Workflow

### Commit Guidelines

We follow [Conventional Commits](https://www.conventionalcommits.org/) for clear commit history.

**Format:**
```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

**Types:**

| Type | Description |
|------|-------------|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation only |
| `style` | Formatting, no code change |
| `refactor` | Code change that neither fixes nor adds |
| `test` | Adding or updating tests |
| `chore` | Maintenance tasks |

**Examples:**

```bash
# Feature
git commit -m "feat(leaderboard): add category filtering"

# Bug fix
git commit -m "fix(payment): handle Stripe webhook timeout"

# Documentation
git commit -m "docs(api): add authentication examples"

# Refactor
git commit -m "refactor(runner): simplify backend adapter interface"
```

### Keep Commits Atomic

- Each commit should represent one logical change
- If you can describe your commit with "and", it should be multiple commits
- Commits should pass tests independently

### Sync Regularly

```bash
# Keep your branch up to date
git fetch origin
git rebase origin/main

# Resolve conflicts if any, then continue
git rebase --continue
```

---

## Code Standards

### Python (Backend, CLI Tools)

**Style Guide:** PEP 8 with the following tools:

| Tool | Purpose | Config |
|------|---------|--------|
| **Black** | Code formatting | `pyproject.toml` |
| **Ruff** | Linting | `pyproject.toml` |
| **mypy** | Type checking | `pyproject.toml` |

**Run checks:**
```bash
# Format code
black .

# Lint
ruff check .

# Type check
mypy .
```

**Type Hints:**
- All function signatures should have type hints
- Use `from __future__ import annotations` for modern syntax
- Pydantic models for data validation

```python
from __future__ import annotations

def calculate_score(
    tier1_results: list[VerdictResult],
    tier2_results: list[VerdictResult],
    tier3_results: list[VerdictResult],
) -> BenchmarkScore:
    """Calculate weighted benchmark score from tier results."""
    ...
```

### TypeScript/JavaScript (Frontend)

**Style Guide:** ESLint + Prettier with project configuration

| Tool | Purpose | Config |
|------|---------|--------|
| **ESLint** | Linting | `eslint.config.js` |
| **Prettier** | Formatting | `.prettierrc` |
| **TypeScript** | Type checking | `tsconfig.json` |

**Run checks:**
```bash
# Lint and fix
pnpm lint --fix

# Type check
pnpm typecheck

# Format
pnpm format
```

**Component Guidelines:**
- Use functional components with hooks
- Use TypeScript for all new code
- Follow React best practices (no direct DOM manipulation)
- Use shadcn/ui components where applicable

```typescript
interface LeaderboardProps {
  version: string;
  filters?: FilterOptions;
}

export function Leaderboard({ version, filters }: LeaderboardProps) {
  const { data, isLoading } = useLeaderboard(version, filters);
  
  if (isLoading) return <LeaderboardSkeleton />;
  
  return (
    <Table>
      {/* ... */}
    </Table>
  );
}
```

### SQL/Database

- Use Alembic migrations for all schema changes
- Never write raw SQL with user input (use ORM parameterization)
- Add indexes for frequently queried columns
- Include `created_at` and `updated_at` on all tables

### Documentation

- Update relevant documentation with code changes
- Use clear, concise language
- Include examples where helpful
- Follow existing document structure

---

## Pull Request Process

### 1. Before Submitting

**Checklist:**
- [ ] Code follows project style guidelines
- [ ] All tests pass locally (`pytest` / `pnpm test`)
- [ ] New functionality has tests
- [ ] Documentation updated if needed
- [ ] No console.log or debug statements
- [ ] No secrets or credentials in code

### 2. Create the PR

**PR Title:** Use conventional commit format
```
feat(leaderboard): add model comparison feature
```

**PR Description Template:**

```markdown
## Summary
Brief description of what this PR does.

## Changes
- Change 1
- Change 2
- Change 3

## Testing
- How you tested this
- Relevant test commands

## Screenshots (if applicable)
[Add screenshots for UI changes]

## Related Issues
Closes #123
```

### 3. PR Requirements

| Requirement | Description |
|-------------|-------------|
| **Tests Pass** | All CI checks must pass |
| **Review Approval** | At least one maintainer approval |
| **No Conflicts** | Must be mergeable with main |
| **Linked Issue** | Reference the issue being addressed |

### 4. Address Review Feedback

- Respond to all comments (even with "acknowledged")
- Push additional commits for changes
- Request re-review when ready

### 5. Merge

Once approved and all checks pass:
- Maintainer will merge using "Squash and merge"
- Branch will be deleted automatically

---

## Code Review Guidelines

### For Reviewers

**Review Checklist:**
- [ ] Code solves the stated problem
- [ ] Tests are adequate
- [ ] Code follows project standards
- [ ] No security issues
- [ ] No performance concerns
- [ ] Documentation is updated

**Review Etiquette:**
- Be constructive and specific
- Explain the "why" behind suggestions
- Distinguish between blocking issues and suggestions
- Acknowledge good work

**Comment Prefixes:**
| Prefix | Meaning |
|--------|---------|
| `nit:` | Minor suggestion, not blocking |
| `question:` | Need clarification |
| `suggestion:` | Consider this approach |
| `blocking:` | Must be addressed before merge |

### For Authors

- Be open to feedback
- Ask for clarification if needed
- Don't take comments personally
- Explain your reasoning when disagreeing

---

## Issue Guidelines

### Bug Reports

**Required Information:**

```markdown
## Description
Clear description of the bug.

## Steps to Reproduce
1. Go to '...'
2. Click on '...'
3. See error

## Expected Behavior
What should happen.

## Actual Behavior
What actually happens.

## Environment
- OS: [e.g., macOS 14.0]
- Browser: [e.g., Chrome 120]
- Version: [e.g., 1.2.0]

## Additional Context
Screenshots, logs, etc.
```

### Feature Requests

**Required Information:**

```markdown
## Problem
Describe the problem or need.

## Proposed Solution
How you think it should work.

## Use Case
Who benefits and how.

## Alternatives Considered
Other approaches you thought about.

## Additional Context
Mockups, examples, etc.
```

---

## Community Standards

### Code of Conduct

We are committed to providing a welcoming and inclusive environment. All contributors are expected to:

- **Be Respectful:** Treat everyone with dignity and respect
- **Be Constructive:** Offer helpful feedback and accept criticism gracefully
- **Be Collaborative:** Work together towards our shared mission
- **Be Patient:** Remember that contributors have varying experience levels

### Communication Channels

| Channel | Purpose |
|---------|---------|
| **GitHub Issues** | Bug reports, feature requests |
| **GitHub Discussions** | General questions, ideas |
| **Discord** | Real-time chat, community |
| **Email** | Private matters, security issues |

### Response Times

| Request Type | Expected Response |
|--------------|-------------------|
| **Security Issues** | Within 24 hours |
| **Bug Reports** | Within 1 week |
| **Feature Requests** | Within 2 weeks |
| **PRs** | Within 1 week |

---

## Recognition

### Contributor Recognition

Contributors are recognized in several ways:

| Recognition | Criteria |
|-------------|----------|
| **Contributors List** | All merged PRs |
| **Release Notes** | Significant contributions mentioned |
| **Special Thanks** | Outstanding contributions |

### Becoming a Maintainer

Active contributors may be invited to become maintainers. Criteria include:

- Consistent, quality contributions over time
- Helpful code reviews and community engagement
- Understanding of project goals and standards
- Demonstrated good judgment

---

## Quick Reference

### Commands Cheat Sheet

```bash
# Setup
git clone [repo-url]
cd great-commission-benchmark
# Follow Local-Development-Setup.md

# Branch
git checkout -b feature/my-feature

# Commit
git add .
git commit -m "feat(scope): description"

# Push
git push -u origin feature/my-feature

# Sync with main
git fetch origin
git rebase origin/main

# Run tests
pytest                    # Python
pnpm test                 # Frontend

# Code quality
black . && ruff check .   # Python
pnpm lint && pnpm format  # Frontend
```

### Important Files

| File | Purpose |
|------|---------|
| `CONTRIBUTING.md` | Points to this document |
| `CODE_OF_CONDUCT.md` | Community standards |
| `SECURITY.md` | Security reporting process |
| `LICENSE` | Project license |

---

## Related Documents

- [Local Development Setup](./Local-Development-Setup.md) — Environment setup
- [Testing Strategies](./Testing-Strategies.md) — Testing approaches
- [Deployment Procedures](./Deployment-Procedures.md) — Deployment workflow
- [Security Practices](./Security-Practices.md) — Security guidelines

---

*Thank you for contributing to the Great Commission Benchmark! Your work helps equip ministry workers around the world.*
