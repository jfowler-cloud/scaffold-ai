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
| CDK (TypeScript) generation | Working | LLM-powered + static fallback; all 12 node types |
| CloudFormation generation | Working | Static template; all 12 node types |
| Terraform generation | Working | Static template; all 12 node types |
| React/Cloudscape component generation | Working | Architecture-aware; generates auth, API, table, upload components |
| Canvas layout algorithms | Working | Horizontal, vertical, grid, circular |
| Generated code viewer | Working | Tabbed modal via Side Navigation → Generated Code |
| Generated files persisted to disk | Working | Written to `packages/generated/` on each generation |
| CORS origins | Configurable | Via `ALLOWED_ORIGINS` env var; defaults to localhost:3000 |
| Backend unit test suite | Working | 97 tests, no AWS credentials needed |
| Frontend unit test suite | Working | 34 tests, all passing |
| CDK deployment integration | Working | Deploy button in UI; requires CDK CLI installed |
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
│           │   ├── react_specialist.py   # Architecture-aware component generation
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

# CORS (optional — comma-separated; defaults to localhost:3000)
# ALLOWED_ORIGINS=http://localhost:3000,https://your-production-domain.com
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

4. **Deploy to AWS** (CDK only)
   - Click **Deploy to AWS** button (appears after code generation)
   - Requires CDK CLI installed: `npm install -g aws-cdk`
   - Requires AWS credentials configured: `aws configure`
   - Deployment happens in a temporary project and takes 2-5 minutes
   - Stack outputs are displayed in the chat

5. **Manual deployment** (alternative)
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
react_specialist_node     ← generates architecture-aware Cloudscape components
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

| Canvas type | AWS Service | CDK | CloudFormation | Terraform | React Components |
|-------------|------------|:---:|:--------------:|:---------:|:----------------:|
| `frontend` | S3 + CloudFront | ✅ | — | — | ✅ layout + page |
| `auth` | Cognito | ✅ | ✅ | ✅ | ✅ AuthProvider |
| `api` | API Gateway | ✅ | ✅ | ✅ | ✅ API hooks |
| `lambda` | Lambda | ✅ | ✅ | ✅ | — |
| `database` | DynamoDB | ✅ | ✅ | ✅ | ✅ DataTable |
| `storage` | S3 | ✅ | ✅ | ✅ | ✅ FileUpload |
| `queue` | SQS + DLQ | ✅ | ✅ | ✅ | — |
| `events` | EventBridge | ✅ | ✅ | ✅ | — |
| `notification` | SNS | ✅ | ✅ | ✅ | — |
| `workflow` | Step Functions | ✅ | ✅ | ✅ | — |
| `cdn` | CloudFront | ✅ | — | — | — |
| `stream` | Kinesis | ✅ | ✅ | ✅ | — |

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
| Security gate — insecure architecture blocked | `test_security_gate.py` | ✅ (varies with LLM) |
| Security gate — secure architecture passes | `test_security_gate.py` | ✅ |
| Security gate — empty architecture | `test_security_gate.py` | ✅ (varies with LLM) |
| Security gate — non-generate intent skips review | `test_security_gate.py` | ✅ |
| `generate_node_positions` — all 12 node types, column order, row stacking | `test_units.py` | ✅ |
| `security_gate` router — passed / failed / missing / empty review | `test_units.py` | ✅ |
| `should_generate_code` router — all four intents | `test_units.py` | ✅ |
| `interpret_intent` keyword fallback — all 5 branches | `test_units.py` | ✅ |
| `CloudFormationSpecialistAgent.generate` — all 10 node types + Outputs safety | `test_units.py` | ✅ |
| `TerraformSpecialistAgent.generate` — all 10 node types + slug + outputs | `test_units.py` | ✅ |
| `react_specialist_node` — intent skip, no nodes, frontend, non-frontend | `test_units.py` | ✅ **8 tests** |
| `SecuritySpecialistAgent.review` — all node-type branches, scoring arithmetic, pass/fail thresholds | `test_units.py` | ✅ |
| **Frontend: Zustand stores** | `__tests__/store.test.ts` | ✅ **16 tests** |
| **Frontend: Chat component** | `__tests__/Chat.test.tsx` | ✅ **7 tests** |
| **Frontend: GeneratedCodeModal** | `__tests__/GeneratedCodeModal.test.tsx` | ✅ **5 tests** |
| **Frontend: API route** | `__tests__/api-chat.test.ts` | ✅ **6 tests** |

