"""FastAPI application for Scaffold AI backend."""

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .graph.workflow import run_workflow
from .graph.state import GraphState, Intent

app = FastAPI(
    title="Scaffold AI Backend",
    description="LangGraph-powered backend for the Scaffold AI platform",
    version="0.1.0",
)

# CORS configuration for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
