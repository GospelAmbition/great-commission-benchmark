"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useSession, signOut } from "next-auth/react";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { MenuIcon, SearchIcon } from "@/lib/icons";
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet";
import { useUserProfile } from "@/lib/useUserProfile";
import { SearchModal } from "./SearchModal";
import { prefetchLeaderboardPage } from "../../lib/leaderboard-prefetch";

export function Header() {
  const { data: session, status } = useSession();
  const { isAdmin, isModerator, isBlogManager, isBenchmarkDeveloper, canViewBenchmark, canModerate, canManageBlog, canAdmin } = useUserProfile();
  const pathname = usePathname();
  const user = session?.user;
  const isLoading = status === "loading";
  const [searchOpen, setSearchOpen] = useState(false);

  // Global keyboard shortcut for search (Cmd+K / Ctrl+K)
  useEffect(() => {
    function handleKeyDown(e: KeyboardEvent) {
      if ((e.metaKey || e.ctrlKey) && e.key === "k") {
        e.preventDefault();
        setSearchOpen(true);
      }
    }
    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, []);

  const isActive = (href: string) => {
    if (href === "/") return pathname === "/";
    return pathname.startsWith(href);
  };

  return (
    <header className="sticky top-0 z-50 w-full bg-background/95 backdrop-blur-md border-b border-white/[0.06]" role="banner">
      <div className="container flex h-14 items-center">
        <Link href="/" className="mr-8 flex items-center space-x-2 group" aria-label="Great Commission Benchmark - Home">
          <div className="flex items-center gap-2">
            <div 
              className="h-6 px-1.5 rounded flex items-center justify-center shadow-[0_0_10px_rgba(220,38,38,0.2)]" 
              style={{ background: 'linear-gradient(135deg, #dc2626 0%, #991b1b 100%)' }}
            >
              <span className="text-white font-bold text-xs">GCB</span>
            </div>
            <span className="font-bold text-lg text-foreground hidden sm:inline">
              Great Commission Benchmark
            </span>
          </div>
        </Link>

        {/* Desktop Navigation */}
        <nav className="hidden md:flex items-center space-x-1 text-sm font-medium" aria-label="Main navigation">
          <Link
            href="/"
            className={`px-3 py-2 rounded-md transition-all ${
              isActive("/")
                ? "text-primary bg-primary/10 font-semibold"
                : "text-muted-foreground hover:text-foreground hover:bg-white/5"
            }`}
          >
            Home
          </Link>
          <Link
            href="/leaderboard"
            onMouseEnter={prefetchLeaderboardPage}
            onFocus={prefetchLeaderboardPage}
            className={`px-3 py-2 rounded-md transition-all ${
              isActive("/leaderboard")
                ? "text-primary bg-primary/10 font-semibold"
                : "text-muted-foreground hover:text-foreground hover:bg-white/5"
            }`}
          >
            Leaderboard
          </Link>
          <Link
            href="/categories"
            className={`px-3 py-2 rounded-md transition-all ${
              isActive("/categories")
                ? "text-primary bg-primary/10 font-semibold"
                : "text-muted-foreground hover:text-foreground hover:bg-white/5"
            }`}
          >
            Categories
          </Link>
          <Link
            href="/insights"
            className={`px-3 py-2 rounded-md transition-all ${
              isActive("/insights")
                ? "text-primary bg-primary/10 font-semibold"
                : "text-muted-foreground hover:text-foreground hover:bg-white/5"
            }`}
          >
            Insights
          </Link>
          <Link
            href="/about"
            className={`px-3 py-2 rounded-md transition-all ${
              isActive("/about")
                ? "text-primary bg-primary/10 font-semibold"
                : "text-muted-foreground hover:text-foreground hover:bg-white/5"
            }`}
          >
            About
          </Link>
        </nav>

        <div className="flex flex-1 items-center justify-end space-x-3">
          {/* Search Button */}
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setSearchOpen(true)}
            className="hidden md:flex h-8 w-8 text-muted-foreground hover:text-foreground hover:bg-white/5"
            aria-label="Search models and providers"
          >
            <SearchIcon className="h-4 w-4" />
          </Button>

          {/* Search Modal */}
          <SearchModal open={searchOpen} onOpenChange={setSearchOpen} />

          {isLoading ? (
            <div className="h-8 w-8 animate-pulse rounded-full bg-white/10" />
          ) : user ? (
            <>
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="ghost" className="relative h-8 w-8 rounded-full ring-2 ring-primary/30 hover:ring-primary/50 transition-all">
                    <Avatar className="h-8 w-8">
                      <AvatarFallback 
                        className="text-white font-semibold text-sm"
                        style={{ background: 'linear-gradient(135deg, #dc2626 0%, #991b1b 100%)' }}
                      >
                        {user.name?.[0] || user.email?.[0] || "U"}
                      </AvatarFallback>
                    </Avatar>
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent className="w-56 bg-card border-white/10" align="end">
                  <div className="px-2 py-1.5 border-b border-white/10">
                    <p className="text-sm font-semibold text-foreground">{user.name || "User"}</p>
                    <p className="text-xs text-muted-foreground">{user.email}</p>
                  </div>
                  <DropdownMenuItem asChild>
                    <Link href="/dashboard" className="cursor-pointer text-foreground">My Dashboard</Link>
                  </DropdownMenuItem>
                  {canModerate && (
                    <DropdownMenuItem asChild>
                      <Link href="/moderator" className="cursor-pointer text-foreground">Moderator Panel</Link>
                    </DropdownMenuItem>
                  )}
                  {canManageBlog && (
                    <DropdownMenuItem asChild>
                      <Link href="/blog-manager" className="cursor-pointer text-foreground">Blog Management</Link>
                    </DropdownMenuItem>
                  )}
                  {canViewBenchmark && (
                    <DropdownMenuItem asChild>
                      <Link href="/benchmark" className="cursor-pointer text-foreground">Benchmark Dashboard</Link>
                    </DropdownMenuItem>
                  )}
                  {canAdmin && (
                    <DropdownMenuItem asChild>
                      <Link href="/admin" className="cursor-pointer text-foreground">Admin Dashboard</Link>
                    </DropdownMenuItem>
                  )}
                  <DropdownMenuSeparator className="bg-white/10" />
                  <DropdownMenuItem asChild>
                    <Link href="/dashboard/settings" className="cursor-pointer text-foreground">Account Settings</Link>
                  </DropdownMenuItem>
                  <DropdownMenuItem 
                    onClick={() => signOut({ callbackUrl: "/" })}
                    className="cursor-pointer text-destructive focus:text-destructive focus:bg-destructive/10"
                  >
                    Logout
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </>
          ) : (
            <Button asChild variant="glow" size="sm">
              <a href="/api/auth/signin">Login</a>
            </Button>
          )}

          {/* Mobile Menu */}
          <Sheet>
            <SheetTrigger asChild className="md:hidden">
              <Button variant="ghost" size="icon" aria-label="Open navigation menu" className="text-foreground hover:bg-white/5">
                <MenuIcon className="h-5 w-5" aria-hidden="true" />
                <span className="sr-only">Toggle menu</span>
              </Button>
            </SheetTrigger>
            <SheetContent side="right" aria-label="Mobile navigation" className="border-l border-white/10 bg-card">
              <nav className="flex flex-col space-y-2 mt-8" aria-label="Mobile navigation">
                <Link
                  href="/"
                  className={`text-base font-medium transition-all px-4 py-2.5 rounded-lg ${
                    isActive("/") 
                      ? "text-primary bg-primary/10 border-l-2 border-primary" 
                      : "text-foreground hover:bg-white/5"
                  }`}
                >
                  Home
                </Link>
                <Link
                  href="/leaderboard"
                  onMouseEnter={prefetchLeaderboardPage}
                  onFocus={prefetchLeaderboardPage}
                  className={`text-base font-medium transition-all px-4 py-2.5 rounded-lg ${
                    isActive("/leaderboard") 
                      ? "text-primary bg-primary/10 border-l-2 border-primary" 
                      : "text-foreground hover:bg-white/5"
                  }`}
                >
                  Leaderboard
                </Link>
                <Link
                  href="/categories"
                  className={`text-base font-medium transition-all px-4 py-2.5 rounded-lg ${
                    isActive("/categories") 
                      ? "text-primary bg-primary/10 border-l-2 border-primary" 
                      : "text-foreground hover:bg-white/5"
                  }`}
                >
                  Categories
                </Link>
                <Link
                  href="/insights"
                  className={`text-base font-medium transition-all px-4 py-2.5 rounded-lg ${
                    isActive("/insights") 
                      ? "text-primary bg-primary/10 border-l-2 border-primary" 
                      : "text-foreground hover:bg-white/5"
                  }`}
                >
                  Insights
                </Link>
                <Link
                  href="/about"
                  className={`text-base font-medium transition-all px-4 py-2.5 rounded-lg ${
                    isActive("/about") 
                      ? "text-primary bg-primary/10 border-l-2 border-primary" 
                      : "text-foreground hover:bg-white/5"
                  }`}
                >
                  About
                </Link>
                
                {user && (
                  <>
                    <div className="h-px bg-white/10 my-2" />
                    <Link
                      href="/dashboard"
                      className="text-base font-medium transition-all px-4 py-2.5 rounded-lg text-foreground hover:bg-white/5"
                    >
                      Dashboard
                    </Link>
                    {isModerator && (
                      <Link
                        href="/moderator"
                        className="text-base font-medium transition-all px-4 py-2.5 rounded-lg text-foreground hover:bg-white/5"
                      >
                        Moderator Panel
                      </Link>
                    )}
                    {canManageBlog && (
                      <Link
                        href="/blog-manager"
                        className="text-base font-medium transition-all px-4 py-2.5 rounded-lg text-foreground hover:bg-white/5"
                      >
                        Blog Management
                      </Link>
                    )}
                    {canViewBenchmark && (
                      <Link
                        href="/benchmark"
                        className="text-base font-medium transition-all px-4 py-2.5 rounded-lg text-foreground hover:bg-white/5"
                      >
                        Benchmark Development
                      </Link>
                    )}
                    {isAdmin && (
                      <Link
                        href="/admin"
                        className="text-base font-medium transition-all px-4 py-2.5 rounded-lg text-foreground hover:bg-white/5"
                      >
                        Admin Dashboard
                      </Link>
                    )}
                  </>
                )}
              </nav>
            </SheetContent>
          </Sheet>
        </div>
      </div>
    </header>
  );
}
