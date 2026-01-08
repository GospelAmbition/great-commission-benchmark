import { proxyToBackend } from "@/lib/backend-auth";

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  return proxyToBackend("/api/admin/blog/posts", {
    queryString: searchParams.toString(),
  });
}

export async function POST(request: Request) {
  const body = await request.json();
  return proxyToBackend("/api/admin/blog/posts", {
    method: "POST",
    body,
  });
}
