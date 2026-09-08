/** Recover full descriptions when OpenRouter's API supplies an ellipsized summary. */
export async function getFullModelDescription(modelId: string, description?: string): Promise<string | undefined> {
  if (!description || !/(?:\.{3}|…)\s*$/.test(description)) return description;

  const parts = modelId.split("/");
  if (parts.length !== 2 || parts.some(part => !part || part === "." || part === "..")) return description;
  const url = `https://openrouter.ai/${parts.map(encodeURIComponent).join("/")}`;
  const prefix = description.replace(/(?:\.{3}|…)\s*$/, "").trimEnd();

  try {
    // Public metadata only: no API key. Cache across requests and bound page latency.
    const response = await fetch(url, {
      next: { revalidate: 86400 },
      signal: AbortSignal.timeout(5000),
    });
    if (!response.ok) return description;
    const html = await response.text();
    const scripts = html.matchAll(/<script\b[^>]*\btype\s*=\s*["']application\/ld\+json["'][^>]*>([\s\S]*?)<\/script\s*>/gi);
    for (const script of scripts) {
      let data: unknown;
      try { data = JSON.parse(script[1]); } catch { continue; }
      const nodes: unknown[] = Array.isArray(data) ? [...data] : [data];
      while (nodes.length) {
        const value = nodes.shift();
        if (!value || typeof value !== "object") continue;
        const node = value as Record<string, unknown>;
        if (Array.isArray(node["@graph"])) nodes.push(...node["@graph"]);
        const types = Array.isArray(node["@type"]) ? node["@type"] : [node["@type"]];
        if (!types.includes("SoftwareApplication") || typeof node.url !== "string" || typeof node.description !== "string") continue;
        const canonical = new URL(node.url);
        if (canonical.origin !== "https://openrouter.ai" || decodeURIComponent(canonical.pathname).replace(/\/$/, "") !== `/${modelId}`) continue;
        const full = node.description.trim();
        // Only replace the supplied summary with its complete continuation.
        if (full.startsWith(prefix) && full.length > description.length && !/(?:\.{3}|…)\s*$/.test(full)) return full;
      }
    }
  } catch {
    // A missing page, changed markup, or timeout must not break benchmark results.
  }
  return description;
}
