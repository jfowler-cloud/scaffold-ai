"""Utility functions for LLM response processing."""


def strip_code_fences(text: str) -> str:
    """
    Strip markdown code fences from LLM response text.

    Handles common fence types: ```json, ```typescript, ```python, ```
    """
    for fence in ("```json", "```typescript", "```python", "```"):
        if fence in text:
            parts = text.split(fence, 1)
            if len(parts) > 1:
                return parts[1].split("```", 1)[0].strip()
    return text.strip()
