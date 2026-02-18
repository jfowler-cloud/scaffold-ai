# Contributing to Scaffold AI

Thank you for your interest in contributing to Scaffold AI! This document provides guidelines and instructions for contributing.

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow

## Getting Started

### Prerequisites
- Python 3.12+
- Node.js 22+
- pnpm 10+
- AWS CLI configured
- uv (Python package manager)

### Setup
```bash
# Clone the repository
git clone https://github.com/jfowler-cloud/scaffold-ai.git
cd scaffold-ai

# Install dependencies
pnpm install

# Backend setup
cd apps/backend
uv sync
cp .env.example .env
# Edit .env with your AWS credentials

# Frontend setup
cd ../web
pnpm install

# Run tests
cd ../backend
uv run pytest

cd ../web
pnpm test
```

## Development Workflow

### 1. Create a Branch
```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

### 2. Make Changes
- Write clean, readable code
- Follow existing code style
- Add tests for new features
- Update documentation

### 3. Run Tests
```bash
# Backend
cd apps/backend
uv run pytest -v

# Frontend
cd apps/web
pnpm test
```

### 4. Commit Changes
```bash
# Use conventional commits
git commit -m "feat: add new feature"
git commit -m "fix: resolve bug"
git commit -m "docs: update README"
git commit -m "test: add tests for X"
```

### Commit Message Format
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `test:` Test additions/changes
- `refactor:` Code refactoring
- `perf:` Performance improvements
- `chore:` Maintenance tasks

### 5. Push and Create PR
```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub.

## Code Style

### Python
- Follow PEP 8
- Use type hints
- Maximum line length: 100 characters
- Use Ruff for linting (runs in pre-commit)

```python
# Good
def process_data(input: str, max_length: int = 100) -> dict:
    """Process input data with validation."""
    if len(input) > max_length:
        raise ValueError(f"Input too long: {len(input)}")
    return {"processed": input.strip()}

# Bad
def process_data(input, max_length=100):
    if len(input) > max_length:
        raise ValueError("Input too long")
    return {"processed": input.strip()}
```

### TypeScript/React
- Use TypeScript strict mode
- Prefer functional components
- Use proper types (no `any`)
- Maximum line length: 100 characters

```typescript
// Good
interface Props {
  message: string;
  onSubmit: (value: string) => void;
}

export function Component({ message, onSubmit }: Props) {
  return <div>{message}</div>;
}

// Bad
export function Component(props: any) {
  return <div>{props.message}</div>;
}
```

## Testing Guidelines

### Backend Tests
- Place tests in `apps/backend/tests/`
- Use pytest fixtures
- Mock external services (Bedrock, AWS)
- Aim for 80%+ coverage

```python
import pytest
from scaffold_ai.services.cost_estimator import CostEstimator

def test_estimate_empty_graph():
    estimator = CostEstimator()
    result = estimator.estimate({"nodes": [], "edges": []})
    assert result["total_monthly"] == 0
```

### Frontend Tests
- Place tests in `apps/web/__tests__/`
- Use Vitest and React Testing Library
- Test user interactions, not implementation

```typescript
import { render, screen } from '@testing-library/react';
import { Chat } from '@/components/Chat';

test('renders chat input', () => {
  render(<Chat />);
  expect(screen.getByRole('textbox')).toBeInTheDocument();
});
```

## Pull Request Guidelines

### PR Title
Use conventional commit format:
- `feat: add cost estimation caching`
- `fix: resolve deployment timeout issue`

### PR Description
Include:
- What changed and why
- Related issue number (if applicable)
- Screenshots (for UI changes)
- Testing performed
- Breaking changes (if any)

### PR Checklist
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] Code follows style guidelines
- [ ] All tests pass
- [ ] No new warnings
- [ ] Commit messages follow convention

## Architecture Guidelines

### Backend
- Keep agents focused and single-purpose
- Use Pydantic for all data models
- Add type hints to all functions
- Handle errors specifically (not broad `except Exception`)
- Add logging for debugging

### Frontend
- Use Cloudscape Design System components
- Keep components small and focused
- Use Zustand for state management
- Implement proper loading states
- Add error boundaries

## Security Guidelines

- Never commit secrets or credentials
- Use environment variables for configuration
- Validate all user input
- Sanitize generated code before writing to disk
- Use pre-commit hooks (automatically installed)

## Documentation

- Update README.md for user-facing changes
- Add docstrings to all functions
- Document complex algorithms
- Update API documentation (FastAPI auto-generates)

## Questions?

- Open an issue for bugs or feature requests
- Start a discussion for questions
- Check existing issues before creating new ones

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.
