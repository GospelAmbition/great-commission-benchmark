# Great Commission Benchmark

A benchmark test designed to evaluate Large Language Models (LLMs) on their ability to support the activities and use cases common to **Great Commission Christians**—missionaries, evangelists, disciple-makers, and others who actively respond to Jesus' command to make disciples.

---

## The Problem

Current AI systems often have guardrails designed to restrict:
- Religious content deemed "coercive"
- Proselytizing activities
- Exclusive truth claims
- Content that challenges other worldviews

These guardrails, while well-intentioned for certain contexts, can significantly impede legitimate religious activity that is protected speech in most democracies and central to the identity and practice of billions of Christians worldwide.

**The benchmark aims to measure how well LLMs can assist Great Commission Christians in their legitimate religious activities without undue restriction.**

---

## What We Test

The benchmark evaluates LLMs across three tiers:

| Tier | Focus | Weight |
|------|-------|--------|
| **Tier 1: Task Capability** | Can the LLM complete practical ministry tasks? | **70%** |
| **Tier 2: Doctrinal Fidelity** | Does it preserve theological accuracy? | **20%** |
| **Tier 3: Worldview Confession** | Can it affirm core Christian truths? | **10%** |

The weighting prioritizes practical utility—users primarily need to know: *"Can I use this LLM for my ministry work?"*

---

## Documentation

All project documentation is in the [`benchmark/`](./benchmark/) folder:

### Start Here
- **[Benchmark Vision](./benchmark/benchmark-vision.md)** — What we're building and why
- **[Categories & Definitions](./benchmark/benchmark-categories.md)** — Canonical reference for all testing categories
- **[Scoring Methodology](./benchmark/benchmark-scoring.md)** — How scores are calculated (70/20/10 weighting, most recent test displayed)

### Platform
- **[Deployment Vision](./benchmark/platform-deployment-vision.md)** — How we deploy as a public resource
- **[Technical Architecture](./benchmark/platform-technical-architecture.md)** — Infrastructure decisions
- **[Testing Methodology](./benchmark/platform-testing-methodology.md)** — How tests are executed

### Processes
- **[Publication Model](./benchmark/process-publication-model.md)** — Progressive trust model for results
- **[Question Security](./benchmark/process-question-security.md)** — How questions are protected
- **[Pricing Model](./benchmark/process-pricing-model.md)** — Financial sustainability

### CLI Tools
- **[GCB Runner CLI](./benchmark/cli-runner-specifications.md)** — Run benchmarks locally (fetches questions from Platform API)

See [`benchmark/README.md`](./benchmark/README.md) for the complete documentation index.

---

## Project Status

**Phase:** Specification & Design (Complete)

The benchmark methodology and platform architecture are fully specified. Implementation is the next phase.

---

## Contributing

This project serves the global Great Commission community. Contributions are welcome from those who share the mission of equipping Christians with AI tools that support—rather than hinder—the spread of the gospel.

---

*"Go therefore and make disciples of all nations..."* — Matthew 28:19
