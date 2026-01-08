/**
 * Catch-all proxy route for public blog API endpoints.
 * 
 * This consolidates multiple duplicate proxy routes into a single dynamic handler.
 * These are PUBLIC endpoints - no authentication required.
 */
import { proxyToBackend } from "@/lib/backend-auth";

type RouteContext = {
  params: Promise<{ path: string[] }>;
};

async function handleRequest(
  request: Request,
  context: RouteContext,
  method: string
) {
  const { path } = await context.params;
  const backendPath = `/api/blog/${path.join("/")}`;
  const { searchParams } = new URL(request.url);

  const options: {
    method?: string;
    body?: unknown;
    queryString?: string;
    allowPublic?: boolean;
  } = {
    // Blog public endpoints don't require authentication
    allowPublic: true,
  };

  if (method !== "GET") {
    options.method = method;
  }

  // For methods that can have a body, try to parse JSON
  if (["POST", "PUT", "PATCH"].includes(method)) {
    try {
      const body = await request.json();
      options.body = body;
    } catch {
      // No JSON body or invalid JSON - that's okay for some endpoints
    }
  }

  // Add query string if present
  const queryString = searchParams.toString();
  if (queryString) {
    options.queryString = queryString;
  }

  return proxyToBackend(backendPath, options);
}

export async function GET(request: Request, context: RouteContext) {
  return handleRequest(request, context, "GET");
}

export async function POST(request: Request, context: RouteContext) {
  return handleRequest(request, context, "POST");
}

export async function PUT(request: Request, context: RouteContext) {
  return handleRequest(request, context, "PUT");
}

export async function PATCH(request: Request, context: RouteContext) {
  return handleRequest(request, context, "PATCH");
}

export async function DELETE(request: Request, context: RouteContext) {
  return handleRequest(request, context, "DELETE");
}
