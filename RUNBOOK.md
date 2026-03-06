# Runbook: Scaffold AI

## Quick Reference

- **PSP Dashboard:** Project Status Portal → scaffold-ai
- **Frontend**: http://localhost:3000 (dev) / S3 + CloudFront (prod)
- **Backend**: http://localhost:8001 (dev)
- **Logs**: CloudWatch Log Group: `/aws/lambda/scaffold-ai-*`
- **Alarms**: CloudWatch Alarms filtered by tag `Project=scaffold-ai`
- **Step Functions**: AWS Console → Step Functions → `ScaffoldAI-Workflow`
- **Repo**: `github.com/jfowler-cloud/scaffold-ai`

---

## Common Scenarios

### Tests failing in PSP

1. Open PSP dashboard, click scaffold-ai
2. Review findings in the Findings tab
3. Check if it's a flaky test (re-trigger single project run)
4. If persistent: check CloudWatch logs for the CodeBuild run
5. Run locally: `cd apps/backend && uv run pytest tests/` and `cd apps/web && pnpm test`

### Backend not responding

```bash
cd apps/backend
uv run uvicorn scaffold_ai.main:app --reload --port 8001
```

Check `VITE_BACKEND_URL` in `apps/web/.env.local` matches the port.

### AWS Bedrock errors (model not available)

1. Verify `AWS_PROFILE` and `AWS_REGION` are set in `apps/backend/.env`
2. Confirm the Bedrock model is enabled in your AWS account (us-east-1 → Bedrock → Model access)
3. Check IAM permissions include `bedrock:InvokeModel`

### Lambda errors spiking

1. Open CloudWatch → Log Insights for the failing function
2. Query:
   ```
   fields @timestamp, @message
   | filter @message like /ERROR/
   | sort @timestamp desc
   ```
3. Check if it's a transient AWS issue (Bedrock throttle, cold start)
4. Check if a recent deploy introduced a regression (compare with last tag)

### Step Functions execution failing

1. AWS Console → Step Functions → `ScaffoldAI-Workflow` → Executions
2. Click the failed execution to see which state failed
3. Check the Lambda error in the state's output
4. Common causes: Bedrock rate limit, malformed input from previous step, timeout

### Coverage dropped

1. PSP will show a COVERAGE_DROP finding
2. Check the PR that caused it — were tests removed or was code added without tests?
3. Run locally: `cd apps/web && pnpm test:coverage` or `cd apps/backend && uv run pytest tests/ --cov=src/ --cov-report=term-missing`

### Frontend build fails after dependency update

```bash
cd apps/web
pnpm install
pnpm type-check   # catch TS errors before build
pnpm build
```

### Canvas not rendering nodes

1. Open browser devtools → Console for React Flow errors
2. Check `useGraphStore` state via React DevTools
3. Verify backend returned `updated_graph.nodes` with valid `id`, `type`, `position`, `data` fields

### Project shows SETUP_FAILURE in PSP

1. Usually a git clone or dependency install issue
2. Check CodeBuild logs for the failed build
3. Common causes: expired GitHub PAT, deleted branch, broken lockfile
