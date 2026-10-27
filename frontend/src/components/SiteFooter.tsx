import Link from "next/link";
import {FaPhone, FaRegSadCry} from "react-icons/fa";
import { MdEmail } from "react-icons/md";
import { SocialLinks } from "./SocialLinks";

export default function SiteFooter() {
    return (
        <footer className="bg-ink py-6 text-muted text-lg">
            <div className="container mx-auto flex flex-col gap-10 md:gap-3 px-3 md:flex-row md:justify-between">

            <div className="flex flex-col gap-5 max-w-xl">
                <Link href="/" className="font-brand text-brand text-3xl">Opus Cinemas</Link>
                    
                <p >
                    Experience the magic of cinema with state-of-the-art
                    technology and premium service. Your journey into the extraordinary starts here.</p>

                <SocialLinks />
            </div>
            <div className="flex flex-col gap-5">
                <h2 className="font-detail text-brand">Contact Us</h2>
                    
                    <div className="flex items-center gap-3">
                        <FaPhone aria-hidden="true" />
                        <span >+1 (236) 444 9999</span>
                    </div>
                
            
                    <div className="flex items-center gap-3 ">
                        <MdEmail aria-hidden="true" />
                        <a href="mailto:info@opuscinemas.com" className="hover:text-brand">info@opuscinemas.com</a>
                    </div>
                  
            </div>

            <div className="flex flex-col gap-5">
                <h2 className="font-detail text-brand">Information</h2>
                <ul >
                    <li><span >Privacy
                            Policy</span></li>
                    <li><span >Terms of
                            Use</span></li>
                    <li><span>Cookie
                            Settings</span></li>
                </ul>
                <hr className="my-1 border-muted" />
                <div >
                    <p >©2026 Opus Cinemas. All rights reserved.</p>
                    <p >Developed by Erick Montes <FaRegSadCry aria-hidden="true" />
                    </p>
                </div>
            </div>  
                
            </div>
        </footer> 
    );
}
