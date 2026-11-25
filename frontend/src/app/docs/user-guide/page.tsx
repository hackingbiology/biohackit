// SPDX-License-Identifier: AGPL-3.0-or-later
// biohack.it — open-source biohacking platform
// Copyright (C) HackingBiology 2026 — https://biohack.it
// Full license text: https://www.gnu.org/licenses/agpl-3.0.html

import Link from "next/link";
import data from "@/content/user-guide.json";
import { userGuideStrings, type UserGuideStrings } from "@/lib/i18n";
import { requestLocale } from "@/lib/request-locale";

const focus =
  "focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-slate-900 dark:focus-visible:outline-slate-100";
const cell = "border-b border-slate-200 dark:border-slate-700 px-3 py-2 align-top";

function Region({
  id,
  caption,
  note,
  t,
  children,
}: {
  id: string;
  caption: string;
  note?: string;
  t: UserGuideStrings;
  children: React.ReactNode;
}) {
  return (
    <section aria-labelledby={id} className="space-y-3">
      <h2 id={id} className="text-2xl font-semibold">
        {caption}
      </h2>
      {note && <p>{note}</p>}
      <div
        role="region"
        aria-label={`${caption}: ${t.tableRegion}`}
        tabIndex={0}
        className={`overflow-x-auto ${focus}`}
      >
        <table className="w-full min-w-[36rem] border-collapse text-left text-sm">
          <caption className="sr-only">{caption}</caption>
          {children}
        </table>
      </div>
    </section>
  );
}

export async function generateMetadata() {
  const t = userGuideStrings[await requestLocale()];
  return { title: `${t.title} — biohack.it` };
}

export default async function UserGuidePage() {
  const t = userGuideStrings[await requestLocale()];
  return (
    <main className="mx-auto max-w-5xl space-y-10 p-4 sm:p-8">
      <header className="space-y-3">
        <Link href="/docs" className={`underline ${focus}`}>
          {t.back}
        </Link>
        <h1 className="text-3xl font-bold tracking-tight">{t.title}</h1>
        <p className="max-w-2xl">{t.intro}</p>
      </header>
      <Region id="steps" caption={t.stepsCaption} t={t}>
        <thead>
          <tr>
            <th scope="col" className={cell}>{t.step}</th>
            <th scope="col" className={cell}>{t.action}</th>
            <th scope="col" className={cell}>{t.route}</th>
          </tr>
        </thead>
        <tbody>
          {data.steps.map((r) => (
            <tr key={r.step}>
              <th scope="row" className={cell}>{r.step}</th>
              <td className={cell}>{r.action}</td>
              <td className={cell}>{r.route}</td>
            </tr>
          ))}
        </tbody>
      </Region>
      <Region id="signin" caption={t.signinCaption} t={t}>
        <thead>
          <tr>
            <th scope="col" className={cell}>{t.method}</th>
            <th scope="col" className={cell}>{t.availability}</th>
            <th scope="col" className={cell}>{t.source}</th>
          </tr>
        </thead>
        <tbody>
          {data.signin.map((r) => (
            <tr key={r.method}>
              <th scope="row" className={cell}>{r.method}</th>
              <td className={cell}>{r.availability}</td>
              <td className={cell}>{r.source}</td>
            </tr>
          ))}
        </tbody>
      </Region>
      <Region id="later" caption={t.laterCaption} note={t.laterNote} t={t}>
        <thead>
          <tr>
            <th scope="col" className={cell}>{t.feature}</th>
            <th scope="col" className={cell}>{t.requirement}</th>
          </tr>
        </thead>
        <tbody>
          {data.later.map((r) => (
            <tr key={r.feature}>
              <th scope="row" className={cell}>{r.feature}</th>
              <td className={cell}>{r.requirement}</td>
            </tr>
          ))}
        </tbody>
      </Region>
    </main>
  );
}
