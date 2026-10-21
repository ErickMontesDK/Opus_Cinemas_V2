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
                

                <SocialLinks />

                
            </div>
            </nav>
        </header>
    );
}


