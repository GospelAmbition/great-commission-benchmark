# Benchmark Documentation

This folder contains the specification and design documents for the Great Commission Benchmark deployment.

---

## Document Structure

### Anchor Documents

| Document | Purpose |
|----------|---------|
| [deployment-vision.md](./deployment-vision.md) | Master vision document — overall strategy and architecture |
| [testing-methodology.md](./testing-methodology.md) | How benchmark tests are designed and executed |
| [deployment-vision-checklist.md](./deployment-vision-checklist.md) | Questions and gaps to resolve; tracks decision progress |

### Core Documents (`core-*.md`)

Fundamental systems and policies that define how the benchmark operates:

| Document | Status | Description |
|----------|--------|-------------|
| [core-publication-model.md](./core-publication-model.md) | ✓ Draft | Progressive trust model for publishing results |
| `core-question-security.md` | *Planned* | Question distribution and contamination prevention |
| `core-pricing-model.md` | *Planned* | Cost structure and sustainability |
| `core-versioning.md` | *Planned* | Benchmark version management |
| `core-data-retention.md` | *Planned* | What we store and why |

### Feature Documents (`feature-*.md`)

Specific features and their implementation details:

| Document | Status | Description |
|----------|--------|-------------|
| `feature-leaderboard.md` | *Planned* | Leaderboard display, filtering, comparison |
| `feature-reviewer-dashboard.md` | *Planned* | Tools for human reviewers |
| `feature-user-notifications.md` | *Planned* | Email and in-app notifications |
| `feature-moderation-workflow.md` | *Planned* | Submission review process |
| `feature-retesting.md` | *Planned* | Model retest triggers and flow |

---

## How to Use This Folder

1. **Start with [deployment-vision.md](./deployment-vision.md)** for the big picture
2. **Check [deployment-vision-checklist.md](./deployment-vision-checklist.md)** for open questions
3. **Dive into `core-*.md` and `feature-*.md`** for detailed designs

When making decisions:
- Document answers in the appropriate `core-` or `feature-` file
- Check off resolved questions in the checklist
- Link between documents to maintain traceability

---

## Contributing

When adding new documents:
- Use `core-` prefix for fundamental policies/systems
- Use `feature-` prefix for specific user-facing functionality
- Update this README with the new document
- Link from the checklist if it resolves an open question

