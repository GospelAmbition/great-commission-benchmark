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

export async function GET(
  request: Request,
  { params }: { params: Promise<{ version: string }> }
) {
  const token = await getBackendToken();
  if (!token) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  const { version } = await params;

  try {
    // First, get the question set ID from the version
    const versionsResponse = await fetch(`${API_URL}/api/admin/question-sets`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    if (!versionsResponse.ok) {
      return NextResponse.json(
        { error: "Failed to fetch versions" },
        { status: versionsResponse.status }
      );
    }

    const versionsData = await versionsResponse.json();
    const questionSet = versionsData.items?.find(
      (qs: { semantic_version: string }) => qs.semantic_version === version
    );

    if (!questionSet) {
      return NextResponse.json(
        { error: "Version not found" },
        { status: 404 }
      );
    }

    // Now get stats for this question set
    const statsResponse = await fetch(
      `${API_URL}/api/admin/question-sets/${questionSet.id}/stats`,
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );

    if (!statsResponse.ok) {
      const error = await statsResponse.json().catch(() => ({
        detail: "Request failed",
      }));
      return NextResponse.json(error, { status: statsResponse.status });
    }

    const data = await statsResponse.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error("Failed to fetch version stats:", error);
    return NextResponse.json(
      { error: "Failed to fetch version stats" },
      { status: 500 }
    );
  }
}
