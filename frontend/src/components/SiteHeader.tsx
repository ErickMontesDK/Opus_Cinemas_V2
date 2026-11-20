import Link from "next/link";
import { SocialLinks } from "./SocialLinks";

export default function SiteHeader() {
    return (
        <header className="bg-ink py-2 text-brand text-2xl">
            <nav>
            <div className="container mx-auto flex flex-col gap-4 items-center justify-between px-3 py-3 md:py-1 md:flex-row">
                <Link href="/" className="font-brand hover:text-paper">
                    Opus Cinemas
                </Link>

                <div className="flex items-center gap-4">
                    <SocialLinks />
                    <Link
                        href="/login"
                        className="rounded-full border-2 border-brand px-4 py-1.5 font-detail text-xs font-semibold tracking-widest uppercase hover:bg-brand hover:text-ink"
                    >
                        Log in
                    </Link>
                </div>
            </div>
            </nav>
        </header>
    );
}


