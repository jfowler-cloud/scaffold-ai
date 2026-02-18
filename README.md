# Scaffold AI

**AI-powered AWS architecture designer built with LangGraph**

[![CI](https://github.com/jfowler-cloud/scaffold-ai/actions/workflows/ci.yml/badge.svg)](https://github.com/jfowler-cloud/scaffold-ai/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-blue.svg)](https://www.typescriptlang.org/)

> **Portfolio Project**: Built in a single day to demonstrate rapid learning of new frameworks (LangGraph, React 19, Next.js 15) and showcase alternatives to AWS-native orchestration. Complements [Resume Tailor AI](https://github.com/jfowler-cloud/resume-tailor-ai) by highlighting framework-agnostic development vs AWS-native approaches.

## 🎯 Why This Project Exists

**Rapid Capability Growth**: After building Resume Tailor AI with AWS Step Functions, I wanted to explore modern AI orchestration frameworks. This project demonstrates:

- **Learning Velocity**: Mastered LangGraph, React 19, and Next.js 15 in a single day
- **Framework Diversity**: AWS-native (Step Functions) vs framework-based (LangGraph) orchestration
- **Architectural Judgment**: Understanding when to use each approach and articulating trade-offs
- **Production Mindset**: Security gates, rate limiting, testing, and validation from day 1

**Portfolio Positioning**:
| Project | Orchestration | Focus | State Management | Best For | Time |
|---------|--------------|-------|------------------|----------|------|
| **Resume Tailor AI** | AWS Step Functions | Deterministic workflow | S3/DynamoDB | Predictable, AWS-native flows | 3 days |
| **Scaffold AI** | LangGraph | AI multi-agent | Built-in memory | Dynamic routing, conversational AI | 1 day |

Both projects showcase production patterns (validation, error handling, security, CI/CD) but with different architectural approaches.

---

## 🎯 Project Purpose

This project showcases:
- **LangGraph Orchestration** - Alternative to AWS Step Functions for AI workflows
- **Multi-Agent Architecture** - Intent classification → Architecture design → Security review → Code generation
- **Rapid Development** - Full-stack AI platform built in 2 weeks
- **Production Patterns** - Security gates, rate limiting, validation, testing
- **Modern Stack** - FastAPI, LangGraph, Next.js 15, React 19, AWS Bedrock

**Why LangGraph over Step Functions?**
- Dynamic routing based on LLM responses
- Built-in memory and state management
- Easier local development and testing
- Better suited for conversational AI flows
- More flexible than rigid state machine definitions

---

## ✨ Key Features

### 🤖 Multi-Agent AI Workflow
```
User Input → Interpreter → Architect → Security Specialist → Code Generator
                ↓              ↓              ↓                    ↓
           Intent Class   Graph Nodes   Security Score      CDK/Terraform/CF
```

- **Interpreter Agent**: Classifies user intent (new feature, modify, explain, deploy)
- **Architect Agent**: Designs AWS serverless architecture with 12 service types
- **Security Specialist**: AWS Well-Architected security validation (blocks insecure designs)
- **Code Generators**: Multi-format IaC (CDK TypeScript, CloudFormation, Terraform, Python CDK)
- **React Specialist**: Generates AWS Cloudscape UI components

### 🔒 Security-First Design
- **Security Gate**: Blocks code generation for architectures scoring <70/100
- **Pre-commit Hooks**: TruffleHog for secrets, AWS credentials detection
- **Input Validation**: Request size limits, user input sanitization
- **Rate Limiting**: 10 req/min chat, 3 req/hr deployment
- **Approval Gates**: Deployment requires manual approval by default

### 🎨 Professional UI
- **AWS Cloudscape Design System**: Console-style professional interface
- **React Flow Canvas**: Visual node graph editor with drag-and-drop
- **Real-time Chat**: Natural language architecture design
- **Code Viewer**: Tabbed modal for generated infrastructure code
- **Dark Mode**: Persistent theme preference

### 📊 Production-Ready Patterns
- **Structured Logging**: Context-aware error tracking
- **Health Checks**: Bedrock connectivity monitoring
- **Cost Estimation**: Real-time AWS cost calculations
- **Deployment Integration**: One-click CDK deployment
- **Test Coverage**: 135+ tests (unit + integration)

---

## 🚀 Quick Start

### Prerequisites
```bash
# Required
- Python 3.12+
- Node.js 22+
- pnpm 10+
- AWS CLI configured
- uv (Python package manager)

# Optional (for deployment)
- AWS CDK CLI
- Docker (for future containerization)
```

### Installation
```bash
# Clone repository
git clone https://github.com/jfowler-cloud/scaffold-ai.git
cd scaffold-ai

# Install dependencies
pnpm install

# Backend setup
cd apps/backend
uv sync
cp .env.example .env
# Edit .env with your AWS credentials

# Run backend (port 8000)
uv run uvicorn scaffold_ai.main:app --reload

# Run frontend (port 3000)
cd ../web
pnpm dev
```

### Environment Variables
```bash
# Backend (.env)
AWS_PROFILE=your-profile
AWS_REGION=us-east-1
BEDROCK_MODEL_ID=us.anthropic.claude-3-haiku-20240307-v1:0
ALLOWED_ORIGINS=http://localhost:3000

# Frontend (.env.local)
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
```

---

## 🏗️ Architecture

### Tech Stack
| Layer | Technology | Why? |
|-------|-----------|------|
| **AI Orchestration** | LangGraph | Dynamic routing, state management, better than Step Functions for AI |
| **LLM** | AWS Bedrock (Claude 3 Haiku) | Cost-effective, fast, AWS-native |
| **Backend** | FastAPI | Async, type-safe, auto-docs |
| **Frontend** | Next.js 15 + React 19 | Server components, streaming |
| **UI Library** | AWS Cloudscape | Professional, accessible, AWS console-style |
| **State** | Zustand | Lightweight, no boilerplate |
| **Canvas** | React Flow | Visual architecture editor |
| **Testing** | pytest + Vitest | Fast, modern |
| **Tooling** | pnpm + Turborepo + uv | Fast installs, monorepo support |

### Project Structure
```
scaffold-ai/
├── apps/
│   ├── backend/              # FastAPI + LangGraph
│   │   ├── src/scaffold_ai/
│   │   │   ├── main.py       # FastAPI app (8 endpoints)
│   │   │   ├── graph/        # LangGraph workflow
│   │   │   │   ├── workflow.py   # DAG definition
│   │   │   │   ├── nodes.py      # Agent implementations
│   │   │   │   └── state.py      # TypedDict state
│   │   │   ├── agents/       # 7 specialist agents
│   │   │   ├── services/     # 8 business services
│   │   │   └── tools/        # Git, CDK synthesis
│   │   └── tests/            # 135+ tests
│   │
│   └── web/                  # Next.js 15 frontend
│       ├── app/              # App router
│       ├── components/       # Cloudscape components
│       │   ├── Canvas.tsx    # React Flow editor
│       │   ├── Chat.tsx      # AI chat interface
│       │   └── nodes/        # 12 AWS service nodes
│       └── lib/              # Zustand stores
│
├── packages/
│   ├── generated/            # IaC output
│   └── ui/                   # Shared components
│
└── docs/
    └── steering/             # Cloudscape patterns
```

---

## 🎓 Development Highlights

### Rapid Iteration (Single Day)
Built complete multi-agent AI platform with production patterns in one intensive development session.

### Key Decisions
1. **LangGraph over Step Functions**: More flexible for AI, easier local dev
2. **Cloudscape over Material-UI**: Professional AWS console aesthetic
3. **FastAPI over Flask**: Async support, type safety, auto-docs
4. **Monorepo**: Shared types, faster iteration
5. **uv over pip**: 10x faster Python package management

### Challenges Solved
- **LLM Reliability**: Fallback to static templates when Bedrock unavailable
- **Security Validation**: Automated scoring prevents insecure architectures
- **Multi-Format IaC**: Unified generator with format-specific renderers
- **State Management**: LangGraph checkpointing for workflow resumption
- **Cost Control**: Rate limiting + approval gates prevent runaway costs

---

## 📊 Metrics

### Code Quality
- **Lines of Code**: 4,568 Python + 2,000 TypeScript
- **Test Coverage**: ~50% (135 tests, all passing)
- **Type Safety**: 80%+ type hints
- **Documentation**: Comprehensive README + ADRs

### Performance
- **Response Time**: <2s for architecture generation
- **LLM Latency**: ~1-3s per agent call
- **Concurrent Users**: Tested up to 10 (rate limited)
- **Memory Usage**: ~200MB backend, ~50MB frontend

### Security
- **Pre-commit Hooks**: ✅ Secrets detection
- **Input Validation**: ✅ Size limits, sanitization
- **Rate Limiting**: ✅ Per IP
- **Security Scanning**: ✅ CodeQL + TruffleHog
- **Approval Gates**: ✅ Deployment requires confirmation

---

## 🔄 Comparison: Resume Tailor AI vs Scaffold AI

**Context**: These two projects showcase different orchestration approaches for different use cases.

### Resume Tailor AI (AWS-Native)
- **Orchestration**: AWS Step Functions
- **Use Case**: Deterministic resume tailoring workflow
- **State**: S3 + DynamoDB
- **Testing**: AWS SDK mocking (moto, localstack)
- **Deployment**: AWS-native (Lambda, Step Functions)
- **Strengths**: Predictable flows, AWS-integrated, production-proven
- **Development Time**: 3 days

### Scaffold AI (Framework-Based)
- **Orchestration**: LangGraph
- **Use Case**: Dynamic AI multi-agent conversations
- **State**: Built-in memory + checkpointing
- **Testing**: Pure Python (no AWS mocking needed)
- **Deployment**: Framework-agnostic (can run anywhere)
- **Strengths**: Dynamic routing, faster local dev, conversational AI
- **Development Time**: 1 day

### Shared Patterns (Production Mindset)
Both projects demonstrate:
- ✅ Validation-first handler pattern
- ✅ Robust error handling with fallbacks
- ✅ Pre-commit hooks (secrets detection)
- ✅ CI/CD with security scanning
- ✅ Rate limiting and cost controls
- ✅ Comprehensive testing
- ✅ Type safety (TypeScript + Python type hints)

### When to Use Each
| Scenario | Choose |
|----------|--------|
| Deterministic workflow with fixed steps | Step Functions |
| Dynamic routing based on LLM responses | LangGraph |
| AWS-native integration required | Step Functions |
| Framework-agnostic, portable solution | LangGraph |
| Need visual workflow editor in AWS Console | Step Functions |
| Rapid local development and debugging | LangGraph |
| Cost-sensitive at scale (>1,500 executions/month) | LangGraph |

**Portfolio Message**: "I can evaluate trade-offs and choose the right orchestration approach based on requirements, not just default to one solution."

---

## 🧪 Testing

### Run Tests
```bash
# Backend (135 tests)
cd apps/backend
uv run pytest -v

# Frontend (34 tests)
cd apps/web
pnpm test

# All tests
pnpm test:all
```

### Test Coverage
- **Unit Tests**: Agents, services, tools
- **Integration Tests**: LangGraph workflow, API endpoints
- **Security Tests**: Input validation, rate limiting, approval gates
- **Frontend Tests**: Components, stores, API integration

---

## 🚀 Deployment

### Local Development
```bash
# Terminal 1: Backend
cd apps/backend && uv run uvicorn scaffold_ai.main:app --reload

# Terminal 2: Frontend
cd apps/web && pnpm dev
```

### Production (Future)
- **Backend**: AWS ECS Fargate or Lambda (FastAPI)
- **Frontend**: Vercel or CloudFront + S3
- **Database**: DynamoDB (for persistence)
- **Monitoring**: CloudWatch + X-Ray
- **CI/CD**: GitHub Actions → AWS

---

## 📚 Documentation

- **[CRITICAL_REVIEW.md](CRITICAL_REVIEW.md)**: 44 identified improvements
- **[CONTRIBUTING.md](CONTRIBUTING.md)**: Development guidelines
- **[ROUND_3_FINDINGS.md](ROUND_3_FINDINGS.md)**: Security audit results
- **[TESTING_SUMMARY.md](TESTING_SUMMARY.md)**: Test coverage details
- **[docs/MULTI_FORMAT_IAC.md](docs/MULTI_FORMAT_IAC.md)**: IaC generation patterns

---

## 🎯 Roadmap

### ✅ Completed (v0.1.0)
- [x] Multi-agent LangGraph workflow
- [x] 12 AWS service types
- [x] Security gate with scoring
- [x] Multi-format IaC (CDK, CF, Terraform)
- [x] React Flow canvas editor
- [x] AWS Cloudscape UI
- [x] Rate limiting + approval gates
- [x] 135+ tests
- [x] Pre-commit security hooks

### 🚧 In Progress (v0.2.0)
- [ ] Authentication (JWT + API keys)
- [ ] Persistence layer (DynamoDB)
- [ ] Cost tracking per user
- [ ] Workflow state persistence
- [ ] Enhanced error handling

### 📋 Planned (v0.3.0)
- [ ] Collaboration features
- [ ] Version control for architectures
- [ ] Template marketplace
- [ ] AI-powered cost optimization
- [ ] Deployment history tracking

---

## 🤝 Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Quick Contribution Guide
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make changes and add tests
4. Run tests: `pnpm test:all`
5. Commit: `git commit -m 'feat: add amazing feature'`
6. Push: `git push origin feature/amazing-feature`
7. Open a Pull Request

---

## 📝 License

MIT License - see [LICENSE](LICENSE) for details.

---

## 👤 Author

**Your Name**
- GitHub: [@jfowler-cloud](https://github.com/jfowler-cloud)
- LinkedIn: [Your LinkedIn](https://linkedin.com/in/yourprofile)
- Portfolio: [Your Portfolio](https://yourportfolio.com)

---

## 🙏 Acknowledgments

- **AWS Cloudscape**: Professional UI components
- **LangGraph**: Flexible AI orchestration
- **React Flow**: Visual graph editor
- **FastAPI**: Modern Python web framework

---

## 📊 Project Stats

![GitHub stars](https://img.shields.io/github/stars/jfowler-cloud/scaffold-ai?style=social)
![GitHub forks](https://img.shields.io/github/forks/jfowler-cloud/scaffold-ai?style=social)
![GitHub issues](https://img.shields.io/github/issues/jfowler-cloud/scaffold-ai)
![GitHub pull requests](https://img.shields.io/github/issues-pr/jfowler-cloud/scaffold-ai)

---

## 🎬 Demo

### Screenshots
*Coming soon - add screenshots of:*
- Canvas with architecture nodes
- Chat interface with AI responses
- Generated code viewer
- Security gate in action
- Deployment flow

### Video Demo
*Coming soon - add video walkthrough*

---

## 💡 Why This Project?

This project demonstrates:

1. **LangGraph Expertise**: Complex multi-agent workflows with dynamic routing ([see comparison](LANGGRAPH_VS_STEP_FUNCTIONS.md))
2. **Rapid Development**: Full-stack AI platform in 2 weeks ([see journey](DEVELOPMENT_JOURNEY.md))
3. **Production Patterns**: Security, testing, monitoring, rate limiting
4. **AWS Knowledge**: 12 service types, Well-Architected principles
5. **Modern Stack**: Latest frameworks (Next.js 15, React 19, FastAPI)
6. **Code Quality**: Type safety, tests, documentation, pre-commit hooks

**Perfect for interviews discussing**:
- AI orchestration alternatives to Step Functions
- Multi-agent system design
- Security-first development
- Rapid prototyping and iteration
- Full-stack development skills

### 📖 Additional Documentation
- **[LANGGRAPH_VS_STEP_FUNCTIONS.md](LANGGRAPH_VS_STEP_FUNCTIONS.md)**: Detailed comparison with cost analysis
- **[DEVELOPMENT_JOURNEY.md](DEVELOPMENT_JOURNEY.md)**: 2-week development timeline and decisions
- **[CRITICAL_REVIEW.md](CRITICAL_REVIEW.md)**: Self-assessment with 44 identified improvements
- **[CONTRIBUTING.md](CONTRIBUTING.md)**: How to contribute to this project

---

**Built with ❤️ to showcase modern AI development patterns**
