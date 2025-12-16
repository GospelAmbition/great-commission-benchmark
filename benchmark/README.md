# Great Commission Benchmark Documentation

This folder contains the specification and design documents for the Great Commission Benchmark—a benchmark test designed to evaluate Large Language Models (LLMs) on their ability to support the activities and use cases common to Great Commission Christians.

---

## The Vision

**[vision.md](./vision.md)** is the foundational vision document that defines:

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
| [vision.md](./vision.md) | **The foundational vision** — defines what we're building, why it matters, who it serves, and what we test |

### Implementation & Deployment Strategy

| Document | Purpose |
|----------|---------|
| [core-deployment-vision.md](./core-deployment-vision.md) | **Implementation strategy** — how we build and deploy the platform as a public resource |
| [core-technical-architecture.md](./core-technical-architecture.md) | Infrastructure decisions and technical stack |
| [core-build-requirements.md](./core-build-requirements.md) | Requirements analysis for building the platform |

### Testing & Methodology

| Document | Purpose |
|----------|---------|
| [decision-testing-methodology.md](./decision-testing-methodology.md) | How benchmark tests are designed and executed |

### Core Systems & Policies

Fundamental systems and policies that define how the benchmark operates:

| Document | Status | Description |
|----------|--------|-------------|
| [decision-publication-model.md](./decision-publication-model.md) | ✓ Draft | Progressive trust model for publishing results |
| [decision-versioning.md](./decision-versioning.md) | ✓ Draft | Benchmark version management |
| [decision-question-security.md](./decision-question-security.md) | ✓ Draft | Question distribution and contamination prevention |
| [decision-pricing-model.md](./decision-pricing-model.md) | ✓ Draft | Cost structure and sustainability |
| [decision-moderation-process.md](./decision-moderation-process.md) | ✓ Draft | Moderator selection and review workflows |
| [decision-testing-methodology.md](./decision-testing-methodology.md) | ✓ Draft | How benchmark tests are designed and executed |

### Operations & Success

| Document | Purpose |
|----------|---------|
| [decision-success-metrics.md](./decision-success-metrics.md) | KPIs and tracking for measuring success |
| [decision-legal-requirements.md](./decision-legal-requirements.md) | Terms of Service, accessibility, and compliance requirements |

---

## How to Use This Documentation

### For Understanding the Project

1. **Start with [vision.md](./vision.md)** — This is the primary vision document that defines what we're building and why
2. **Read [core-deployment-vision.md](./core-deployment-vision.md)** — Understand how the vision translates into a deployable platform
3. **Explore core documents** — Dive into specific systems and policies as needed

### For Building the Platform

1. **Reference [vision.md](./vision.md)** — Ensure all decisions align with the core vision
2. **Follow [core-deployment-vision.md](./core-deployment-vision.md)** — Use the deployment stages and roadmap as your guide
3. **Consult [core-technical-architecture.md](./core-technical-architecture.md)** — Technical decisions and infrastructure
4. **Check core documents** — Understand policies and systems before implementing features

### For Making Decisions

When making decisions:
- **Anchor to [vision.md](./vision.md)** — Does this decision serve Great Commission Christians?
- **Reference [core-deployment-vision.md](./core-deployment-vision.md)** — Does this fit the implementation strategy?
- **Document in appropriate core/feature files** — Maintain traceability
- **Link between documents** — Show how decisions connect to the vision

---

## Document Relationships

```
vision.md (Primary Vision)
    │
    ├──→ core-deployment-vision.md (Implementation Strategy)
    │       │
    │       ├──→ core-technical-architecture.md (Technical Decisions)
    │       ├──→ core-build-requirements.md (Requirements)
    │       └──→ decision-testing-methodology.md (How Tests Work)
    │
    ├──→ decision-publication-model.md (How Results Are Published)
    ├──→ decision-versioning.md (Question Set Management)
    ├──→ decision-question-security.md (Question Protection)
    ├──→ decision-pricing-model.md (Financial Model)
    ├──→ decision-moderation-process.md (Review Workflows)
    ├──→ decision-success-metrics.md (Measuring Success)
    └──→ decision-legal-requirements.md (Compliance)
```

---

## Contributing

When adding new documents:
- **Anchor to [vision.md](./vision.md)** — Ensure alignment with the core vision
- Use `core-` prefix for strategic/architectural decisions
- Use `decision-` prefix for fundamental policies/systems
- Use `feature-` prefix for specific user-facing functionality
- Update this README with the new document
- Link from related documents to maintain traceability

---

*"Go therefore and make disciples of all nations..."* — Matthew 28:19
