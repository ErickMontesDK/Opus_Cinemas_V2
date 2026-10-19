import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  images: {
    // Posters come from TMDB's image CDN
    remotePatterns: [{ protocol: "https", hostname: "image.tmdb.org" }],
  },
};

export default nextConfig;
