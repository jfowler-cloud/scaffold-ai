# CLAUDE.md — Scaffold AI

This file provides context for AI assistants working on the Scaffold AI codebase.

## Project Overview

Scaffold AI is a generative UI platform for visually designing full-stack AWS serverless architectures. Users describe what they want to build using natural language chat, and the system:

1. Displays an interactive node graph (React Flow canvas) populated by AI-generated AWS service components
2. Runs a multi-agent LangGraph workflow (intent → architect → security → code generation)
3. Generates production-ready Infrastructure as Code in CDK (TypeScript), CloudFormation (YAML), or Terraform (HCL)

The frontend is built with AWS Cloudscape Design System for an AWS Console-style experience.

---

## Repository Structure

```
scaffold-ai/
├── apps/
│   ├── web/                          # Next.js 15 frontend (port 3000)
│   │   ├── app/
│   │   │   ├── api/chat/route.ts     # API proxy to FastAPI backend
│   │   │   ├── layout.tsx
│   │   │   └── page.tsx              # Main page with Cloudscape AppLayout
│   │   ├── components/
│   │   │   ├── Canvas.tsx            # React Flow graph editor
│   │   │   ├── Chat.tsx              # Chat panel with IaC format selector
│   │   │   ├── GeneratedCodeModal.tsx# Tabbed code viewer modal
│   │   │   └── nodes/                # 12 AWS service node components
│   │   └── lib/
│   │       └── store.ts              # Zustand state (useGraphStore, useChatStore)
│   │
│   └── backend/                      # FastAPI + LangGraph (port 8000)
│       ├── pyproject.toml
│       └── src/scaffold_ai/
│           ├── main.py               # FastAPI app, CORS, /api/chat endpoint
│           ├── graph/
│           │   ├── state.py          # GraphState TypedDict, all type definitions
│           │   ├── workflow.py       # LangGraph DAG definition
│           │   └── nodes.py          # All node functions + LLM prompts
│           ├── agents/
│           │   ├── architect.py          # ARCHITECT_SYSTEM_PROMPT + ArchitectAgent
│           │   ├── cdk_specialist.py     # CDK_SYSTEM_PROMPT + CDKSpecialistAgent
│           │   ├── cloudformation_specialist.py
│           │   ├── terraform_specialist.py
│           │   ├── react_specialist.py
│           │   ├── interpreter.py
│           │   └── security_specialist.py # Security review + fallback static analysis
│           └── tools/
│               ├── git_operator.py
│               └── synthesizer.py
│
├── packages/
│   ├── ui/                           # Shared UI components (@scaffold-ai/ui)
│   ├── generated/
│   │   ├── infrastructure/           # Generated CDK/CF/Terraform output
│   │   └── web/                      # Generated React component output
│   ├── eslint-config/
│   └── typescript-config/
│
├── docs/
│   └── steering/                     # AI steering docs (Cloudscape, CDK, SaaS patterns)
│       ├── foundations.md
│       ├── layout-patterns.md
│       ├── form-patterns.md
│       ├── table-and-collections.md
│       ├── navigation-patterns.md
│       ├── feedback-patterns.md
│       ├── charts-and-data-viz.md
│       └── genai-patterns.md
│
├── package.json                      # Root: pnpm + Turborepo scripts
├── pnpm-workspace.yaml
└── turbo.json
```

---

## Tech Stack

| Layer | Technology | Version |
|-------|-----------|---------|
| Frontend framework | Next.js | 15.2.0 |
| UI library | React | 19 |
| Graph editor | @xyflow/react (React Flow) | 12 |
| State management | Zustand | 5 |
| UI components | AWS Cloudscape Design System | 3+ |
| Backend framework | FastAPI | 0.115+ |
| AI orchestration | LangGraph | 0.2+ |
| LLM provider | AWS Bedrock (Claude 3 Haiku) | — |
| Python package manager | uv | — |
| JS package manager | pnpm | 10.30 |
| Build orchestration | Turborepo | 2.5 |
| Node.js | — | >=22 |
| Python | — | >=3.12 |

---

