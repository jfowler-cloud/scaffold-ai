"""AI Agent definitions for Scaffold AI."""

# Active agents — used by graph/nodes.py
from .security_specialist import SecuritySpecialistAgent
from .cdk_specialist import CDKSpecialistAgent
from .react_specialist import ReactSpecialistAgent

# Specialist agents — imported lazily in nodes.py
from .cloudformation_specialist import CloudFormationSpecialistAgent
from .terraform_specialist import TerraformSpecialistAgent
from .python_cdk_specialist import PythonCDKSpecialist

# NOTE: InterpreterAgent and ArchitectAgent contain useful system prompts and
# keyword-based logic but are not wired into the LangGraph workflow yet.
# The real intent classification and architecture design live in graph/nodes.py.
# These are kept for future refactoring — either wire them up or remove them.

__all__ = [
    "SecuritySpecialistAgent",
    "CDKSpecialistAgent",
    "ReactSpecialistAgent",
    "CloudFormationSpecialistAgent",
    "TerraformSpecialistAgent",
    "PythonCDKSpecialist",
]
