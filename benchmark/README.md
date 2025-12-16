# Great Commission Benchmark Documentation

This folder contains the specification and design documents for the Great Commission Benchmark—a benchmark test designed to evaluate Large Language Models (LLMs) on their ability to support the activities and use cases common to Great Commission Christians.

---

## The Vision

**[benchmark-vision.md](./benchmark-vision.md)** is the foundational vision document that defines:

- **What** we're building: A benchmark to evaluate LLMs for Great Commission Christians
- **Why** it matters: Current AI guardrails can impede legitimate religious activity
- **Who** it serves: Missionaries, evangelists, disciple-makers, and ministry workers
- **What** it tests: Six use case categories, theological minimums, and worldview adherence

**Start here.** Everything else flows from this vision.

---

## Document Structure

### Primary Vision Document

| Document | Purpose |
|----------|---------|
| [benchmark-vision.md](./benchmark-vision.md) | **The foundational vision** — defines what we're building, why it matters, who it serves, and what we test |

### Implementation & Deployment Strategy

| Document | Purpose |
|----------|---------|
| [platform-deployment-vision.md](./platform-deployment-vision.md) | **Implementation strategy** — how we build and deploy the platform as a public resource |
| [platform-technical-architecture.md](./platform-technical-architecture.md) | Infrastructure decisions and technical stack |
| [platform-build-requirements.md](./platform-build-requirements.md) | Requirements analysis for building the platform |

### Testing & Methodology

| Document | Purpose |
|----------|---------|
| [platform-testing-methodology.md](./platform-testing-methodology.md) | How benchmark tests are designed and executed |

### Core Systems & Policies

Fundamental systems and policies that define how the benchmark operates:

| Document | Status | Description |
|----------|--------|-------------|
| [process-publication-model.md](./process-publication-model.md) | ✓ Draft | Progressive trust model for publishing results |
| [platform-versioning.md](./platform-versioning.md) | ✓ Draft | Benchmark version management |
| [process-question-security.md](./process-question-security.md) | ✓ Draft | Question distribution and contamination prevention |
| [process-pricing-model.md](./process-pricing-model.md) | ✓ Draft | Cost structure and sustainability |
| [process-moderation-process.md](./process-moderation-process.md) | ✓ Draft | Moderator selection and review workflows |
| [platform-testing-methodology.md](./platform-testing-methodology.md) | ✓ Draft | How benchmark tests are designed and executed |

### Operations & Success

| Document | Purpose |
|----------|---------|
| [process-success-metrics.md](./process-success-metrics.md) | KPIs and tracking for measuring success |
| [process-legal-requirements.md](./process-legal-requirements.md) | Terms of Service, accessibility, and compliance requirements |

---

## How to Use This Documentation

### For Understanding the Project

1. **Start with [benchmark-vision.md](./benchmark-vision.md)** — This is the primary vision document that defines what we're building and why
2. **Read [platform-deployment-vision.md](./platform-deployment-vision.md)** — Understand how the vision translates into a deployable platform
3. **Explore platform documents** — Dive into specific systems and policies as needed

### For Building the Platform

1. **Reference [benchmark-vision.md](./benchmark-vision.md)** — Ensure all decisions align with the core vision
2. **Follow [platform-deployment-vision.md](./platform-deployment-vision.md)** — Use the deployment stages and roadmap as your guide
3. **Consult [platform-technical-architecture.md](./platform-technical-architecture.md)** — Technical decisions and infrastructure
4. **Check platform documents** — Understand policies and systems before implementing features

### For Making Decisions

When making decisions:
- **Anchor to [benchmark-vision.md](./benchmark-vision.md)** — Does this decision serve Great Commission Christians?
- **Reference [platform-deployment-vision.md](./platform-deployment-vision.md)** — Does this fit the implementation strategy?
- **Document in appropriate platform/feature files** — Maintain traceability
- **Link between documents** — Show how decisions connect to the vision

---

## Document Relationships

```
benchmark-vision.md (Primary Vision)
    │
    ├──→ platform-deployment-vision.md (Implementation Strategy)
    │       │
    │       ├──→ platform-technical-architecture.md (Technical Decisions)
    │       ├──→ platform-build-requirements.md (Requirements)
    │       └──→ platform-testing-methodology.md (How Tests Work)
    │
    ├──→ process-publication-model.md (How Results Are Published)
    ├──→ platform-versioning.md (Question Set Management)
    ├──→ process-question-security.md (Question Protection)
    ├──→ process-pricing-model.md (Financial Model)
    ├──→ process-moderation-process.md (Review Workflows)
    ├──→ process-success-metrics.md (Measuring Success)
    └──→ process-legal-requirements.md (Compliance)
```

---

## Contributing

When adding new documents:
- **Anchor to [benchmark-vision.md](./benchmark-vision.md)** — Ensure alignment with the core vision
- Use `platform-` prefix for strategic/architectural decisions
- Use `process-` prefix for fundamental policies/systems
- Use `feature-` prefix for specific user-facing functionality
- Update this README with the new document
- Link from related documents to maintain traceability

---

*"Go therefore and make disciples of all nations..."* — Matthew 28:19
