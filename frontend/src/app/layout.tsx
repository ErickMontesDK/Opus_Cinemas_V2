import type { Metadata } from "next";
import { Gugi, Orbitron, Roboto } from "next/font/google";
import "./globals.css";
import SiteHeader from "@/components/SiteHeader";
import SiteFooter from "@/components/SiteFooter";

const gugi = Gugi({ variable: "--font-gugi", subsets: ["latin"], weight: "400" });
const orbitron = Orbitron({ variable: "--font-orbitron", subsets: ["latin"] });
const roboto = Roboto({ variable: "--font-roboto", subsets: ["latin"]});

export const metadata: Metadata = {
  title: "Opus Cinemas",
  description: "Showtimes, live seat selection and online tickets.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html className={`${gugi.variable} ${orbitron.variable} ${roboto.variable}`} lang="en">
      <body>
        <SiteHeader />
        

        <main className="flex flex-1">
        {children}
        </main>

        <SiteFooter />
            
      </body>

    </html>
  );
}
