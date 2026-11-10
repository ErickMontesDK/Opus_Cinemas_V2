// youtube-nocookie.com is YouTube's privacy-enhanced mode: no tracking cookies until the visitor plays the video.
const EMBED_BASE_URL = "https://www.youtube-nocookie.com/embed";

export function trailerEmbedUrl(trailer: string): string | null {
  if (!trailer) {
    return null;
  }

  try {
    const key = new URL(trailer).searchParams.get("v");
    return key ? `${EMBED_BASE_URL}/${encodeURIComponent(key)}` : null;
  } catch {
    // new URL() throws on a malformed URL; the page just hides the trailer.
    return null;
  }
}
