import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL = process.env.BACKEND_URL || "http://localhost:8000";

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { message, graph } = body;

    // Forward request to FastAPI backend
    const response = await fetch(`${BACKEND_URL}/api/chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        user_input: message,
        graph_json: graph,
      }),
    });

    if (!response.ok) {
      // If backend is not available, return a helpful message
      if (response.status === 502 || response.status === 503) {
        return NextResponse.json({
          message:
            "Backend service is not available. Please ensure the FastAPI server is running on port 8000.",
        });
      }
      throw new Error(`Backend error: ${response.status}`);
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error("Chat API error:", error);

    // Return a friendly message if backend is unreachable
    if (error instanceof TypeError && error.message.includes("fetch")) {
      return NextResponse.json({
        message:
          "Cannot connect to the backend. Please start the FastAPI server with: cd apps/backend && uv run uvicorn scaffold_ai.main:app --reload",
      });
    }

    return NextResponse.json(
      { error: "Failed to process request" },
      { status: 500 }
    );
  }
}
