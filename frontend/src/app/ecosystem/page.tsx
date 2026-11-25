// SPDX-License-Identifier: AGPL-3.0-or-later
// biohack.it — open-source biohacking platform
// Copyright (C) HackingBiology 2026 — https://biohack.it
// Full license text: https://www.gnu.org/licenses/agpl-3.0.html

import Link from "next/link";
import data from "@/content/ecosystem.json";
import { ecosystemStrings } from "@/lib/i18n";
import { requestLocale } from "@/lib/request-locale";

const focus =
  "focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-slate-900 dark:focus-visible:outline-slate-100";
const cell = "border-b border-slate-200 dark:border-slate-700 px-3 py-2 align-top";

function field(fields: Partial<Record<string, string>>, key: string): string {
  return fields[key] ?? "unknown";
}

export async function generateMetadata() {
  const t = ecosystemStrings[await requestLocale()];
  return { title: `${t.title} — biohack.it` };
}

export default async function EcosystemPage() {
  const t = ecosystemStrings[await requestLocale()];
  return (
    <main className="mx-auto max-w-5xl space-y-10 p-4 sm:p-8">
      <header className="space-y-3">
        <Link href="/" className={`underline ${focus}`}>
          {t.back}
        </Link>
        <h1 className="text-3xl font-bold tracking-tight">{t.title}</h1>
        <p className="max-w-2xl">{t.intro}</p>
      </header>

      <section aria-labelledby="build-on" className="space-y-6">
        <h2 id="build-on" className="text-2xl font-semibold">
          {t.scanHeading}
        </h2>
        {data.scans.map((scan) => (
          <section key={scan.file} aria-labelledby={`scan-${scan.file}`}>
            <h3 id={`scan-${scan.file}`} className="mb-2 text-lg font-semibold">
              {scan.title}
            </h3>
            <div
              role="region"
              aria-label={`${scan.title}: ${t.tableRegion}`}
              tabIndex={0}
              className={`overflow-x-auto ${focus}`}
            >
              <table className="w-full min-w-[40rem] border-collapse text-left text-sm">
                <caption className="sr-only">{scan.title}</caption>
                <thead>
                  <tr>
                    <th scope="col" className={cell}>{t.name}</th>
                    <th scope="col" className={cell}>{t.licence}</th>
                    <th scope="col" className={cell}>{t.agpl}</th>
                    <th scope="col" className={cell}>{t.decision}</th>
                    <th scope="col" className={cell}>{t.verified}</th>
                  </tr>
                </thead>
                <tbody>
                  {scan.entries.map((e) => (
                    <tr key={e.name}>
                      <th scope="row" className={cell}>
                        <a
                          href={field(e.fields, "URL")}
                          rel="noopener noreferrer"
                          className={`underline ${focus}`}
                        >
                          {e.name}
                        </a>
                      </th>
                      <td className={cell}>{field(e.fields, "Licence")}</td>
                      <td className={cell}>
                        {field(e.fields, "AGPL-compatible")}
                      </td>
                      <td className={cell}>
                        {field(e.fields, "Decision")}
                        {e.fields["Provisional"] && (
                          <p className="mt-1">
                            <strong>{t.provisional}:</strong>{" "}
                            {e.fields["Provisional"]}
                          </p>
                        )}
                        {e.fields["Licence note"] && (
                          <details className="mt-1">
                            <summary className={focus}>{t.licenceNote}</summary>
                            <p>{e.fields["Licence note"]}</p>
                          </details>
                        )}
                      </td>
                      <td className={cell}>{field(e.fields, "Verified")}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
        ))}
      </section>

      <section aria-labelledby="give-back" className="space-y-3">
        <h2 id="give-back" className="text-2xl font-semibold">
          {t.giveBackHeading}
        </h2>
        <p>{t.giveBackIntro}</p>
        <p className="font-semibold">{t.approval}</p>
        <div
          role="region"
          aria-label={`${t.giveBackHeading}: ${t.tableRegion}`}
          tabIndex={0}
          className={`overflow-x-auto ${focus}`}
        >
          <table className="w-full min-w-[40rem] border-collapse text-left text-sm">
            <caption className="sr-only">{t.giveBackHeading}</caption>
            <thead>
              <tr>
                <th scope="col" className={cell}>{t.date}</th>
                <th scope="col" className={cell}>{t.upstream}</th>
                <th scope="col" className={cell}>{t.contribution}</th>
                <th scope="col" className={cell}>{t.status}</th>
              </tr>
            </thead>
            <tbody>
              {data.giveback.map((g) => (
                <tr key={g.upstream}>
                  <td className={cell}>{g.date}</td>
                  <th scope="row" className={cell}>
                    <a
                      href={g.link}
                      rel="noopener noreferrer"
                      className={`underline ${focus}`}
                    >
                      {g.upstream}
                    </a>
                  </th>
                  <td className={cell}>{g.contribution}</td>
                  <td className={cell}>{g.status}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </main>
  );
}
