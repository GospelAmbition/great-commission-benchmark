import { proxyToBackend } from "@/lib/backend-auth";

export async function DELETE(
  request: Request,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id } = await params;
  return proxyToBackend(`/api/admin/test-runs/${id}`, {
    method: "DELETE",
  });
}
