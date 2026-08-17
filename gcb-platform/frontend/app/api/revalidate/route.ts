/**
 * On-demand ISR revalidation for pages that embed leaderboard data.
 * Called by the backend after a test is published or admin cache refresh.
 *
 * Auth: WARM_SECRET or REVALIDATE_SECRET query param (same secret as /api/warm).
 */
import { revalidatePath } from "next/cache";
import { NextRequest, NextResponse } from "next/server";

const DEFAULT_PATHS = ["/", "/leaderboard", "/categories"];

function isAuthorized(secret: string | null): boolean {
  if (!secret) return false;
  const expected = process.env.WARM_SECRET || process.env.REVALIDATE_SECRET;
  return Boolean(expected && secret === expected);
}

export async function POST(request: NextRequest) {
  const secret = request.nextUrl.searchParams.get("secret");
  if (!isAuthorized(secret)) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  let paths = DEFAULT_PATHS;
  try {
    const body = await request.json();
    if (Array.isArray(body?.paths) && body.paths.every((p: unknown) => typeof p === "string")) {
      paths = body.paths;
    }
  } catch {
    // No JSON body — use defaults.
  }

  for (const path of paths) {
    revalidatePath(path, "layout");
  }

  return NextResponse.json({ revalidated: paths });
}
