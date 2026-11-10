import { trailerEmbedUrl } from "@/lib/youtube";

type TrailerEmbedProps = {
  trailer: string;
  title: string;
};

export default function TrailerEmbed({ trailer, title }: TrailerEmbedProps) {
  const embedUrl = trailerEmbedUrl(trailer);
  if (!embedUrl) {
    return null;
  }

  return (
    <iframe
      src={embedUrl}
      title={`${title} trailer`}
      loading="lazy"
      allow="accelerometer; encrypted-media; gyroscope; picture-in-picture"
      allowFullScreen
      // YouTube refuses to play embeds that do not send the page origin as the referrer.
      referrerPolicy="strict-origin-when-cross-origin"
      className="aspect-video w-full rounded-2xl border border-paper/10 shadow-lg"
    />
  );
}
