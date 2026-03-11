---
inclusion: always
---

# Portfolio Project Standards

> Every project scaffold-ai generates must comply with these standards so the Project Status Portal (PSP) can monitor it automatically, agents can fix it unattended, and it can be bootstrapped rapidly.

---

## Daily Workflow

```
Morning: PSP Dashboard → situational awareness
  ↓
Idea Fairy → pick next work item
  ↓
Project Planner → design & plan
  ↓
Scaffold AI → bootstrap new repo from this standard
  ↓
Build → write code with full test coverage from day one
  ↓
PSP monitors it automatically
```

---

## 1. Mono-Repo Structure

Every generated project follows this layout exactly:

```
project-name/
├── apps/
│   ├── agents/              # AI agents (Strands, Python)
│   │   ├── pyproject.toml
│   │   └── tests/
│   ├── functions/           # Lambda handlers (Python)
│   │   ├── pyproject.toml
│   │   └── tests/
│   ├── infra/               # CDK stacks (TypeScript)
│   │   ├── lib/
│   │   ├── test/
│   │   └── package.json
│   └── web/                 # React frontend (TypeScript)
│       ├── src/
│       │   └── __tests__/
│       ├── e2e/
│       ├── vitest.config.ts
│       └── playwright.config.ts
├── config.json              # PSP-compatible project config
├── CLAUDE.md                # AI assistant instructions
├── RUNBOOK.md               # Incident response guide
├── CHANGELOG.md             # Version history
├── dev.sh                   # Local dev startup script
├── docker-compose.yml       # LocalStack for local AWS simulation
└── README.md
```

### Project Type Variations

| Project Type | `apps/agents/` | `apps/functions/` | `apps/web/` | `apps/infra/` |
|---|:-:|:-:|:-:|:-:|
| Full-stack AI app | Y | Y | Y | Y |
| API-only service | - | Y | - | Y |
| Frontend-only | - | - | Y | Y |
| Agent-only | Y | Y | - | Y |

---

## 2. Frontend Framework: React + Vite SPA (Default)

**Default to React SPA (Vite) unless SSR is genuinely required.**

| Framework | When to Use | Hosting | Cost |
|---|---|---|---|
| **React + Vite (SPA)** | Default — dashboards, internal tools, AI UIs, anything behind auth | S3 + CloudFront | ~$1/mo |
| **Next.js (SSR)** | Only when SSR is genuinely needed: public SEO pages, dynamic OG tags | Amplify Hosting | Pay-per-request |

Only use Next.js when the project needs one of:
- Public-facing pages that search engines must index (not behind auth)
- Dynamic OG/meta tags for social sharing
- Server-side API proxying (though Lambda functions handle this too)

**scaffold-ai** has been migrated to React + Vite SPA (migration complete).

---

## 3. UI Theme: Dark Mode with Red Accent

Every generated frontend uses dark-mode-first with a red accent palette.

### Dark Mode Default

```typescript
const [darkMode, setDarkMode] = useState<boolean>(() => {
  const saved = localStorage.getItem('${projectPrefix}-darkMode')
  return saved !== null ? JSON.parse(saved) : true
})

useEffect(() => {
  applyMode(darkMode ? Mode.Dark : Mode.Light)
  localStorage.setItem('${projectPrefix}-darkMode', JSON.stringify(darkMode))
}, [darkMode])
```

### Red Accent — Cloudscape Projects (`index.css`)

```css
html body {
  --color-primary-500-q9c16y: #e8001c !important;  /* Primary */
  --color-primary-600-1lcy1k: #cc0018 !important;
  --color-primary-700-n6k121: #a80014 !important;
  --color-primary-400-n8h4bx: #ff5c5c !important;
  --color-primary-300-5q65ox: #ff9a9a !important;
  --color-primary-200-vubr4w: #ffc5c5 !important;
  --color-primary-100-f62fz9: #ffe0e0 !important;
  --color-primary-50-1y05xv:  #fff1f1 !important;
}
```

### Red Accent — Tailwind Projects (`tailwind.config.ts`)

