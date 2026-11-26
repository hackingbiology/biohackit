// SPDX-License-Identifier: AGPL-3.0-or-later
// biohack.it — open-source biohacking platform
// Copyright (C) HackingBiology 2026 — https://biohack.it
// Full license text: https://www.gnu.org/licenses/agpl-3.0.html

// Plain-fetch client for the django-allauth headless browser API.
// No auth dependency: WebAuthn goes through the browser's own API.

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
const BASE = `${API_URL}/_allauth/browser/v1`;

export interface SocialProvider {
  id: string;
  name: string;
}

export interface AllauthResult {
  status: number;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  body: any;
}

export function csrfToken(): string {
  if (typeof document === "undefined") return "";
  const m = document.cookie.match(/(?:^|;\s*)csrftoken=([^;]+)/);
  return m ? decodeURIComponent(m[1]) : "";
}

async function call(
  method: "GET" | "POST" | "DELETE",
  path: string,
  data?: unknown,
): Promise<AllauthResult> {
  const res = await fetch(`${BASE}${path}`, {
    method,
    credentials: "include",
    headers: {
      Accept: "application/json",
      ...(data !== undefined ? { "Content-Type": "application/json" } : {}),
      "X-CSRFToken": csrfToken(),
    },
    body: data !== undefined ? JSON.stringify(data) : undefined,
  });
  let body: unknown = {};
  try {
    body = await res.json();
  } catch {
    /* empty body */
  }
  return { status: res.status, body };
}

/** rapamycin.news (the community forum) is listed first. */
export function orderProviders(providers: SocialProvider[]): SocialProvider[] {
  const rank = (p: SocialProvider) => (p.id === "discourse_connect" ? 0 : 1);
  return [...providers].sort((a, b) => rank(a) - rank(b));
}

/** Only providers the server has configured are returned (possibly none). */
export async function getProviders(): Promise<SocialProvider[]> {
  const { body } = await call("GET", "/config");
  const list = body?.data?.socialaccount?.providers ?? [];
  return orderProviders(
    list.map((p: SocialProvider) => ({ id: p.id, name: p.name })),
  );
}

export async function requestLoginCode(email: string): Promise<AllauthResult> {
  return call("POST", "/auth/code/request", { email });
}

export async function confirmLoginCode(code: string): Promise<AllauthResult> {
  return call("POST", "/auth/code/confirm", { code });
}

/** Ends the allauth session (headless browser API). */
export async function logoutSession(): Promise<AllauthResult> {
  return call("DELETE", "/auth/session");
}

export function isAuthenticated(r: AllauthResult): boolean {
  return r.status === 200 && r.body?.meta?.is_authenticated === true;
}

/** Social login is a top-level form POST so the provider can redirect back. */
export function startProviderLogin(providerId: string, callbackUrl: string) {
  const form = document.createElement("form");
  form.method = "POST";
  form.action = `${BASE}/auth/provider/redirect`;
  const fields: Record<string, string> = {
    provider: providerId,
    callback_url: callbackUrl,
    process: "login",
    csrfmiddlewaretoken: csrfToken(),
  };
  for (const [name, value] of Object.entries(fields)) {
    const input = document.createElement("input");
    input.type = "hidden";
    input.name = name;
    input.value = value;
    form.appendChild(input);
  }
  document.body.appendChild(form);
  form.submit();
}

export function passkeysSupported(): boolean {
  return (
    typeof window !== "undefined" &&
    typeof window.PublicKeyCredential !== "undefined" &&
    "parseRequestOptionsFromJSON" in window.PublicKeyCredential
  );
}

export async function loginWithPasskey(): Promise<AllauthResult> {
  const opts = await call("GET", "/auth/webauthn/authenticate");
  const requestOptions = opts.body?.data?.request_options;
  if (!requestOptions) return opts;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const PKC = window.PublicKeyCredential as any;
  const publicKey = PKC.parseRequestOptionsFromJSON(requestOptions);
  const cred = (await navigator.credentials.get({ publicKey })) as
    | (Credential & { toJSON(): unknown })
    | null;
  if (!cred) return { status: 400, body: {} };
  return call("POST", "/auth/webauthn/authenticate", {
    credential: cred.toJSON(),
  });
}
