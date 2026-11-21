// SPDX-License-Identifier: AGPL-3.0-or-later
// biohack.it — open-source biohacking platform
// Copyright (C) HackingBiology 2026 — https://biohack.it
// Full license text: https://www.gnu.org/licenses/agpl-3.0.html

"use client";

import { useEffect, useState } from "react";
import {
  SocialProvider,
  confirmLoginCode,
  getProviders,
  isAuthenticated,
  loginWithPasskey,
  passkeysSupported,
  requestLoginCode,
  startProviderLogin,
} from "@/lib/allauth";
import { pickLocale, signInStrings } from "@/lib/i18n";

const inputClass =
  "block w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-transparent px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-slate-500";
const btnClass =
  "w-full rounded-lg border border-slate-300 dark:border-slate-600 px-4 py-2.5 text-sm font-semibold hover:bg-slate-50 dark:hover:bg-slate-800 focus:outline-none focus:ring-2 focus:ring-slate-500 disabled:opacity-50";

export default function SignInForm({
  lang,
  onSignedIn,
}: {
  lang?: string;
  onSignedIn: () => void;
}) {
  const t = signInStrings[pickLocale(lang)];
  const [providers, setProviders] = useState<SocialProvider[]>([]);
  const [email, setEmail] = useState("");
  const [code, setCode] = useState("");
  const [codeSent, setCodeSent] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [passkeys, setPasskeys] = useState(false);

  useEffect(() => {
    getProviders()
      .then(setProviders)
      .catch(() => setProviders([]));
    setPasskeys(passkeysSupported());
  }, []);

  async function sendCode(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setBusy(true);
    try {
      const r = await requestLoginCode(email);
      // 401 with a pending "login_by_code" flow is the expected success.
      if (r.status === 401 || r.status === 200) setCodeSent(true);
      else setError(t.error);
    } catch {
      setError(t.error);
    } finally {
      setBusy(false);
    }
  }

  async function confirm(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setBusy(true);
    try {
      const r = await confirmLoginCode(code);
      if (isAuthenticated(r)) onSignedIn();
      else setError(t.codeError);
    } catch {
      setError(t.codeError);
    } finally {
      setBusy(false);
    }
  }

  async function passkey() {
    setError(null);
    try {
      const r = await loginWithPasskey();
      if (isAuthenticated(r)) onSignedIn();
      else setError(t.passkeyError);
    } catch {
      setError(t.passkeyError);
    }
  }

  return (
    <div className="w-full max-w-sm space-y-6">
      <div className="space-y-1">
        <h1 className="text-2xl font-bold">{t.title}</h1>
        <p className="text-sm text-slate-600 dark:text-slate-300">{t.intro}</p>
      </div>

      {providers.length > 0 && (
        <ul className="space-y-2" aria-label={t.continueWith}>
          {providers.map((p) => (
            <li key={p.id}>
              <button
                type="button"
                className={btnClass}
                onClick={() =>
                  startProviderLogin(
                    p.id,
                    `${window.location.origin}/dashboard`,
                  )
                }
              >
                {t.continueWith}{" "}
                {p.id === "discourse_connect" ? "rapamycin.news" : p.name}
              </button>
            </li>
          ))}
        </ul>
      )}

      {passkeys && (
        <button type="button" className={btnClass} onClick={passkey}>
          {t.passkey}
        </button>
      )}

      <p className="text-center text-sm text-slate-600 dark:text-slate-300">
        {t.or}
      </p>

      {!codeSent ? (
        <form onSubmit={sendCode} className="space-y-3">
          <label htmlFor="email" className="block text-sm font-medium">
            {t.email}
          </label>
          <input
            id="email"
            type="email"
            autoComplete="email webauthn"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            aria-describedby={error ? "form-error" : undefined}
            className={inputClass}
          />
          <button type="submit" disabled={busy} className={btnClass}>
            {busy ? t.sending : t.sendCode}
          </button>
        </form>
      ) : (
        <form onSubmit={confirm} className="space-y-3">
          <p role="status" className="text-sm">
            {t.codeSent}
          </p>
          <label htmlFor="code" className="block text-sm font-medium">
            {t.code}
          </label>
          <input
            id="code"
            autoComplete="one-time-code"
            required
            value={code}
            onChange={(e) => setCode(e.target.value)}
            aria-describedby={error ? "form-error" : undefined}
            className={inputClass}
          />
          <button type="submit" disabled={busy} className={btnClass}>
            {t.confirm}
          </button>
        </form>
      )}

      {error && (
        <p id="form-error" role="alert" className="text-sm text-red-700">
          {error}
        </p>
      )}
    </div>
  );
}
