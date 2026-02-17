# scaffold-ai

Generative UI platform for designing full-stack applications (React 19 + AWS CDK) using a visual node graph and natural language chat.

## Structure

```
scaffold-ai/
├── apps/
│   ├── web/          # Next.js 15 frontend
│   └── backend/      # FastAPI + LangGraph backend
├── packages/
│   ├── ui/           # Shared UI components (shadcn)
│   ├── eslint-config/
│   ├── typescript-config/
│   └── generated/    # Generated CDK + React output
└── turbo.json
```

## Getting Started

```bash
# Install dependencies
pnpm install

# Run development servers
pnpm dev

# Run only frontend
pnpm dev:web

# Run only backend
pnpm dev:backend
```

## Tech Stack

- **Frontend**: Next.js 15, React 19, React Flow, Zustand, Tailwind CSS, shadcn/ui
- **Backend**: FastAPI, LangGraph, LangChain, AWS Bedrock
- **Infrastructure**: AWS CDK (generated)
