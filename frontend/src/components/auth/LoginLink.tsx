"use client";

import Link from "next/link";
import { usePathname, useSearchParams } from "next/navigation";

import { safeNextPath, withNext } from "@/lib/redirect";

export default function LoginLink({ className }: { className: string }) {
  const pathname = usePathname();
  const searchParams = useSearchParams();

  let next: string;
  if (pathname === "/login" || pathname === "/register") {
    // On the auth pages, keep the page the user originally came from.
    next = safeNextPath(searchParams.get("next"));
  } else {
    const query = searchParams.toString();
    next = query ? `${pathname}?${query}` : pathname;
  }

  return (
    <Link href={withNext("/login", next)} className={className}>
      Log in
    </Link>
  );
}
