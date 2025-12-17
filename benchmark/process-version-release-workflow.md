# Process: Version Release Workflow

This document outlines the practical steps for releasing new benchmark versions.

---

## Overview

Releases follow a predictable process: prepare, validate, announce, lock, and publish. The workflow differs slightly based on release type.

---

## Release Types

| Type | Version Change | Example | Typical Timeline |
|------|---------------|---------|------------------|
| **Patch** | 1.1 → 1.1.1 | Bug fixes, judge prompt clarifications | 1-2 days |
| **Minor** | 1.0 → 1.1 | Question additions/refinements | 1-2 weeks |
| **Major** | 1.x → 2.0 | New question set (annual or contamination response) | 4-6 weeks |

---

## Patch Release Workflow

Use for bug fixes and methodology refinements that don't change questions.

### Steps

1. **Identify fix**
   - Document the issue being corrected
   - Confirm fix doesn't affect question content

2. **Apply changes**
   - Update judge prompts, scoring thresholds, or calibration as needed
   - Test changes against calibration set

3. **Update changelog**
   - Document what changed and why
   - Note that existing results remain fully comparable

4. **Deploy**
   - No announcement period required
   - Deploy immediately after validation

---

## Minor Release Workflow

Use for question additions, refinements, or small category updates.

### Pre-Release (1-2 weeks before)

1. **Prepare question changes**
   - Finalize new/updated questions in draft state
   - Ensure questions pass validation (formatting, calibration)
   - Review category coverage and tier distribution

2. **Internal review**
   - Committee reviews proposed changes
   - Human reviewers validate expected verdicts for new questions
   - Address any concerns

### Release Week

3. **Final validation**
   - Run pre-publish validation checks:
     - [ ] All categories have minimum question count
     - [ ] Tier distribution meets requirements
     - [ ] All questions have calibration data
     - [ ] No duplicate questions

4. **Announce**
   - Post announcement with release date (minimum 3 days notice)
   - List summary of changes

5. **Lock and publish**
   - Lock question set (becomes immutable)
   - Generate JSON export for platform
   - Build CLI bundle
   - Deploy to production

6. **Update documentation**
   - Add changelog entry
   - Update any affected spec documents

---

## Major Release Workflow

Use for new question sets (annual refresh or contamination response).

### Planning Phase (4-6 weeks before)

1. **Determine scope**
   - Define what's changing and why
   - Set target question counts per category
   - Establish timeline

2. **Question development**
   - Draft new questions
   - Maintain security (no public exposure of new questions)
   - Track progress against targets

### Review Phase (2-3 weeks before)

3. **Internal review**
   - Committee reviews complete question set
   - Human reviewers calibrate expected verdicts
   - Iterate based on feedback

4. **Pre-publish validation**
   - Full validation suite:
     - [ ] All categories have required question counts
     - [ ] Tier distribution is balanced
     - [ ] All questions have calibration data
     - [ ] Question diversity is adequate
     - [ ] No questions appear in known training data

### Transition Phase (1-2 weeks before)

5. **Public announcement**
   - Announce new version with release date
   - Provide 2-week minimum notice
   - Explain what's changing and why

6. **Grace period begins**
   - In-progress tests continue on current version
   - New tests can optionally wait for new version

### Release Day

7. **Lock and publish**
   - Lock new question set
   - Generate all exports (JSON, CLI bundle)
   - Deploy to production
   - New version becomes default

8. **Archive old version**
   - Previous version moves to "archived" state
   - Old results remain accessible via version filter
   - Leaderboard defaults to new version

### Post-Release

9. **Documentation**
   - Complete changelog entry
   - Update marketing version mapping
   - Announce completion

---

## Validation Checklist

Before any release, verify:

### Questions
- [ ] All questions have required fields (id, category, tier, prompt)
- [ ] Expected verdicts are set for calibration questions
- [ ] No formatting errors or invalid characters

### Coverage
- [ ] Each category has minimum question count
- [ ] Tier distribution matches targets (Tier 1: ~40%, Tier 2: ~40%, Tier 3: ~20%)
- [ ] Total question count meets version requirements

### Technical
- [ ] JSON export generates without errors
- [ ] CLI bundle compiles successfully
- [ ] Version numbers are correct and consistent

---

## Emergency Release (Contamination Response)

If question contamination is detected:

1. **Assess severity**
   - How many questions exposed?
   - Evidence in training data?

2. **Immediate action**
   - Mark affected questions as compromised
   - Begin expedited major release process

3. **Accelerated timeline**
   - Skip extended planning phase
   - Minimum 1-week announcement period
   - Prioritize replacing compromised questions

4. **Communication**
   - Transparent announcement of contamination
   - Explain impact on existing results
   - Provide clear timeline for new version

---

## Roles

| Role | Responsibilities |
|------|------------------|
| **Release Manager** | Coordinates timeline, ensures checklist completion |
| **Question Committee** | Reviews and approves question changes |
| **Technical Lead** | Validates exports, deploys to production |
| **Communications** | Drafts announcements, updates documentation |

For small teams, one person may fill multiple roles.

---

## Related Documents

- [Platform Versioning](./platform-versioning.md) — Version format, lifecycle, and display
- [Question Security](./process-question-security.md) — Protecting questions from contamination
- [Publication Model](./process-publication-model.md) — How results are published

