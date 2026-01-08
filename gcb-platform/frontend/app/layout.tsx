import type { Metadata } from "next";
import { SessionProvider } from "@/components/providers/SessionProvider";
import { Toaster } from "@/components/ui/sonner";
import { Header } from "@/components/layout/Header";
import { Footer } from "@/components/layout/Footer";
import { UmamiAnalytics } from "@/components/analytics/UmamiAnalytics";
import "./globals.css";

export const metadata: Metadata = {
  title: "Great Commission Benchmark",
  description: "Evaluating LLMs on their ability to support Great Commission Christians",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@100;200;300;400;500;600&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="antialiased font-sans bg-background text-foreground">
        <SessionProvider>
          {/* Skip to main content link for accessibility */}
          <a
            href="#main-content"
            className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 focus:z-[100] focus:px-4 focus:py-2 focus:bg-red-700 focus:text-white focus:rounded-md focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-700"
          >
            Skip to main content
          </a>
          <div className="flex min-h-screen flex-col">
            <Header />
            <main id="main-content" className="flex-1" role="main" tabIndex={-1}>
              {children}
            </main>
            <Footer />
          </div>
          <Toaster />
          <UmamiAnalytics />
        </SessionProvider>
      </body>
    </html>
  );
}