```typescript
export default {
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        accent: {
          50:  '#fff1f1',
          100: '#ffe0e0',
          200: '#ffc5c5',
          300: '#ff9a9a',
          400: '#ff5c5c',
          500: '#e8001c',  // Primary
          600: '#cc0018',
          700: '#a80014',
          800: '#8a0010',
          900: '#6b000c',
        }
      }
    }
  }
}
```

Usage: `bg-accent-500 hover:bg-accent-600 text-white`

### Dark Mode Toggle (All Projects)

```typescript
// In top navigation
{ type: 'button', text: darkMode ? '☀️ Light' : '🌙 Dark', onClick: () => setDarkMode(d => !d) }
```

---

## 4. Test Coverage Requirements

| Layer | Minimum | Framework | Report |
|---|:-:|---|---|
| Frontend unit | 95% lines | Vitest + React Testing Library | Istanbul JSON |
| Frontend E2E | All critical flows | Playwright | JSON reporter |
| Backend unit | 95% lines | pytest + moto | coverage.json |
| Agents | 95% lines | pytest + mocked tools | coverage.json |
| CDK infra | Snapshots + assertions | Jest + CDK assertions | — |

### `vitest.config.ts` (Required)

```typescript
coverage: {
  provider: 'istanbul',
  reporter: ['text', 'json', 'lcov'],
  include: ['src/**/*.{ts,tsx}'],
  exclude: ['src/main.tsx', 'src/test/**'],
  thresholds: { lines: 95, branches: 90, functions: 90, statements: 95 }
}
```

### `pyproject.toml` pytest config (Required)

```toml
[tool.pytest.ini_options]
addopts = "--cov=. --cov-report=json --cov-report=term-missing -q"

[dependency-groups]
dev = [
    "pytest>=8.0",
    "pytest-cov>=5.0",
    "pytest-json-report>=1.5",
    "moto[dynamodb,s3,ssm,secretsmanager]>=5.0"
]
```

### `package.json` scripts (Frontend)

```json
{
  "scripts": {
    "test": "vitest --run",
    "test:coverage": "vitest --run --coverage",
    "test:e2e": "playwright test",
    "test:e2e:headed": "playwright test --headed"
  }
}
```

---

## 5. PSP Integration

### `config.json` (project root)

```json
{
  "testCommands": {
    "backend": "cd apps/functions && uv run pytest tests/ --cov=. --cov-report=json -q",
    "frontend": "cd apps/web && npm run test:coverage",
    "e2e": "cd apps/web && npm run test:e2e"
  }
}
```

### S3 Artifact Names PSP Expects

| File | Producer |
|---|---|
| `backend-results.json` | `pytest --json-report` |
| `backend-coverage.json` | `pytest --cov --cov-report=json` |
| `frontend-results.json` | vitest JSON reporter |
| `frontend-coverage.json` | Istanbul JSON |
| `e2e-results.json` | Playwright JSON reporter |

### After Bootstrap

1. Add entry to `project-status-portal/config.json` projects array
2. Run `SeedProjects` Lambda (or Admin UI) to register
3. Verify first test run passes in PSP dashboard

---

## 6. Observability

### Lambda Powertools (Every Handler)

```python
from aws_lambda_powertools import Logger, Metrics, Tracer

logger = Logger(service="project-name")
metrics = Metrics(namespace="ProjectName")
tracer = Tracer()

@logger.inject_lambda_context
@metrics.log_metrics
@tracer.capture_lambda_handler
def handler(event, context):
    ...
```

### Required CloudWatch Alarms (CDK)

| Alarm | Threshold |
|---|---|
| Lambda error rate | > 5% over 5 min → SNS → Slack |
| Lambda duration P99 | > 80% of timeout → SNS → Slack |
| DynamoDB throttled requests | > 0 over 1 min → SNS → Slack |
| Step Functions execution failed | > 0 → SNS → Slack |
| API 5xx rate | > 1% over 5 min → SNS → Slack |

### Resource Tagging (Required)

