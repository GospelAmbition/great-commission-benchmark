import { apiClient } from "@/lib/api";
import { AboutContent } from "./about-content";
import { toVersionInfo, type VersionInfo } from "./versions";

async function loadVersions(): Promise<VersionInfo[] | null> {
  try {
    const data = await apiClient.getVersions();
    return toVersionInfo(data.versions || []);
  } catch {
    // Fall back to the client fetching versions itself.
    return null;
  }
}

// Render per request so data is never frozen at build time.
export const dynamic = "force-dynamic";

export default async function AboutPage() {
  return <AboutContent initialVersions={await loadVersions()} />;
}