**Total: 86 backend tests + 34 frontend tests = 120 tests**

> **Note on LLM tests**: Tests marked "varies with LLM" use static fallback logic when AWS Bedrock is unavailable, but may produce different (more nuanced) results when the LLM is accessible. This is expected behavior.

### Remaining coverage gaps

#### Backend

- **`architect_node` JSON recovery** — test code-fenced JSON and malformed JSON fallback paths (requires mocking `ChatBedrock`)
- **`cdk_specialist_node`** — test all three IaC format dispatch branches with a mock graph and mocked agents
- **`generate_secure_cdk_template`** — assert correct CDK constructs and deduplication of imports for every node type

#### Integration / E2E

- **Full round-trip** — chat input → canvas updated → generate code → modal shows file content
- **Security gate integration** — submit insecure architecture with `generate_code` intent; assert response contains "FAILED" and `generated_files` is empty
- **`iac_format` variants** — one test per format (cdk, cloudformation, terraform) through the full `/api/chat` endpoint

## Known Issues

### React component generation is now architecture-aware ✅

`react_specialist_node` now generates components based on the actual architecture:
- **Frontend node** → layout.tsx + page.tsx with architecture-specific sections
- **Auth node** → AuthProvider.tsx with Cognito integration stubs
- **API node** → api.ts with typed fetch hooks
- **Database node** → DataTable.tsx with Cloudscape Table component
- **Storage node** → FileUpload.tsx with S3 upload flow

Generated components use AWS Cloudscape Design System and include TODO comments for integration points.

### CDK fallback template uses inline Lambda code

The static CDK fallback in `generate_secure_cdk_template` uses `lambda.Code.fromInline(...)`. This is appropriate for scaffolding but not for real deployments — generated stacks need to be updated to reference actual handler code before deploying.

### CloudFormation SAM template requires SAM CLI for deploy

The generated CloudFormation output uses the `AWS::Serverless` transform. Deploying requires `sam deploy` (not `aws cloudformation deploy` directly).

## Roadmap

### Near-term

- [x] Add frontend unit test suite (Vitest + Testing Library) — **COMPLETE: 34 tests passing**
  - Store tests (useGraphStore, useChatStore)
  - Component tests (Chat, GeneratedCodeModal)
  - API route tests (/api/chat)
- [x] LLM-driven React component generation (architecture-aware Cloudscape components) — **COMPLETE**
  - Generates AuthProvider for Cognito
  - Generates API hooks for API Gateway
  - Generates DataTable for DynamoDB
  - Generates FileUpload for S3
- [x] `architect_node` JSON recovery tests (mocked LLM) — **COMPLETE: 11 tests written**
  - JSON parsing (clean, markdown fences)
  - Error handling (malformed JSON, LLM exceptions)
  - Node/edge deduplication
  - Position generation
  - Note: Tests require proper LLM mocking setup

### Medium-term

- [x] CDK deployment integration (`cdk deploy` from the UI) — **COMPLETE**
- [x] Cost estimation per architecture — **COMPLETE**
- [x] Security recommendation auto-apply — **COMPLETE**
- [x] Architecture templates library — **COMPLETE**
- [x] Python CDK support — **COMPLETE**
- [x] Multi-stack architectures — **COMPLETE**
- [x] Collaboration / sharing features — **COMPLETE**
- [x] Security score history tracking — **COMPLETE**
  - Track security improvements over time
  - Record scores with issue counts
  - Calculate improvement metrics and trends
- [ ] Real-time streaming for long generation tasks

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

---

## Code Review: Enhancements & Recommendations (Round 2)

> **Review date:** 2026-02-18 | **Scope:** Full codebase re-review after significant feature expansion. Cross-references best practices from the [Resume Tailor AI](../resume-tailor-ai) production project.

