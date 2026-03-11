"""FastAPI application for Scaffold AI backend — Step Functions orchestration."""

import json
import os

import boto3
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, field_validator
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from .services.cdk_deployment import CDKDeploymentService
from .services.cost_estimator import CostEstimator
from .services.security_autofix import SecurityAutoFix
from .services.security_history import SecurityHistoryService
from .services.sharing import SharingService
from .services.templates import ArchitectureTemplates

load_dotenv()

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="Scaffold AI Backend",
    description="Step Functions + Strands backend for Scaffold AI",
    version="2.0.0",
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

_raw_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:3001")
ALLOWED_ORIGINS = [o.strip() for o in _raw_origins.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

# Services (stateless, no LangGraph)
deployment_service = CDKDeploymentService()
cost_estimator = CostEstimator()
security_autofix = SecurityAutoFix()
templates = ArchitectureTemplates()
sharing_service = SharingService()
security_history = SecurityHistoryService()

_sfn = boto3.client("stepfunctions", region_name=os.getenv("AWS_REGION", "us-east-1"))
WORKFLOW_ARN = os.getenv("WORKFLOW_ARN", "")


# ── Request / Response models ──────────────────────────────────────────────────

class ChatRequest(BaseModel):
    user_input: str
    graph_json: dict | None = None
    iac_format: str = "cdk"

    @field_validator("user_input")
    @classmethod
    def validate_user_input(cls, v: str) -> str:
        if len(v) > 5000:
            raise ValueError("user_input must be 5000 characters or less")
        if not v.strip():
            raise ValueError("user_input cannot be empty")
        return v

    @field_validator("iac_format")
    @classmethod
    def validate_iac_format(cls, v: str) -> str:
        allowed = ["cdk", "cloudformation", "terraform", "python-cdk"]
        if v not in allowed:
            raise ValueError(f"iac_format must be one of: {', '.join(allowed)}")
        return v

    @field_validator("graph_json")
    @classmethod
    def validate_graph_json(cls, v: dict | None) -> dict | None:
        if v and len(v.get("nodes", [])) > 50:
            raise ValueError("graph_json cannot have more than 50 nodes")
        return v


class ChatStartResponse(BaseModel):
    execution_arn: str


class ExecutionStatusResponse(BaseModel):
    status: str  # RUNNING | SUCCEEDED | FAILED | TIMED_OUT | ABORTED
    message: str | None = None
    updated_graph: dict | None = None
    generated_files: list[dict] | None = None
    error: str | None = None


class DeployRequest(BaseModel):
    stack_name: str
    cdk_code: str
    app_code: str
    region: str = "us-east-1"
    profile: str | None = None
    require_approval: bool = True

    @field_validator("stack_name")
    @classmethod
    def validate_stack_name(cls, v: str) -> str:
        import re
        if not re.match(r"^[A-Za-z][A-Za-z0-9-]{0,127}$", v):
            raise ValueError("stack_name must be alphanumeric with hyphens, start with letter, 1-128 chars")
        return v


class GraphRequest(BaseModel):
    graph: dict

    @field_validator("graph")
    @classmethod
    def validate_graph(cls, v: dict) -> dict:
        if len(v.get("nodes", [])) > 50:
            raise ValueError("Graph cannot have more than 50 nodes")
        return v


class ShareRequest(BaseModel):
    graph: dict
    title: str = "Shared Architecture"


class SecurityHistoryRequest(BaseModel):
    architecture_id: str
    score: int
    issues: list[dict] = []


class PlanImportRequest(BaseModel):
    plan_id: str
    project_name: str
    description: str
    architecture: str
    tech_stack: dict[str, str]
    requirements: dict[str, str]
    review_findings: list[dict] | None = None
    review_summary: str | None = None
    full_plan: dict | None = None


class DeployResponse(BaseModel):
    success: bool
    message: str | None = None
    error: str | None = None
    outputs: dict | None = None


# ── Endpoints ──────────────────────────────────────────────────────────────────

@app.get("/")
async def root() -> dict:
    return {"status": "ok", "service": "scaffold-ai-backend", "version": "2.0.0"}


@app.get("/health")
async def health() -> dict:
    status = {"status": "healthy", "services": {}}
    try:
        import boto3 as _b
        _b.client("bedrock-runtime", region_name=os.getenv("AWS_REGION", "us-east-1"))
        status["services"]["bedrock"] = "available"
    except Exception:
        status["services"]["bedrock"] = "unavailable"
        status["status"] = "degraded"

    status["services"]["step_functions"] = "configured" if WORKFLOW_ARN else "not_configured"
    return status


@app.post("/api/chat", response_model=ChatStartResponse)
@limiter.limit("10/minute")
async def chat(request: Request, body: ChatRequest):
    """
    Start a chat workflow execution via Step Functions.
    Returns execution_arn immediately — poll /api/chat/{arn}/status for result.
    """
    if not WORKFLOW_ARN:
        raise HTTPException(status_code=503, detail="Workflow not configured (WORKFLOW_ARN missing)")

    payload = {
        "user_input": body.user_input.replace("skip_security_check", "").strip(),
        "graph_json": body.graph_json or {"nodes": [], "edges": []},
        "iac_format": body.iac_format,
        "skip_security": "skip_security_check" in body.user_input,
        "generated_files": [],
        "response": "",
        "security_review": None,
    }

    try:
        resp = _sfn.start_execution(
            stateMachineArn=WORKFLOW_ARN,
            input=json.dumps(payload),
        )
        return ChatStartResponse(execution_arn=resp["executionArn"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start workflow: {e}")


@app.get("/api/chat/{execution_arn:path}/status", response_model=ExecutionStatusResponse)
@limiter.limit("60/minute")
async def chat_status(request: Request, execution_arn: str):
    """Poll Step Functions execution status."""
    try:
        resp = _sfn.describe_execution(executionArn=execution_arn)
        status = resp["status"]

        if status == "SUCCEEDED":
            output = json.loads(resp.get("output", "{}"))
            return ExecutionStatusResponse(
                status=status,
                message=output.get("response", ""),
                updated_graph=output.get("graph_json"),
                generated_files=output.get("generated_files", []),
            )
        elif status in ("FAILED", "TIMED_OUT", "ABORTED"):
            return ExecutionStatusResponse(status=status, error=resp.get("cause", "Execution failed"))
        else:
            return ExecutionStatusResponse(status=status)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/graph")
async def get_sample_graph():
    return {
        "nodes": [
            {"id": "db-1", "type": "database", "position": {"x": 250, "y": 100}, "data": {"label": "DynamoDB", "type": "database"}},
            {"id": "auth-1", "type": "auth", "position": {"x": 100, "y": 250}, "data": {"label": "Cognito Auth", "type": "auth"}},
            {"id": "api-1", "type": "api", "position": {"x": 400, "y": 250}, "data": {"label": "REST API", "type": "api"}},
        ],
        "edges": [
            {"id": "e1", "source": "auth-1", "target": "api-1"},
            {"id": "e2", "source": "api-1", "target": "db-1"},
        ],
    }


@app.post("/api/deploy", response_model=DeployResponse)
@limiter.limit("3/hour")
async def deploy_stack(http_request: Request, request: DeployRequest):
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
    return {"cdk_available": deployment_service.cdk_version is not None, "cdk_version": deployment_service.cdk_version}


@app.post("/api/cost/estimate")
@limiter.limit("20/minute")
async def estimate_cost(request: Request, body: GraphRequest):
    try:
        estimate = cost_estimator.estimate(body.graph)
        tips = cost_estimator.get_optimization_tips(body.graph)
        return {**estimate, "optimization_tips": tips}
    except Exception:
        raise HTTPException(status_code=500, detail="Cost estimation failed")


@app.post("/api/security/autofix")
@limiter.limit("10/minute")
async def security_autofix_endpoint(request: Request, body: GraphRequest):
    try:
        updated_graph, changes = security_autofix.analyze_and_fix(body.graph)
        score = security_autofix.get_security_score(updated_graph)
        return {"updated_graph": updated_graph, "changes": changes, "security_score": score}
    except Exception:
        raise HTTPException(status_code=500, detail="Security autofix failed")


@app.get("/api/templates")
@limiter.limit("30/minute")
async def list_templates(request: Request):
    return templates.list_templates()


@app.get("/api/templates/{template_id}")
@limiter.limit("30/minute")
async def get_template(request: Request, template_id: str):
    try:
        return templates.get_template(template_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.post("/api/share")
@limiter.limit("10/minute")
async def create_share(request: Request, body: ShareRequest):
    share_id = sharing_service.create_share_link(body.graph, body.title)
    return {"share_id": share_id, "url": f"/shared/{share_id}"}


@app.get("/api/share/{share_id}")
@limiter.limit("30/minute")
async def get_shared(request: Request, share_id: str):
    architecture = sharing_service.get_shared_architecture(share_id)
    if not architecture:
        raise HTTPException(status_code=404, detail="Shared architecture not found")
    return architecture


@app.post("/api/security/history")
@limiter.limit("20/minute")
async def record_security_score(request: Request, body: SecurityHistoryRequest):
    security_history.record_score(body.architecture_id, body.score, body.issues)
    return {"status": "recorded"}


@app.get("/api/security/history/{architecture_id}")
@limiter.limit("30/minute")
async def get_security_history(request: Request, architecture_id: str):
    history = security_history.get_history(architecture_id)
    improvement = security_history.get_improvement(architecture_id)
    return {"history": history, "improvement": improvement}


_SESSIONS_TABLE = os.getenv("SESSIONS_TABLE", "scaffold-ai-sessions")
_dynamodb = boto3.resource("dynamodb", region_name=os.getenv("AWS_REGION", "us-east-1"))


@app.post("/api/import/plan")
@limiter.limit("20/minute")
async def import_plan(request: Request, body: PlanImportRequest):
    import uuid
    from datetime import datetime, timezone
    from decimal import Decimal

    session_id = str(uuid.uuid4())
    ttl = int(datetime.now(timezone.utc).timestamp()) + 86400  # 24h expiry

    item: dict = {
        "sessionId": session_id,
        "plan_id": body.plan_id,
        "project_name": body.project_name,
        "description": body.description,
        "architecture": body.architecture,
        "tech_stack": body.tech_stack,
        "requirements": body.requirements,
        "imported_at": datetime.now(timezone.utc).isoformat(),
        "ttl": ttl,
    }
    if body.review_findings:
        item["review_findings"] = body.review_findings
    if body.review_summary:
        item["review_summary"] = body.review_summary
    if body.full_plan:
        item["full_plan"] = body.full_plan

    try:
        table = _dynamodb.Table(_SESSIONS_TABLE)
        # Convert floats to Decimals for DynamoDB
        item = json.loads(json.dumps(item), parse_float=Decimal)
        table.put_item(Item=item)
    except Exception:
        # Fallback to in-memory if DynamoDB unavailable (local dev)
        if not hasattr(app.state, "_imported_plans"):
            app.state._imported_plans = {}
        app.state._imported_plans[session_id] = item

    review_context = ""
    if body.review_findings:
        crit_high = [f for f in body.review_findings if f.get("risk_level") in ("critical", "high")]
        if crit_high:
            review_context = f"\n\n⚠️ {len(crit_high)} critical/high findings from security reviews — please address these in the architecture."
    if body.review_summary:
        review_context += f"\n\nReview Summary:\n{body.review_summary[:2000]}"

    prompt = (
        f"I have a project plan from Project Planner AI:\n\n"
        f"Project: {body.project_name}\nArchitecture: {body.architecture}\n"
        f"Tech Stack: {', '.join(f'{k}: {v}' for k, v in body.tech_stack.items())}\n\n"
        f"Please help me build this architecture on AWS.{review_context}"
    )
    return {"session_id": session_id, "message": "Plan imported successfully", "initial_prompt": prompt}


@app.get("/api/import/plan/{session_id}")
@limiter.limit("30/minute")
async def get_imported_plan(request: Request, session_id: str):
    plan = None
    try:
        table = _dynamodb.Table(_SESSIONS_TABLE)
        resp = table.get_item(Key={"sessionId": session_id})
        plan = resp.get("Item")
    except Exception:
        # Fallback to in-memory
        plans = getattr(app.state, "_imported_plans", {})
        plan = plans.get(session_id)

    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found or expired")

    # Remove DynamoDB internal fields from response
    plan.pop("sessionId", None)
    plan.pop("ttl", None)
    return plan
