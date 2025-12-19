import { auth } from "@/auth"
import { NextResponse } from "next/server"
import * as jose from "jose"

export async function GET() {
  const session = await auth()
  
  if (!session) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
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
