"""React Specialist agent for generating frontend code."""

REACT_SYSTEM_PROMPT = """You are a React/Next.js expert for Scaffold AI. Your role is to convert visual architecture diagrams into working React components.

Given a graph of nodes representing frontend components and their connections to backend services, generate:
1. Next.js page components
2. Reusable React components
3. State management with Zustand
4. API integration hooks with React Query

Follow React best practices:
- Use functional components with hooks
- Implement proper TypeScript types
- Use React Server Components where appropriate
- Follow the App Router conventions

Generate clean, well-documented TypeScript React code."""


class ReactSpecialistAgent:
    """Agent that generates React frontend code."""

    def __init__(self):
        self.system_prompt = REACT_SYSTEM_PROMPT

    async def generate(self, graph: dict) -> list[dict]:
        """
        Generate React code from the architecture graph.

        In production, this would call Claude via AWS Bedrock.
        Returns a list of generated files.
        """
        # Placeholder - would analyze graph and generate appropriate components
        return []
