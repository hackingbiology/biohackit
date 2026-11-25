// SPDX-License-Identifier: AGPL-3.0-or-later
// biohack.it — open-source biohacking platform
// Copyright (C) HackingBiology 2026 — https://biohack.it
// Full license text: https://www.gnu.org/licenses/agpl-3.0.html

import Link from "next/link";
import data from "@/content/architecture.json";
import { architectureStrings, type ArchitectureStrings } from "@/lib/i18n";
import { requestLocale } from "@/lib/request-locale";

const focus =
  "focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-slate-900 dark:focus-visible:outline-slate-100";
const cell = "border-b border-slate-200 dark:border-slate-700 px-3 py-2 align-top";

function Region({
  caption,
  t,
  children,
}: {
  caption: string;
  t: ArchitectureStrings;
  children: React.ReactNode;
}) {
  return (
    <div
      role="region"
      aria-label={`${caption}: ${t.tableRegion}`}
      tabIndex={0}
      className={`overflow-x-auto ${focus}`}
    >
      <table className="w-full min-w-[40rem] border-collapse text-left text-sm">
        <caption className="mb-2 text-left text-lg font-semibold">{caption}</caption>
        {children}
      </table>
    </div>
  );
}

export async function generateMetadata() {
  const t = architectureStrings[await requestLocale()];
  return { title: `${t.title} — biohack.it` };
}

export default async function ArchitecturePage() {
  const t = architectureStrings[await requestLocale()];
  return (
    <main className="mx-auto max-w-5xl space-y-10 p-4 sm:p-8">
      <header className="space-y-3">
        <Link href="/docs" className={`underline ${focus}`}>
          {t.back}
        </Link>
        <h1 className="text-3xl font-bold tracking-tight">{t.title}</h1>
        <p className="max-w-2xl">{t.intro}</p>
      </header>
      <Region caption={t.builtCaption} t={t}>
        <thead>
          <tr>
            <th scope="col" className={cell}>{t.component}</th>
            <th scope="col" className={cell}>{t.layer}</th>
            <th scope="col" className={cell}>{t.path}</th>
            <th scope="col" className={cell}>{t.purpose}</th>
          </tr>
        </thead>
        <tbody>
          {data.built.map((r) => (
            <tr key={r.component}>
              <th scope="row" className={cell}>{r.component}</th>
              <td className={cell}>{t.layerLabels[r.layer] ?? r.layer}</td>
              <td className={cell}>{r.path}</td>
              <td className={cell}>{r.purpose}</td>
            </tr>
          ))}
        </tbody>
      </Region>
      <Region caption={t.specifiedCaption} t={t}>
        <thead>
          <tr>
            <th scope="col" className={cell}>{t.component}</th>
            <th scope="col" className={cell}>{t.requirement}</th>
          </tr>
        </thead>
        <tbody>
          {data.specified.map((r) => (
            <tr key={r.component}>
              <th scope="row" className={cell}>{r.component}</th>
              <td className={cell}>{r.requirement}</td>
            </tr>
          ))}
        </tbody>
      </Region>
    </main>
  );
}
