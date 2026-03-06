# Runbook: Scaffold AI

## Quick Reference

- **Frontend**: http://localhost:3000 (dev) / S3 + CloudFront (prod)
- **Backend**: http://localhost:8001 (dev)
- **Logs**: CloudWatch Log Group: `/aws/lambda/scaffold-ai-*`

---

## Common Scenarios

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

### Frontend build fails after dependency update

```bash
cd apps/web
pnpm install
pnpm type-check   # catch TS errors before build
pnpm build
```

### Tests failing

```bash
# Frontend
cd apps/web && pnpm test

# Backend
cd apps/backend && uv run pytest tests/ -v
```

### Canvas not rendering nodes

1. Open browser devtools → Console for React Flow errors
2. Check `useGraphStore` state via React DevTools
3. Verify backend returned `updated_graph.nodes` with valid `id`, `type`, `position`, `data` fields

### Generated code download not working

1. Check `generatedFiles` in Zustand store is non-empty
2. JSZip is loaded dynamically — check for network errors on import
3. Verify browser allows blob URL downloads

### Security autofix returns no changes

Expected if architecture already passes security review. Check `security_score.percentage` in the response — if < 100%, the backend may have an issue parsing the graph.

---

## PSP Registration (TODO)

1. Add entry to `project-status-portal/config.json`
2. Run `SeedProjects` Lambda
3. Verify first test run passes in PSP dashboard
