# Railway Deployment Monitor for Cursor

This tool automatically monitors Railway deployments, detects failures, and extracts error logs into a format that Cursor can read and use for iterative fixes.

## Quick Start

### 1. Install Railway CLI

```bash
npm install -g @railway/cli
railway login
railway link  # Link to your Railway project
```

### 2. Check for Failed Deployments

```bash
# Check all services
python scripts/watch_deployments.py

# Check specific service
python scripts/watch_deployments.py --service next-frontend
python scripts/watch_deployments.py --service fastapi-backend
```

### 3. Use with Cursor

After running the script, if there are failures, it will create `.deployment-errors.md` in your project root. You can then:

1. **Open the file in Cursor**: The error report will be automatically available
2. **Ask Cursor to fix it**: 
   ```
   "Read .deployment-errors.md and fix the deployment issues"
   ```
3. **Iterative fixing**: After fixing, run the script again to check if the fix worked

## Usage Options

### One-time Check

```bash
python3 scripts/watch_deployments.py
```

### Watch Mode (Continuous Monitoring)

```bash
# Watch every 30 seconds (default)
python3 scripts/watch_deployments.py --watch

# Watch with custom interval
python3 scripts/watch_deployments.py --watch --interval 60
```

### Custom Output File

```bash
python3 scripts/watch_deployments.py --output my-errors.md
```

### Using the Shell Wrapper

```bash
# Quick check
./scripts/watch-deployments.sh

# Check specific service
./scripts/watch-deployments.sh next-frontend

# Watch mode (set environment variable)
WATCH_MODE=1 ./scripts/watch-deployments.sh
```

## How It Works

1. **Fetches Recent Deployments**: Uses Railway CLI to get the last 5 deployments
2. **Detects Failures**: Identifies deployments with failed/error status
3. **Extracts Logs**: Fetches full deployment logs for failed deployments
4. **Analyzes Errors**: Finds error lines and context
5. **Generates Report**: Creates a markdown file with:
   - Deployment metadata (ID, service, status, timestamp)
   - Key error lines with line numbers
   - Error context (surrounding lines)
   - Full logs (last 5000 characters)

## Integration with Cursor Workflow

### Automated Fix Cycle

1. **Deploy fails** → Railway shows error
2. **Run monitor** → `python3 scripts/watch_deployments.py`
3. **Cursor reads** → `.deployment-errors.md` is automatically available
4. **Ask Cursor** → "Fix the deployment errors in .deployment-errors.md"
5. **Cursor fixes** → Makes code changes
6. **Deploy again** → Push changes, Railway redeploys
7. **Verify** → Run monitor again to confirm fix

### Example Cursor Prompts

```
"Check .deployment-errors.md and fix the deployment failure"
```

```
"Read the latest deployment errors and create a fix"
```

```
"The deployment is failing. Use .deployment-errors.md to diagnose and fix it"
```

## Output Format

The generated `.deployment-errors.md` file includes:

- **Deployment Info**: ID, service, status, timestamps
- **Error Summary**: Count of error lines found
- **Key Error Lines**: Specific lines with errors (with line numbers)
- **Error Context**: Surrounding code/logs for each error
- **Full Logs**: Complete deployment logs (truncated to last 5000 chars)

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

### No Deployments Found

- Ensure you're linked to the correct Railway project
- Check that deployments exist in Railway dashboard
- Verify service names match exactly (case-sensitive)

### Can't Fetch Logs

- Railway CLI might need updating: `npm update -g @railway/cli`
- Some Railway plans have log retention limits
- Try checking the Railway dashboard directly

## Advanced Usage

### CI/CD Integration

You can integrate this into your CI/CD pipeline:

```yaml
# Example GitHub Actions
- name: Check deployment status
  run: |
    npm install -g @railway/cli
    railway login --token ${{ secrets.RAILWAY_TOKEN }}
    python3 scripts/watch_deployments.py
  if: failure()
```

### Custom Error Detection

Modify `watch_deployments.py` to add custom error patterns:

```python
error_keywords = ["error", "failed", "exception", "your-custom-pattern"]
```

## Notes

- The error file (`.deployment-errors.md`) is gitignored by default
- Logs are truncated to prevent huge files
- The script focuses on the most recent failed deployment
- Railway CLI must be authenticated and linked to your project
