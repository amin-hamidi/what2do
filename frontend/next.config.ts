import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "standalone",
  images: {
    remotePatterns: [
      { protocol: "https", hostname: "www.dallasobserver.com" },
      { protocol: "https", hostname: "www.dallasites101.com" },
      { protocol: "https", hostname: "www.visitdallas.com" },
      { protocol: "https", hostname: "www.siloshows.com" },
      { protocol: "https", hostname: "**.mlb.com" },
      { protocol: "https", hostname: "**.nba.com" },
      { protocol: "https", hostname: "**.nhl.com" },
      { protocol: "https", hostname: "**.nfl.com" },
    ],
  },
  async headers() {
    return [
      {
        source: "/(.*)",
        headers: [
          { key: "X-Frame-Options", value: "DENY" },
          { key: "X-Content-Type-Options", value: "nosniff" },
          { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
        ],
      },
    ];
  },
};

export default nextConfig;
