export const NEWSLETTER_PROMISE = "New model evaluations and insights for Great Commission work. A monthly digest, plus occasional highlights on important model releases.";
export const NEWSLETTER_SOURCES = ["header", "home_hero", "home_results", "model_results", "model_archived", "insights_header", "article_header", "article_end", "leaderboard", "recent_tests", "footer", "newsletter_page"] as const;
export type NewsletterSource = (typeof NEWSLETTER_SOURCES)[number];
export function newsletterSource(value: string | null): NewsletterSource {
  return NEWSLETTER_SOURCES.includes(value as NewsletterSource) ? value as NewsletterSource : "newsletter_page";
}
