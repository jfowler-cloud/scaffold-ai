"""Interpreter agent for understanding user intent."""

INTERPRETER_SYSTEM_PROMPT = """You are an intent classification agent for Scaffold AI, a visual application architecture designer.

Your job is to analyze the user's message and classify their intent into one of these categories:

1. new_feature - User wants to add new functionality or components
   Examples: "add a database", "I need authentication", "create an API endpoint"

2. modify_graph - User wants to change existing architecture
   Examples: "remove the database", "connect auth to the API", "rename the component"

3. generate_code - User wants to generate actual code from the architecture
   Examples: "generate the CDK code", "create the React components", "deploy this"

4. explain - User wants to understand the current architecture or get help
   Examples: "what does this do?", "explain the flow", "how does auth connect?"

5. unknown - Cannot determine intent, need clarification

Respond with ONLY the intent category name, nothing else."""


class InterpreterAgent:
    """Agent that interprets user intent from natural language."""

    def __init__(self):
        self.system_prompt = INTERPRETER_SYSTEM_PROMPT

    async def classify(self, user_input: str) -> str:
        """
        Classify user intent.

        In production, this would call Claude via AWS Bedrock.
        For now, returns a simple keyword-based classification.
        """
        user_input_lower = user_input.lower()

        if any(word in user_input_lower for word in ["add", "create", "new", "include", "need"]):
            return "new_feature"
        elif any(word in user_input_lower for word in ["change", "modify", "update", "remove", "delete", "connect"]):
            return "modify_graph"
        elif any(word in user_input_lower for word in ["generate", "code", "deploy", "build", "cdk", "export"]):
            return "generate_code"
        elif any(word in user_input_lower for word in ["explain", "what", "how", "why", "help", "?"]):
            return "explain"
        else:
            return "new_feature"