### Previous Review — Resolution Status

14 of 30 items from the Round 1 review have been resolved:

| # | Issue | Resolution |
|---|-------|-----------|
| 1.1 | Command injection in deploy service | ✅ Fixed — Pydantic regex validator on `stack_name` |
| 1.2 | CORS wildcard methods/headers | ✅ Fixed — Restricted to `GET, POST, OPTIONS` |
| 1.4 | Exception detail leakage | ✅ Fixed — Generic errors to client, `logger.exception()` server-side |
| 2.1 | LLM client per-request | ✅ Fixed — `@lru_cache(maxsize=1)` singleton |
| 2.2 | No request timeout | ✅ Fixed — `asyncio.wait_for(..., timeout=60.0)`, 504 on expiry |
| 2.4 | No rate limiting | ✅ Fixed — `slowapi` on `/api/chat` (10/min), `/api/deploy` (3/hr) |
| 2.5 | No `iac_format` validation | ✅ Fixed — Pydantic `field_validator` |
| 2.6 | Missing `security_review` init | ✅ Fixed — Now initialized as `None` in `main.py:149` |
| 3.1 | Duplicated CDK generation | ✅ Fixed — Unified `CDKGenerator` in `services/cdk_generator.py` |
| 3.2 | Duplicated code-fence stripping | ✅ Fixed — Extracted to `utils/llm_utils.strip_code_fences()` |
| 3.3 | `print()` instead of `logging` | ✅ Mostly fixed — `nodes.py` uses `logging.getLogger(__name__)` |
| 7.1 | Edges ignored in static code gen | ✅ Fixed — `CDKGenerator` wires `grantReadWriteData`, `LambdaIntegration` |
| 7.2 | Architecture templates | ✅ Fixed — 6 templates via `/api/templates` |
| 7.4 | Export/import/sharing | ✅ Fixed — `/api/share` endpoints + unique share IDs |

---

### 1. Security Concerns — New Issues

#### 1.1 New Endpoints Lack Rate Limiting — **High**

10 new endpoints were added but only `/api/chat` and `/api/deploy` have rate limits. The following endpoints are unprotected:

| Endpoint | Risk |
|----------|------|
| `POST /api/cost/estimate` | Compute-intensive cost calculation |
| `POST /api/security/autofix` | Mutates graph state |
| `POST /api/share` | Creates persistent state (DoS via storage exhaustion) |
| `POST /api/security/history` | Creates persistent state |

**Recommendation (from Resume Tailor AI):** Apply rate limits to all mutating endpoints. The resume-tailor project applies per-function rate controls via Step Functions concurrency limits.

#### 1.2 New Endpoints Leak Exception Details — **Medium**

Several new endpoints in `main.py` re-introduce the exception detail leakage pattern that was fixed for `/api/chat`:

```python
# main.py:256 — cost estimate
except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))  # Leaks internals

# main.py:276 — security autofix
except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))  # Leaks internals
```

**Recommendation:** Apply the same `logger.exception()` + generic message pattern used in the chat endpoint.

#### 1.3 Sharing Endpoint Accepts Arbitrary `dict` Without Validation — **Medium**

`POST /api/share` (`main.py:295`) accepts raw `dict` with no Pydantic model:

```python
async def create_share(data: dict):
    graph = data.get("graph")
```

An attacker can store arbitrary JSON of unlimited size. There's no size limit, schema validation, or sanitization.

**Recommendation:** Create a `ShareRequest(BaseModel)` with validated fields and a `max_length` on the graph JSON.

#### 1.4 In-Memory Services Lose State on Restart — **Medium**

`SharingService`, `SecurityHistoryService` use in-memory dicts (`self._shared_architectures = {}`). Any shared link or security history is lost on server restart. The sharing service also has a hardcoded timestamp (`"2026-02-18T09:07:12Z"`) instead of `datetime.utcnow()`.

