// SPDX-License-Identifier: AGPL-3.0-or-later
// biohack.it — open-source biohacking platform
// Copyright (C) HackingBiology 2026 — https://biohack.it
// Full license text: https://www.gnu.org/licenses/agpl-3.0.html

import Link from "next/link";
import data from "@/content/ai-surfaces.json";
import { aiSurfacesStrings, type AiSurfacesStrings } from "@/lib/i18n";
import { requestLocale } from "@/lib/request-locale";

const focus =
  "focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-slate-900 dark:focus-visible:outline-slate-100";
const cell = "border-b border-slate-200 dark:border-slate-700 px-3 py-2 align-top";

interface Row {
  surface: string;
  kind: string;
  where: string;
  status: string;
}

function SurfaceTable({
  caption,
  rows,
  t,
}: {
  caption: string;
  rows: Row[];
  t: AiSurfacesStrings;
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
        <thead>
          <tr>
            <th scope="col" className={cell}>{t.surface}</th>
            <th scope="col" className={cell}>{t.kind}</th>
            <th scope="col" className={cell}>{t.where}</th>
            <th scope="col" className={cell}>{t.status}</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((r) => (
            <tr key={r.surface}>
              <th scope="row" className={cell}>{r.surface}</th>
              <td className={cell}>{t.kindLabels[r.kind] ?? r.kind}</td>
              <td className={cell}>{r.where}</td>
              <td className={cell}>{t.statusLabels[r.status] ?? r.status}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export async function generateMetadata() {
  const t = aiSurfacesStrings[await requestLocale()];
  return { title: `${t.title} — biohack.it` };
}

export default async function AiSurfacesPage() {
  const t = aiSurfacesStrings[await requestLocale()];
  return (
    <main className="mx-auto max-w-5xl space-y-10 p-4 sm:p-8">
      <header className="space-y-3">
        <Link href="/docs" className={`underline ${focus}`}>
          {t.back}
        </Link>
        <h1 className="text-3xl font-bold tracking-tight">{t.title}</h1>
        <p className="max-w-2xl">{t.intro}</p>
      </header>
      <SurfaceTable caption={t.aiCaption} rows={data.ai} t={t} />
      <SurfaceTable caption={t.deterministicCaption} rows={data.deterministic} t={t} />
    </main>
  );
}
