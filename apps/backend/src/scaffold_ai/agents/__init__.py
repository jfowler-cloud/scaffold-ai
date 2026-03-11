"""AI Agent definitions for Scaffold AI."""

# Active agents — used by graph/nodes.py
from .security_specialist import SecuritySpecialistAgent
from .cdk_specialist import CDKSpecialistAgent
from .react_specialist import ReactSpecialistAgent

# Specialist agents — imported lazily in nodes.py
from .cloudformation_specialist import CloudFormationSpecialistAgent
from .terraform_specialist import TerraformSpecialistAgent
from .python_cdk_specialist import PythonCDKSpecialist

# interpreter.py and architect.py contain system prompt constants only.
# The actual intent classification and architecture design run as Lambda
# handlers via Step Functions (see apps/functions/).

__all__ = [
    "SecuritySpecialistAgent",
    "CDKSpecialistAgent",
    "ReactSpecialistAgent",
    "CloudFormationSpecialistAgent",
    "TerraformSpecialistAgent",
    "PythonCDKSpecialist",
]
