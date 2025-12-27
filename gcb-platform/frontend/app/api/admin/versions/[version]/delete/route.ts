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

// DELETE /api/admin/versions/[version]/delete - delete a version
export async function DELETE(
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
    const listResponse = await fetch(`${API_URL}/api/admin/question-sets`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    if (!listResponse.ok) {
      return NextResponse.json(
        { error: "Failed to fetch question sets" },
        { status: listResponse.status }
      );
    }

    const listData = await listResponse.json();
    const questionSet = listData.items?.find(
      (qs: { semantic_version: string }) => qs.semantic_version === version
    );

    if (!questionSet) {
      return NextResponse.json(
        { error: "Version not found" },
        { status: 404 }
      );
    }

    // Now delete the question set
    const response = await fetch(
      `${API_URL}/api/admin/question-sets/${questionSet.id}`,
      {
        method: "DELETE",
        headers: {
          Authorization: `Bearer ${token}`,
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
    console.error("Failed to delete version:", error);
    return NextResponse.json(
      { error: "Failed to delete version" },
      { status: 500 }
    );
  }
}





