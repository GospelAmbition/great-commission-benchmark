import { NextResponse } from "next/server";
import { auth } from "./auth";
import {
  allowPageRequest,
  clientIpFromHeaders,
  isScannerPath,
} from "./lib/crawler-guard";

export default auth((req) => {
  const pathname = req.nextUrl.pathname;
  if (isScannerPath(pathname)) {
    return new NextResponse(null, { status: 404 });
  }
  // Frontend API routes (warm/revalidate) are not visitor page crawls.
  if (pathname.startsWith("/api/")) {
    return;
  }
  const ip = clientIpFromHeaders(req.headers);
  if (!allowPageRequest(ip, req.headers)) {
    return new NextResponse("Too Many Requests", {
      status: 429,
      headers: {
        "Retry-After": "30",
        "Cache-Control": "no-store",
      },
    });
  }
});

export const config = {
  matcher: [
    /*
     * Match all request paths except for:
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico, sitemap.xml, robots.txt (metadata files)
     * - api/auth (NextAuth routes)
     */
    "/((?!_next/static|_next/image|favicon.ico|sitemap.xml|robots.txt|api/auth).*)",
  ],
};
