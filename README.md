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
  - Deploy button in Chat component
  - Backend deployment service
  - Temporary project creation
  - Bootstrap and deploy automation
- [ ] Python CDK support
- [ ] Multi-stack architectures (split large graphs into nested stacks)
- [ ] Architecture templates library (pre-built patterns)
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

---

## Code Review: Enhancements & Recommendations

> **Reviewer note:** The following is a thorough architectural and code-quality review of the Scaffold AI codebase. Items are organized by priority (critical → high → medium → low) within each category.

### 1. Security Concerns

#### 1.1 Command Injection in CDK Deployment Service — **Critical**

`apps/backend/src/scaffold_ai/services/cdk_deployment.py` passes user-supplied `stack_name` directly into file paths and shell commands without sanitization:

```python
# Line 178 — stack_name used in file path
with open(project_path / "lib" / f"{stack_name.lower()}-stack.ts", "w") as f:
```

The `stack_name` comes from the `DeployRequest` Pydantic model, which only validates it as a `str`. A malicious value like `../../etc/passwd` or a name containing shell metacharacters could be exploited.

**Recommendation:** Add strict validation to `DeployRequest`:
```python
from pydantic import BaseModel, field_validator
import re

class DeployRequest(BaseModel):
    stack_name: str

    @field_validator("stack_name")
    @classmethod
    def validate_stack_name(cls, v: str) -> str:
        if not re.match(r'^[A-Za-z][A-Za-z0-9-]{0,127}$', v):
            raise ValueError("stack_name must be alphanumeric with hyphens, 1-128 chars")
        return v
```

#### 1.2 CORS Allows All Methods and Headers — **Medium**

`apps/backend/src/scaffold_ai/main.py:27-31` uses `allow_methods=["*"]` and `allow_headers=["*"]`. While the origins are configurable, wildcard methods and headers weaken CORS protection.

**Recommendation:** Restrict to the methods and headers actually used:
```python
allow_methods=["GET", "POST", "OPTIONS"],
allow_headers=["Content-Type", "Authorization"],
```

#### 1.3 CDK Fallback Template CORS Uses `ALL_ORIGINS` — **Medium**

The generated API Gateway code in both `nodes.py:657` and `cdk_specialist.py:327-329` sets `allowOrigins: apigateway.Cors.ALL_ORIGINS`. This propagates into production infrastructure.

**Recommendation:** Generate a parameterized CORS origin (e.g., from a CDK context variable or stack parameter) instead of a wildcard.

#### 1.4 Exception Detail Leakage — **Low**

`main.py:118` raises `HTTPException(status_code=500, detail=str(e))`, which can leak internal implementation details (file paths, library versions, stack traces) to API consumers.

**Recommendation:** Log the full exception server-side, return a generic message to the client:
```python
except Exception as e:
    logger.exception("Chat endpoint error")
    raise HTTPException(status_code=500, detail="An internal error occurred.")
```

---

### 2. Architecture & Design

#### 2.1 LLM Client Created on Every Request — **High**

`nodes.py:13-19` creates a new `ChatBedrock` client on every call to `get_llm()`. Each node function (interpret, architect, security review, CDK generation) calls `get_llm()` independently, meaning a single request creates up to 4 client instances.

**Recommendation:** Use a module-level singleton or dependency-injected client:
```python
from functools import lru_cache

@lru_cache(maxsize=1)
def get_llm():
    return ChatBedrock(...)
```

Or better, accept the LLM as a parameter for testability.

#### 2.2 No Request Timeout or Cancellation — **High**

The `/api/chat` endpoint (`main.py:86`) invokes the full LangGraph workflow with no timeout. If the LLM is slow or hangs, the request blocks indefinitely. The Next.js proxy (`route.ts`) also has no timeout on its `fetch()` call.

**Recommendation:**
- Add `asyncio.wait_for()` with a configurable timeout (e.g., 60s) around `run_workflow()`.
- Add `AbortController` with a timeout on the frontend fetch.
- Consider returning a 202 with a job ID for long-running generations.

#### 2.3 CDK Deployment Runs Synchronously — **High**

`CDKDeploymentService.deploy()` uses blocking `subprocess.run()` calls inside an `async` endpoint. The `npm install` step alone has a 120-second timeout, and `cdk deploy` has a 600-second timeout. This blocks the FastAPI event loop.