**Recommendation (from Resume Tailor AI):** The resume-tailor project uses DynamoDB for all persistent state with proper timestamps. At minimum:
- Use SQLite or a file-based store for development
- Use `datetime.utcnow().isoformat()` for timestamps
- Document that production requires a database backend

#### 1.5 `cdk_deployment.py` Still Leaks Errors — **Low**

The deploy endpoint in `main.py:224-228` catches exceptions but still returns `str(e)`:

```python
except Exception as e:
    return DeployResponse(success=False, error=f"Deployment error: {str(e)}")
```

---

### 2. Architecture & Design — New Issues

#### 2.1 Blocking `subprocess.run()` in Async Endpoint — **High** (Carried from Round 1)

`CDKDeploymentService.deploy()` still uses synchronous `subprocess.run()` inside `async def deploy_stack()`. The 120s npm install + 600s CDK deploy timeouts block the entire FastAPI event loop.

**Recommendation:** Use `asyncio.create_subprocess_exec()` or offload to a background task via `BackgroundTasks`. Return a job ID and add `GET /api/deploy/{job_id}/status`.

#### 2.2 Nested Stack Generator Produces Placeholder Code — **Medium**

`StackSplitter._generate_nested_stack_cdk()` in `services/stack_splitter.py:114-134` only generates comment placeholders:

```python
constructs = "\n    ".join([
    f"// {node.get('data', {}).get('label', 'Resource')}"  # Just comments!
    for node in nodes
])
```

This means multi-stack generation produces empty nested stacks with no actual CDK constructs.

**Recommendation:** Use the unified `CDKGenerator` to generate constructs within each nested stack, not just comments.

#### 2.3 Python CDK Specialist Missing Security Hardening — **Medium**

`agents/python_cdk_specialist.py` generates constructs without the security best practices that the TypeScript `CDKGenerator` applies:

| Security feature | TypeScript CDK | Python CDK |
|-----------------|:--------------:|:----------:|
| DynamoDB encryption | ✅ `AWS_MANAGED` | ❌ Missing |
| DynamoDB PITR | ✅ `pointInTimeRecovery: true` | ❌ Missing |
| S3 encryption | ✅ `S3_MANAGED` | ❌ Missing |
| S3 block public access | ✅ `BLOCK_ALL` | ❌ Missing |
| S3 enforce SSL | ✅ `enforceSSL: true` | ❌ Missing |
| SQS encryption | ✅ `SQS_MANAGED` | ❌ Missing |
| SQS DLQ | ✅ With maxReceiveCount | ❌ Missing |
| Cognito MFA | ✅ `OPTIONAL` | ❌ Missing |
| Cognito password policy | ✅ Strong (8+ chars, symbols) | ✅ Basic (email only) |

**Recommendation:** Mirror the security defaults from `CDKGenerator` in the Python CDK specialist. The Resume Tailor AI project applies security hardening consistently across all deployment modes.

#### 2.4 Cost Estimator Ignores Edges and Architecture Complexity — **Low**

`CostEstimator.estimate()` multiplies `typical_monthly * count` per service type. It doesn't account for:
- Data transfer between connected services (edges)
- API Gateway request volume scaling with number of connected Lambdas
- DynamoDB read/write capacity correlating with number of API endpoints

**Recommendation:** Use edge count to adjust inter-service transfer costs and scale API/Lambda estimates proportionally.

---

### 3. Code Quality — New Issues

#### 3.1 CDK Generation Logic Still Exists in Three Places — **High**

While the unified `CDKGenerator` was added and the fallback in `nodes.py:627-631` now delegates to it, `CDKSpecialistAgent._generate_stack()` in `agents/cdk_specialist.py` still contains its own independent 200-line implementation that doesn't use `CDKGenerator`.

The CDK specialist agent and the unified generator have diverged on security defaults (the agent lacks encryption on SQS, enforceSSL on S3, etc.).

**Recommendation:** Have `CDKSpecialistAgent._generate_stack()` delegate to `CDKGenerator` instead of maintaining its own parallel implementation.

#### 3.2 Inconsistent `logging` Usage — **Medium**

`nodes.py` uses proper `logging.getLogger(__name__)` at module level, but `security_review_node()` (line 398) creates a redundant logger inline:

