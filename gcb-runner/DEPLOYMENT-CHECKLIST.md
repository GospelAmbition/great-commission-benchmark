# GCB Runner Deployment Checklist

Complete checklist for releasing the `gcb-runner` CLI tool as standalone executables distributed via the GCB website.

---

## Release Overview

| Attribute | Value |
|-----------|-------|
| **Package Name** | `gcb-runner` |
| **Distribution** | Private (website download) |
| **Format** | Standalone executables (PyInstaller) |
| **Download URL** | `https://greatcommissionbenchmark.ai/runner` |
| **Manifest** | `https://greatcommissionbenchmark.ai/downloads/manifest.json` |

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
- [ ] `gcb-runner update` - Auto-update check works

---

## Build Checklist

### 1. Prepare Build Environment

- [ ] Clean previous build artifacts
  ```bash
  cd gcb-runner
  rm -rf dist/ build/ *.egg-info gcb_runner.egg-info/
  ```

- [ ] Create fresh virtual environment
  ```bash
  python -m venv build-env
  source build-env/bin/activate  # Linux/macOS
  # build-env\Scripts\activate   # Windows
  pip install --upgrade pip
  pip install -e ".[dev]"
  ```

- [ ] Verify PyInstaller is installed
  ```bash
  python -m PyInstaller --version
  ```

### 2. Build Standalone Executable

- [ ] Build for current platform
  ```bash
  python scripts/build.py
  ```

- [ ] Verify build output
  ```bash
  ls -la dist/release/
  # Should show:
  # gcb-runner-macos-arm64    (Apple Silicon)
  # gcb-runner-macos-x64      (Intel Mac)
  # gcb-runner-linux-x64      (Linux)
  # gcb-runner.exe            (Windows)
  # manifest.json             (always generated)
  ```

- [ ] Check executable size (typically 20-40 MB)
  ```bash
  du -h dist/release/gcb-runner-*
  ```

### 3. Test Built Executable

- [ ] Test execution (on current platform)
  ```bash
  ./dist/release/gcb-runner-macos-arm64 --version
  # Should output: gcb-runner X.Y.Z
  ```

- [ ] Run smoke tests
  ```bash
  ./dist/release/gcb-runner-macos-arm64 --help
  ./dist/release/gcb-runner-macos-arm64 versions
  ```

- [ ] Test interactive menu launches
  ```bash
  ./dist/release/gcb-runner-macos-arm64
  # Should show interactive menu
  ```

- [ ] Test configuration wizard
  ```bash
  ./dist/release/gcb-runner-macos-arm64 config --help
  ```

---

## Multi-Platform Builds

Each platform must be built on native hardware or via CI:

### macOS (Apple Silicon)
```bash
# On M1/M2/M3 Mac
python scripts/build.py
# Output: dist/release/gcb-runner-macos-arm64
```

### macOS (Intel)
```bash
# On Intel Mac
python scripts/build.py
# Output: dist/release/gcb-runner-macos-x64
```

### Linux x64

