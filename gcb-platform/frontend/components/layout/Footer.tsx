import Link from "next/link";

export function Footer() {
  return (
    <footer className="bg-info text-info-foreground" role="contentinfo" aria-label="Site footer">
      {/* Top accent line */}
      <div className="h-1 w-full" style={{ background: 'linear-gradient(135deg, #a11824 0%, #7a1219 100%)' }} />
      
      <div className="container py-10 md:py-12">
        <div className="grid grid-cols-2 gap-6 md:grid-cols-4 md:gap-8">
          <div>
            <h3 className="mb-3 text-sm font-semibold text-info-foreground">Platform</h3>
            <ul className="space-y-2 text-sm">
              <li>
                <Link href="/" className="text-info-muted hover:text-red-400 transition-colors">
                  Home
                </Link>
              </li>
              <li>
                <Link href="/research" className="text-info-muted hover:text-red-400 transition-colors">
                  Research
                </Link>
              </li>
              <li>
                <Link href="/about" className="text-info-muted hover:text-red-400 transition-colors">
                  Methodology
                </Link>
              </li>
            </ul>
          </div>
          <div>
            <h3 className="mb-3 text-sm font-semibold text-info-foreground">Community</h3>
            <ul className="space-y-2 text-sm">
              <li>
                <Link href="/contribute" className="text-info-muted hover:text-red-400 transition-colors">
                  Contribute
                </Link>
              </li>
              <li>
                <Link href="/dashboard/settings" className="text-info-muted hover:text-red-400 transition-colors">
                  Newsletter
                </Link>
              </li>
            </ul>
          </div>
          <div>
            <h3 className="mb-3 text-sm font-semibold text-info-foreground">Legal</h3>
            <ul className="space-y-2 text-sm">
              <li>
                <Link href="/terms" className="text-info-muted hover:text-red-400 transition-colors">
                  Terms of Service
                </Link>
              </li>
              <li>
                <Link href="/privacy" className="text-info-muted hover:text-red-400 transition-colors">
                  Privacy Policy
                </Link>
              </li>
              <li>
                <Link href="/tester-agreement" className="text-info-muted hover:text-red-400 transition-colors">
                  Tester Agreement
                </Link>
              </li>
            </ul>
          </div>
          <div>
            <h3 className="mb-3 text-sm font-semibold text-info-foreground">Connect</h3>
            <ul className="space-y-2 text-sm">
              <li>
                <a
                  href="mailto:contact@example.com"
                  className="text-info-muted hover:text-red-400 transition-colors"
                >
                  Contact
                </a>
              </li>
            </ul>
          </div>
        </div>
        
        <div className="mt-8 pt-6 border-t border-info-border space-y-3">
          <div className="text-center text-xs text-info-muted/70">
            <p>
              <span className="text-red-400">Disclaimer:</span> This benchmark is for informational purposes only and does 
              not constitute an endorsement or recommendation of any AI model or service.
            </p>
          </div>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-2 text-sm text-info-muted">
            <div className="flex items-center gap-2">
              <div className="w-6 h-6 rounded flex items-center justify-center" style={{ background: 'linear-gradient(135deg, #a11824 0%, #7a1219 100%)' }}>
                <span className="text-white font-bold text-xs">GCB</span>
              </div>
              <span className="font-medium text-info-foreground/80">Great Commission Benchmark</span>
            </div>
            <span className="hidden sm:inline text-info-muted/50">•</span>
            <p>© {new Date().getFullYear()} All rights reserved.</p>
          </div>
        </div>
      </div>
    </footer>
  );
}