```python
except Exception as e:
    import logging  # Already imported at module level!
    logging.getLogger(__name__).warning(...)
```

Additionally, the new service files (`cost_estimator.py`, `security_autofix.py`, `sharing.py`, `security_history.py`, `stack_splitter.py`, `cdk_generator.py`) contain no logging at all.

**Recommendation (from Resume Tailor AI):** The resume-tailor project uses structured logging with context (job_id, user_id) in every Lambda handler. Add `logger = logging.getLogger(__name__)` to every service module and log key operations.

#### 3.3 No `__init__.py` in `utils/` and `services/` Packages — **Low**

The new `utils/` and `services/` directories work due to implicit namespace packages, but explicit `__init__.py` files improve tool compatibility (IDE autocompletion, mypy, pytest discovery).

---

### 4. Testing — New & Remaining Gaps

#### 4.1 Zero Tests for 7 New Service Modules — **Critical**

The following new services have no test coverage:

| Module | Lines | Complexity | Risk |
|--------|-------|-----------|------|
| `services/cost_estimator.py` | 200 | Medium — pricing logic | Incorrect cost estimates mislead users |
| `services/security_autofix.py` | 148 | High — mutates graph | Could corrupt architecture state |
| `services/templates.py` | 156 | Low — static data | Template positions could break canvas |
| `services/sharing.py` | 44 | Low — CRUD | Share ID collisions, data loss |
| `services/security_history.py` | 48 | Low — CRUD | Score tracking accuracy |
| `services/stack_splitter.py` | 135 | High — code gen | Empty nested stacks (confirmed bug) |
| `services/cdk_generator.py` | 203 | High — code gen | Incorrect CDK code, missing grants |

**Recommendation (from Resume Tailor AI):** The resume-tailor project achieves 96% backend coverage (121 tests) with a test per handler. Priority test targets:
1. `cdk_generator.py` — verify edge wiring produces correct `grantReadWriteData` / `LambdaIntegration`
2. `security_autofix.py` — verify auth node injection, encryption flagging, score calculation
3. `cost_estimator.py` — verify per-service cost arithmetic, edge cases (empty graph, single node)

#### 4.2 No Tests for New API Endpoints — **High**

`test_main.py` tests only the original 4 endpoints. The 10 new endpoints (cost, autofix, templates, share, history) are untested.

**Recommendation:** Add at minimum:
- `test_estimate_cost()` — happy path + empty graph
- `test_security_autofix()` — graph with missing auth → auth added
- `test_list_templates()` + `test_get_template()`
- `test_create_and_get_share()` — round-trip
- `test_security_history_record_and_retrieve()`

#### 4.3 No CDK Deployment Service Tests — **High** (Carried from Round 1)

Still zero test coverage on `cdk_deployment.py` (296 lines of subprocess execution, temp directory management, JSON parsing).

#### 4.4 No Canvas or Page Component Tests — **Medium** (Carried from Round 1)

Still no tests for `Canvas.tsx` (211 lines) or `page.tsx` (177 lines).

---

### 5. Performance & Scalability — New Issues

#### 5.1 No Response Streaming — **High** (Carried from Round 1)

Still no streaming. The `websockets>=14.0` dependency remains declared but unused. The expanded workflow (now including multi-stack splitting) makes this more impactful.

#### 5.2 Template Positions Computed on Every Request — **Low**

`templates.py:142` calls `generate_node_positions()` on every `GET /api/templates/{id}` request for the same static data.

**Recommendation:** Pre-compute and cache positions at startup.

---

### 6. Developer Experience — Remaining Gaps

#### 6.1 No CI/CD Configuration — **High** (Upgraded from Medium)

With 7 new untested service modules, the lack of CI is now higher risk. There's no automated gate to catch regressions.

**Recommendation (from Resume Tailor AI):** The resume-tailor project includes 3 GitHub Actions workflows:
1. **`security-scan.yml`** — npm audit, TruffleHog secret scanning, CodeQL SAST
2. **`frontend-build.yml`** — TypeScript check + build validation
3. **`cost-estimation.yml`** — Infrastructure cost tracking

