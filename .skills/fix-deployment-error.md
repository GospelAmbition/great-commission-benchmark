Review the latest Railway deployment failure, fix the error(s), and push a new commit.

Debug approach:
1. Run a local build to reproduce the error: `cd gcb-platform/frontend && npm run build`
2. If backend: `cd gcb-platform/backend && pip install -e . && python -c "from app.main import app"`
3. Fix all TypeScript/build errors until the build succeeds
4. Commit and push the fix