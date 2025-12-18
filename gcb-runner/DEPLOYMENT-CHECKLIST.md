# GCB Runner Deployment Checklist

Complete checklist for releasing the `gcb-runner` CLI tool to PyPI.

---

## Release Overview

| Attribute | Value |
|-----------|-------|
| **Package Name** | `gcb-runner` |
| **Distribution** | PyPI |
| **Language** | Python 3.10+ |
| **Source** | `gcb-runner/` directory |

---

## Pre-Release Checklist

### 1. Code Quality

- [ ] All unit tests pass locally
  ```bash
  cd gcb-runner
  pytest -v
  ```

- [ ] Test coverage meets minimum threshold (80%+)
  ```bash
  pytest --cov=gcb_runner --cov-report=html
  ```

- [ ] Linting passes
  ```bash
  ruff check gcb_runner/
  ```

- [ ] Type checking passes
  ```bash
  mypy gcb_runner/
  ```

- [ ] No security vulnerabilities in dependencies
  ```bash
  pip-audit
  ```

### 2. Version Management

- [ ] Version number updated in `pyproject.toml`
  ```toml
  [project]
  version = "X.Y.Z"
  ```

- [ ] Version follows SemVer:
  - **MAJOR**: Breaking changes to CLI interface or export format
  - **MINOR**: New features, new backend support
  - **PATCH**: Bug fixes, documentation updates

- [ ] `__version__` updated in `gcb_runner/__init__.py`
  ```python
  __version__ = "X.Y.Z"
  ```

### 3. Documentation

- [ ] `README.md` updated with any new features
- [ ] CLI help text is accurate (`--help` for all commands)
- [ ] `CHANGELOG.md` updated with release notes
  ```markdown
  ## [X.Y.Z] - YYYY-MM-DD
  
  ### Added
  - New feature description
  
  ### Changed
  - Changed behavior description
  
  ### Fixed
  - Bug fix description
  ```

- [ ] Installation instructions are current
- [ ] Configuration examples are accurate

### 4. Benchmark Version Compatibility

- [ ] Platform API compatibility verified
  - Test against staging API: `https://staging.gcbenchmark.org/api/runner/versions`
  - Test against production API: `https://gcbenchmark.org/api/runner/versions`

- [ ] Export schema version is correct in code
  ```python
  "format_version": "1.0"  # Verify this matches platform expectations
  ```

- [ ] Judge prompts fetch correctly from API

### 5. Backend Testing

Test each LLM backend:

- [ ] **OpenRouter** backend works
  ```bash
  gcb-runner test --model gpt-4o --backend openrouter --dry-run
  ```

- [ ] **LM Studio** backend works (if available)
  ```bash
  gcb-runner test --model local-model --backend lmstudio --dry-run
  ```

- [ ] **Ollama** backend works (if available)
  ```bash
  gcb-runner test --model llama3.2 --backend ollama --dry-run
  ```

- [ ] **Direct OpenAI** backend works
  ```bash
  gcb-runner test --model gpt-4o --backend openai --dry-run
  ```

- [ ] **Direct Anthropic** backend works
  ```bash
  gcb-runner test --model claude-3.5-sonnet --backend anthropic --dry-run
  ```

### 6. CLI Commands Verification

Test all CLI commands:

- [ ] `gcb-runner config` - Configuration wizard works
- [ ] `gcb-runner versions` - Lists available benchmark versions
- [ ] `gcb-runner test` - Test execution works
- [ ] `gcb-runner results` - Results display works
- [ ] `gcb-runner view` - Web viewer launches correctly
- [ ] `gcb-runner report` - HTML report generates
- [ ] `gcb-runner export` - JSON export works
- [ ] `gcb-runner upload` - Upload flow works (test with staging)

### 7. Cross-Platform Testing

- [ ] Tested on **macOS**
- [ ] Tested on **Linux** (Ubuntu/Debian)
- [ ] Tested on **Windows** (if possible)

### 8. Dependencies

- [ ] All dependencies pinned to minimum compatible versions
- [ ] No unnecessary dependencies included
- [ ] Dependencies use latest secure versions
  ```bash
  pip list --outdated
  ```

---

## Build Checklist

### 1. Clean Build Environment

- [ ] Remove previous build artifacts
  ```bash
  rm -rf dist/ build/ *.egg-info gcb_runner.egg-info/
  ```

- [ ] Create fresh virtual environment for testing
  ```bash
  python -m venv test-env
  source test-env/bin/activate
  pip install --upgrade pip build twine
  ```

### 2. Build Package

- [ ] Build source distribution and wheel
  ```bash
  python -m build
  ```

- [ ] Verify build output
  ```bash
  ls -la dist/
  # Should show:
  # gcb_runner-X.Y.Z.tar.gz
  # gcb_runner-X.Y.Z-py3-none-any.whl
  ```

- [ ] Check package contents
  ```bash
  tar -tzf dist/gcb_runner-X.Y.Z.tar.gz | head -20
  ```

### 3. Local Installation Test

- [ ] Install from built wheel
  ```bash
  pip install dist/gcb_runner-X.Y.Z-py3-none-any.whl
  ```

- [ ] Verify installation
  ```bash
  gcb-runner --version
  # Should output: gcb-runner X.Y.Z
  ```

- [ ] Run smoke test
  ```bash
  gcb-runner versions
  ```

---

## TestPyPI Release (Staging)

### 1. Upload to TestPyPI

- [ ] Configure TestPyPI credentials (if not done)
  ```bash
  # Create ~/.pypirc or use environment variables
  # TWINE_USERNAME=__token__
  # TWINE_PASSWORD=pypi-xxx
  ```

