import Link from "next/link";
import { Suspense } from "react";

import UserMenu from "@/components/auth/UserMenu";
import { SocialLinks } from "./SocialLinks";

export default function SiteHeader() {
    return (
        <header className="bg-ink py-2 text-brand text-2xl">
            <nav>
            <div className="container mx-auto flex flex-col gap-4 items-center justify-between px-3 py-3 md:py-1 md:flex-row">
                <Link href="/" className="font-brand hover:text-paper">
                    Opus Cinemas
                </Link>

                <div className="flex flex-wrap items-center justify-center gap-4">
                    <SocialLinks />
                    {/* The rest of the header does not wait for the /api/me/ call. */}
                    <Suspense fallback={<div className="h-8 w-24" aria-hidden="true" />}>
                        <UserMenu />
                    </Suspense>
                </div>
            </div>
            </nav>
        </header>
    );
}
