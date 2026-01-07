import { auth } from "@/auth";
import { NextRequest, NextResponse } from "next/server";
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

export async function POST(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  const token = await getBackendToken();
  if (!token) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  try {
    const { id } = await params;
    
    const response = await fetch(`${API_URL}/api/admin/blog/posts/${id}/unpublish`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: "Request failed" }));
      return NextResponse.json(error, { status: response.status });
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error("Failed to unpublish blog post:", error);
    return NextResponse.json(
      { error: "Failed to unpublish blog post" },
      { status: 500 }
    );
  }
}

