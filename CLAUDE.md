# Scaffold AI

## What It Does

Scaffold AI is an AI-powered AWS architecture designer. Describe what you want to build in natural language, and it generates a visual node graph of AWS services plus deployable IaC code (CDK TypeScript, CDK Python, CloudFormation, or Terraform).

## Architecture

- **Frontend**: React + Vite SPA, Cloudscape UI, React Flow canvas, Zustand state
- **Backend**: FastAPI + Step Functions + Strands, AWS Bedrock (Claude), Python 3.12+
- **IaC**: CDK TypeScript (default), CDK Python, CloudFormation YAML, Terraform HCL

## Key Files

- `apps/web/src/App.tsx` — main layout (Cloudscape AppLayout + split panel chat)
- `apps/web/components/Chat.tsx` — AI chat + code generation UI
- `apps/web/components/Canvas.tsx` — React Flow architecture canvas
- `apps/backend/src/scaffold_ai/main.py` — FastAPI app entrypoint
- `apps/web/lib/store.ts` — Zustand stores (chat, graph)
- `apps/web/lib/config.ts` — backend URL config (`VITE_BACKEND_URL`)

## Dev Setup

```bash
# Backend
cd apps/backend && uv sync
uv run uvicorn scaffold_ai.main:app --reload --port 8001

# Frontend
cd apps/web && pnpm install
pnpm dev   # http://localhost:3000
```

## Environment Variables

**Frontend** (`apps/web/.env.local`):
```
VITE_BACKEND_URL=http://localhost:8001
```

**Backend** (`apps/backend/.env`):
```
AWS_REGION=us-east-1
AWS_PROFILE=admin
```

## Testing

```bash
# Frontend
cd apps/web && pnpm test
pnpm test:coverage

# Backend
cd apps/backend && uv run pytest tests/ --cov=src/ --cov-report=term-missing
```

## API Endpoints

- `POST /api/chat` — fire-and-poll: accepts `user_input`, `graph_json`, `iac_format`; returns `{ execution_arn }`
- `GET /api/chat/{arn}/status` — poll execution: returns `{ status, message, updated_graph, generated_files }`
- `POST /api/security/autofix` — security review: accepts `graph`; returns `updated_graph`, `changes`, `security_score`
- `POST /api/import/plan` — import plan from Project Planner AI; returns `{ session_id, initial_prompt }`
- `GET /api/import/plan/{session_id}` — fetch imported plan data

## IaC Formats

| Value | Output |
|---|---|
| `cdk` | CDK TypeScript (default) |
| `python-cdk` | CDK Python |
| `cloudformation` | CloudFormation YAML |
| `terraform` | Terraform HCL |

## PSP Integration

Not yet registered. See `config.json` for test commands.