**Option 1: Using Docker (Recommended if you don't have Linux)**
```bash
# Build Linux executable using Docker (works on macOS/Windows)
./build-linux.sh

# Or manually:
docker build -f Dockerfile.build-linux -t gcb-runner-builder .
CONTAINER_ID=$(docker create gcb-runner-builder)
docker cp $CONTAINER_ID:/build/dist/release/gcb-runner-linux-x64 ./dist/release/
docker rm $CONTAINER_ID
```

**Option 2: On a Linux machine**
```bash
# On Linux x64
python scripts/build.py
# Output: dist/release/gcb-runner-linux-x64
```

**Option 3: Using GitHub Actions**
```bash
# Push to GitHub and trigger the build-linux workflow
# Or manually trigger: Actions → Build Linux Executable → Run workflow
# Download the artifact from the workflow run
```

### Windows x64
```powershell
# On Windows
python scripts\build.py
# Output: dist\release\gcb-runner.exe
```

### GitHub Actions (Recommended for All Platforms)

For consistent multi-platform builds, use GitHub Actions:

```yaml
# .github/workflows/build.yml
name: Build Executables

on:
  push:
    tags:
      - 'v*'

jobs:
  build:
    strategy:
      matrix:
        os: [macos-14, macos-13, ubuntu-latest, windows-latest]
        # macos-14 = ARM64, macos-13 = Intel
    
    runs-on: ${{ matrix.os }}
    
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install -e ".[dev]"
      - run: python scripts/build.py
      - uses: actions/upload-artifact@v4
        with:
          name: gcb-runner-${{ matrix.os }}
          path: dist/release/gcb-runner*
```

---

## Generate Final Manifest

After all platform builds are complete:

- [ ] Collect all executables into `dist/release/`
  ```bash
  ls dist/release/
  # gcb-runner-macos-arm64
  # gcb-runner-macos-x64
  # gcb-runner-linux-x64
  # gcb-runner.exe
  ```

- [ ] Generate manifest with all platforms
  ```bash
  python scripts/build.py --manifest-only
  ```

- [ ] Verify manifest.json
  ```bash
  cat dist/release/manifest.json
  ```

  Expected structure:
  ```json
  {
    "version": "X.Y.Z",
    "released_at": "2024-12-26T12:00:00+00:00",
    "downloads": {
      "macos-arm64": {
        "filename": "gcb-runner-macos-arm64",
        "sha256": "abc123...",
        "size": 31457280
      },
      "macos-x64": { ... },
      "linux-x64": { ... },
      "windows-x64": { ... }
    },
    "release_notes": "GCB Runner vX.Y.Z",
    "minimum_version": "0.1.0"
  }
  ```

---

## Website Deployment

### 1. Upload Files

Upload the built executables and manifest to the website:

- [ ] Copy files to frontend public directory
  ```bash
  cp dist/release/gcb-runner-* ../gcb-platform/frontend/public/downloads/
  cp dist/release/manifest.json ../gcb-platform/frontend/public/downloads/
  ```

- [ ] Verify all files present
  ```bash
  ls -la ../gcb-platform/frontend/public/downloads/
  # gcb-runner-macos-arm64
  # gcb-runner-macos-x64
  # gcb-runner-linux-x64
  # gcb-runner.exe
  # manifest.json
  ```

### 2. Deploy Frontend

- [ ] Commit and push changes
  ```bash
  cd ../gcb-platform/frontend
  git add public/downloads/
  git commit -m "Release GCB Runner vX.Y.Z"
  git push
  ```

- [ ] Deploy to production
  ```bash
  # Follow platform deployment procedures
  ```

### 3. Verify Downloads

- [ ] Test manifest URL
  ```bash
  curl https://greatcommissionbenchmark.ai/downloads/manifest.json
  ```

- [ ] Test download URLs
  ```bash
  # Verify each platform download link works
  curl -I https://greatcommissionbenchmark.ai/downloads/gcb-runner-macos-arm64
  ```

- [ ] Verify SHA256 hashes match
  ```bash
  # Download and verify
  curl -O https://greatcommissionbenchmark.ai/downloads/gcb-runner-macos-arm64
  shasum -a 256 gcb-runner-macos-arm64
  # Compare with manifest.json
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

### 2. GitHub Release (Optional)

- [ ] Create GitHub release from tag
  ```bash
  gh release create vX.Y.Z \
    --title "GCB Runner vX.Y.Z" \
    --notes-file CHANGELOG.md \
    dist/release/gcb-runner-* \
    dist/release/manifest.json
  ```

### 3. Test Auto-Update

- [ ] Install previous version
- [ ] Run `gcb-runner update --check`
- [ ] Verify new version is detected
- [ ] Run `gcb-runner update` and confirm upgrade works

### 4. Communication

- [ ] Update project documentation if needed
- [ ] Notify testers of new version (if applicable)

---

## Rollback Procedure

If critical issues are discovered after release:

### 1. Restore Previous Version

- [ ] Retrieve previous version executables from backup or git tag
- [ ] Update manifest.json with previous version info
- [ ] Redeploy to website

### 2. Communication

Notify users:
- Update /runner page with notice
- Send notification to active testers if possible

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

## Build Environment Reference

### Required Tools

```bash
# Install development dependencies
pip install -e ".[dev]"

# This includes:
# - pytest (testing)
# - pyinstaller (building executables)
# - ruff (linting)
# - mypy (type checking)
# - pip-audit (security audit)
```

### Project Structure

```
gcb-runner/
├── gcb_runner/           # Source code
├── scripts/
│   ├── build.py          # Build script
│   └── generate_hashes.py  # Hash generation utility
├── gcb-runner.spec       # PyInstaller configuration
├── pyproject.toml        # Project configuration
├── README.md             # User documentation
├── CHANGELOG.md          # Version history
└── dist/
    └── release/          # Built executables (generated)
        ├── gcb-runner-macos-arm64
        ├── gcb-runner-macos-x64
        ├── gcb-runner-linux-x64
        ├── gcb-runner.exe
        └── manifest.json
```

---

## Checklist Summary

### Pre-Release (Do First)
- [ ] Tests pass
- [ ] Version updated in `pyproject.toml` and `__init__.py`
- [ ] Documentation updated
- [ ] Changelog updated
- [ ] All backends tested
- [ ] All CLI commands verified

### Build & Test
- [ ] Clean build environment
- [ ] PyInstaller build succeeds
- [ ] Executable runs correctly
- [ ] Smoke tests pass
- [ ] Interactive menu works

### Multi-Platform (For Full Release)
- [ ] macOS ARM64 built
- [ ] macOS x64 built
- [ ] Linux x64 built
- [ ] Windows x64 built
- [ ] Final manifest.json generated

### Website Deployment
- [ ] Files uploaded to frontend/public/downloads/
- [ ] Frontend deployed
- [ ] Download links verified
- [ ] SHA256 hashes verified

### Post-Release
- [ ] Git tag created and pushed
- [ ] Auto-update tested
- [ ] Announcement posted (if applicable)

---

## Related Documents

- [CLI Runner Specifications](../benchmark/cli-runner-specifications.md) — Feature specs
- [CLI Runner Tech Stack](../benchmark/cli-runner-tech-stack.md) — Technology decisions
- [Deployment Procedures](../documents/Deployment-Procedures.md) — Platform deployment
- [Export Schema Validation](../benchmark/spec-export-schema-validation.md) — Export format

---

*Last Updated: December 2024*
