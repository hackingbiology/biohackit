// SPDX-License-Identifier: AGPL-3.0-or-later
// biohack.it — open-source biohacking platform
// Copyright (C) HackingBiology 2026 — https://biohack.it
// Full license text: https://www.gnu.org/licenses/agpl-3.0.html

import Link from "next/link";

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-8">
      <div className="max-w-2xl w-full space-y-8 text-center">
        <div className="space-y-3">
          <h1 className="text-5xl font-bold tracking-tight">biohack.it</h1>
          <p className="text-xl text-slate-600 dark:text-slate-400">
            Document your protocol. Measure your results. Share what works.
          </p>
        </div>

        <p className="text-base text-slate-500 dark:text-slate-400 max-w-lg mx-auto">
          An open-source platform for biohackers to track biomarkers, log
          interventions, and share structured protocols publicly — with full
          scientific rigour.
        </p>

        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Link
            href="/sign-up"
            className="inline-flex items-center justify-center rounded-lg bg-slate-900 dark:bg-slate-100 px-6 py-3 text-sm font-semibold text-white dark:text-slate-900 hover:opacity-90 transition-opacity"
          >
            Get started
          </Link>
          <Link
            href="/sign-in"
            className="inline-flex items-center justify-center rounded-lg border border-slate-200 dark:border-slate-700 px-6 py-3 text-sm font-semibold hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors"
          >
            Sign in
          </Link>
        </div>
      </div>
    </main>
  );
}
