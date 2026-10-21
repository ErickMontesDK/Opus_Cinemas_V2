import { FaFacebookF, FaInstagram, FaXTwitter } from "react-icons/fa6";

const socialLinksInfo = [
    {
        href: "https://www.facebook.com",
        label: "Facebook",
        icon: FaFacebookF,
    },
    {
        href: "https://www.instagram.com",
        label: "Instagram",
        icon: FaInstagram,
    },
    {
        href: "https://www.x.com",
        label: "X (Twitter)",
        icon: FaXTwitter,
    },
]

export const SocialLinks = () => {
    return (
        <div className="flex-row flex gap-3">
            {socialLinksInfo.map((link) => (
                <a key={link.label} href={link.href} 
                className="bg-ink text-brand border-2 p-2 rounded-full hover:bg-brand hover:text-ink " 
                target="_blank" rel="noopener noreferrer" aria-label={link.label}>
                    <link.icon aria-hidden="true" />
                </a>
            ))}
        </div>  
    );
}