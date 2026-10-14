import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Confirm newsletter subscription | Great Commission Benchmark",
  robots: { index: false, follow: false },
  referrer: "no-referrer",
};

export default function ConfirmNewsletterLayout({ children }: { children: React.ReactNode }) {
  return children;
}
