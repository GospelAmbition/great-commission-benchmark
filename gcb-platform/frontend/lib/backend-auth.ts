/**
 * Shared utilities for backend authentication in API routes.
 * 
 * This module provides a centralized way to handle backend authentication
 * from Next.js API routes, eliminating code duplication across route handlers.
 */

import { auth } from "@/auth";
import { NextResponse } from "next/server";
import * as jose from "jose";
import { API_URL } from "@/lib/api";

// Remove trailing slashes from API_URL to prevent double-slash URLs
const BACKEND_URL = API_URL.replace(/\/+$/, '');

/**
 * Generate a JWT token for authenticating with the backend API.
 * Uses the NextAuth session to create a signed token.
 * 
 * @param request - The incoming request object (needed to read session cookies)
 * @returns The JWT token string, or null if no session exists
 */
export async function getBackendToken(request?: Request): Promise<string | null> {
  // auth() reads from request context. trustHost: true in auth.ts helps production proxies.
  const session = await auth();

  if (!session) return null;

  const secret = process.env.NEXTAUTH_SECRET;
  if (!secret) {
    console.error("[proxy] NEXTAUTH_SECRET is not set");
    throw new Error("Auth not configured");
  }
  const token = await new jose.SignJWT({
    sub: session.user?.id,
    email: session.user?.email,
    name: session.user?.name,
  })
    .setProtectedHeader({ alg: "HS256" })
    .setIssuedAt()
    .setExpirationTime("1h")
    .sign(new TextEncoder().encode(secret));

  return token;
}

/**
 * Options for backend proxy requests
 */
interface ProxyRequestOptions {
  /** HTTP method (GET, POST, PUT, PATCH, DELETE) */
  method?: string;
  /** Request body for POST/PUT/PATCH requests */
  body?: unknown;
  /** Additional headers to include */
  headers?: Record<string, string>;
  /** Query string from the original request */
  queryString?: string;
  /** If true, allows unauthenticated requests (for public endpoints) */
  allowPublic?: boolean;
}

/**
 * Make a request to the backend API.
 * Handles token generation, error handling, and response formatting.
 * 
 * @param endpoint - The backend API endpoint (e.g., "/api/admin/users")
 * @param options - Request options
 * @returns NextResponse with the backend response or error
 */
export async function proxyToBackend(
  endpoint: string,
  options: ProxyRequestOptions = {},
  request?: Request
): Promise<NextResponse> {
  const { method = "GET", body, headers = {}, queryString, allowPublic = false } = options;

  // Validate config (helps diagnose production 500s)
  if (!BACKEND_URL || BACKEND_URL.includes("localhost")) {
    const msg = process.env.NODE_ENV === "production"
      ? "NEXT_PUBLIC_API_URL must be set to production backend URL"
      : "Backend URL not configured";
    console.error(`[proxy] ${msg}. BACKEND_URL=${BACKEND_URL || "(empty)"}`);
  }

  let token: string | null = null;
  try {
    token = await getBackendToken(request);
  } catch (authError) {
    console.error(`[proxy] Auth error for ${endpoint}:`, authError);
    return NextResponse.json(
      { error: "Authentication error", detail: "Failed to get session" },
      { status: 500 }
    );
  }

  // If authentication is required and no token exists, return 401
  if (!token && !allowPublic) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  const url = queryString
    ? `${BACKEND_URL}${endpoint}?${queryString}`
    : `${BACKEND_URL}${endpoint}`;

  const fetchHeaders: Record<string, string> = {
    "Content-Type": "application/json",
    ...headers,
  };

  if (token) {
    fetchHeaders.Authorization = `Bearer ${token}`;
  }

  const fetchOptions: RequestInit = {
    method,
    headers: fetchHeaders,
  };

  if (body && method !== "GET") {
    fetchOptions.body = JSON.stringify(body);
  }

  try {
    const response = await fetch(url, fetchOptions);

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: "Request failed" }));
      return NextResponse.json(error, { status: response.status });
    }

    const text = await response.text();
    if (!text) {
      return NextResponse.json({ success: true });
    }

    const data = JSON.parse(text);
    return NextResponse.json(data);
  } catch (error) {
    const errMsg = (error as Error)?.message || String(error);
    console.error(`[proxy] Backend request failed for ${endpoint} url=${url}:`, errMsg);
    return NextResponse.json(
      {
        error: "Failed to communicate with backend",
        ...(process.env.NODE_ENV === "development" && { detail: errMsg }),
      },
      { status: 500 }
    );
  }
}

/**
 * Make an authenticated multipart/form-data request to the backend API.
 * Used for file uploads.
 * 
 * @param endpoint - The backend API endpoint
 * @param formData - FormData containing the file(s)
 * @returns NextResponse with the backend response or error
 */
export async function proxyFormDataToBackend(
  endpoint: string,
  formData: FormData,
  request?: Request
): Promise<NextResponse> {
  const token = await getBackendToken(request);
  if (!token) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  try {
    const response = await fetch(`${BACKEND_URL}${endpoint}`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
        // Don't set Content-Type - fetch will set it automatically with boundary for FormData
      },
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: "Upload failed" }));
      return NextResponse.json(error, { status: response.status });
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error(`Backend upload failed for ${endpoint}:`, error);
    return NextResponse.json(
      { error: "Failed to upload to backend" },
      { status: 500 }
    );
  }
}

