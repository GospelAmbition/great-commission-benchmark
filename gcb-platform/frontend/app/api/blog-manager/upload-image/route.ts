import { proxyFormDataToBackend } from "@/lib/backend-auth";

export async function POST(request: Request) {
  const formData = await request.formData();
  return proxyFormDataToBackend("/api/admin/blog/upload-image", formData, request);
}
