// SPDX-License-Identifier: AGPL-3.0-or-later
// biohack.it — open-source biohacking platform
// Copyright (C) HackingBiology 2026 — https://biohack.it
// Full license text: https://www.gnu.org/licenses/agpl-3.0.html

import Link from "next/link";
import data from "@/content/changelog.json";
import { changelogStrings } from "@/lib/i18n";
import { requestLocale } from "@/lib/request-locale";

const focus =
  "focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-slate-900 dark:focus-visible:outline-slate-100";
const cell = "border-b border-slate-200 dark:border-slate-700 px-3 py-2 align-top";

export async function generateMetadata() {
  const t = changelogStrings[await requestLocale()];
  return { title: `${t.title} — biohack.it` };
}

export default async function ChangelogPage() {
  const t = changelogStrings[await requestLocale()];
  return (
    <main className="mx-auto max-w-5xl space-y-10 p-4 sm:p-8">
      <header className="space-y-3">
        <Link href="/docs" className={`underline ${focus}`}>
          {t.back}
        </Link>
        <h1 className="text-3xl font-bold tracking-tight">{t.title}</h1>
        <p className="max-w-2xl">{t.intro}</p>
      </header>
      {data.days.map((day) => (
        <section key={day.date} aria-labelledby={`day-${day.date}`} className="space-y-3">
          <h2 id={`day-${day.date}`} className="text-2xl font-semibold">
            <time dateTime={day.date}>{day.date}</time>
          </h2>
          <div
            role="region"
            aria-label={`${day.date}: ${t.tableRegion}`}
            tabIndex={0}
            className={`overflow-x-auto ${focus}`}
          >
            <table className="w-full min-w-[36rem] border-collapse text-left text-sm">
              <caption className="sr-only">{`${t.caption} ${day.date}`}</caption>
              <thead>
                <tr>
                  <th scope="col" className={cell}>{t.summary}</th>
                  <th scope="col" className={cell}>{t.change}</th>
                  <th scope="col" className={cell}>{t.commit}</th>
                </tr>
              </thead>
              <tbody>
                {day.entries.map((e) => (
                  <tr key={e.commit}>
                    <th scope="row" className={cell}>{e.summary}</th>
                    <td className={cell}>{e.change}</td>
                    <td className={cell}>{e.commit}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      ))}
    </main>
  );
}
