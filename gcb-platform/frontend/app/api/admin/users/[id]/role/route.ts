import { proxyToBackend } from "@/lib/backend-auth";

export async function PUT(
  request: Request,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id } = await params;
  const body = await request.json();
  
  return proxyToBackend(`/api/admin/users/${id}/role`, {
    method: "PUT",
    body,
  });
}
