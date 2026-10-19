import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  images: {
    // Posters come from TMDB's image CDN
    remotePatterns: [{ protocol: "https", hostname: "image.tmdb.org" }],
  },
  // Do not generate AGENTS.md (AI assistant instructions) on `next dev`
  agentRules: false,
};

export default nextConfig;
