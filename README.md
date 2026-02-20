# Scaffold AI

**AI-powered AWS architecture designer built with LangGraph**

[![CI](https://github.com/jfowler-cloud/scaffold-ai/actions/workflows/ci.yml/badge.svg)](https://github.com/jfowler-cloud/scaffold-ai/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-blue.svg)](https://www.typescriptlang.org/)

![Built in 1 Day](https://img.shields.io/badge/Built%20in-1%20Day-brightgreen?style=flat-square)
![Tests: 116](https://img.shields.io/badge/Tests-116%20passing-brightgreen?style=flat-square)
![LangGraph](https://img.shields.io/badge/LangGraph-Multi--Agent-purple?style=flat-square)
![Security](https://img.shields.io/badge/Security-Gates%20%2B%20Rate%20Limiting-blue?style=flat-square)

Describe your application in natural language and Scaffold AI designs the AWS serverless architecture, runs a security review against AWS Well-Architected principles, and generates deployment-ready infrastructure-as-code -- all through a visual canvas and chat interface.

## Why This Project

After building [Resume Tailor AI](https://github.com/jfowler-cloud/resume-tailor-ai) with AWS Step Functions, I wanted to explore modern AI orchestration beyond AWS-native tooling. I picked up LangGraph -- a framework I had no prior experience with -- and built this full-stack multi-agent platform in a single day.

The goal was to demonstrate:

- **Learning velocity** -- Shipping production-quality code in unfamiliar frameworks, fast
- **Architectural judgment** -- Knowing when LangGraph fits better than Step Functions (and vice versa), rather than defaulting to one tool
- **Production mindset** -- Security gates, rate limiting, input validation, and testing from the start, not bolted on later

| | Resume Tailor AI | Scaffold AI | Career Path Architect |
|---|---|---|---|
| **Purpose** | Resume optimization | AWS architecture design | Career planning |
| **Orchestration** | AWS Step Functions | LangGraph | LangGraph |
| **Agents** | Step Functions workflow | 4 LangGraph agents | 6 LangGraph agents |
| **Development** | 3 days | 1 day | 2 hours |
| **Tests** | 212 tests, 98% | 116 tests | 142 tests, 99% |
| **Features** | Resume tailoring | Architecture generation | Roadmap + Critical Review |

Both projects share the same production patterns (validation, error handling, pre-commit hooks, CI/CD, rate limiting, testing) -- the difference is the orchestration approach chosen to match the problem. See [LangGraph vs Step Functions](LANGGRAPH_VS_STEP_FUNCTIONS.md) for a detailed technical comparison.

---

## Screenshots

| Blank canvas | Architecture generated from prompt |
|:---:|:---:|
| ![Blank canvas](docs/images/blank_canvas.png) | ![Populated canvas](docs/images/populate_canvas.png) |

| Security review (failed -- score 62/100) | Architecture updated with security fixes |
|:---:|:---:|
| ![Failed security review](docs/images/failed_security_review.png) | ![Security fixes applied](docs/images/incorporated_security_review_feedback_updated_canvas.png) |

| Generated CDK code | Export and deploy options |
|:---:|:---:|
| ![Generated code viewer](docs/images/generated_code_view.png) | ![Download and deploy](docs/images/options_to_download_zip_and_deploy.png) |

---

## How It Works

```
User Input --> Interpreter --> Architect --> Security Specialist --> Code Generator
                  |               |                |                      |
            Intent class    Graph nodes     Security score         CDK / Terraform / CF
```

- **Interpreter Agent** -- Classifies user intent (new feature, modify, explain, deploy)
- **Architect Agent** -- Designs AWS serverless architecture with 12 service types
- **Security Specialist** -- Validates against AWS Well-Architected principles; blocks insecure designs (score < 70/100)
- **Code Generators** -- Multi-format IaC output (CDK TypeScript, CDK Python, CloudFormation, Terraform)
- **React Specialist** -- Generates AWS Cloudscape UI components

---

## Key Features

- **Visual Canvas** -- React Flow node graph editor with drag-and-drop AWS service nodes
- **AI Chat** -- Natural language architecture design powered by AWS Bedrock (Claude)
- **Security Gate** -- Automated scoring blocks code generation for insecure architectures
- **Multi-Format IaC** -- Generate CDK TypeScript, CDK Python, CloudFormation, or Terraform
- **Code Viewer** -- Tabbed modal for browsing generated infrastructure code
- **Export & Deploy** -- Download as ZIP or deploy directly to AWS with CDK
- **Rate Limiting** -- 10 req/min chat, 3 req/hr deployment
- **Dark Mode** -- Persistent theme preference
- **Pre-commit Hooks** -- TruffleHog secrets detection, AWS credentials scanning

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| AI Orchestration | LangGraph |
| LLM | AWS Bedrock (Claude) |
| Backend | FastAPI |
| Frontend | Next.js 15 + React 19 |
| UI Library | AWS Cloudscape Design System |
| State | Zustand |
| Canvas | React Flow |
| Testing | pytest + Vitest |
| Tooling | pnpm + Turborepo + uv |

---

## Quick Start

### Prerequisites

- Python 3.12+
- Node.js 22+
- pnpm 10+
- AWS CLI configured with Bedrock access
- [uv](https://docs.astral.sh/uv/) (Python package manager)

### Installation

```bash
# Clone repository
git clone https://github.com/jfowler-cloud/scaffold-ai.git
cd scaffold-ai

# Install frontend dependencies
pnpm install

# Backend setup
cd apps/backend
uv sync
cp .env.example .env
# Edit .env with your AWS credentials
```

### Running Locally

```bash
# Terminal 1: Backend (port 8000)
cd apps/backend
uv run uvicorn scaffold_ai.main:app --reload

# Terminal 2: Frontend (port 3000)
cd apps/web
pnpm dev
```

### Environment Variables

**Backend** (`apps/backend/.env`):
```bash
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
BACKEND_URL=http://localhost:8000
```

**Frontend** (`apps/web/.env.local`):
```bash
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
```

---

## Project Structure

```
scaffold-ai/
├── apps/
│   ├── backend/                # FastAPI + LangGraph
│   │   ├── src/scaffold_ai/
│   │   │   ├── main.py         # FastAPI app
│   │   │   ├── graph/          # LangGraph workflow (DAG, nodes, state)
│   │   │   ├── agents/         # Specialist agents
│   │   │   ├── services/       # Business services
│   │   │   └── tools/          # Git, CDK synthesis
│   │   └── tests/
│   │
│   └── web/                    # Next.js 15 frontend
│       ├── app/                # App router
│       ├── components/         # Cloudscape components, Canvas, Chat
│       └── lib/                # Zustand stores
│
├── packages/
│   ├── generated/              # IaC output
│   └── ui/                     # Shared components
│
└── docs/
    └── steering/               # Cloudscape UI patterns
```

---

## Testing

```bash
# Backend tests
cd apps/backend
uv run pytest -v

# Frontend tests
cd apps/web
pnpm test

# All tests (from root)
pnpm test:all
```

Tests cover agents, services, LangGraph workflow integration, API endpoints, input validation, rate limiting, and frontend components/stores.

---

## Portfolio Comparison

| | Resume Tailor AI | Scaffold AI |
|---|---|---|
| **Orchestration** | AWS Step Functions | LangGraph |
| **Use case** | Deterministic resume tailoring | Dynamic AI multi-agent conversations |
| **State management** | S3 + DynamoDB | LangGraph built-in memory |
| **Deployment** | AWS-native (Lambda, Step Functions) | Framework-agnostic |
| **Best for** | Predictable workflows, AWS-integrated | Dynamic routing, conversational AI |

Both projects share production patterns: input validation, error handling, pre-commit hooks, CI/CD with security scanning, rate limiting, and comprehensive testing.

---

## Documentation

- [LangGraph vs Step Functions](LANGGRAPH_VS_STEP_FUNCTIONS.md) -- Technical comparison with cost analysis
- [Development Journey](DEVELOPMENT_JOURNEY.md) -- Build timeline and key decisions
- [Multi-Format IaC](docs/MULTI_FORMAT_IAC.md) -- IaC generation patterns
- [Contributing](CONTRIBUTING.md) -- Development setup and guidelines
- [Testing Summary](TESTING_SUMMARY.md) -- Test coverage and strategy
- [Security Audit](SECURITY_AUDIT.md) -- Security review and improvements
- [Critical Review](CRITICAL_REVIEW.md) -- Self-assessment and roadmap

---

## Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make changes and add tests
4. Run tests: `pnpm test:all`
5. Commit: `git commit -m 'feat: add amazing feature'`
6. Push and open a Pull Request

---

## License

MIT License -- see [LICENSE](LICENSE) for details.

## Author

**James Fowler**
- GitHub: [@jfowler-cloud](https://github.com/jfowler-cloud)
- LinkedIn: [James Fowler](https://www.linkedin.com/in/james-fowler-aws-cloud-architect-dev-ops-professional/)
