# Scaffold AI

Generative UI platform for designing full-stack AWS serverless applications using a visual node graph editor and natural language chat. Built with AWS Cloudscape Design System for a professional, accessible, AWS console-style experience.

## Features

- **Visual Architecture Designer** — Drag-and-drop node graph editor powered by React Flow
- **Natural Language Chat** — Describe what you want to build and watch it appear on the canvas
- **Multi-Agent AI Workflow** — Intent classification → architecture design → security review → code generation
- **Security Gate** — AWS Well-Architected security validation blocks code generation for insecure designs
- **12 AWS Service Types** — Lambda, API Gateway, DynamoDB, Cognito, S3, SQS, SNS, EventBridge, Step Functions, Kinesis, CloudFront, Kinesis Streams
- **Multi-Format IaC** — Export to CDK (TypeScript), CloudFormation (YAML), or Terraform (HCL)
- **AWS Cloudscape UI** — Professional, accessible UI matching the AWS Console experience
- **Serverless-First** — Pay-per-request, event-driven patterns baked in
- **Multi-Tenant Ready** — SaaS architecture patterns with DynamoDB tenant isolation

## Tech Stack

| Layer | Technologies |
|-------|-------------|
| **Frontend** | Next.js 15, React 19, React Flow (@xyflow/react), Zustand, AWS Cloudscape Design System |
| **Backend** | FastAPI, LangGraph, LangChain, AWS Bedrock (Claude 3 Haiku) |
| **IaC Output** | AWS CDK (TypeScript), CloudFormation (SAM YAML), Terraform (HCL) |
| **Tooling** | pnpm 10, Turborepo 2, uv |

## Current Status

| Capability | Status | Notes |
|-----------|--------|-------|
| Chat → canvas architecture | Working | Falls back to rule-based if Bedrock unavailable |
| Security gate | Working | LLM review with static fallback |
| CDK (TypeScript) generation | Working | LLM-powered + static fallback |
| CloudFormation generation | Working | Static template; all 12 node types mapped correctly |
| Terraform generation | Working | Static template; all 12 node types mapped correctly |
| React/Cloudscape component generation | Partial | Generates layout.tsx + page.tsx for `frontend` nodes; static template only |
| Canvas layout algorithms | Working | Horizontal, vertical, grid, circular |
| Generated code viewer | Working | Tabbed modal via Side Navigation → Generated Code |
| CDK deployment integration | Not started | |
| Cost estimation | Not started | |

## Project Structure

```
scaffold-ai/
├── apps/
│   ├── web/                          # Next.js 15 frontend (port 3000)
│   │   ├── app/
│   │   │   ├── api/chat/route.ts     # Proxy → FastAPI backend
│   │   │   ├── layout.tsx
│   │   │   └── page.tsx              # Cloudscape AppLayout shell
│   │   ├── components/
│   │   │   ├── Canvas.tsx            # React Flow editor + toolbar
│   │   │   ├── Chat.tsx              # Chat panel + IaC selector + Generate button
│   │   │   ├── GeneratedCodeModal.tsx# Tabbed code viewer (Cloudscape Modal)
│   │   │   └── nodes/                # 12 AWS service node components
│   │   └── lib/
│   │       └── store.ts              # Zustand: useGraphStore + useChatStore
│   │
│   └── backend/                      # FastAPI + LangGraph (port 8000)
│       ├── pyproject.toml
│       ├── tests/
│       │   ├── test_main.py          # FastAPI endpoint tests
│       │   └── test_security_gate.py # LangGraph workflow integration tests
│       └── src/scaffold_ai/
│           ├── main.py               # FastAPI app, CORS, endpoints
│           ├── graph/
│           │   ├── state.py          # GraphState TypedDict + all type definitions
│           │   ├── workflow.py       # LangGraph DAG
│           │   └── nodes.py          # Node functions + LLM prompts (main logic)
│           ├── agents/
│           │   ├── architect.py
│           │   ├── cdk_specialist.py
│           │   ├── cloudformation_specialist.py
│           │   ├── terraform_specialist.py
│           │   ├── react_specialist.py   # Stub — not yet implemented
│           │   ├── interpreter.py
│           │   └── security_specialist.py
│           └── tools/
│               ├── git_operator.py
│               └── synthesizer.py
│
├── packages/
│   ├── ui/                           # Shared UI library (@scaffold-ai/ui)
│   ├── generated/
│   │   ├── infrastructure/           # IaC output landing zone
│   │   └── web/                      # Future: generated React components
│   ├── eslint-config/
│   └── typescript-config/
│
├── docs/
│   └── steering/                     # Cloudscape UI steering documentation
│       ├── foundations.md
│       ├── layout-patterns.md
│       ├── form-patterns.md
│       ├── table-and-collections.md
│       ├── navigation-patterns.md
│       ├── feedback-patterns.md
│       ├── charts-and-data-viz.md
│       └── genai-patterns.md
│
├── CLAUDE.md                         # AI assistant onboarding guide
└── turbo.json
```