## Development Commands

### From the repo root (Turborepo)

```bash
pnpm dev           # Start both frontend (3000) and backend (8000)
pnpm build         # Build all packages
pnpm lint          # Lint all packages
pnpm dev:web       # Frontend only
pnpm dev:backend   # Backend only
```

### Backend (apps/backend)

```bash
# Run with uv (backend package manager)
uv run uvicorn scaffold_ai.main:app --reload --host 0.0.0.0 --port 8000

# Testing
uv run pytest                     # All tests
uv run pytest tests/test_main.py  # API tests only
uv run pytest tests/test_security_gate.py  # Security gate tests

# Linting / type checking
uv run ruff check src tests
uv run mypy src
```

### Frontend (apps/web)

```bash
# From apps/web or via Turborepo filter
next dev --turbopack   # Dev server (Turbopack enabled)
next build
next lint
tsc --noEmit           # Type check
```

---

## Environment Variables

The backend reads `.env` from `apps/backend/`. Copy `.env.example` to get started:

```env
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_access_key       # Or use AWS CLI profiles
AWS_SECRET_ACCESS_KEY=your_secret_key
BEDROCK_MODEL_ID=us.anthropic.claude-3-haiku-20240307-v1:0  # Optional, this is the default
```

The Next.js frontend reads:

```env
BACKEND_URL=http://localhost:8000  # Set in apps/web/.env or root .env
```

AWS credentials can also be provided via `aws configure` (recommended for local development). The IAM user/role needs `bedrock:InvokeModel` permission.

---

## Architecture & Data Flow

### Request lifecycle (chat message)

```
Browser → POST /api/chat (Next.js route handler)
        → POST http://localhost:8000/api/chat (FastAPI)
        → LangGraph workflow:
            1. interpret_intent  (Claude classifies: new_feature | modify_graph | generate_code | explain)
            2. architect_node    (Claude designs graph JSON with nodes + edges)
            3. security_review_node  [only if intent == generate_code]
            4. security_gate router  → "passed" | "failed"
            5. cdk_specialist_node   [only if security passed]
            6. react_specialist_node [stub, generates future Cloudscape components]
        → ChatResponse { message, updated_graph, generated_files }
        → Frontend updates Canvas (setGraph) and stores generated files
```

### LangGraph workflow (apps/backend/src/scaffold_ai/graph/workflow.py)

```
interpret → architect → [should_generate_code?]
                            ↓ "generate"
                        security_review → [security_gate?]
                                              ↓ "passed"
                                          cdk_specialist → react_specialist → END
                                              ↓ "failed"
                                          END (response contains FAILED message)
                            ↓ "respond"
                        END
```

### Security Gate

- Runs before every code generation request
- Score 0–100; pass criteria: **no critical issues** and **≤3 high-severity issues**
- Falls back to `SecuritySpecialistAgent.review()` (static rule-based) if LLM call fails
- Scoring: `-30` per critical, `-15` per high, `-5` per medium issue

### IaC format selection

The frontend sends `iac_format` (`cdk` | `cloudformation` | `terraform`) with every request.
`cdk_specialist_node` in `nodes.py` dispatches to the appropriate specialist agent class.
Generated files land in `packages/generated/infrastructure/`.

---

## Key Source Files

| File | Purpose |
|------|---------|
| `apps/backend/src/scaffold_ai/graph/state.py` | All TypedDicts: `GraphState`, `SecurityReview`, `GeneratedFile` |
| `apps/backend/src/scaffold_ai/graph/nodes.py` | LLM prompts + all node functions; main logic lives here |
| `apps/backend/src/scaffold_ai/graph/workflow.py` | LangGraph DAG wiring |
| `apps/backend/src/scaffold_ai/main.py` | FastAPI app: `ChatRequest`, `ChatResponse`, `/api/chat` |
| `apps/backend/src/scaffold_ai/agents/security_specialist.py` | Security review logic + fallback static analysis |
| `apps/backend/src/scaffold_ai/agents/cdk_specialist.py` | CDK TypeScript generation agent |
| `apps/web/lib/store.ts` | Zustand stores: `useGraphStore`, `useChatStore` |
| `apps/web/components/Canvas.tsx` | React Flow canvas, node type registry, layout controls |
| `apps/web/components/Chat.tsx` | Chat UI, IaC format selector, Generate Code button |
| `apps/web/app/api/chat/route.ts` | Next.js API route proxying to FastAPI |
| `apps/web/app/page.tsx` | Cloudscape AppLayout: top nav, side nav, split panel, help panel |

