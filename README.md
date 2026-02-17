# Scaffold AI

Generative UI platform for designing full-stack AWS applications using a visual node graph editor and natural language chat. Built with AWS Cloudscape Design System for a professional, accessible, AWS console-style experience.

## ✨ New Features

- **🔒 Security Gate** - Validates architectures before code generation (blocks insecure designs)
- **📦 Multi-Format IaC** - Generate code in CDK (TypeScript), CloudFormation (YAML), or Terraform (HCL)
- **🎯 One-Click Generation** - "Generate Code" button for instant infrastructure code
- **📁 Code Viewer** - View all generated files in a tabbed modal interface

## Features

- **Visual Architecture Designer** - Drag-and-drop node graph editor powered by React Flow
- **Natural Language Chat** - Describe what you want to build and watch it appear
- **Multi-Agent AI Workflow** - Intent classification, architecture design, security review, and code generation
- **Security-First** - AWS Well-Architected security validation before code generation
- **12 AWS Service Types** - Lambda, API Gateway, DynamoDB, Cognito, S3, SQS, SNS, EventBridge, Step Functions, Kinesis, CloudFront, Streams
- **Multi-Format Code Generation** - Export to CDK (TypeScript), CloudFormation (YAML), or Terraform (HCL)
- **AWS Cloudscape UI** - Professional, accessible UI matching the AWS Console experience
- **Serverless-First** - Best practices baked in (pay-per-request, event-driven patterns)
- **Multi-Tenant Ready** - SaaS architecture patterns with tenant isolation

## Tech Stack

| Layer | Technologies |
|-------|-------------|
| **Frontend** | Next.js 15, React 19, React Flow, Zustand, AWS Cloudscape Design System |
| **Backend** | FastAPI, LangGraph, LangChain, AWS Bedrock (Claude 3 Haiku) |
| **Infrastructure** | AWS CDK (TypeScript), CloudFormation, Terraform |
| **Tooling** | pnpm, Turborepo, uv |

## Kiro Powers Integration

This project integrates steering documentation from multiple Kiro powers for enhanced AI-assisted development:

### Cloudscape Design System
- **90+ production-ready components** with built-in accessibility (WCAG 2.1 AA)
- **GenAI components** - ChatBubble, Avatar, PromptInput, LoadingBar for AI interfaces
- **Token-based theming** with light/dark mode support

### AWS Infrastructure as Code
- **CDK best practices** - L2 constructs, security, testing
- **CloudFormation validation** - cfn-lint, cfn-guard compliance checking
- **Deployment troubleshooting** - Pattern-based diagnostics

### Cloud Architect (CDK Python)
- **Well-Architected framework** adherence
- **Lambda design patterns** - Layered architecture, AWS Powertools
- **Testing strategy** - Remocal testing, unit/integration tests

### SaaS Builder
- **Multi-tenant architecture** - Tenant isolation at data layer
- **Billing integration** - Stripe, usage metering
- **Security patterns** - JWT, RBAC, encryption

## Steering Files

The project includes comprehensive steering documentation in `docs/steering/`:

### Cloudscape Design (`docs/steering/`)
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

### CDK Python Development (`docs/steering/cdk-python/`)
| File | Purpose |
|------|---------|
| `cdk-development-guidelines.md` | CDK constructs, stacks, naming conventions |
| `cloud-engineer-agent.md` | Agent tools and capabilities |
| `testing-strategy.md` | Remocal testing, unit/integration patterns |

### SaaS Architecture (`docs/steering/saas-builder/`)
| File | Purpose |
|------|---------|
| `architecture-principles.md` | Multi-tenancy, cost optimization, security |
| `billing-and-payments.md` | Stripe integration, usage metering |
| `implementation-patterns.md` | API design, Lambda patterns, DynamoDB keys |
| `repository-structure.md` | Project organization |

### AWS IaC (`docs/steering/aws-iac/`)
| File | Purpose |
|------|---------|
| `POWER.md` | CDK workflow, validation, troubleshooting |

## Project Structure

```
scaffold-ai/
├── apps/
│   ├── web/                    # Next.js frontend with Cloudscape
│   │   ├── app/                # App router pages
│   │   ├── components/         # React components
│   │   │   ├── Canvas.tsx      # React Flow graph editor
│   │   │   ├── Chat.tsx        # Cloudscape chat interface
│   │   │   └── nodes/          # 12 AWS service node components
│   │   └── lib/
│   │       └── store.ts        # Zustand state management
│   │
│   └── backend/                # FastAPI + LangGraph
│       └── src/scaffold_ai/
│           ├── main.py         # API endpoints
│           ├── graph/          # LangGraph workflow
│           │   ├── workflow.py # Multi-agent orchestration
│           │   └── state.py    # State management
│           └── agents/         # Specialized AI agents
│               ├── architect.py       # AWS Well-Architected design
│               ├── cdk_specialist.py  # CDK TypeScript generation
│               └── react_specialist.py # Cloudscape React generation
│
├── packages/
│   ├── ui/                     # Shared UI components
│   ├── generated/              # AI-generated CDK + React output
│   ├── eslint-config/
│   └── typescript-config/
│
├── docs/
│   └── steering/               # Kiro powers steering documentation
│       ├── foundations.md      # Cloudscape foundations
│       ├── layout-patterns.md  # Cloudscape layouts
│       ├── genai-patterns.md   # Cloudscape GenAI
│       ├── cdk-python/         # CDK development guidelines
│       ├── saas-builder/       # Multi-tenant SaaS patterns
│       └── aws-iac/            # AWS IaC best practices
│
└── turbo.json
```