**Recommendation:** Use `asyncio.create_subprocess_exec()` or offload to a background task queue (Celery, ARQ, or FastAPI `BackgroundTasks`). Return a deployment ID and poll for status.

#### 2.4 No Rate Limiting — **Medium**

There is no rate limiting on any endpoint. The `/api/chat` endpoint triggers LLM calls (which cost money), and `/api/deploy` triggers real AWS deployments.

**Recommendation:** Add rate limiting via `slowapi` or a middleware:
```python
from slowapi import Limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/api/chat")
@limiter.limit("10/minute")
async def chat(request: Request, body: ChatRequest): ...
```

#### 2.5 No Input Validation on `iac_format` — **Medium**

`ChatRequest.iac_format` accepts any string. If an unsupported format is passed, it silently falls through to the CDK default branch in `cdk_specialist_node`.

**Recommendation:** Use a `Literal` type:
```python
from typing import Literal

class ChatRequest(BaseModel):
    iac_format: Literal["cdk", "cloudformation", "terraform"] = "cdk"
```

#### 2.6 `security_review` Missing from `GraphState` Initialization — **Medium**

In `main.py:97-106`, the initial state does not include `security_review: None`. While `TypedDict` doesn't enforce this at runtime, it means `state.get("security_review")` is the only safe access pattern, and any direct `state["security_review"]` would raise `KeyError`.

**Recommendation:** Explicitly initialize `security_review: None` in the initial state dict.

---

### 3. Code Quality & Maintainability

#### 3.1 Duplicated CDK Generation Logic — **High**

CDK code generation exists in three places:
1. `nodes.py:586-803` — `generate_secure_cdk_template()` (fallback)
2. `agents/cdk_specialist.py:265-478` — `CDKSpecialistAgent._generate_stack()`
3. LLM-generated code via `CDK_GENERATOR_PROMPT`

The fallback in `nodes.py` and the agent in `cdk_specialist.py` have diverged — they generate different security configurations (e.g., the fallback includes encryption on SQS queues, the agent does not). The fallback includes `BlockPublicAccess.BLOCK_ALL` and `enforceSSL` on S3, the agent includes CORS.

**Recommendation:** Extract a single `StaticCDKGenerator` class used by both the fallback and the specialist agent. Apply the security-hardened version consistently.

#### 3.2 Duplicated JSON Code-Fence Stripping — **Medium**

The pattern for stripping markdown code fences from LLM responses is duplicated in 3 locations (`nodes.py:252-255`, `nodes.py:389-392`, `nodes.py:536-539`):
```python
if "```json" in response_text:
    response_text = response_text.split("```json")[1].split("```")[0]
elif "```" in response_text:
    response_text = response_text.split("```")[1].split("```")[0]
```

**Recommendation:** Extract a utility function:
```python
def strip_code_fences(text: str) -> str:
    """Strip markdown code fences from LLM response text."""
    for fence in ("```json", "```typescript", "```"):
        if fence in text:
            return text.split(fence, 1)[1].split("```", 1)[0]
    return text
```

#### 3.3 `print()` Used Instead of `logging` — **Medium**

The backend uses `print()` for all diagnostic output (`nodes.py:208,297,303,397,545,581,583,828`; `cdk_deployment.py` also lacks logging). This loses log levels, timestamps, and structured context.

**Recommendation:** Replace with Python `logging`:
```python
import logging
logger = logging.getLogger(__name__)

