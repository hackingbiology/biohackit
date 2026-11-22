// SPDX-License-Identifier: AGPL-3.0-or-later
// biohack.it — open-source biohacking platform
// Copyright (C) HackingBiology 2026 — https://biohack.it
// Full license text: https://www.gnu.org/licenses/agpl-3.0.html

import { apiFetch } from "./api";
import { logoutSession } from "./allauth";

export interface TokenPair {
  access: string;
  refresh: string;
}

// Tokens are stored via the Next.js Route Handler that sets httpOnly cookies.
// These client-side helpers call those route handlers (not the DRF API directly)
// so that tokens never touch client-side JS storage.

export async function register(
  email: string,
  password: string,
): Promise<TokenPair> {
  const res = await apiFetch("/api/auth/register/", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
  return res.json() as Promise<TokenPair>;
}

export async function login(
  email: string,
  password: string,
): Promise<TokenPair> {
  const res = await apiFetch("/api/auth/token/", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
  return res.json() as Promise<TokenPair>;
}

export async function refreshToken(refresh: string): Promise<{ access: string }> {
  const res = await apiFetch("/api/auth/token/refresh/", {
    method: "POST",
    body: JSON.stringify({ refresh }),
  });
  return res.json() as Promise<{ access: string }>;
}

export async function logout(): Promise<void> {
  // The browser session lives in allauth's session cookie; the headless
  // API ends it (allauth answers 401 once the session is gone, which is fine).
  await logoutSession();
}