## Getting Started

### Prerequisites

- Node.js 22+
- pnpm 10+
- Python 3.12+
- uv (Python package manager)
- AWS account with Bedrock access

### Installation

```bash
# Clone the repository
git clone https://github.com/jfowler-cloud/scaffold-ai.git
cd scaffold-ai

# Install dependencies
pnpm install
```

### Environment Variables

Create a `.env` file in `apps/backend/`:

```env
# AWS Bedrock Configuration
# Option 1: Use AWS CLI credentials (recommended)
AWS_REGION=us-east-1

# Option 2: Or provide credentials directly
# AWS_ACCESS_KEY_ID=your_access_key
# AWS_SECRET_ACCESS_KEY=your_secret_key

# Bedrock Model (optional - defaults to Claude 3 Haiku)
BEDROCK_MODEL_ID=us.anthropic.claude-3-haiku-20240307-v1:0
```

**AWS Setup:**
1. Configure AWS CLI: `aws configure`
2. Enable Bedrock access: AWS Console → Bedrock → Model access → Enable Anthropic Claude models
3. Ensure your IAM user/role has `bedrock:InvokeModel` permission

### Running the Application

```bash
# From project root
cd scaffold-ai
pnpm dev

# This starts:
# - Frontend at http://localhost:3000
# - Backend at http://localhost:8000
```

## Usage

1. **Design Architecture**
   - Type in chat: "Build a todo app with user authentication"
   - AI creates nodes on the canvas (Cognito, API Gateway, Lambda, DynamoDB)

2. **Select IaC Format**
   - Choose from dropdown: CDK (TypeScript), CloudFormation (YAML), or Terraform (HCL)

3. **Generate Code**
   - Click "Generate Code" button
   - Security gate validates architecture
   - View generated code in sidebar: "Generated Code"

4. **Deploy** (optional)
   - Copy generated code to your project
   - Deploy with `cdk deploy`, `sam deploy`, or `terraform apply`

## Architecture Patterns

### Serverless-First Design

Scaffold AI generates architectures following AWS best practices:

```
Frontend → API Gateway → Lambda → DynamoDB
                      ↘ SQS → Lambda (async)
```

### Multi-Tenant SaaS Pattern

For SaaS applications with tenant isolation:

```
Cognito (JWT with tenant claims)
    ↓
API Gateway → Lambda Authorizer (extract tenant)
    ↓
Lambda → DynamoDB (pk: ${tenantId}#${entityType}#${id})
```

### Event-Driven Pattern

For decoupled, scalable architectures:

```
Lambda → EventBridge → [Lambda, SQS, SNS, Step Functions]
```

## How It Works

### 1. Visual Node Editor

The canvas supports 12 AWS service types:

| Node | Service | Use Case |
|------|---------|----------|
| Frontend | Next.js/React | Static site with CloudFront |
| Auth | Cognito | User authentication, JWT |
| API | API Gateway | REST/HTTP APIs |
| Lambda | Lambda | Serverless compute |
| Database | DynamoDB | NoSQL with tenant isolation |
| Storage | S3 | Object storage |
| Queue | SQS | Async processing |
| Events | EventBridge | Event bus |
| Notification | SNS | Pub/sub |
| Workflow | Step Functions | Orchestration |
| CDN | CloudFront | Content delivery |
| Stream | Kinesis | Real-time data |

### 2. Natural Language Chat

Describe your architecture:

```
You: "Build a multi-tenant SaaS with user authentication, REST API, and database"
```

The AI will:
1. Design tenant-isolated DynamoDB schema
2. Configure Cognito with JWT tenant claims
3. Set up API Gateway with Lambda authorizer
4. Generate Lambda functions with RBAC

### 3. Code Generation

#### CDK Infrastructure

Generated code follows AWS Well-Architected best practices:

```typescript
// DynamoDB with tenant isolation
const table = new dynamodb.Table(this, 'DataTable', {
  partitionKey: { name: 'pk', type: dynamodb.AttributeType.STRING },
  sortKey: { name: 'sk', type: dynamodb.AttributeType.STRING },
  billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
  pointInTimeRecovery: true,
});

// Lambda with Powertools
const fn = new lambda.Function(this, 'ApiHandler', {
  runtime: lambda.Runtime.NODEJS_20_X,
  handler: 'index.handler',
  tracing: lambda.Tracing.ACTIVE,
  environment: {
    TABLE_NAME: table.tableName,
    POWERTOOLS_SERVICE_NAME: 'my-service',
  },
});

// Least privilege IAM
table.grantReadWriteData(fn);
```

