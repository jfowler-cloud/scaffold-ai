"""FastAPI application for Scaffold AI backend."""

import os
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .graph.workflow import run_workflow
from .graph.state import GraphState, Intent
from .services.cdk_deployment import CDKDeploymentService
from .services.cost_estimator import CostEstimator

app = FastAPI(
    title="Scaffold AI Backend",
    description="LangGraph-powered backend for the Scaffold AI platform",
    version="0.1.0",
)

# CORS — configurable via ALLOWED_ORIGINS env var (comma-separated).
# Defaults to localhost:3000 for local development.
_raw_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000")
ALLOWED_ORIGINS = [o.strip() for o in _raw_origins.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize deployment service
deployment_service = CDKDeploymentService()
cost_estimator = CostEstimator()


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""

    user_input: str
    graph_json: dict | None = None
    iac_format: str = "cdk"  # cdk, cloudformation, or terraform


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


class DeployResponse(BaseModel):
    """Response model for deployment endpoint."""

    success: bool
    message: str | None = None
    error: str | None = None
    outputs: dict | None = None


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "ok", "service": "scaffold-ai-backend"}


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Process a chat message through the LangGraph workflow.

    This endpoint:
    1. Interprets the user's intent
    2. Routes to appropriate agents (architect, CDK specialist, React specialist)
    3. Returns the response and any graph/file updates
    """
    try:
        # Initialize state
        initial_state: GraphState = {
            "user_input": request.user_input,
            "intent": "new_feature",  # Will be determined by interpreter
            "graph_json": request.graph_json or {"nodes": [], "edges": []},
            "iac_format": request.iac_format,
            "generated_files": [],
            "errors": [],
            "retry_count": 0,
            "response": "",
        }

        # Run the workflow
        result = await run_workflow(initial_state)

        return ChatResponse(
            message=result.get("response", "I processed your request."),
            updated_graph=result.get("graph_json"),
            generated_files=result.get("generated_files"),
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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
async def deploy_stack(request: DeployRequest):
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
            profile=request.profile
        )
        
        return DeployResponse(**result)
    
    except Exception as e:
        return DeployResponse(
            success=False,
            error=f"Deployment error: {str(e)}"
        )


@app.get("/api/deploy/status")
async def deployment_status():
    """Check if CDK CLI is available."""
    return {
        "cdk_available": deployment_service.cdk_version is not None,
        "cdk_version": deployment_service.cdk_version
    }


@app.post("/api/cost/estimate")
async def estimate_cost(graph: dict):
    """
    Estimate monthly AWS costs for an architecture.
    
    Returns cost breakdown by service and optimization tips.
    """
    try:
        estimate = cost_estimator.estimate(graph)
        tips = cost_estimator.get_optimization_tips(graph)
        
        return {
            **estimate,
            "optimization_tips": tips
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

