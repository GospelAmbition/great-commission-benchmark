import Link from "next/link";

export function Footer() {
  return (
    <footer className="border-t bg-muted/50" role="contentinfo" aria-label="Site footer">
      <div className="container py-12 md:py-16">
        <div className="grid grid-cols-2 gap-8 md:grid-cols-4">
          <div>
            <h3 className="mb-4 text-sm font-semibold">Platform</h3>
            <ul className="space-y-2 text-sm">
              <li>
                <Link href="/" className="text-muted-foreground hover:text-foreground">
                  Home
                </Link>
              </li>
              <li>
                <Link href="/research" className="text-muted-foreground hover:text-foreground">
                  Research
                </Link>
              </li>
              <li>
                <Link href="/about" className="text-muted-foreground hover:text-foreground">
                  Methodology
                </Link>
              </li>
            </ul>
          </div>
          <div>
            <h3 className="mb-4 text-sm font-semibold">Community</h3>
            <ul className="space-y-2 text-sm">
              <li>
                <Link href="/contribute" className="text-muted-foreground hover:text-foreground">
                  Contribute
                </Link>
              </li>
              <li>
                <a
                  href="https://github.com"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-muted-foreground hover:text-foreground"
                >
                  GitHub
                </a>
              </li>
              <li>
                <a
                  href="https://discord.com"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-muted-foreground hover:text-foreground"
                >
                  Discord
                </a>
              </li>
            </ul>
          </div>
          <div>
            <h3 className="mb-4 text-sm font-semibold">Legal</h3>
            <ul className="space-y-2 text-sm">
              <li>
                <Link href="/terms" className="text-muted-foreground hover:text-foreground">
                  Terms of Service
                </Link>
              </li>
              <li>
                <Link href="/privacy" className="text-muted-foreground hover:text-foreground">
                  Privacy Policy
                </Link>
              </li>
              <li>
                <Link href="/tester-agreement" className="text-muted-foreground hover:text-foreground">
                  Tester Agreement
                </Link>
              </li>
            </ul>
          </div>
          <div>
            <h3 className="mb-4 text-sm font-semibold">Connect</h3>
            <ul className="space-y-2 text-sm">
              <li>
                <a
                  href="mailto:contact@example.com"
                  className="text-muted-foreground hover:text-foreground"
                >
                  Contact
                </a>
              </li>
              <li>
                <Link href="/api/docs" className="text-muted-foreground hover:text-foreground">
                  API Documentation
                </Link>
              </li>
            </ul>
          </div>
        </div>
        <div className="mt-12 border-t pt-8 space-y-4">
          <div className="text-center text-xs text-muted-foreground">
            <p>
              <strong>Disclaimer:</strong> This benchmark is for informational purposes only and does 
              not constitute an endorsement or recommendation of any AI model or service.
            </p>
          </div>
          <div className="text-center text-sm text-muted-foreground">
            <p>© {new Date().getFullYear()} Great Commission Benchmark. All rights reserved.</p>
          </div>
        </div>
      </div>
    </footer>
  );
}
