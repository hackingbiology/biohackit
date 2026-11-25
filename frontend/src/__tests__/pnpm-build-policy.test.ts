// SPDX-License-Identifier: AGPL-3.0-or-later
import { describe, expect, it } from "@jest/globals";
import { readFileSync } from "fs";
import { join } from "path";

const root = join(__dirname, "..", "..");
const read = (name: string): string => readFileSync(join(root, name), "utf8");

type Pkg = {
  packageManager?: string;
  pnpm?: { onlyBuiltDependencies?: string[]; ignoredBuiltDependencies?: string[] };
};
const pkg: Pkg = JSON.parse(read("package.json"));
const lock = read("pnpm-lock.yaml");

// Packages known to ship an install/postinstall build script. The v9 lockfile
// does not record requiresBuild, so they are listed here; each one present in
// the lockfile must be explicitly allowed or ignored, or pnpm >= 10 fails with
// ERR_PNPM_IGNORED_BUILDS.
const BUILD_SCRIPT_PACKAGES = ["sharp", "unrs-resolver"];

const inLockfile = (name: string): boolean =>
  new RegExp(`^ {2}${name}@\\d`, "m").test(lock);

describe("pnpm pinning and build-script policy", () => {
  // scenario: dev-process::staging-runs-production-servers
  it("pins an exact pnpm version", () => {
    expect(pkg.packageManager).toMatch(/^pnpm@\d+\.\d+\.\d+(\+sha\d+\.[0-9a-f]+)?$/);
  });

  // scenario: dev-process::staging-runs-production-servers
  it("allows or ignores every lockfile package with a build script", () => {
    const allowed = pkg.pnpm?.onlyBuiltDependencies ?? [];
    const ignored = pkg.pnpm?.ignoredBuiltDependencies ?? [];
    for (const name of BUILD_SCRIPT_PACKAGES) {
      expect(inLockfile(name)).toBe(true);
      expect(allowed.includes(name) || ignored.includes(name)).toBe(true);
    }
    expect(allowed).toContain("sharp");
    expect(ignored).toContain("unrs-resolver");
  });

  // scenario: dev-process::staging-runs-production-servers
  it("copies package.json, the lockfile and any pnpm config into the deps stage", () => {
    const dockerfile = read("Dockerfile");
    const deps = dockerfile.split(/^FROM /m).find((s) => s.includes(" AS deps")) ?? "";
    const copy = deps.split("\n").find((l) => l.startsWith("COPY ")) ?? "";
    expect(copy).toContain("package.json");
    expect(copy).toContain("pnpm-lock.yaml");
    for (const file of ["pnpm-workspace.yaml"]) {
      let exists = true;
      try {
        read(file);
      } catch {
        exists = false;
      }
      if (exists) expect(copy).toContain(file);
    }
  });
});