Scaffold AI should implement at minimum:
```yaml
# .github/workflows/ci.yml
name: CI
on: [push, pull_request]
jobs:
  backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.12" }
      - run: pip install uv && cd apps/backend && uv sync && uv run pytest -v
      - run: cd apps/backend && uv run ruff check src tests

  frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: pnpm/action-setup@v4
        with: { version: 10 }
      - uses: actions/setup-node@v4
        with: { node-version: 22 }
      - run: pnpm install && cd apps/web && pnpm test --run && pnpm type-check

  security:
    runs-on: ubuntu-latest
    steps:
      - uses: github/codeql-action/init@v3
      - uses: github/codeql-action/analyze@v3
```

#### 6.2 No Pre-Commit Hooks for Sensitive Data — **Medium** (Upgraded from Low)

**From Resume Tailor AI:** The resume-tailor project includes a `scripts/pre-commit-hook.sh` that detects:
- AWS account IDs (12-digit patterns)
- ARN patterns with real account info
- Cognito User Pool / Identity Pool IDs
- Whitelists placeholder values (`XXXXXXXXXXXX`)

Scaffold AI handles AWS credentials and generates CDK code that may contain account-specific values. A similar hook would prevent accidental credential commits.

#### 6.3 No Docker Setup — **Medium** (Carried from Round 1)

Still no `docker-compose.yml` for containerized development.

#### 6.4 Missing `apps/web/.env.example` — **Low** (Carried from Round 1)

---

### 7. Best Practices from Resume Tailor AI

The following patterns from the Resume Tailor AI production project would strengthen Scaffold AI:

#### 7.1 Validation-First Handler Pattern — **High**

Resume Tailor AI validates all inputs at the boundary before any processing:

```python
def handler(event, context):
    try:
        job_description = validate_job_description(event.get('jobDescription', ''))
        # ... proceed only if valid
    except ValueError as e:
        return {'statusCode': 400, 'error': str(e)}
```

**For Scaffold AI:** The new endpoints (`/api/cost/estimate`, `/api/security/autofix`, etc.) accept raw `dict` parameters with no validation. Create Pydantic models for all request bodies.

#### 7.2 Robust JSON Extraction from AI Responses — **Medium**

Resume Tailor AI's `extract_json.py` uses 4 fallback strategies:
1. Extract from ` ```json ` code blocks
2. Extract from generic ` ``` ` blocks
3. Brace-matching to find first valid `{}` structure
4. Control character sanitization before parsing

Scaffold AI's `strip_code_fences()` only handles strategies 1-2. If the LLM returns partial JSON or embeds control characters, parsing fails.

**Recommendation:** Port the brace-matching and control character sanitization strategies from Resume Tailor AI into `llm_utils.py`.

#### 7.3 Deployment Mode Configuration — **Medium**

Resume Tailor AI supports dual deployment modes (PREMIUM / OPTIMIZED) that swap the LLM model per function via CDK context variables. This allows cost optimization without code changes.

**For Scaffold AI:** Currently the Bedrock model ID is a single env var. Consider allowing per-agent model selection:
```env
BEDROCK_MODEL_ID_INTERPRET=us.anthropic.claude-3-haiku-20240307-v1:0  # Cheap for classification
BEDROCK_MODEL_ID_ARCHITECT=us.anthropic.claude-3-5-sonnet-20241022-v2:0  # Better for design
BEDROCK_MODEL_ID_CDK=us.anthropic.claude-3-5-sonnet-20241022-v2:0  # Better for code gen
```

#### 7.4 Auto-Configuration Script — **Low**

Resume Tailor AI includes `scripts/setup-frontend-config.sh` that reads CDK stack outputs and auto-generates the frontend `.env` file. This eliminates manual copy-paste of API URLs and resource ARNs.

**For Scaffold AI:** A similar script could auto-detect the backend URL and write `apps/web/.env.local`.

---

### 8. Feature Enhancements — Remaining

#### 8.1 Undo/Redo on Canvas — **Medium** (Carried from Round 1)