## Getting Started

### Prerequisites

- Node.js 22+
- pnpm 10+
- Python 3.12+
- [uv](https://docs.astral.sh/uv/) (Python package manager)
- AWS account with Bedrock access (or use offline/fallback mode)

### Installation

```bash
git clone https://github.com/jfowler-cloud/scaffold-ai.git
cd scaffold-ai

# Install JS dependencies
pnpm install

# Install Python dependencies
cd apps/backend && uv sync && cd ../..
```

### Environment Variables

Create `apps/backend/.env` (copy from `.env.example`):

```env
# AWS Bedrock — Option 1: use AWS CLI profile (recommended)
AWS_REGION=us-east-1

# Option 2: explicit credentials
# AWS_ACCESS_KEY_ID=your_access_key
# AWS_SECRET_ACCESS_KEY=your_secret_key

# Model (optional — defaults to Claude 3 Haiku)
BEDROCK_MODEL_ID=us.anthropic.claude-3-haiku-20240307-v1:0
```

Create `apps/web/.env.local`:

```env
BACKEND_URL=http://localhost:8000
```

**AWS Setup:**
1. `aws configure` to set up CLI credentials
2. AWS Console → Bedrock → Model access → enable Anthropic Claude models
3. IAM user/role needs `bedrock:InvokeModel`

> **Offline / no-AWS mode:** If Bedrock is unreachable, the backend falls back to static security analysis and rule-based CDK generation. Chat messages that trigger LLM calls return friendly error text; the canvas and code viewer remain functional.

### Running

```bash
# From repo root — starts both services via Turborepo
pnpm dev

# Frontend:  http://localhost:3000
# Backend:   http://localhost:8000
# API docs:  http://localhost:8000/docs
```

## Usage

1. **Design your architecture**
   - Type in the chat panel: *"Build a todo app with user authentication"*
   - The AI creates nodes on the canvas (Cognito, API Gateway, Lambda, DynamoDB)
   - Drag and connect nodes to refine the design manually

2. **Select IaC format**
   - Use the dropdown above the chat input: CDK (TypeScript), CloudFormation (YAML), or Terraform (HCL)

3. **Generate infrastructure code**
   - Click **Generate Code** — the security gate runs first
   - If security passes, code is generated and stored
   - Open **Side Navigation → Generated Code** to view all files in a tabbed modal

4. **Deploy** (manual step)
   - Copy the generated files to your project
   - CDK: `cdk deploy`
   - CloudFormation/SAM: `sam deploy`
   - Terraform: `terraform init && terraform apply`

## How It Works

### Multi-Agent LangGraph Workflow

```
User message
    │
    ▼
interpret_intent          ← classifies: new_feature | modify_graph | generate_code | explain
    │
    ▼
architect_node            ← designs/updates graph JSON (nodes + edges)
    │
    ├─ intent != generate_code ──────────────────────────────────► END (return response)
    │
    ▼
security_review_node      ← evaluates against AWS Well-Architected security checklist
    │
    ├─ FAILED (score < 70 or critical issues) ───────────────────► END (return FAILED message)
    │
    ▼
cdk_specialist_node       ← generates IaC (CDK / CloudFormation / Terraform)
    │
    ▼
react_specialist_node     ← [stub] future Cloudscape component generation
    │
    ▼
END → ChatResponse { message, updated_graph, generated_files }
```

### Security Gate

Architectures are scored 0–100 before code generation:

| Criterion | Weight |
|-----------|--------|
| Authentication & authorization | 25 pts |
| Encryption at rest + in transit | 25 pts |
| Network security | 20 pts |
| Monitoring & logging | 15 pts |
| Well-Architected best practices | 15 pts |

**Scoring deductions:** −30 per critical issue, −15 per high, −5 per medium.
**Pass criteria:** score ≥ 70, zero critical issues, ≤ 3 high-severity issues.

When the LLM is unavailable, `SecuritySpecialistAgent` provides a rule-based static fallback that checks every node type for service-specific security controls.

### Node Types and IaC Coverage

| Canvas type | AWS Service | CDK | CloudFormation | Terraform |
|-------------|------------|:---:|:--------------:|:---------:|
| `frontend` | S3 + CloudFront | ✅ | — | — |
| `auth` | Cognito | ✅ | ✅ | ✅ |
| `api` | API Gateway | ✅ | ✅ | ✅ |
| `lambda` | Lambda | ✅ | ✅ | ✅ |
| `database` | DynamoDB | ✅ | ✅ | ✅ |
| `storage` | S3 | ✅ | ✅ | ✅ |
| `queue` | SQS + DLQ | ✅ | ✅ | ✅ |
| `events` | EventBridge | ✅ | ✅ | ✅ |
| `notification` | SNS | ✅ | ✅ | ✅ |
| `workflow` | Step Functions | ✅ | ✅ | ✅ |
| `cdn` | CloudFront | ✅ (commented) | — | — |
| `stream` | Kinesis | ✅ | ✅ | ✅ |

## Development

### Commands

```bash
# Root (Turborepo)
pnpm dev              # Start all services
pnpm build            # Build all packages
pnpm lint             # Lint all packages
pnpm dev:web          # Frontend only
pnpm dev:backend      # Backend only

# Backend
cd apps/backend
uv sync                                        # Install / sync Python deps
uv run pytest                                  # All tests
uv run pytest tests/test_main.py -v            # API endpoint tests
uv run pytest tests/test_security_gate.py -v   # Security gate tests
uv run ruff check src tests                    # Lint
uv run mypy src                                # Type check

# Frontend
cd apps/web
pnpm dev              # Dev server (Turbopack)
pnpm build
pnpm lint
pnpm type-check       # tsc --noEmit
```

### Adding a New AWS Service Node

1. `apps/web/components/nodes/<Name>Node.tsx` — create the React Flow node component
2. `apps/web/components/Canvas.tsx` — register in `nodeTypes` map and `nodeColors`
3. `apps/web/lib/store.ts` — add the type key to `NodeType` union and `typeOrder`
4. `apps/backend/src/scaffold_ai/graph/nodes.py` — add a branch in `generate_secure_cdk_template` and in the architect prompt's node type list
5. `apps/backend/src/scaffold_ai/agents/cdk_specialist.py` — add CDK generation template

### Cloudscape Component Patterns

Always import components individually for tree-shaking:

```tsx
import Button from '@cloudscape-design/components/button';
import Container from '@cloudscape-design/components/container';
import SpaceBetween from '@cloudscape-design/components/space-between';

// Event pattern — always destructure { detail }
<Input
  value={value}
  onChange={({ detail }) => setValue(detail.value)}
/>

// Spacing pattern
<SpaceBetween size="l">
  <FormField label="Name"><Input /></FormField>
</SpaceBetween>
```

Reference patterns in `docs/steering/`.

## Testing

### Running tests

```bash
cd apps/backend
uv run pytest -v                     # Full suite (requires AWS credentials for LLM calls)
uv run pytest tests/test_main.py -v  # API tests (no AWS needed)
```

Tests use `pytest-asyncio` with `asyncio_mode = "auto"`. LLM-hitting tests require Bedrock credentials; without them the LLM calls fail and workflow nodes fall back to static logic — which means test assertions about LLM-generated content may still pass via the fallback path.

### Existing coverage

| Area | File | Notes |
|------|------|-------|
| FastAPI endpoints (`/`, `/health`, `/api/graph`, `/api/chat`) | `test_main.py` | Basic happy-path only |
| Security gate — insecure architecture blocked | `test_security_gate.py` | ✅ |
| Security gate — secure architecture passes | `test_security_gate.py` | ✅ |
| Security gate — empty architecture | `test_security_gate.py` | ✅ |
| Security gate — non-generate intent skips review | `test_security_gate.py` | ✅ |

### Test coverage gaps (areas needing tests)

The following areas have no automated coverage and should be prioritized:

#### High priority — backend unit tests

- **`interpret_intent` fallback** — mock LLM failure; assert keyword-based intent classification works for each intent keyword set
- **`architect_node` JSON parsing** — test recovery from malformed JSON, code-fenced JSON (`\`\`\`json`), and missing keys
- **`generate_node_positions`** — pure function; test column assignment per node type and row stacking for duplicate types
- **`SecuritySpecialistAgent.review`** — unit test every node-type branch (storage, database, api, lambda, queue, auth) independently; verify scoring arithmetic
- **`cdk_specialist.py` `_generate_stack`** — assert correct CDK constructs emitted for every node type; verify deduplication of imports
- **`CloudFormationSpecialistAgent.generate`** — assert all 12 node types produce the expected resource types in `Resources`; verify DLQ is created alongside queue; verify Outputs only reference ARN-capable resource types
- **`TerraformSpecialistAgent.generate`** — assert all 12 node types produce valid HCL blocks; verify `slug` variable generates correct resource names; verify outputs section
- **`cdk_specialist_node`** — test all three IaC format branches (cdk / cloudformation / terraform) with a mock graph
- **`security_gate` router function** — unit test both "passed" and "failed" return values directly

#### High priority — frontend unit tests (no test suite exists yet)

Recommended: Vitest + @testing-library/react.

- **`useGraphStore`** — `addNode`, `removeNode`, `onConnect`, `setGraph`, `applyLayout` (all four modes); assert node positions after layout
- **`useChatStore`** — `addMessage`, `setGeneratedFiles`, `clearMessages`
- **`Canvas`** — render test: all 12 node types appear in the dropdowns
- **`Chat`** — Generate Code button disabled when `nodes.length === 0`; input clears after submit
- **`GeneratedCodeModal`** — empty-state render; tabs render when files are populated
- **API route (`app/api/chat/route.ts`)** — mock `fetch`; test 502/503 graceful fallback message, successful response forwarding, fetch TypeError handling

#### Medium priority — integration / E2E

- Full round-trip: chat input → canvas updated → generate code → modal shows file content
- Security gate integration: submit insecure architecture with `generate_code` intent; assert response contains "FAILED" and `generated_files` is empty
- `iac_format` variants: one test per format (cdk, cloudformation, terraform) through the full `/api/chat` endpoint

## Known Issues

### CORS allows only localhost:3000

`apps/backend/src/scaffold_ai/main.py` hard-codes `allow_origins=["http://localhost:3000"]`. Any non-local deployment requires updating this value or making it configurable via an environment variable.

### Generated files are not persisted to disk

Generated files are returned in the API response and kept in client-side Zustand state only. Refreshing the browser clears them. The `packages/generated/` directory has placeholder `.gitkeep` files but nothing writes there at runtime.

### React component generation is static template only

`react_specialist_node` calls `ReactSpecialistAgent.generate()` which produces a generic Cloudscape `layout.tsx` + `page.tsx` regardless of the specific architecture. It only fires when there is a `frontend` node; other node types do not yet influence the generated components. True LLM-driven, architecture-aware component generation is not yet implemented.

### CDK fallback template uses inline Lambda code

The static CDK fallback in `generate_secure_cdk_template` uses `lambda.Code.fromInline(...)`. This is appropriate for scaffolding but not for real deployments — generated stacks need to be updated to reference actual handler code before deploying.

### CloudFormation SAM template requires SAM CLI for deploy

The generated CloudFormation output uses the `AWS::Serverless` transform. Deploying requires `sam deploy` (not `aws cloudformation deploy` directly).

## Roadmap

### Near-term

- [ ] Add frontend unit test suite (Vitest + Testing Library)
- [ ] Add backend unit tests for node functions with mocked LLM (no AWS credentials needed)
- [ ] Make CORS origins configurable via environment variable
- [ ] LLM-driven React component generation (architecture-aware Cloudscape components)
- [ ] Persist generated files to `packages/generated/` on disk at generation time
- [ ] CDK CloudFront (`cdn`) node — currently generates a comment placeholder only

### Medium-term

- [ ] Persist generated files to `packages/generated/` on disk
- [ ] Python CDK support
- [ ] Multi-stack architectures (split large graphs into nested stacks)
- [ ] Architecture templates library (pre-built patterns)
- [ ] CDK deployment integration (`cdk deploy` from the UI)

### Longer-term

- [ ] Cost estimation per architecture
- [ ] Collaboration / sharing features
- [ ] Real-time streaming for long generation tasks
- [ ] Security recommendation auto-apply (add missing nodes/config automatically)
- [ ] Security score history tracking

## Architecture Patterns

### Serverless-First API

```
Frontend → API Gateway → Lambda → DynamoDB
                      ↘ SQS → Lambda (async workers)
```

### Multi-Tenant SaaS

```
Cognito (JWT with tenant claims)
    ↓
API Gateway → Lambda Authorizer (extract tenantId from JWT)
    ↓
Lambda → DynamoDB
         pk: ${tenantId}#${entityType}#${id}
         sk: metadata | #{relationType}#${relatedId}
```

### Event-Driven

```
Lambda → EventBridge → [Lambda, SQS, SNS, Step Functions]
```

### File Upload

```
Frontend → API Gateway → Lambda (generate presigned URL)
Frontend → S3 (direct upload) → Lambda trigger → DynamoDB (metadata)
```

## Steering Documentation

Cloudscape UI patterns are documented in `docs/steering/` for AI assistants and developers:

| File | Purpose |
|------|---------|
| `foundations.md` | Design tokens, spacing, colors, typography, theming |
| `layout-patterns.md` | AppLayout, ContentLayout, Container, Grid, SpaceBetween |
| `form-patterns.md` | Form, FormField, Input, Select, validation |
| `table-and-collections.md` | Table, Cards, filtering, pagination, useCollection |
| `navigation-patterns.md` | SideNavigation, Tabs, BreadcrumbGroup, Button |
| `feedback-patterns.md` | Alert, Flashbar, Modal, StatusIndicator, Spinner |
| `charts-and-data-viz.md` | LineChart, BarChart, PieChart patterns |
| `genai-patterns.md` | ChatBubble, PromptInput, Avatar, LoadingBar for AI |

For AI assistant onboarding, see [`CLAUDE.md`](./CLAUDE.md).

## Acknowledgments

- [AWS Cloudscape Design System](https://cloudscape.design) — UI components
- [React Flow](https://reactflow.dev) — Node graph visualization
- [LangGraph](https://github.com/langchain-ai/langgraph) — Multi-agent orchestration
- [kiro-powers (praveenc)](https://github.com/praveenc/kiro-powers) — Cloudscape steering docs
- [kiro-powers (official)](https://github.com/kirodotdev/powers) — AWS IaC, Cloud Architect, SaaS Builder patterns

## License

MIT