---

## Node Types

The canvas supports exactly 12 AWS service node types. Both frontend and backend must agree on these identifiers:

| Type key | AWS Service | Frontend component |
|----------|------------|-------------------|
| `frontend` | Next.js / React on S3+CloudFront | `FrontendNode.tsx` |
| `auth` | Cognito User Pool | `AuthNode.tsx` |
| `api` | API Gateway REST/HTTP | `APINode.tsx` |
| `lambda` | Lambda Function | `LambdaNode.tsx` |
| `database` | DynamoDB | `DatabaseNode.tsx` |
| `storage` | S3 Bucket | `StorageNode.tsx` |
| `queue` | SQS Queue | `QueueNode.tsx` |
| `events` | EventBridge | `EventsNode.tsx` |
| `notification` | SNS Topic | `NotificationNode.tsx` |
| `workflow` | Step Functions | `WorkflowNode.tsx` |
| `cdn` | CloudFront | `CdnNode.tsx` |
| `stream` | Kinesis Data Streams | `StreamNode.tsx` |

### Adding a new node type

1. Create `apps/web/components/nodes/<Name>Node.tsx`
2. Register it in `nodeTypes` map in `apps/web/components/Canvas.tsx`
3. Add a color to `nodeColors` in `Canvas.tsx`
4. Add the type to `NodeType` union in `apps/web/lib/store.ts`
5. Add layout column order in `typeOrder` in `store.ts`
6. Add CDK generation logic in `apps/backend/src/scaffold_ai/graph/nodes.py` (`generate_secure_cdk_template`) and in `apps/backend/src/scaffold_ai/agents/cdk_specialist.py`
7. Update the architect prompt's node type list in `nodes.py`

---

## State Management (Frontend)

Two Zustand stores in `apps/web/lib/store.ts`:

**`useGraphStore`** — React Flow graph state
- `nodes: AppNode[]`, `edges: Edge[]`, `selectedNode`
- `setGraph(nodes, edges)` — called when backend returns `updated_graph`
- `addNode`, `removeNode`, `updateNode`
- `applyLayout(type)` — rearranges nodes (horizontal / vertical / grid / circular)

**`useChatStore`** — Chat state
- `messages: Message[]`, `isLoading: boolean`
- `generatedFiles: GeneratedFile[]` — populated when code generation succeeds
- `setGeneratedFiles(files)` — triggers display in `GeneratedCodeModal`

---

## Backend State (`GraphState`)

All LangGraph nodes receive and return `GraphState` (defined in `state.py`):

```python
class GraphState(TypedDict):
    user_input: str          # Raw user message
    intent: Intent           # Classified intent
    graph_json: dict         # React Flow graph { nodes, edges }
    iac_format: str          # "cdk" | "cloudformation" | "terraform"
    security_review: SecurityReview | None
    generated_files: list[GeneratedFile]
    errors: list[str]
    retry_count: int
    response: str            # Final message to return to user
```

Nodes return `{**state, <updated_keys>}` to preserve all prior state.

---

## Coding Conventions

### Python (backend)

- Python 3.12+, type hints required
- `TypedDict` for all structured data (no Pydantic in the graph layer)
- Async node functions: `async def node_name(state: GraphState) -> GraphState`
- LLM calls via `ChatBedrock` from `langchain_aws`; always `await llm.ainvoke(messages)`
- JSON parsing with fallback: strip markdown code fences, then `json.loads()`
- All exceptions caught and logged; return graceful error state, never raise from nodes
- Tests use `pytest-asyncio` with `asyncio_mode = "auto"` (no `@pytest.mark.asyncio` needed on every test, but it is present in existing tests)