```typescript
Tags.of(stack).add('Project', 'project-name');
Tags.of(stack).add('Environment', 'production');
Tags.of(stack).add('ManagedBy', 'cdk');
Tags.of(stack).add('CostCenter', 'portfolio');
```

---

## 7. CI/CD

### `.github/workflows/ci.yml`

```yaml
name: CI
on: [push, pull_request]

jobs:
  frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
      - run: cd apps/web && npm ci
      - run: cd apps/web && npx tsc --noEmit
      - run: cd apps/web && npm run test:coverage
      - run: cd apps/web && npx playwright install --with-deps
      - run: cd apps/web && npm run test:e2e

  backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v4
      - run: cd apps/functions && uv sync
      - run: cd apps/functions && uv run ruff check .
      - run: cd apps/functions && uv run pytest tests/

  infrastructure:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
      - run: cd apps/infra && npm ci
      - run: cd apps/infra && npx cdk synth
      - run: cd apps/infra && npm test

  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: cd apps/web && npm audit --audit-level=high
      - uses: astral-sh/setup-uv@v4
      - run: cd apps/functions && uv run pip-audit
      - uses: github/codeql-action/init@v3
      - uses: github/codeql-action/analyze@v3
```

### `.github/dependabot.yml`

```yaml
version: 2
updates:
  - package-ecosystem: "npm"
    directory: "/apps/web"
    schedule: { interval: "weekly" }
    open-pull-requests-limit: 5
  - package-ecosystem: "pip"
    directory: "/apps/functions"
    schedule: { interval: "weekly" }
    open-pull-requests-limit: 5
  - package-ecosystem: "pip"
    directory: "/apps/agents"
    schedule: { interval: "weekly" }
    open-pull-requests-limit: 5
  - package-ecosystem: "npm"
    directory: "/apps/infra"
    schedule: { interval: "weekly" }
    open-pull-requests-limit: 5
```

---

## 8. Secrets Management

| Secret | Storage | Rotation |
|---|---|---|
| GitHub PAT | Secrets Manager (`psp/github-pat`) | 90-day expiry, alarm at 14 days |
| Slack webhook | SSM Parameter (`psp/slack-webhook-url`) | Manual on channel change |
| Per-project API keys | Secrets Manager | Automatic rotation via Lambda where supported |

---

## 9. Local Development

### `docker-compose.yml` (Required)

```yaml
version: '3.8'
services:
  localstack:
    image: localstack/localstack:latest
    ports:
      - "4566:4566"
    environment:
      - SERVICES=dynamodb,s3,secretsmanager,ssm,lambda,stepfunctions
      - DEFAULT_REGION=us-east-1
      - DOCKER_HOST=unix:///var/run/docker.sock
    volumes:
      - "/var/run/docker.sock:/var/run/docker.sock"
      - "./scripts/localstack-init:/etc/localstack/init/ready.d"
```

### `dev.sh` Pattern

```bash
#!/bin/bash
docker-compose up -d
until curl -s http://localhost:4566/_localstack/health | grep -q '"dynamodb": "running"'; do sleep 1; done
cd apps/functions && uv sync &
cd apps/web && VITE_AWS_ENDPOINT=http://localhost:4566 npm run dev &
```

---

## 10. Versioning

