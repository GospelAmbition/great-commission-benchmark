import { auth } from "@/auth";
import { NextResponse } from "next/server";
import * as jose from "jose";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function getBackendToken() {
  const session = await auth();
  if (!session) return null;

  const secret = new TextEncoder().encode(process.env.NEXTAUTH_SECRET!);
  const token = await new jose.SignJWT({
    sub: session.user?.id,
    email: session.user?.email,
    name: session.user?.name,
  })
    .setProtectedHeader({ alg: "HS256" })
    .setIssuedAt()
    .setExpirationTime("1h")
    .sign(secret);

  return token;
}

async function getQuestionSetId(token: string, version: string): Promise<string | null> {
  const response = await fetch(`${API_URL}/api/admin/question-sets`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  
  if (!response.ok) return null;
  
  const data = await response.json();
  const qs = data.items?.find(
    (item: { semantic_version: string }) => item.semantic_version === version
  );
  return qs?.id || null;
}

export async function POST(
  request: Request,
  { params }: { params: Promise<{ version: string }> }
) {
  const token = await getBackendToken();
  if (!token) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  const { version } = await params;

  try {
    // Get question set ID from version string
    const questionSetId = await getQuestionSetId(token, version);
    if (!questionSetId) {
      return NextResponse.json({ error: "Version not found" }, { status: 404 });
    }

    // Unlock the question set
    const response = await fetch(
      `${API_URL}/api/admin/question-sets/${questionSetId}/unlock`,
      {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      }
    );

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: "Request failed" }));
      return NextResponse.json(error, { status: response.status });
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error("Failed to unlock version:", error);
    return NextResponse.json(
      { error: "Failed to unlock version" },
      { status: 500 }
    );
  }
}
