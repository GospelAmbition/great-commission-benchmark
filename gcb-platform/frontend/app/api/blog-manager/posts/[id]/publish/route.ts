import { proxyToBackend } from "@/lib/backend-auth";

export async function POST(
  request: Request,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id } = await params;
  return proxyToBackend(`/api/admin/blog/posts/${id}/publish`, {
    method: "POST",
  });
}
