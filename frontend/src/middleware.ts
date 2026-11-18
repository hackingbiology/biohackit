// SPDX-License-Identifier: AGPL-3.0-or-later
// biohack.it — open-source biohacking platform
// Copyright (C) HackingBiology 2026 — https://biohack.it
// Full license text: https://www.gnu.org/licenses/agpl-3.0.html

import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

// Routes that require authentication.
const PROTECTED_PREFIXES = ["/dashboard"];

export function middleware(request: NextRequest): NextResponse {
  const { pathname } = request.nextUrl;
  const isProtected = PROTECTED_PREFIXES.some((prefix) =>
    pathname.startsWith(prefix),
  );

  if (isProtected) {
    // Access token is stored as an httpOnly cookie named `access_token`.
    const token = request.cookies.get("access_token");
    if (!token) {
      const signIn = new URL("/sign-in", request.url);
      signIn.searchParams.set("next", pathname);
      return NextResponse.redirect(signIn);
    }
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/dashboard/:path*"],
};