- [ ] Upload to TestPyPI
  ```bash
  python -m twine upload --repository testpypi dist/*
  ```

- [ ] Verify upload successful
  - Check: `https://test.pypi.org/project/gcb-runner/`

### 2. TestPyPI Installation Test

- [ ] Create clean test environment
  ```bash
  deactivate
  rm -rf test-env
  python -m venv test-env
  source test-env/bin/activate
  ```

- [ ] Install from TestPyPI
  ```bash
  pip install --index-url https://test.pypi.org/simple/ \
    --extra-index-url https://pypi.org/simple/ \
    gcb-runner==X.Y.Z
  ```
  
  > Note: `--extra-index-url` needed because dependencies are on real PyPI

- [ ] Verify installation works
  ```bash
  gcb-runner --version
  gcb-runner --help
  ```

- [ ] Run basic smoke tests
  ```bash
  gcb-runner versions
  gcb-runner config --help
  ```

---

## Production PyPI Release

### 1. Final Verification

- [ ] TestPyPI testing completed successfully
- [ ] All checklist items above are complete
- [ ] Release has been approved by project maintainer

### 2. Upload to PyPI

- [ ] Upload to production PyPI
  ```bash
  python -m twine upload dist/*
  ```

- [ ] Verify upload successful
  - Check: `https://pypi.org/project/gcb-runner/`

### 3. Production Installation Test

- [ ] Create clean test environment
  ```bash
  deactivate
  rm -rf test-env
  python -m venv test-env
  source test-env/bin/activate
  ```

- [ ] Install from PyPI
  ```bash
  pip install gcb-runner
  ```

- [ ] Verify version
  ```bash
  gcb-runner --version
  # Should output: gcb-runner X.Y.Z
  ```

- [ ] Full smoke test
  ```bash
  # Test help
  gcb-runner --help
  
  # Test version listing
  gcb-runner versions
  
  # Test config (interactive - manual verification)
  gcb-runner config --help
  ```

---

## Post-Release Checklist

### 1. Git Tagging

- [ ] Create annotated git tag
  ```bash
  git tag -a vX.Y.Z -m "Release vX.Y.Z - Brief description"
  ```

- [ ] Push tag to origin
  ```bash
  git push origin vX.Y.Z
  ```

### 2. GitHub Release

- [ ] Create GitHub release from tag
  ```bash
  gh release create vX.Y.Z \
    --title "GCB Runner vX.Y.Z" \
    --notes-file RELEASE_NOTES.md
  ```
  
  Or via GitHub web UI:
  - Go to Releases → Draft a new release
  - Select tag `vX.Y.Z`
  - Title: `GCB Runner vX.Y.Z`
  - Description: Copy from CHANGELOG

- [ ] Attach release artifacts (optional)
  - Built wheel file
  - Source tarball

### 3. Communication

- [ ] Update project documentation if needed
- [ ] Notify community of release (if applicable)
  - Discord/Slack announcement
  - Email newsletter
  - Social media

### 4. Monitoring

- [ ] Monitor PyPI download stats
  - Check: `https://pypistats.org/packages/gcb-runner`

- [ ] Monitor for issue reports
  - Check GitHub Issues for new bug reports

- [ ] Verify no regression in platform integration
  - Check platform logs for runner API errors

---

## Rollback Procedure

If critical issues are discovered after release:

### 1. Yank the Release (Soft Removal)

- [ ] Yank from PyPI (prevents new installs but allows existing pins)
  ```bash
  # Via PyPI web interface or:
  pip install --upgrade twine
  # Note: PyPI yank is typically done via web UI
  ```

### 2. Users Can Downgrade

Communicate to users:
```bash
pip install gcb-runner==X.Y.Z-1  # Previous version
```

### 3. Quick Fix Release

- [ ] Fix the critical issue
- [ ] Increment patch version (X.Y.Z+1)
- [ ] Follow full release checklist again

---

## Release Cadence

| Release Type | Frequency | Description |
|--------------|-----------|-------------|
| **Major** | As needed | Breaking changes |
| **Minor** | Monthly | New features |
| **Patch** | As needed | Bug fixes |
| **Hotfix** | Immediate | Critical security/bug fixes |

---

## Environment Setup Reference

### Required Tools

```bash
# Install build tools
pip install --upgrade pip build twine

# Install testing tools  
pip install pytest pytest-cov ruff mypy pip-audit

# Install GitHub CLI (for releases)
brew install gh  # macOS
# or: sudo apt install gh  # Linux
```

### PyPI Configuration

Create `~/.pypirc`:
```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-xxx  # Your PyPI API token

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-xxx  # Your TestPyPI API token
```

Or use environment variables:
```bash
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=pypi-xxx
```

---

## Checklist Summary

### Pre-Release (Do First)
- [ ] Tests pass
- [ ] Version updated
- [ ] Documentation updated
- [ ] Changelog updated
- [ ] All backends tested
- [ ] Cross-platform tested

### Build & Test
- [ ] Clean build
- [ ] Package built
- [ ] Local install works
- [ ] TestPyPI upload
- [ ] TestPyPI install works

### Production Release
- [ ] PyPI upload
- [ ] PyPI install works
- [ ] Git tag created
- [ ] GitHub release created

### Post-Release
- [ ] Announcement posted
- [ ] Monitoring in place

---

## Related Documents

- [CLI Runner Specifications](../benchmark/cli-runner-specifications.md) — Feature specs
- [CLI Runner Tech Stack](../benchmark/cli-runner-tech-stack.md) — Technology decisions
- [Deployment Procedures](../documents/Deployment-Procedures.md) — Platform deployment
- [Export Schema Validation](../benchmark/spec-export-schema-validation.md) — Export format

---

*Last Updated: December 2024*
