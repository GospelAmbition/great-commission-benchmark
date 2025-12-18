// In Auth0 v4, authentication is handled via middleware.
// This route file is kept for backwards compatibility but the actual
// auth handling is done in middleware.ts using auth0.middleware()

export const GET = async () => {
  return new Response("Auth handled via middleware", { status: 200 });
};

export const POST = async () => {
  return new Response("Auth handled via middleware", { status: 200 });
};