logger.warning("LLM intent classification failed", exc_info=True)
```

#### 3.4 README Stale Data — **Low**

Several README entries are outdated:
- Line 40: "97 tests" vs actual 82 backend tests passing.
- Line 79: `react_specialist.py` described as "Stub — not yet implemented" but it is fully implemented (611 lines, architecture-aware generation).
- Line 227: `react_specialist_node` described as "[stub] future Cloudscape component generation" but it works.
- Line 361: "86 backend tests + 34 frontend tests = 120 tests" — backend count may need updating.

**Recommendation:** Audit all numeric claims and status descriptions; consider generating test counts from CI output.

---

### 4. Testing Gaps

#### 4.1 No CDK Deployment Service Tests — **High**

`CDKDeploymentService` has zero test coverage. It executes shell commands, creates temp directories, writes files, and parses JSON outputs — all untested.

**Recommendation:** Add unit tests mocking `subprocess.run`:
- Test project structure creation
- Test bootstrap success/failure paths
- Test deploy with outputs
- Test timeout handling
- Test cleanup of temp directories

#### 4.2 No Edge-Aware Code Generation Tests — **Medium**

The CDK generators produce constructs based on nodes but ignore edges entirely. While the LLM path considers edges in its prompt, the static fallback generators (`generate_secure_cdk_template`, `CDKSpecialistAgent._generate_stack`) do not wire up connections (e.g., Lambda → DynamoDB grants, API Gateway → Lambda integrations).

**Recommendation:** Add tests verifying that when edges connect API → Lambda → Database nodes, the generated code includes `grantReadWriteData` and `LambdaIntegration` calls.

#### 4.3 No Frontend Integration Tests — **Medium**

There are no tests for the `Canvas` component or the `page.tsx` AppLayout. The Canvas component handles node type registration, layout controls, and edge styling — all untested.

**Recommendation:** Add Vitest tests for:
- Canvas renders with mock nodes
- Layout dropdown triggers `applyLayout`
- Add Service dropdown creates nodes
- Node selection updates state

#### 4.4 No Error Path Tests for API Route — **Low**

`apps/web/app/api/chat/route.ts` has tests for 502/503 and `TypeError`, but no test for malformed JSON responses from the backend.

---

### 5. Performance & Scalability

#### 5.1 No Response Streaming — **High**

The full LangGraph workflow (interpret → architect → security → generate) must complete before any response is sent. For complex architectures, this can mean 10-30 seconds of silence.

**Recommendation:** Implement Server-Sent Events (SSE) or WebSocket streaming to send incremental updates:
- "Classifying intent..."
- "Designing architecture..."
- "Running security review..."
- "Generating CDK code..."

The `websockets` dependency is already declared but unused.

#### 5.2 Frontend Fetches Are Not Debounced — **Low**

Rapid clicking of "Generate Code" or "Send" while a request is in-flight is guarded by `isLoading`, but there's no debounce on the chat input or protection against double-submit race conditions if `setLoading(true)` hasn't propagated yet.

**Recommendation:** Use an `AbortController` ref to cancel in-flight requests when a new one starts.

---

### 6. Developer Experience

#### 6.1 No `docker-compose.yml` — **Medium**

The project requires Node.js 22+, Python 3.12+, pnpm, and uv — a non-trivial setup. There's no containerized development option.

**Recommendation:** Add a `docker-compose.yml` with web and backend services. This also helps with CI reproducibility.

#### 6.2 No CI/CD Configuration — **Medium**

There are no GitHub Actions, CircleCI, or other CI configs. Tests pass locally but there's no automated verification on PRs.

**Recommendation:** Add a GitHub Actions workflow:
```yaml
# .github/workflows/ci.yml
jobs:
  backend-tests:
    steps:
      - uses: actions/setup-python@v5
        with: { python-version: "3.12" }
      - run: pip install uv && cd apps/backend && uv sync && uv run pytest -v

  frontend-tests:
    steps:
      - uses: pnpm/action-setup@v4
      - run: pnpm install && cd apps/web && pnpm test --run
