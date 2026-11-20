import type { NextConfig } from "next";

// Server-only: the browser never sees this URL, it always calls the relative /api/ path.
const API_URL = process.env.API_URL;
if (!API_URL) {
  throw new Error("API_URL is not set. Copy .env.example to .env.local.");
}

const nextConfig: NextConfig = {
  images: {
    // Posters come from TMDB's image CDN
    remotePatterns: [{ protocol: "https", hostname: "image.tmdb.org" }],
  },
  // Do not generate AGENTS.md (AI assistant instructions) on `next dev`
  agentRules: false,
  // Django URLs end with "/"; the default redirect to "/path" would drop the body of a POST.
  skipTrailingSlashRedirect: true,
  async rewrites() {
    // Same-origin proxy, so Django's cookies belong to the frontend domain (docs/AUTH.md).
    // :path* does not keep the trailing slash, so both sides spell it out.
    return [{ source: "/api/:path*/", destination: `${API_URL}/api/:path*/` }];
  },
};

export default nextConfig;