- **SemVer**: MAJOR (breaking), MINOR (new features), PATCH (fixes)
- Tag releases on main: `git tag -a v1.2.0 -m "description"`
- Maintain `CHANGELOG.md` in [Keep a Changelog](https://keepachangelog.com/) format

---

## 11. Cost Monitoring

### Budget Alarm (CDK, Required)

```typescript
new budgets.CfnBudget(this, 'ProjectBudget', {
  budget: {
    budgetName: `${projectName}-monthly`,
    budgetLimit: { amount: 10, unit: 'USD' },
    budgetType: 'COST',
    timeUnit: 'MONTHLY',
    costFilters: { TagKeyValue: [`user:Project$${projectName}`] }
  },
  notificationsWithSubscribers: [{
    notification: {
      comparisonOperator: 'GREATER_THAN',
      notificationType: 'ACTUAL',
      threshold: 80,
      thresholdType: 'PERCENTAGE'
    },
    subscribers: [{ address: 'your-email@example.com', subscriptionType: 'EMAIL' }]
  }]
});
```

Expected monthly cost per project: **$3–10** (alert threshold: $25)

---

## 12. Accessibility

### Playwright + axe-core (Required in E2E)

```typescript
import AxeBuilder from '@axe-core/playwright';

test('page has no accessibility violations', async ({ page }) => {
  await page.goto('/');
  const results = await new AxeBuilder({ page })
    .withTags(['wcag2a', 'wcag2aa'])
    .analyze();
  expect(results.violations).toEqual([]);
});
```

Add `@axe-core/playwright` to devDependencies.

---

## 13. Bootstrap Checklist

When scaffold-ai generates a new project, it must produce all of:

### Files

- [ ] `apps/web/` — React + Vite scaffold (Cloudscape or Tailwind)
- [ ] `apps/web/src/index.css` — Red accent theme (Cloudscape) OR `tailwind.config.ts` with accent colors
- [ ] `apps/web/vitest.config.ts` — With 95% coverage thresholds
- [ ] `apps/web/playwright.config.ts` — E2E config
- [ ] `apps/web/src/__tests__/App.test.tsx` — Starter unit test
- [ ] `apps/web/e2e/01-navigation.spec.ts` — Starter E2E (includes axe a11y check)
- [ ] `apps/functions/` — Lambda handlers with Powertools
- [ ] `apps/functions/tests/conftest.py` — moto fixtures + env vars
- [ ] `apps/functions/tests/test_*.py` — Starter test per handler
- [ ] `apps/agents/` — Strands agent scaffold (if applicable)
- [ ] `apps/agents/tests/` — Agent tests with mocked tools
- [ ] `apps/infra/lib/` — CDK stacks (database, auth, functions, workflow)
- [ ] `apps/infra/test/` — Snapshot + assertion tests
- [ ] `config.json` — PSP-compatible project config
- [ ] `.github/workflows/ci.yml` — CI pipeline (frontend, backend, infra, security jobs)
- [ ] `.github/dependabot.yml` — Dependency scanning
- [ ] `CLAUDE.md` — AI assistant context
- [ ] `RUNBOOK.md` — Incident response guide
- [ ] `CHANGELOG.md` — Version history
- [ ] `dev.sh` — Local dev startup
- [ ] `docker-compose.yml` — LocalStack
- [ ] `README.md` — Project overview

### CDK Account Context

```typescript
const account = app.node.tryGetContext('account') || 'testing';
const config = {
  testing: { account: '111111111111', region: 'us-east-1', removalPolicy: RemovalPolicy.DESTROY },
  prod:    { account: '222222222222', region: 'us-east-1', removalPolicy: RemovalPolicy.RETAIN },
};
```

---

## 14. Definition of "Production Ready"

A project is production-ready when ALL of the following are true:

1. Follows mono-repo structure (Section 1)
2. React + Vite SPA unless SSR is genuinely required (Section 2)
3. Dark mode with red accent theme applied (Section 3)
4. Frontend unit coverage ≥ 95% with thresholds enforced (Section 4)
5. Frontend E2E covers all critical flows including a11y checks (Sections 4, 12)
6. Backend unit coverage ≥ 95% with thresholds enforced (Section 4)
7. CDK snapshot + assertion tests exist for all stacks (Section 4)
8. CI/CD pipeline with security scanning runs on every push (Section 7)
9. Dependabot enabled for all package ecosystems (Section 7)
10. Secrets have rotation policy or expiry monitoring (Section 8)
11. CloudWatch alarms configured for errors, latency, throttles (Section 6)
12. Cost budget alarm with project tagging (Section 11)
13. `RUNBOOK.md` exists with common triage scenarios (Section 13)
14. `CHANGELOG.md` maintained, releases tagged with SemVer (Section 10)
15. Local dev works via docker-compose + LocalStack (Section 9)
16. Registered in PSP and passing daily automated runs (Section 5)
17. `CLAUDE.md` exists with project context for AI-assisted development
