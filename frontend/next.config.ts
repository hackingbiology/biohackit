// SPDX-License-Identifier: AGPL-3.0-or-later
// biohack.it — open-source biohacking platform
// Copyright (C) HackingBiology 2026 — https://biohack.it
// Full license text: https://www.gnu.org/licenses/agpl-3.0.html

import type { NextConfig } from "next";

// Rewrites and headers are evaluated at build time in standalone output, so
// BACKEND_INTERNAL_URL and NOINDEX must be set when `next build` runs.
const nextConfig: NextConfig = {
  output: "standalone",
  // Django routes need their trailing slash; without this Next 308-strips it
  // and Django APPEND_SLASH re-adds it, looping.
  skipTrailingSlashRedirect: true,
  experimental: {
    typedRoutes: false,
  },
  async rewrites() {
    const backend = process.env.BACKEND_INTERNAL_URL ?? "http://backend:8000";
    return [
      { source: "/api/:path*/", destination: `${backend}/api/:path*/` },
      { source: "/_allauth/:path*/", destination: `${backend}/_allauth/:path*/` },
      { source: "/api/:path*", destination: `${backend}/api/:path*` },
      { source: "/_allauth/:path*", destination: `${backend}/_allauth/:path*` },
    ];
  },
  async headers() {
    if (process.env.NOINDEX !== "1") return [];
    return [
      {
        source: "/:path*",
        headers: [{ key: "X-Robots-Tag", value: "noindex" }],
      },
    ];
  },
};

export default nextConfig;