```

#### 6.3 Missing `.env.example` in `apps/web/` — **Low**

The backend has a `.env.example` but the frontend's `apps/web/.env.local` is only documented in the README, not templated.

**Recommendation:** Add `apps/web/.env.example`:
```env
BACKEND_URL=http://localhost:8000
```

#### 6.4 No Pre-commit Hooks — **Low**

No linting or formatting runs automatically before commits. Both `ruff` (Python) and `eslint` (TypeScript) are configured but not enforced.

**Recommendation:** Add `husky` + `lint-staged` for the JS side and `pre-commit` for the Python side.

---

### 7. Feature Enhancements

#### 7.1 Edge-Aware Infrastructure Wiring — **High**

The static CDK generators produce isolated constructs with no inter-service connections. When a user draws an edge from API Gateway → Lambda → DynamoDB, the generated CDK should include:
```typescript
api.root.addResource('items').addMethod('GET', new apigateway.LambdaIntegration(fn));
table.grantReadWriteData(fn);
```

Currently, each node generates standalone code. The edges are passed to the LLM prompt but not used by the static fallback.

**Recommendation:** Parse the `edges` array in `_generate_stack()` and emit grant/integration calls for each connection.

#### 7.2 Architecture Templates — **Medium**

The chat is the only way to create architectures. Pre-built templates (CRUD API, file upload pipeline, event-driven microservice) would accelerate onboarding.

**Recommendation:** Add a `/api/templates` endpoint and a template picker in the UI that populates the canvas with a known-good graph.

#### 7.3 Undo/Redo on Canvas — **Medium**

There's no undo/redo for canvas operations. A user who accidentally deletes a node after a long design session has no recourse.

**Recommendation:** Add temporal state with `zustand/middleware`:
```typescript
import { temporal } from 'zundo';
const useGraphStore = create<GraphState>()(temporal((set, get) => ({ ... })));
```

#### 7.4 Export/Import Architecture — **Medium**

Users can't save or share their architecture designs. The graph state is ephemeral.

**Recommendation:** Add "Export JSON" and "Import JSON" buttons that serialize/deserialize the graph store to a file.

#### 7.5 Generated Code Diff View — **Low**

When regenerating code, the previous version is silently replaced. A diff view would help users understand what changed.

#### 7.6 Stack Destroy Capability — **Low**

`CDKDeploymentService.destroy()` returns "not yet implemented". Users who deploy via the UI have no way to clean up.

---

### 8. Summary Matrix

| # | Issue | Severity | Category | Effort |
|---|-------|----------|----------|--------|
| 1.1 | Command injection in deploy service | Critical | Security | Small |
| 2.1 | LLM client created per-request | High | Performance | Small |
| 2.2 | No request timeout | High | Reliability | Small |
| 2.3 | Blocking subprocess in async endpoint | High | Architecture | Medium |
| 3.1 | Duplicated CDK generation logic | High | Maintainability | Medium |
| 4.1 | No deployment service tests | High | Testing | Medium |
| 5.1 | No response streaming | High | UX/Performance | Large |
| 7.1 | Edges ignored in static code gen | High | Feature gap | Medium |
| 1.2 | CORS wildcards | Medium | Security | Small |
| 1.3 | Generated API uses ALL_ORIGINS | Medium | Security | Small |
| 2.4 | No rate limiting | Medium | Security | Small |
| 2.5 | No `iac_format` validation | Medium | Reliability | Small |
| 2.6 | Missing `security_review` init | Medium | Reliability | Small |
| 3.2 | Duplicated code-fence stripping | Medium | Maintainability | Small |
| 3.3 | `print()` instead of `logging` | Medium | Observability | Small |
| 4.2 | No edge-aware generation tests | Medium | Testing | Medium |
| 4.3 | No Canvas component tests | Medium | Testing | Medium |
| 6.1 | No Docker setup | Medium | Dev Experience | Medium |
| 6.2 | No CI/CD | Medium | Dev Experience | Medium |
| 7.2 | Architecture templates | Medium | Feature | Medium |
| 7.3 | No undo/redo | Medium | Feature | Small |
| 7.4 | No export/import | Medium | Feature | Small |
| 1.4 | Exception detail leakage | Low | Security | Small |
| 3.4 | README stale data | Low | Documentation | Small |
| 4.4 | Missing API route error tests | Low | Testing | Small |
| 5.2 | No fetch debounce | Low | Reliability | Small |
| 6.3 | Missing web `.env.example` | Low | Dev Experience | Small |
| 6.4 | No pre-commit hooks | Low | Dev Experience | Small |
| 7.5 | No code diff view | Low | Feature | Medium |
| 7.6 | Stack destroy not implemented | Low | Feature | Medium |

---

## Acknowledgments

- [AWS Cloudscape Design System](https://cloudscape.design) — UI components
- [React Flow](https://reactflow.dev) — Node graph visualization
- [LangGraph](https://github.com/langchain-ai/langgraph) — Multi-agent orchestration
- [kiro-powers (praveenc)](https://github.com/praveenc/kiro-powers) — Cloudscape steering docs
- [kiro-powers (official)](https://github.com/kirodotdev/powers) — AWS IaC, Cloud Architect, SaaS Builder patterns

## License

MIT
