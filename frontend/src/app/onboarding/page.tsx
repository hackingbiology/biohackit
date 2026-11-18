// SPDX-License-Identifier: AGPL-3.0-or-later
// biohack.it — open-source biohacking platform
// Copyright (C) HackingBiology 2026 — https://biohack.it
// Full license text: https://www.gnu.org/licenses/agpl-3.0.html

import Link from "next/link";

export default function OnboardingPage() {
  return (
    <main className="flex min-h-screen items-center justify-center p-8">
      <div className="max-w-lg w-full space-y-6">
        <h1 className="text-2xl font-bold">Welcome to biohack.it</h1>
        <p className="text-slate-600 dark:text-slate-400">
          Your profile is public by default. Here&apos;s why that matters:
        </p>
        <ul className="list-disc list-inside space-y-2 text-slate-700 dark:text-slate-300 text-sm">
          <li>
            Public biomarker data lets others see what protocols actually work.
          </li>
          <li>
            Copy-trading for health only functions when results are visible.
          </li>
          <li>
            You can make any individual measurement or the whole profile private
            at any time.
          </li>
        </ul>
        <Link
          href="/dashboard"
          className="inline-flex items-center justify-center rounded-lg bg-slate-900 dark:bg-slate-100 px-6 py-3 text-sm font-semibold text-white dark:text-slate-900 hover:opacity-90 transition-opacity"
        >
          Continue →
        </Link>
      </div>
    </main>
  );
}
