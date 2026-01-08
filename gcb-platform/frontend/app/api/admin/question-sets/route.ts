import { proxyToBackend } from "@/lib/backend-auth";

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  return proxyToBackend("/api/admin/question-sets", {
    queryString: searchParams.toString(),
  });
}