### TypeScript (frontend)

- Strict TypeScript throughout
- Cloudscape components imported individually for tree-shaking:
  `import Button from '@cloudscape-design/components/button'`
- Cloudscape event pattern: `onChange={({ detail }) => setValue(detail.value)}`
- React Flow nodes receive `data: { label, type, config? }` via `AppNode`
- No direct DOM manipulation; use React state and Cloudscape components

### Cloudscape UI patterns

- Use `SpaceBetween` for consistent spacing between components
- Use `Container` with `Header` for page sections
- Use `AppLayout` with `splitPanel` for the main page shell
- Use `ButtonDropdown` for multi-option actions
- Use `Select` with `{ label, value }` options; handle via `detail.selectedOption`
- Use `Textarea` instead of `Input` for multi-line chat input

---

## Testing

### Backend tests

Located in `apps/backend/tests/`. Run with `uv run pytest`.

- `test_main.py` — FastAPI endpoint tests using `httpx.AsyncClient` with `ASGITransport`
- `test_security_gate.py` — LangGraph workflow integration tests

Test isolation: tests call the real LangGraph workflow; LLM calls will fail without AWS credentials. Ensure AWS credentials are configured or mock the LLM if running offline.

### Frontend tests

No frontend test suite exists yet. TypeScript type checking via `tsc --noEmit`.

---

## Generated Code Output

Generated files are returned in `ChatResponse.generated_files` as `[{ path, content }]`.
The frontend stores them in `useChatStore.generatedFiles` and displays them in `GeneratedCodeModal.tsx`.

| Format | Output path |
|--------|------------|
| CDK (TypeScript) | `packages/generated/infrastructure/lib/scaffold-ai-stack.ts` |
| CloudFormation | `packages/generated/infrastructure/template.yaml` |
| Terraform | `packages/generated/infrastructure/main.tf` |

The `packages/generated/` directory has placeholder `.gitkeep` files and is intended for AI-generated output.

---

## Security Model

The security gate enforces AWS Well-Architected security best practices before any code is generated:

- **Authentication**: API Gateway must have auth (Cognito/IAM/Lambda authorizer)
- **Encryption**: S3 (SSE), DynamoDB (at-rest), SQS (KMS), Kinesis (managed)
- **Access control**: Least-privilege IAM (use grant methods, no wildcards)
- **Resilience**: DLQ on SQS, PITR on DynamoDB, S3 versioning
- **Monitoring**: X-Ray tracing on Lambda and API Gateway, CloudWatch logging

The static fallback in `SecuritySpecialistAgent` scores architectures even when the LLM is unavailable. Score thresholds: pass requires score ≥70 with no critical issues and ≤3 high-severity issues.

---

## Common Workflows for AI Assistants

### Adding a new IaC format

1. Create `apps/backend/src/scaffold_ai/agents/<format>_specialist.py` with an agent class implementing `async def generate(self, graph: dict) -> str`
2. Add a branch in `cdk_specialist_node` in `nodes.py` for the new format
3. Add the option to the `Select` component in `apps/web/components/Chat.tsx`

### Modifying the LangGraph workflow

Edit `apps/backend/src/scaffold_ai/graph/workflow.py`. The workflow uses `StateGraph(GraphState)`. After adding nodes/edges, recompile via `workflow.compile()`.

### Modifying system prompts

All LLM prompts live in `apps/backend/src/scaffold_ai/graph/nodes.py` (as module-level string constants) and in the `agents/` directory (as class attributes). Update the relevant prompt string; no structural changes needed.

### Debugging the backend

Run with `--reload` and check stdout for `print()` statements in node functions. LLM errors fall back to static logic. FastAPI auto-generates docs at `http://localhost:8000/docs`.

### Adding Cloudscape components to the frontend

Follow the patterns in `docs/steering/`. Import components individually:

```tsx
import Button from '@cloudscape-design/components/button';
import SpaceBetween from '@cloudscape-design/components/space-between';
```

Do not import from `@cloudscape-design/components` directly (no tree-shaking).
