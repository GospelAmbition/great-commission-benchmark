import { cache } from "react";
import { notFound } from "next/navigation";
import { API_URL, type ModelResponse } from "@/lib/api";

export type ModelParams = { params: Promise<{ id: string[] }> };

export const getModel = cache(async (id: string): Promise<ModelResponse> => {
  // Catch-all params may preserve encoded slashes from existing internal links.
  let modelId = id;
  try {
    modelId = decodeURIComponent(id);
  } catch {
    notFound();
  }
  const query = new URLSearchParams({ model_id: modelId });
  const response = await fetch(`${API_URL}/api/public/models/by-id?${query}`, {
    cache: "no-store",
  });
  if (response.status === 404) notFound();
  if (!response.ok) throw new Error("Unable to load model details");
  return response.json();
});
