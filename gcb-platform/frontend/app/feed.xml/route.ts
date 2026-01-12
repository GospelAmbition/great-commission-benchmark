import { SITE_CONFIG, getBaseUrl, getCanonicalUrl } from "@/lib/seo";
import { API_URL } from "@/lib/api";

interface BlogPost {
  id: string;
  title: string;
  slug: string;
  excerpt?: string;
  content?: string;
  featured_image_url?: string;
  status: string;
  author: {
    id: string;
    name?: string;
    email: string;
  };
  categories: Array<{ name: string; slug: string }>;
  created_at: string;
  updated_at: string;
  published_at?: string;
}

// Helper to escape XML special characters
function escapeXml(text: string): string {
  return text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&apos;");
}

// Helper to format date for RSS
function formatRssDate(dateString: string): string {
  const date = new Date(dateString);
  return date.toUTCString();
}

// Helper to strip HTML tags for description
function stripHtml(html: string): string {
  return html.replace(/<[^>]*>/g, "").trim();
}

// Generate RSS feed XML
function generateRssFeed(posts: BlogPost[]): string {
  const baseUrl = getBaseUrl();
  const feedUrl = getCanonicalUrl("/feed.xml");
  const now = new Date().toUTCString();

  const items = posts
    .map((post) => {
      const postUrl = getCanonicalUrl(`/insights/${post.slug}`);
      const pubDate = formatRssDate(post.published_at || post.created_at);
      const description = post.excerpt || (post.content ? stripHtml(post.content).substring(0, 300) + "..." : post.title);
      const categories = post.categories.map((cat) => `<category>${escapeXml(cat.name)}</category>`).join("\n        ");

      return `    <item>
      <title>${escapeXml(post.title)}</title>
      <link>${postUrl}</link>
      <guid isPermaLink="true">${postUrl}</guid>
      <pubDate>${pubDate}</pubDate>
      <description>${escapeXml(description)}</description>
      ${post.author?.name ? `<author>${escapeXml(post.author.email)} (${escapeXml(post.author.name)})</author>` : ""}
      ${categories}
      ${post.featured_image_url ? `<enclosure url="${escapeXml(post.featured_image_url)}" type="image/jpeg" />` : ""}
    </item>`;
    })
    .join("\n");

  return `<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom" xmlns:content="http://purl.org/rss/1.0/modules/content/">
  <channel>
    <title>${escapeXml(SITE_CONFIG.name)} - Insights</title>
    <link>${baseUrl}</link>
    <description>${escapeXml(SITE_CONFIG.description)}</description>
    <language>en-US</language>
    <lastBuildDate>${now}</lastBuildDate>
    <atom:link href="${feedUrl}" rel="self" type="application/rss+xml"/>
    <image>
      <url>${baseUrl}/og-image.png</url>
      <title>${escapeXml(SITE_CONFIG.name)}</title>
      <link>${baseUrl}</link>
    </image>
    <copyright>© ${new Date().getFullYear()} ${escapeXml(SITE_CONFIG.name)}</copyright>
    <managingEditor>${SITE_CONFIG.email} (${escapeXml(SITE_CONFIG.name)})</managingEditor>
    <webMaster>${SITE_CONFIG.email} (${escapeXml(SITE_CONFIG.name)})</webMaster>
    <ttl>60</ttl>
${items}
  </channel>
</rss>`;
}

// Fetch blog posts from API
async function fetchBlogPosts(): Promise<BlogPost[]> {
  try {
    const response = await fetch(`${API_URL}/api/blog/posts?limit=50`, {
      next: { revalidate: 3600 }, // Cache for 1 hour
    });
    
    if (!response.ok) {
      console.error("Failed to fetch blog posts:", response.status);
      return [];
    }
    
    const data = await response.json();
    return data.items || [];
  } catch (error) {
    console.error("Error fetching blog posts:", error);
    return [];
  }
}

export async function GET() {
  const posts = await fetchBlogPosts();
  const feed = generateRssFeed(posts);

  return new Response(feed, {
    headers: {
      "Content-Type": "application/rss+xml; charset=utf-8",
      "Cache-Control": "public, max-age=3600, s-maxage=3600",
    },
  });
}
