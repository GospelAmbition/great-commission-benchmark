import NextAuth from "next-auth"
import Google from "next-auth/providers/google"

export const { handlers, auth, signIn, signOut } = NextAuth({
  providers: [
    Google({
      clientId: process.env.GOOGLE_CLIENT_ID!,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
    }),
  ],
  callbacks: {
    async jwt({ token, account, profile }) {
      // Store the Google provider account ID in the token
      if (account) {
        token.sub = account.providerAccountId
        token.email = profile?.email || (typeof account.email === 'string' ? account.email : undefined)
        token.name = profile?.name || (typeof account.name === 'string' ? account.name : undefined)
      }
      return token
    },
    async session({ session, token }) {
      // Add the provider account ID to the session
      if (session.user) {
        session.user.id = token.sub as string
        session.user.email = token.email as string
        session.user.name = token.name as string
      }
      // Include the JWT token in the session for API calls
      // @ts-ignore - NextAuth types don't include accessToken by default
      session.accessToken = token
      return session
    },
  },
  session: {
    strategy: "jwt",
  },
  secret: process.env.NEXTAUTH_SECRET,
})
