"""FastAPI application for Scaffold AI backend."""

import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, field_validator
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from .graph.state import GraphState
from .graph.workflow import run_workflow
from .services.cdk_deployment import CDKDeploymentService
from .services.cost_estimator import CostEstimator
from .services.security_autofix import SecurityAutoFix
from .services.security_history import SecurityHistoryService
from .services.sharing import SharingService
from .services.templates import ArchitectureTemplates

load_dotenv()

# Rate limiter
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="Scaffold AI Backend",
    description="LangGraph-powered backend for the Scaffold AI platform",
    version="0.1.0",
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS — configurable via ALLOWED_ORIGINS env var (comma-separated).
# Defaults to localhost:3000 for local development.
_raw_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000")
ALLOWED_ORIGINS = [o.strip() for o in _raw_origins.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

# Initialize deployment service
deployment_service = CDKDeploymentService()
cost_estimator = CostEstimator()
security_autofix = SecurityAutoFix()
templates = ArchitectureTemplates()
sharing_service = SharingService()
security_history = SecurityHistoryService()


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""

    user_input: str
    graph_json: dict | None = None
    iac_format: str = "cdk"  # cdk, cloudformation, terraform, or python-cdk

    @field_validator("user_input")
    @classmethod
    def validate_user_input(cls, v: str) -> str:
        """Validate user input length."""
        if len(v) > 5000:
            raise ValueError("user_input must be 5000 characters or less")
        if not v.strip():
            raise ValueError("user_input cannot be empty")
        return v

    @field_validator("iac_format")
    @classmethod
    def validate_iac_format(cls, v: str) -> str:
        """Validate IaC format."""
        allowed = ["cdk", "cloudformation", "terraform", "python-cdk"]
        if v not in allowed:
            raise ValueError(f"iac_format must be one of: {', '.join(allowed)}")
        return v


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""

    message: str
    updated_graph: dict | None = None
    generated_files: list[dict] | None = None


class DeployRequest(BaseModel):
    """Request model for deployment endpoint."""

    stack_name: str
    cdk_code: str
    app_code: str
    region: str = "us-east-1"
    profile: str | None = None
    require_approval: bool = True

    @field_validator("stack_name")
    @classmethod
    def validate_stack_name(cls, v: str) -> str:
        """Validate stack name to prevent command injection."""
        import re

        if not re.match(r"^[A-Za-z][A-Za-z0-9-]{0,127}$", v):
            raise ValueError(
                "stack_name must be alphanumeric with hyphens, start with letter, 1-128 chars"
            )
        return v


class GraphRequest(BaseModel):
    """Request model for graph-based endpoints."""

    graph: dict


class ShareRequest(BaseModel):
    """Request model for sharing endpoint."""

    graph: dict
    title: str = "Shared Architecture"


class SecurityHistoryRequest(BaseModel):
    """Request model for security history."""

    architecture_id: str
    score: int
    issues: list[dict] = []


class DeployResponse(BaseModel):
    """Response model for deployment endpoint."""

    success: bool
    message: str | None = None
    error: str | None = None
    outputs: dict | None = None


@app.get("/")
async def root() -> dict:
    """Root endpoint with API information."""
    return {"status": "ok", "service": "scaffold-ai-backend", "version": "0.1.0"}


@app.get("/health")
async def health() -> dict:
    """
    Health check endpoint with service status.

    Returns:
        dict: Health status including Bedrock availability
    """
    health_status = {"status": "healthy", "services": {}}

    # Check Bedrock connectivity
    try:
        from .graph.nodes import get_llm

        get_llm()  # Just check if it initializes
        health_status["services"]["bedrock"] = "available"
    except Exception:
        health_status["services"]["bedrock"] = "unavailable"
        health_status["status"] = "degraded"

    return health_status


@app.post("/api/chat", response_model=ChatResponse)
@limiter.limit("10/minute")
async def chat(request: Request, body: ChatRequest):
    """
    Process a chat message through the LangGraph workflow.

    This endpoint:
    1. Interprets the user's intent
    2. Routes to appropriate agents (architect, CDK specialist, React specialist)
    3. Returns the response and any graph/file updates
    """
    import asyncio
    import logging

    logger = logging.getLogger(__name__)

    try:
        # Initialize state
        initial_state: GraphState = {
            "user_input": body.user_input,
            "intent": "new_feature",  # Will be determined by interpreter
            "graph_json": body.graph_json or {"nodes": [], "edges": []},
            "iac_format": body.iac_format,
            "generated_files": [],
            "errors": [],
            "retry_count": 0,
            "response": "",
            "security_review": None,
        }

        # Run the workflow with timeout
        result = await asyncio.wait_for(run_workflow(initial_state), timeout=60.0)

        return ChatResponse(
            message=result.get("response", "I processed your request."),
            updated_graph=result.get("graph_json"),
            generated_files=result.get("generated_files"),
        )

    except asyncio.TimeoutError:
        logger.error("Workflow timeout after 60 seconds")
        raise HTTPException(
            status_code=504, detail="Request timeout - operation took too long"
        )
    except Exception:
        logger.exception("Chat endpoint error")
        raise HTTPException(status_code=500, detail="An internal error occurred")


@app.get("/api/graph")
async def get_sample_graph():
    """Return a sample graph for testing."""
    return {
        "nodes": [
            {
                "id": "db-1",
                "type": "database",
                "position": {"x": 250, "y": 100},
                "data": {"label": "PostgreSQL", "type": "database"},
            },
            {
                "id": "auth-1",
                "type": "auth",
                "position": {"x": 100, "y": 250},
                "data": {"label": "Cognito Auth", "type": "auth"},
            },
            {
                "id": "api-1",
                "type": "api",
                "position": {"x": 400, "y": 250},
                "data": {"label": "REST API", "type": "api"},
            },
        ],
        "edges": [
            {"id": "e1", "source": "auth-1", "target": "api-1"},
            {"id": "e2", "source": "api-1", "target": "db-1"},
        ],
    }


@app.post("/api/deploy", response_model=DeployResponse)
@limiter.limit("3/hour")
async def deploy_stack(http_request: Request, request: DeployRequest):
    """
    Deploy a CDK stack to AWS.

    This endpoint:
    1. Creates a temporary CDK project
    2. Installs dependencies
    3. Bootstraps CDK (if needed)
    4. Deploys the stack
    5. Returns deployment status and outputs
    """
    try:
        result = deployment_service.deploy(
            stack_name=request.stack_name,
            cdk_code=request.cdk_code,
            app_code=request.app_code,
            region=request.region,
            profile=request.profile,
            require_approval=request.require_approval,
        )

        return DeployResponse(**result)

    except Exception as e:
        return DeployResponse(success=False, error=f"Deployment error: {str(e)}")


@app.get("/api/deploy/status")
async def deployment_status():
    """Check if CDK CLI is available."""
    return {
        "cdk_available": deployment_service.cdk_version is not None,
        "cdk_version": deployment_service.cdk_version,
    }


@app.post("/api/cost/estimate")
@limiter.limit("20/minute")
async def estimate_cost(request: Request, body: GraphRequest):
    """
    Estimate monthly AWS costs for an architecture.

    Returns cost breakdown by service and optimization tips.
    """
    import logging

    logger = logging.getLogger(__name__)

    try:
        estimate = cost_estimator.estimate(body.graph)
        tips = cost_estimator.get_optimization_tips(body.graph)

        return {**estimate, "optimization_tips": tips}
    except Exception:
        logger.exception("Cost estimation error")
        raise HTTPException(status_code=500, detail="Cost estimation failed")


@app.post("/api/security/autofix")
@limiter.limit("10/minute")
async def security_autofix_endpoint(request: Request, body: GraphRequest):
    """
    Automatically fix security issues in architecture.

    Returns updated graph with security improvements applied.
    """
    import logging

    logger = logging.getLogger(__name__)

    try:
        updated_graph, changes = security_autofix.analyze_and_fix(body.graph)
        score = security_autofix.get_security_score(updated_graph)

        return {
            "updated_graph": updated_graph,
            "changes": changes,
            "security_score": score,
        }
    except Exception:
        logger.exception("Security autofix error")
        raise HTTPException(status_code=500, detail="Security autofix failed")


@app.get("/api/templates")
@limiter.limit("30/minute")
async def list_templates(request: Request):
    """List all available architecture templates."""
    return templates.list_templates()


@app.get("/api/templates/{template_id}")
@limiter.limit("30/minute")
async def get_template(request: Request, template_id: str):
    """Get a specific architecture template."""
    try:
        return templates.get_template(template_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.post("/api/share")
@limiter.limit("10/minute")
async def create_share(request: Request, body: ShareRequest):
    """Create a shareable link for an architecture."""
    share_id = sharing_service.create_share_link(body.graph, body.title)
    return {"share_id": share_id, "url": f"/shared/{share_id}"}


@app.get("/api/share/{share_id}")
@limiter.limit("30/minute")
async def get_shared(request: Request, share_id: str):
    """Get a shared architecture by ID."""
    architecture = sharing_service.get_shared_architecture(share_id)

    if not architecture:
        raise HTTPException(status_code=404, detail="Shared architecture not found")

    return architecture


@app.post("/api/security/history")
@limiter.limit("20/minute")
async def record_security_score(request: Request, body: SecurityHistoryRequest):
    """Record a security score for history tracking."""
    security_history.record_score(body.architecture_id, body.score, body.issues)
    return {"status": "recorded"}


@app.get("/api/security/history/{architecture_id}")
@limiter.limit("30/minute")
async def get_security_history(request: Request, architecture_id: str):
    """Get security score history for an architecture."""
    history = security_history.get_history(architecture_id)
    improvement = security_history.get_improvement(architecture_id)

    return {"history": history, "improvement": improvement}
