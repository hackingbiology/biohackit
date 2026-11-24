// SPDX-License-Identifier: AGPL-3.0-or-later
import { afterEach, describe, expect, it } from "@jest/globals";
import nextConfig from "../../next.config";

describe("next.config staging behaviour", () => {
  const original = process.env.NOINDEX;
  afterEach(() => {
    if (original === undefined) delete process.env.NOINDEX;
    else process.env.NOINDEX = original;
  });

  // scenario: dev-process::staging-not-indexed
  it("sets X-Robots-Tag noindex when NOINDEX=1", async () => {
    process.env.NOINDEX = "1";
    const headers = await nextConfig.headers!();
    expect(headers).toEqual([
      {
        source: "/:path*",
        headers: [{ key: "X-Robots-Tag", value: "noindex" }],
      },
    ]);
  });

  // scenario: dev-process::staging-not-indexed
  it("sets no robots header when NOINDEX is not 1", async () => {
    delete process.env.NOINDEX;
    expect(await nextConfig.headers!()).toEqual([]);
  });

  // scenario: dev-process::staging-runs-production-servers
  it("rewrites /api and /_allauth to the backend", async () => {
    const rewrites = (await nextConfig.rewrites!()) as {
      source: string;
      destination: string;
    }[];
    const sources = rewrites.map((r) => r.source);
    expect(sources).toContain("/api/:path*");
    expect(sources).toContain("/_allauth/:path*");
  });

  // scenario: dev-process::staging-runs-production-servers
  it("keeps trailing slashes so Django APPEND_SLASH cannot loop", async () => {
    expect(nextConfig.skipTrailingSlashRedirect).toBe(true);
    const rewrites = (await nextConfig.rewrites!()) as {
      source: string;
      destination: string;
    }[];
    const sources = rewrites.map((r) => r.source);
    const slash = rewrites.find((r) => r.source === "/api/:path*/");
    expect(slash?.destination.endsWith("/api/:path*/")).toBe(true);
    expect(sources.indexOf("/api/:path*/")).toBeLessThan(
      sources.indexOf("/api/:path*"),
    );
    expect(sources.indexOf("/_allauth/:path*/")).toBeLessThan(
      sources.indexOf("/_allauth/:path*"),
    );
  });
});
