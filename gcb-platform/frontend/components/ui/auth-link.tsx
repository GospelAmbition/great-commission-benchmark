"use client";

import { useSession } from "next-auth/react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { MouseEvent, ReactNode } from "react";

interface AuthLinkProps {
  href: string;
  children: ReactNode;
  className?: string;
}

export function AuthLink({ href, children, className }: AuthLinkProps) {
  const { data: session, status } = useSession();
  const router = useRouter();

  function handleClick(e: MouseEvent<HTMLAnchorElement>) {
    if (status === "loading") {
      e.preventDefault();
      return;
    }
    
    if (!session?.user) {
      e.preventDefault();
      router.push(`/api/auth/signin?callbackUrl=${encodeURIComponent(href)}`);
    }
  }

  return (
    <Link href={href} onClick={handleClick} className={className}>
      {children}
    </Link>
  );
}
