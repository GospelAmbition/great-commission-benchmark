import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Unsubscribe | Great Commission Benchmark",
  robots: { index: false, follow: false },
  referrer: "no-referrer",
};

export default function UnsubscribeLayout({ children }: { children: React.ReactNode }) {
  return children;
}
