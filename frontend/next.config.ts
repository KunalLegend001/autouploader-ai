import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Standalone output for Docker deployments (Railway etc.)
  output: "standalone",
  async rewrites() {
    return [
      {
        source: '/api/v1/:path*',
        destination: 'https://au-backend-api-kunal.up.railway.app/api/v1/:path*'
      }
    ]
  }
};

export default nextConfig;
