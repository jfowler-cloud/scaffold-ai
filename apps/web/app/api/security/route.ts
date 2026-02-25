import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL = process.env.BACKEND_URL || "http://localhost:8001";

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();

    const response = await fetch(`${BACKEND_URL}/api/security/autofix`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      if (response.status === 502 || response.status === 503) {
        return NextResponse.json(
          { error: "Backend service unavailable" },
          { status: 503 }
        );
      }
      throw new Error(`Backend error: ${response.status}`);
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error("Security autofix proxy error:", error);
    return NextResponse.json(
      { error: "Failed to process security request" },
      { status: 500 }
    );
  }
}
