"use client";

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
import { Menu } from "lucide-react";
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet";
import { useUserProfile } from "@/lib/useUserProfile";

export function Header() {
  const { data: session, status } = useSession();
  const { isAdmin, isModerator, isBenchmarkDeveloper } = useUserProfile();
  const pathname = usePathname();
  const user = session?.user;
  const isLoading = status === "loading";

  const isActive = (href: string) => {
    if (href === "/") return pathname === "/";
    return pathname.startsWith(href);
  };

  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60" role="banner">
      <div className="container flex h-16 items-center">
        <Link href="/" className="mr-6 flex items-center space-x-2" aria-label="Great Commission Benchmark - Home">
          <span className="font-bold text-xl">Great Commission Benchmark</span>
        </Link>

        {/* Desktop Navigation */}
        <nav className="hidden md:flex items-center space-x-6 text-sm font-medium" aria-label="Main navigation">
          <Link
            href="/"
            className={`transition-colors hover:text-foreground/80 pb-1 border-b-2 ${
              isActive("/")
                ? "text-foreground border-foreground"
                : "text-foreground/60 border-transparent"
            }`}
          >
            Home
          </Link>
          <Link
            href="/research"
            className={`transition-colors hover:text-foreground/80 pb-1 border-b-2 ${
              isActive("/research")
                ? "text-foreground border-foreground"
                : "text-foreground/60 border-transparent"
            }`}
          >
            Research
          </Link>
          <Link
            href="/contribute"
            className={`transition-colors hover:text-foreground/80 pb-1 border-b-2 ${
              isActive("/contribute")
                ? "text-foreground border-foreground"
                : "text-foreground/60 border-transparent"
            }`}
          >
            Contribute
          </Link>
          <Link
            href="/about"
            className={`transition-colors hover:text-foreground/80 pb-1 border-b-2 ${
              isActive("/about")
                ? "text-foreground border-foreground"
                : "text-foreground/60 border-transparent"
            }`}
          >
            About
          </Link>
        </nav>

        <div className="flex flex-1 items-center justify-end space-x-4">
          {isLoading ? (
            <div className="h-8 w-8 animate-pulse rounded-full bg-muted" />
          ) : user ? (
            <>
              <Link href="/dashboard" className="hidden md:block">
                <Button variant="ghost" size="sm">
                  Dashboard
                </Button>
              </Link>
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="ghost" className="relative h-8 w-8 rounded-full">
                    <Avatar className="h-8 w-8">
                      <AvatarFallback>
                        {user.name?.[0] || user.email?.[0] || "U"}
                      </AvatarFallback>
                    </Avatar>
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent className="w-56" align="end">
                  <div className="px-2 py-1.5">
                    <p className="text-sm font-medium">{user.name || "User"}</p>
                    <p className="text-xs text-muted-foreground">{user.email}</p>
                  </div>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem asChild>
                    <Link href="/dashboard">My Dashboard</Link>
                  </DropdownMenuItem>
                  <DropdownMenuItem asChild>
                    <Link href="/dashboard/settings">Account Settings</Link>
                  </DropdownMenuItem>
                  {isModerator && (
                    <>
                      <DropdownMenuSeparator />
                      <DropdownMenuItem asChild>
                        <Link href="/moderator">Moderator Panel</Link>
                      </DropdownMenuItem>
                    </>
                  )}
                  {isBenchmarkDeveloper && (
                    <DropdownMenuItem asChild>
                      <Link href="/benchmark">Benchmark Development</Link>
                    </DropdownMenuItem>
                  )}
                  {isAdmin && (
                    <>
                      <DropdownMenuSeparator />
                      <DropdownMenuItem asChild>
                        <Link href="/admin">Admin Dashboard</Link>
                      </DropdownMenuItem>
                    </>
                  )}
                  <DropdownMenuSeparator />
                  <DropdownMenuItem onClick={() => signOut({ callbackUrl: "/" })}>
                    Logout
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </>
          ) : (
            <Button asChild>
              <a href="/api/auth/signin">Login</a>
            </Button>
          )}

          {/* Mobile Menu */}
          <Sheet>
            <SheetTrigger asChild className="md:hidden">
              <Button variant="ghost" size="icon" aria-label="Open navigation menu">
                <Menu className="h-5 w-5" aria-hidden="true" />
                <span className="sr-only">Toggle menu</span>
              </Button>
            </SheetTrigger>
            <SheetContent side="right" aria-label="Mobile navigation">
              <nav className="flex flex-col space-y-4 mt-8" aria-label="Mobile navigation">
                <Link
                  href="/"
                  className={`text-lg font-medium transition-colors hover:text-foreground/80 pl-3 border-l-2 ${
                    isActive("/") ? "border-foreground" : "border-transparent"
                  }`}
                >
                  Home
                </Link>
                <Link
                  href="/research"
                  className={`text-lg font-medium transition-colors hover:text-foreground/80 pl-3 border-l-2 ${
                    isActive("/research") ? "border-foreground" : "border-transparent"
                  }`}
                >
                  Research
                </Link>
                <Link
                  href="/contribute"
                  className={`text-lg font-medium transition-colors hover:text-foreground/80 pl-3 border-l-2 ${
                    isActive("/contribute") ? "border-foreground" : "border-transparent"
                  }`}
                >
                  Contribute
                </Link>
                <Link
                  href="/about"
                  className={`text-lg font-medium transition-colors hover:text-foreground/80 pl-3 border-l-2 ${
                    isActive("/about") ? "border-foreground" : "border-transparent"
                  }`}
                >
                  About
                </Link>
                {user && (
                  <>
                    <Link
                      href="/dashboard"
                      className="text-lg font-medium transition-colors hover:text-foreground/80"
                    >
                      Dashboard
                    </Link>
                    {isModerator && (
                      <Link
                        href="/moderator"
                        className="text-lg font-medium transition-colors hover:text-foreground/80"
                      >
                        Moderator Panel
                      </Link>
                    )}
                    {isBenchmarkDeveloper && (
                      <Link
                        href="/benchmark"
                        className="text-lg font-medium transition-colors hover:text-foreground/80"
                      >
                        Benchmark Development
                      </Link>
                    )}
                    {isAdmin && (
                      <Link
                        href="/admin"
                        className="text-lg font-medium transition-colors hover:text-foreground/80"
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
