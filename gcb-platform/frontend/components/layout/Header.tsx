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
  const { isAdmin, isModerator, isBlogManager, isBenchmarkDeveloper } = useUserProfile();
  const pathname = usePathname();
  const user = session?.user;
  const isLoading = status === "loading";

  const isActive = (href: string) => {
    if (href === "/") return pathname === "/";
    return pathname.startsWith(href);
  };

  return (
    <header className="sticky top-0 z-50 w-full bg-white shadow-sm" role="banner">
      {/* Top brand accent line */}
      <div className="h-1 w-full" style={{ background: 'linear-gradient(135deg, #a11824 0%, #7a1219 100%)' }} />
      
      <div className="container flex h-14 items-center">
        <Link href="/" className="mr-8 flex items-center space-x-2 group" aria-label="Great Commission Benchmark - Home">
          <div className="flex items-center gap-2">
            <div 
              className="w-8 h-8 rounded-lg flex items-center justify-center shadow-sm group-hover:shadow-md transition-shadow"
              style={{ background: 'linear-gradient(135deg, #a11824 0%, #7a1219 100%)' }}
            >
              <span className="text-white font-bold text-sm">GCB</span>
            </div>
            <span className="font-bold text-lg text-slate-900 hidden sm:inline">
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
                ? "text-red-700 bg-red-50 font-semibold"
                : "text-slate-600 hover:text-red-700 hover:bg-red-50"
            }`}
          >
            Home
          </Link>
          <Link
            href="/research"
            className={`px-3 py-2 rounded-md transition-all ${
              isActive("/research")
                ? "text-red-700 bg-red-50 font-semibold"
                : "text-slate-600 hover:text-red-700 hover:bg-red-50"
            }`}
          >
            Research
          </Link>
          <Link
            href="/action"
            className={`px-3 py-2 rounded-md transition-all ${
              isActive("/action")
                ? "text-red-700 bg-red-50 font-semibold"
                : "text-slate-600 hover:text-red-700 hover:bg-red-50"
            }`}
          >
            Action
          </Link>
          <Link
            href="/about"
            className={`px-3 py-2 rounded-md transition-all ${
              isActive("/about")
                ? "text-red-700 bg-red-50 font-semibold"
                : "text-slate-600 hover:text-red-700 hover:bg-red-50"
            }`}
          >
            About
          </Link>
        </nav>

        <div className="flex flex-1 items-center justify-end space-x-3">
          {isLoading ? (
            <div className="h-8 w-8 animate-pulse rounded-full bg-slate-200" />
          ) : user ? (
            <>
              <Link href="/dashboard" className="hidden md:block">
                <Button variant="outline" size="sm" className="border-slate-300 text-slate-700 hover:border-red-200 hover:bg-red-50">
                  Dashboard
                </Button>
              </Link>
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="ghost" className="relative h-8 w-8 rounded-full ring-2 ring-red-200 hover:ring-red-300 transition-all">
                    <Avatar className="h-8 w-8">
                      <AvatarFallback 
                        className="text-white font-semibold text-sm"
                        style={{ background: 'linear-gradient(135deg, #a11824 0%, #7a1219 100%)' }}
                      >
                        {user.name?.[0] || user.email?.[0] || "U"}
                      </AvatarFallback>
                    </Avatar>
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent className="w-56" align="end">
                  <div className="px-2 py-1.5 border-b border-slate-200">
                    <p className="text-sm font-semibold text-slate-900">{user.name || "User"}</p>
                    <p className="text-xs text-slate-500">{user.email}</p>
                  </div>
                  <DropdownMenuItem asChild>
                    <Link href="/dashboard" className="cursor-pointer text-slate-700">My Dashboard</Link>
                  </DropdownMenuItem>
                  {isModerator && (
                    <DropdownMenuItem asChild>
                      <Link href="/moderator" className="cursor-pointer text-slate-700">Moderator Panel</Link>
                    </DropdownMenuItem>
                  )}
                  {isBlogManager && (
                    <DropdownMenuItem asChild>
                      <Link href="/blog-manager" className="cursor-pointer text-slate-700">Blog Management</Link>
                    </DropdownMenuItem>
                  )}
                  {isBenchmarkDeveloper && (
                    <DropdownMenuItem asChild>
                      <Link href="/benchmark" className="cursor-pointer text-slate-700">Benchmark Development</Link>
                    </DropdownMenuItem>
                  )}
                  {isAdmin && (
                    <DropdownMenuItem asChild>
                      <Link href="/admin" className="cursor-pointer text-slate-700">Admin Dashboard</Link>
                    </DropdownMenuItem>
                  )}
                  <DropdownMenuSeparator />
                  <DropdownMenuItem asChild>
                    <Link href="/dashboard/settings" className="cursor-pointer text-slate-700">Account Settings</Link>
                  </DropdownMenuItem>
                  <DropdownMenuItem 
                    onClick={() => signOut({ callbackUrl: "/" })}
                    className="cursor-pointer text-red-700 focus:text-red-700 focus:bg-red-50"
                  >
                    Logout
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </>
          ) : (
            <Button asChild variant="brand" size="sm">
              <a href="/api/auth/signin">Login</a>
            </Button>
          )}

          {/* Mobile Menu */}
          <Sheet>
            <SheetTrigger asChild className="md:hidden">
              <Button variant="ghost" size="icon" aria-label="Open navigation menu" className="text-slate-700 hover:bg-red-50">
                <Menu className="h-5 w-5" aria-hidden="true" />
                <span className="sr-only">Toggle menu</span>
              </Button>
            </SheetTrigger>
            <SheetContent side="right" aria-label="Mobile navigation" className="border-l-0 shadow-xl">
              {/* Mobile brand accent */}
              <div className="absolute top-0 left-0 right-0 h-1" style={{ background: 'linear-gradient(135deg, #a11824 0%, #7a1219 100%)' }} />
              
              <nav className="flex flex-col space-y-2 mt-8" aria-label="Mobile navigation">
                <Link
                  href="/"
                  className={`text-base font-medium transition-all px-4 py-2.5 rounded-lg ${
                    isActive("/") 
                      ? "text-red-700 bg-red-50 border-l-4 border-red-700" 
                      : "text-slate-700 hover:bg-red-50"
                  }`}
                >
                  Home
                </Link>
                <Link
                  href="/research"
                  className={`text-base font-medium transition-all px-4 py-2.5 rounded-lg ${
                    isActive("/research") 
                      ? "text-red-700 bg-red-50 border-l-4 border-red-700" 
                      : "text-slate-700 hover:bg-red-50"
                  }`}
                >
                  Research
                </Link>
                <Link
                  href="/action"
                  className={`text-base font-medium transition-all px-4 py-2.5 rounded-lg ${
                    isActive("/action") 
                      ? "text-red-700 bg-red-50 border-l-4 border-red-700" 
                      : "text-slate-700 hover:bg-red-50"
                  }`}
                >
                  Action
                </Link>
                <Link
                  href="/about"
                  className={`text-base font-medium transition-all px-4 py-2.5 rounded-lg ${
                    isActive("/about") 
                      ? "text-red-700 bg-red-50 border-l-4 border-red-700" 
                      : "text-slate-700 hover:bg-red-50"
                  }`}
                >
                  About
                </Link>
                
                {user && (
                  <>
                    <div className="h-px bg-slate-200 my-2" />
                    <Link
                      href="/dashboard"
                      className="text-base font-medium transition-all px-4 py-2.5 rounded-lg text-slate-700 hover:bg-red-50"
                    >
                      Dashboard
                    </Link>
                    {isModerator && (
                      <Link
                        href="/moderator"
                        className="text-base font-medium transition-all px-4 py-2.5 rounded-lg text-slate-700 hover:bg-red-50"
                      >
                        Moderator Panel
                      </Link>
                    )}
                    {isBlogManager && (
                      <Link
                        href="/blog-manager"
                        className="text-base font-medium transition-all px-4 py-2.5 rounded-lg text-slate-700 hover:bg-red-50"
                      >
                        Blog Management
                      </Link>
                    )}
                    {isBenchmarkDeveloper && (
                      <Link
                        href="/benchmark"
                        className="text-base font-medium transition-all px-4 py-2.5 rounded-lg text-slate-700 hover:bg-red-50"
                      >
                        Benchmark Development
                      </Link>
                    )}
                    {isAdmin && (
                      <Link
                        href="/admin"
                        className="text-base font-medium transition-all px-4 py-2.5 rounded-lg text-slate-700 hover:bg-red-50"
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
