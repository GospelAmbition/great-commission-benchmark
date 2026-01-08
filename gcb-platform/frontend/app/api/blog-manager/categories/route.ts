import { proxyToBackend } from "@/lib/backend-auth";

export async function GET() {
  return proxyToBackend("/api/admin/blog/categories");
}

export async function POST(request: Request) {
  const body = await request.json();
  return proxyToBackend("/api/admin/blog/categories", {
    method: "POST",
    body,
  });
}