#### React Components (Cloudscape)

Generated frontend uses Cloudscape Design System:

```tsx
import AppLayout from '@cloudscape-design/components/app-layout';
import Table from '@cloudscape-design/components/table';
import StatusIndicator from '@cloudscape-design/components/status-indicator';

export default function ResourcesPage() {
  return (
    <AppLayout
      content={
        <Table
          columnDefinitions={[
            { id: 'name', header: 'Name', cell: item => item.name },
            { id: 'status', header: 'Status', cell: item => (
              <StatusIndicator type={item.statusType}>
                {item.status}
              </StatusIndicator>
            )},
          ]}
          items={resources}
          selectionType="multi"
        />
      }
    />
  );
}
```

## Development

### Commands

```bash
# Root commands
pnpm dev              # Run all services
pnpm build            # Build all packages
pnpm lint             # Lint all packages

# Frontend (apps/web)
pnpm dev:web          # Dev server

# Backend (apps/backend)
pnpm dev:backend      # Dev server
cd apps/backend
uv run pytest         # Run tests
uv run ruff check     # Lint
uv run mypy src       # Type check
```

### Using Cloudscape Components

Follow the patterns in `docs/steering/`:

```tsx
// Import components individually for tree-shaking
import Button from '@cloudscape-design/components/button';
import Container from '@cloudscape-design/components/container';

// Use the { detail } event pattern
<Input
  value={value}
  onChange={({ detail }) => setValue(detail.value)}
/>

// Use SpaceBetween for consistent spacing
<SpaceBetween size="l">
  <FormField label="Name"><Input /></FormField>
  <FormField label="Email"><Input type="email" /></FormField>
</SpaceBetween>
```

### Adding New Service Types

1. Create node component in `apps/web/components/nodes/`
2. Register in `apps/web/components/Canvas.tsx`
3. Add CDK template in `apps/backend/src/scaffold_ai/agents/cdk_specialist.py`
4. Add Cloudscape template in `apps/backend/src/scaffold_ai/agents/react_specialist.py`
5. Update architect agent patterns in `apps/backend/src/scaffold_ai/agents/architect.py`

## Testing Strategy

Following the remocal testing approach from cloud-architect power:

### Unit Tests
- Pure business logic with mocks
- Fast execution (<1s)
- Test individual functions

### Integration Tests
- Lambda code locally with real AWS services
- 1-5s execution
- Full debugging with breakpoints

### CDK Tests
- Fine-grained assertions
- Snapshot testing
- Resource property validation

## Security Gate

Scaffold AI includes a security gate that validates architectures before code generation:

- **Automatic Security Review** - Evaluates architecture against AWS Well-Architected security best practices
- **Security Scoring** - 0-100 score based on authentication, data protection, network security, monitoring, and compliance
- **Blocks Insecure Designs** - Code generation is prevented if security score < 70 or critical issues exist
- **Actionable Feedback** - Detailed explanations of issues and recommendations for fixes

See `apps/backend/SECURITY_GATE_SUMMARY.md` for full documentation.

## Multi-Format IaC Support

Generate infrastructure code in your preferred format:

| Format | File | Use Case |
|--------|------|----------|
| **CDK (TypeScript)** | `lib/scaffold-ai-stack.ts` | Type-safe, L2 constructs, AWS native |
| **CloudFormation (YAML)** | `template.yaml` | AWS SAM, native AWS format |
| **Terraform (HCL)** | `main.tf` | Multi-cloud, enterprise workflows |

All formats include the same security best practices and are validated by the security gate.

See `docs/MULTI_FORMAT_IAC.md` for examples and usage.

## Acknowledgments

- [AWS Cloudscape Design System](https://cloudscape.design) - UI components
- [kiro-powers (praveenc)](https://github.com/praveenc/kiro-powers) - Cloudscape steering
- [kiro-powers (official)](https://github.com/kirodotdev/powers) - AWS IaC, Cloud Architect, SaaS Builder
- [React Flow](https://reactflow.dev) - Node graph visualization
- [LangGraph](https://github.com/langchain-ai/langgraph) - Multi-agent orchestration

## Roadmap

- [x] Cloudscape Design System integration
- [x] Multi-format IaC generation (CDK, CloudFormation, Terraform)
- [x] Security gate with AWS Well-Architected validation
- [x] One-click code generation button
- [x] Generated code viewer with tabs
- [x] Multi-tenant SaaS patterns
- [ ] React component generation (Cloudscape pages)
- [ ] Python CDK support
- [ ] Multi-stack architectures
- [ ] CDK deployment integration
- [ ] Cost estimation
- [ ] Architecture templates library
- [ ] Collaboration features

## License

MIT
