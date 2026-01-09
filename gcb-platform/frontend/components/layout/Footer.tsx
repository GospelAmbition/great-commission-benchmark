import Link from "next/link";

export function Footer() {
  return (
    <footer className="relative bg-surface border-t border-white/[0.06] overflow-hidden" role="contentinfo" aria-label="Site footer">
      <div className="absolute inset-0 bg-gradient-to-b from-[#09090b] via-[#220a0a] to-[#09090b] opacity-80" />
      <div className="relative container py-10 md:py-12">
        <div className="grid grid-cols-2 gap-6 md:grid-cols-4 md:gap-8">
          <div>
            <h3 className="mb-3 text-sm font-semibold text-foreground">Platform</h3>
            <ul className="space-y-2 text-sm">
              <li>
                <Link href="/about" className="text-muted-foreground hover:text-primary transition-colors">
                  Methodology
                </Link>
              </li>
              <li>
                <Link href="/categories" className="text-muted-foreground hover:text-primary transition-colors">
                  Categories
                </Link>
              </li>
              <li>
                <Link href="/faq" className="text-muted-foreground hover:text-primary transition-colors">
                  FAQ
                </Link>
              </li>
              <li>
                <Link href="/runner" className="text-muted-foreground hover:text-primary transition-colors">
                  Testing CLI
                </Link>
              </li>
            </ul>
          </div>
          <div>
            <h3 className="mb-3 text-sm font-semibold text-foreground">Community</h3>
            <ul className="space-y-2 text-sm">
              <li>
                <Link href="/sponsor" className="text-muted-foreground hover:text-primary transition-colors">
                  Sponsor a Model Test
                </Link>
              </li>
              <li>
                <Link href="/contribute/support" className="text-muted-foreground hover:text-primary transition-colors">
                  Support the Project
                </Link>
              </li>
            </ul>
          </div>
          <div>
            <h3 className="mb-3 text-sm font-semibold text-foreground">Legal</h3>
            <ul className="space-y-2 text-sm">
              <li>
                <Link href="/terms" className="text-muted-foreground hover:text-primary transition-colors">
                  Terms of Service
                </Link>
              </li>
              <li>
                <Link href="/privacy" className="text-muted-foreground hover:text-primary transition-colors">
                  Privacy Policy
                </Link>
              </li>
              <li>
                <Link href="/tester-agreement" className="text-muted-foreground hover:text-primary transition-colors">
                  Tester Agreement
                </Link>
              </li>
            </ul>
          </div>
          <div>
            <h3 className="mb-3 text-sm font-semibold text-foreground">Connect</h3>
            <ul className="space-y-2 text-sm">
              <li>
                <Link href="/contact" className="text-muted-foreground hover:text-primary transition-colors">
                  Contact
                </Link>
              </li>
              <li>
                <Link href="/newsletter" className="text-muted-foreground hover:text-primary transition-colors">
                  Newsletter
                </Link>
              </li>
            </ul>
          </div>
        </div>
        
        <div className="mt-8 pt-6 border-t border-white/[0.06] space-y-3">
          <div className="text-center text-xs text-muted-foreground/70">
            <p>
              <span className="text-white">Disclaimer:</span> This benchmark is for informational purposes only and does 
              not constitute an endorsement or recommendation of any AI model or service.
            </p>
          </div>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-2 text-sm text-muted-foreground">
            <div className="flex items-center gap-2">
              <div 
                className="h-6 px-1.5 rounded flex items-center justify-center shadow-[0_0_10px_rgba(220,38,38,0.2)]" 
                style={{ background: 'linear-gradient(135deg, #dc2626 0%, #991b1b 100%)' }}
              >
                <span className="text-white font-bold text-xs">GCB</span>
              </div>
              <span className="font-medium text-foreground/80">Great Commission Benchmark</span>
            </div>
            <span className="hidden sm:inline text-muted-foreground/50">•</span>
            <p>© {new Date().getFullYear()} All rights reserved.</p>
          </div>
        </div>
      </div>
    </footer>
  );
}
