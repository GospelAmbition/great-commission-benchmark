import { proxyToBackend } from "@/lib/backend-auth";

export async function GET(
  request: Request,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id } = await params;
  return proxyToBackend(`/api/admin/question-sets/${id}/stats`);
}
