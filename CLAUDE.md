# Scaffold AI

## What It Does

AI-powered AWS architecture designer. Describe what you want to build in natural language, and it generates a visual node graph of AWS services plus deployable IaC code (CDK TypeScript, CDK Python, CloudFormation, or Terraform).

## Architecture

- **Frontend**: React 19 + Vite SPA, Cloudscape UI, React Flow canvas, Zustand state, Amplify Authenticator, react-markdown + remark-gfm
- **Backend**: Step Functions + Lambda (Strands agents), AWS Bedrock (Claude), Python 3.13+
- **Auth**: Cognito User Pool + Identity Pool → temporary AWS credentials (no API Gateway)
- **IaC**: CDK v2 TypeScript infrastructure
- **Hosting**: S3 + CloudFront

## Mono-Repo Layout

```
scaffold-ai/
├── apps/
│   ├── web/                      # React 19 + Vite + Cloudscape SPA
│   │   ├── src/
│   │   │   ├── App.tsx           # Amplify auth wrapper, AppLayout, dark/light toggle, toast context, keyboard shortcuts
│   │   │   ├── main.tsx          # Entry point, configureAmplify()
│   │   │   └── index.css         # SA design tokens (--sa-*), dark/light themes, chat markdown, session sidebar, responsive
│   │   ├── components/
│   │   │   ├── Canvas.tsx        # React Flow architecture canvas (65 AWS node types)
│   │   │   ├── Chat.tsx          # AI chat + code generation UI + session sidebar + markdown rendering
│   │   │   ├── GeneratedCodeModal.tsx
│   │   │   └── PlannerNotification.tsx
│   │   ├── lib/
│   │   │   ├── amplify.ts        # Amplify config from VITE_* env vars
│   │   │   ├── api.ts            # AWS SDK calls (SFN StartExecution, Lambda Invoke)
│   │   │   ├── security-autofix.ts  # Client-side security analysis
│   │   │   ├── store.ts          # Zustand stores (chat, graph)
│   │   │   ├── usePlannerImport.ts  # DynamoDB handoff from Project Planner AI
│   │   │   └── config.ts         # Re-exports from amplify config
│   │   ├── __tests__/            # Vitest unit tests
│   │   └── package.json
│   ├── functions/                # Lambda handlers (Python 3.13+, uv)
│   │   ├── interpret/            # Parse user intent, extract architecture changes
│   │   ├── architect/            # Generate/update architecture graph via Strands
│   │   ├── security_review/      # Security gate before code generation
│   │   ├── cdk_specialist/       # Generate IaC code (CDK/CFN/TF/Python-CDK)
│   │   ├── react_specialist/     # Generate React + Cloudscape frontend code
│   │   ├── get_execution/        # Poll SFN execution status
│   │   └── tests/
│   ├── infra/                    # CDK v2 TypeScript
│   │   ├── lib/
│   │   │   ├── database-stack.ts   # Cognito, DynamoDB, S3, CloudFront
│   │   │   ├── functions-stack.ts  # Lambda functions + layers + alarms
│   │   │   └── workflow-stack.ts   # Step Functions state machine
│   │   └── layers/               # Lambda layers (shared + agents)
│   └── backend/                  # FastAPI (legacy, not deployed to prod)
├── config.json
└── CLAUDE.md
```

## Key Architecture Decisions

- **No API Gateway** — frontend calls SFN + Lambda directly via Cognito identity pool credentials
- **Fire-and-poll pattern**: Frontend starts SFN execution via `StartExecutionCommand`, polls via Lambda `InvokeCommand` for `get_execution`
- **Client-side security autofix**: Security analysis runs in browser (no AWS call needed)
- **Lambda modules are self-contained**: Each function directory contains all needed Python modules (no imports from backend package)
- **Cross-region Bedrock**: IAM policy includes us-east-1, us-east-2, us-west-2 for `us.*` inference profile routing
- **DynamoDB handoff**: Project Planner AI writes plan data to `project-planner-handoff` table, scaffold-ai reads via URL params

## Dev Setup

```bash
# Frontend
cd apps/web && pnpm install
pnpm dev   # http://localhost:3000

# Backend (legacy local dev)
cd apps/backend && uv sync
uv run uvicorn scaffold_ai.main:app --reload --port 8001
```

## Environment Variables

**Frontend** (`apps/web/.env.local`):
```
VITE_AWS_REGION=us-east-1
VITE_USER_POOL_ID=us-east-1_ouXZdiLOe
VITE_USER_POOL_CLIENT_ID=7bih9lmkfsq36r5lm77dradjf9
VITE_IDENTITY_POOL_ID=us-east-1:867b384b-8300-48fb-ad2b-98186cd29206
VITE_WORKFLOW_ARN=arn:aws:states:us-east-1:831729228662:stateMachine:ScaffoldAI-Workflow
VITE_GET_EXECUTION_FN=scaffold-ai-get_execution
```

## Testing

```bash
# Frontend
cd apps/web && pnpm test
pnpm test:coverage

# Lambda functions
cd apps/functions && uv run pytest tests/ --cov=. --cov-report=term-missing -q

# CDK
cd apps/infra && npm test
```

## IaC Formats

| Value | Output |
|---|---|
| `cdk` | CDK TypeScript (default, LLM-generated via Strands) |
| `python-cdk` | CDK Python (template-based) |
| `cloudformation` | CloudFormation YAML (template-based) |
| `terraform` | Terraform HCL (template-based) |

## Deployment

```bash
# CDK infrastructure
cd apps/infra && npx cdk deploy --all --profile cdk-deploy-prod --require-approval never

# Frontend to CloudFront
./deploy-frontend.sh   # Requires AWS_PROFILE with S3/CloudFront access
```

## UI Theme

Dark mode default (localStorage persisted, toggle in TopNav). Red accent Cloudscape theme. CSS custom properties with `--sa-*` prefix in `apps/web/src/index.css` — dark `:root` defaults, `body.sa-light` overrides. Primary: `#e8001c`. Portfolio-wide dark Amplify Authenticator sign-in page. Chat markdown rendered via `react-markdown` + `remark-gfm` with `.chat-markdown` styles. Toast notifications via Flashbar in AuthContext. Keyboard shortcuts: Ctrl+K (focus), Escape (close). Session sidebar with rename/delete. Responsive media queries for mobile.

## PSP Integration

Monitored by Project Status Portal. Test commands in `config.json`.
