/** Signed newsletter action URLs must not initialize analytics or support widgets. */
export function isNewsletterActionPath(pathname: string | null) {
  const path = pathname?.replace(/\/$/, "");
  return path === "/newsletter/confirm" || path === "/newsletter/unsubscribe";
}

/** Retain the action token in component state, not the displayed URL/history. */
export function readNewsletterActionToken() {
  const url = new URL(window.location.href);
  const token = url.searchParams.get("token");
  if (token) {
    url.searchParams.delete("token");
    window.history.replaceState(window.history.state, "", url.pathname + url.search + url.hash);
  }
  return token;
}
