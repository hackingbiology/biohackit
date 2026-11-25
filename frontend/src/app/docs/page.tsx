// SPDX-License-Identifier: AGPL-3.0-or-later
// biohack.it — open-source biohacking platform
// Copyright (C) HackingBiology 2026 — https://biohack.it
// Full license text: https://www.gnu.org/licenses/agpl-3.0.html

import Link from "next/link";
import {
  aiSurfacesStrings,
  architectureStrings,
  changelogStrings,
  userGuideStrings,
} from "@/lib/i18n";
import { requestLocale } from "@/lib/request-locale";

const focus =
  "focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-slate-900 dark:focus-visible:outline-slate-100";

export async function generateMetadata() {
  const t = aiSurfacesStrings[await requestLocale()];
  return { title: `${t.docsIndex} — biohack.it` };
}

export default async function DocsIndex() {
  const locale = await requestLocale();
  const t = aiSurfacesStrings[locale];
  const a = architectureStrings[locale];
  const u = userGuideStrings[locale];
  const c = changelogStrings[locale];
  return (
    <main className="mx-auto max-w-3xl space-y-6 p-4 sm:p-8">
      <h1 className="text-3xl font-bold tracking-tight">{t.docsIndex}</h1>
      <ul className="list-disc space-y-2 pl-6">
        <li>
          <Link href="/docs/ai-surfaces" className={`underline ${focus}`}>
            {t.title}
          </Link>
        </li>
        <li>
          <Link href="/docs/architecture" className={`underline ${focus}`}>
            {a.title}
          </Link>
        </li>
        <li>
          <Link href="/docs/user-guide" className={`underline ${focus}`}>
            {u.title}
          </Link>
        </li>
        <li>
          <Link href="/docs/changelog" className={`underline ${focus}`}>
            {c.title}
          </Link>
        </li>
      </ul>
    </main>
  );
}
