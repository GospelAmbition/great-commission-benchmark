import { auth } from "@/auth"
import { NextResponse } from "next/server"
import * as jose from "jose"

export async function GET(request: Request) {
  // In NextAuth v5, auth() automatically reads from request context
  const session = await auth()
  
  if (!session) {
    // Return 200 with null token instead of 401 to avoid console errors
    // The frontend handles null tokens gracefully for public endpoints
    return NextResponse.json({ token: null })
  }

  // Create a JWT token for the backend
  // This token will be verified by the backend using NEXTAUTH_SECRET
  const secret = new TextEncoder().encode(process.env.NEXTAUTH_SECRET!)
  
  const token = await new jose.SignJWT({
    sub: session.user?.id,
    email: session.user?.email,
    name: session.user?.name,
  })
    .setProtectedHeader({ alg: "HS256" })
    .setIssuedAt()
    .setExpirationTime("1h")
    .sign(secret)

  return NextResponse.json({ token })
}
