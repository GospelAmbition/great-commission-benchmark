# Railway Build Monitor for Cursor

This tool automatically monitors Railway builds, detects build failures, and extracts build error logs into a format that Cursor can read and use for iterative fixes.

## Quick Start

### 1. Install Railway CLI

```bash
npm install -g @railway/cli
railway login
railway link  # Link to your Railway project
```

### 2. Check for Failed Builds

```bash
# Check all services
python scripts/watch_builds.py

# Check specific service
python scripts/watch_builds.py --service next-frontend
python scripts/watch_builds.py --service fastapi-backend
```

### 3. Use with Cursor

After running the script, if there are build failures, it will create `.build-errors.md` in your project root. You can then:

1. **Open the file in Cursor**: The error report will be automatically available
2. **Ask Cursor to fix it**: 
   ```
   "Read .build-errors.md and fix the build issues"
   ```
3. **Iterative fixing**: After fixing, run the script again to check if the fix worked

## Usage Options

### One-time Check

```bash
python scripts/watch_builds.py
```

### Watch Mode (Continuous Monitoring)

```bash
# Watch every 30 seconds (default)
python scripts/watch_builds.py --watch

# Watch with custom interval
python scripts/watch_builds.py --watch --interval 60
```

### Custom Output File

```bash
python scripts/watch_builds.py --output my-build-errors.md
```

### Using the Shell Wrapper

```bash
# Quick check
./scripts/watch-builds.sh

# Check specific service
./scripts/watch-builds.sh next-frontend

# Watch mode (set environment variable)
WATCH_MODE=1 ./scripts/watch-builds.sh
```

## How It Works

1. **Fetches Recent Builds**: Uses Railway CLI to get the last 5 builds/deployments
2. **Detects Build Failures**: Identifies builds with failed/error status
3. **Extracts Build Logs**: Fetches full build logs for failed builds
4. **Analyzes Build Errors**: Finds build-specific error lines and context:
   - npm/package errors
   - Compilation errors
   - TypeScript/ESLint errors
   - Dependency conflicts
   - Memory/resource issues
5. **Generates Report**: Creates a markdown file with:
   - Build metadata (ID, service, status, timestamp)
   - Key error lines with line numbers
   - Error context (surrounding build output)
   - Full build logs (last 10000 characters)

## Integration with Cursor Workflow

### Automated Fix Cycle

1. **Build fails** → Railway shows build error
2. **Run monitor** → `python scripts/watch_builds.py`
3. **Cursor reads** → `.build-errors.md` is automatically available
4. **Ask Cursor** → "Fix the build errors in .build-errors.md"
5. **Cursor fixes** → Makes code changes (fixes dependencies, syntax, etc.)
6. **Deploy again** → Push changes, Railway rebuilds
7. **Verify** → Run monitor again to confirm fix

### Example Cursor Prompts

```
"Check .build-errors.md and fix the build failure"
```

```
"Read the latest build errors and create a fix"
```

```
"The build is failing. Use .build-errors.md to diagnose and fix it"
```

## Build Error Detection

The script specifically looks for:

- **npm/package errors**: `npm err`, `install failed`, `dependency error`
- **Compilation errors**: `syntax error`, `compilation error`, `tsc error`
- **Module errors**: `cannot find module`, `module not found`
- **Type errors**: `type error`, `typescript error`
- **Build failures**: `build failed`, `build error`, `next build error`
- **Resource errors**: `out of memory`, `killed`, `signal`
- **Exit codes**: `exit code`, `non-zero exit`, `command failed`

## Output Format

The generated `.build-errors.md` file includes:

- **Build Info**: ID, service, status, timestamps
- **Error Summary**: Count of error lines found, build-phase vs runtime errors
- **Key Error Lines**: Specific lines with errors (with line numbers)
- **Error Context**: Surrounding build output for each error
- **Full Build Logs**: Complete build logs (truncated to last 10000 chars)
- **Common Fix Suggestions**: Quick reference for common build issues

## Troubleshooting

### Railway CLI Not Found

```bash
npm install -g @railway/cli
```

### Not Logged In

```bash
railway login
```

### Project Not Linked

```bash
railway link
```

### No Builds Found

- Ensure you're linked to the correct Railway project
- Check that builds exist in Railway dashboard
- Verify service names match exactly (case-sensitive)
- Railway may combine build and deployment info - the script handles this

### Can't Fetch Build Logs

- Railway CLI might need updating: `npm update -g @railway/cli`
- Some Railway plans have log retention limits
- Try checking the Railway dashboard directly
- Build logs are often included in deployment logs

## Differences from Deployment Monitor

- **Focus**: Build failures vs deployment failures
- **Error Detection**: Build-specific patterns (npm, compilation, etc.)
- **Log Analysis**: Distinguishes build-phase errors from runtime errors
- **Context**: More context lines (3 before/after vs 2)
- **Log Size**: Larger log excerpts (10000 chars vs 5000)

## Advanced Usage

### CI/CD Integration

You can integrate this into your CI/CD pipeline:

```yaml
# Example GitHub Actions
- name: Check build status
  run: |
    npm install -g @railway/cli
    railway login --token ${{ secrets.RAILWAY_TOKEN }}
    python scripts/watch_builds.py
  if: failure()
```

### Custom Build Error Detection

Modify `watch_builds.py` to add custom error patterns:

```python
build_error_keywords = [
    "error", "failed", "your-custom-pattern"
]
```

## Notes

- The error file (`.build-errors.md`) is gitignored by default
- Logs are truncated to prevent huge files
- The script focuses on the most recent failed build
- Railway CLI must be authenticated and linked to your project
- Build logs may be mixed with deployment logs in Railway
