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

export async function GET() {
  const token = await getBackendToken();
  if (!token) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  try {
    // Get question sets from backend
    const response = await fetch(`${API_URL}/api/admin/question-sets`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: "Request failed" }));
      return NextResponse.json(error, { status: response.status });
    }

    const data = await response.json();
    
    // Fetch stats for each question set to get actual counts
    const versions = await Promise.all(
      (data.items || []).map(async (qs: {
        id: string;
        semantic_version: string;
        marketing_version: string;
        status: string;
        created_at: string;
      }) => {
        // Fetch stats for this question set
        let questionCount = 0;
        let tier1Count = 0;
        let tier2Count = 0;
        let tier3Count = 0;

        try {
          const statsResponse = await fetch(
            `${API_URL}/api/admin/question-sets/${qs.id}/stats`,
            {
              headers: {
                Authorization: `Bearer ${token}`,
              },
            }
          );

          if (statsResponse.ok) {
            const stats = await statsResponse.json();
            questionCount = stats.total_questions || 0;
            tier1Count = stats.tier_stats?.[1]?.count || 0;
            tier2Count = stats.tier_stats?.[2]?.count || 0;
            tier3Count = stats.tier_stats?.[3]?.count || 0;
          }
        } catch (statsError) {
          console.error(`Failed to fetch stats for ${qs.id}:`, statsError);
        }

        return {
          version: qs.semantic_version,
          status: qs.status === "active" ? "published" : qs.status,
          question_count: questionCount,
          tier1_count: tier1Count,
          tier2_count: tier2Count,
          tier3_count: tier3Count,
          created_at: qs.created_at,
          is_current: qs.status === "active",
        };
      })
    );

    return NextResponse.json({ versions });
  } catch (error) {
    console.error("Failed to fetch versions:", error);
    return NextResponse.json(
      { error: "Failed to fetch versions" },
      { status: 500 }
    );
  }
}

export async function POST(request: Request) {
  const token = await getBackendToken();
  if (!token) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  try {
    const body = await request.json();
    
    const response = await fetch(`${API_URL}/api/admin/question-sets`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        semantic_version: body.version || "1.0",
        marketing_version: body.marketing_version || `Version ${body.version || "1.0"}`,
        notes: body.notes,
      }),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: "Request failed" }));
      return NextResponse.json(error, { status: response.status });
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error("Failed to create version:", error);
    return NextResponse.json(
      { error: "Failed to create version" },
      { status: 500 }
    );
  }
}
