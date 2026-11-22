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
    // Session: allauth's `sessionid` cookie (browser sign-in) or the JWT
    // `access_token` cookie (API clients). Presence check only; the backend
    // verifies it on every data request.
    const hasSession =
      request.cookies.has("sessionid") || request.cookies.has("access_token");
    if (!hasSession) {
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