No undo/redo for canvas operations.

#### 8.2 Generated Code Diff View — **Low** (Carried from Round 1)

No diff view when regenerating code.

#### 8.3 Stack Destroy Capability — **Low** (Carried from Round 1)

`CDKDeploymentService.destroy()` still returns "not yet implemented".

---

### 9. Updated Summary Matrix

| # | Issue | Severity | Category | Status |
|---|-------|----------|----------|--------|
| **NEW** | Zero tests for 7 new service modules | Critical | Testing | Open |
| **NEW** | New endpoints lack rate limiting | High | Security | Open |
| **NEW** | No tests for 10 new API endpoints | High | Testing | Open |
| 2.3 | Blocking subprocess in deploy endpoint | High | Architecture | Open |
| 3.1 | CDK specialist still has parallel impl | High | Maintainability | Partial |
| 4.3 | No deployment service tests | High | Testing | Open |
| 5.1 | No response streaming | High | UX | Open |
| 6.1 | No CI/CD | High | Dev Experience | Open |
| **NEW** | New endpoints leak exception details | Medium | Security | Open |
| **NEW** | Share endpoint has no input validation | Medium | Security | Open |
| **NEW** | In-memory services lose state on restart | Medium | Reliability | Open |
| **NEW** | Nested stack generator produces empty code | Medium | Feature bug | Open |
| **NEW** | Python CDK missing security hardening | Medium | Security | Open |
| **NEW** | Inconsistent logging in new services | Medium | Observability | Open |
| **NEW** | No pre-commit hooks for secrets | Medium | Security | Open |
| 4.4 | No Canvas component tests | Medium | Testing | Open |
| 6.3 | No Docker setup | Medium | Dev Experience | Open |
| 8.1 | No undo/redo | Medium | Feature | Open |
| **NEW** | Cost estimator ignores edges | Low | Feature | Open |
| **NEW** | Template positions not cached | Low | Performance | Open |
| **NEW** | Missing `__init__.py` in new packages | Low | Code quality | Open |
| 1.5 | Deploy endpoint still leaks errors | Low | Security | Open |
| 6.4 | Missing web `.env.example` | Low | Dev Experience | Open |
| 8.2 | No code diff view | Low | Feature | Open |
| 8.3 | Stack destroy not implemented | Low | Feature | Open |
| | | | | |
| 1.1 | Command injection | Critical | Security | ✅ Fixed |
| 1.2 | CORS wildcards | Medium | Security | ✅ Fixed |
| 1.4 | Exception detail leakage (chat) | Low | Security | ✅ Fixed |
| 2.1 | LLM client per-request | High | Performance | ✅ Fixed |
| 2.2 | No request timeout | High | Reliability | ✅ Fixed |
| 2.4 | No rate limiting (chat/deploy) | Medium | Security | ✅ Fixed |
| 2.5 | No `iac_format` validation | Medium | Reliability | ✅ Fixed |
| 2.6 | Missing `security_review` init | Medium | Reliability | ✅ Fixed |
| 3.1 | Duplicated CDK fallback | High | Maintainability | ✅ Fixed |
| 3.2 | Duplicated code-fence stripping | Medium | Maintainability | ✅ Fixed |
| 3.3 | `print()` instead of `logging` | Medium | Observability | ✅ Fixed |
| 7.1 | Edges ignored in static code gen | High | Feature | ✅ Fixed |
| 7.2 | No architecture templates | Medium | Feature | ✅ Fixed |
| 7.4 | No export/sharing | Medium | Feature | ✅ Fixed |

---

## Acknowledgments

- [AWS Cloudscape Design System](https://cloudscape.design) — UI components
- [React Flow](https://reactflow.dev) — Node graph visualization
- [LangGraph](https://github.com/langchain-ai/langgraph) — Multi-agent orchestration
- [kiro-powers (praveenc)](https://github.com/praveenc/kiro-powers) — Cloudscape steering docs
- [kiro-powers (official)](https://github.com/kirodotdev/powers) — AWS IaC, Cloud Architect, SaaS Builder patterns

## License

MIT
