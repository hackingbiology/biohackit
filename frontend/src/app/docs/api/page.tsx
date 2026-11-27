// SPDX-License-Identifier: AGPL-3.0-or-later
// biohack.it — open-source biohacking platform
// Copyright (C) HackingBiology 2026 — https://biohack.it
// Full license text: https://www.gnu.org/licenses/agpl-3.0.html

import Link from "next/link";
import data from "@/content/api-reference.json";
import { apiReferenceStrings } from "@/lib/i18n";
import { blocks } from "@/lib/markdown-blocks";
import { requestLocale } from "@/lib/request-locale";

const focus =
  "focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-slate-900 dark:focus-visible:outline-slate-100";
const cell = "border-b border-slate-200 dark:border-slate-700 px-3 py-2 align-top";

function Inline({ text }: { text: string }) {
  return (
    <>
      {text.split("`").map((piece, i) =>
        i % 2 === 1 ? (
          <code key={i} className="break-words font-mono text-[0.9em]">
            {piece}
          </code>
        ) : (
          piece
        ),
      )}
    </>
  );
}

function Body({ body }: { body: string }) {
  return (
    <>
      {blocks(body).map((b, i) =>
        b.kind === "code" ? (
          <pre
            key={i}
            tabIndex={0}
            className={`overflow-x-auto rounded bg-slate-100 p-3 text-sm dark:bg-slate-800 ${focus}`}
          >
            <code>{b.text}</code>
          </pre>
        ) : b.kind === "table" ? (
          <div
            key={i}
            role="region"
            aria-label={b.head.join(", ")}
            tabIndex={0}
            className={`overflow-x-auto ${focus}`}
          >
            <table className="w-full min-w-[20rem] border-collapse text-left text-sm">
              <thead>
                <tr>
                  {b.head.map((h, j) => (
                    <th key={j} scope="col" className={cell}>
                      <Inline text={h} />
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {b.rows.map((r, j) => (
                  <tr key={j}>
                    {r.map((c, k) => (
                      <td key={k} className={cell}>
                        <Inline text={c} />
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : b.kind === "list" ? (
          <ul key={i} className="list-disc space-y-1 pl-6">
            {b.items.map((item, j) => (
              <li key={j}>
                <Inline text={item} />
              </li>
            ))}
          </ul>
        ) : (
          <p key={i}>
            <Inline text={b.text} />
          </p>
        ),
      )}
    </>
  );
}

export async function generateMetadata() {
  const t = apiReferenceStrings[await requestLocale()];
  return { title: `${t.title} — biohack.it` };
}

export default async function ApiReferencePage() {
  const t = apiReferenceStrings[await requestLocale()];
  return (
    <main className="mx-auto max-w-4xl space-y-10 p-4 sm:p-8">
      <header className="space-y-3">
        <Link href="/docs" className={`underline ${focus}`}>
          {t.back}
        </Link>
        <h1 className="text-3xl font-bold tracking-tight">{t.title}</h1>
        <p className="max-w-2xl">{t.intro}</p>
      </header>
      <section aria-labelledby="overview" className="space-y-3">
        <h2 id="overview" className="text-2xl font-semibold">
          {t.overviewCaption}
        </h2>
        <div
          role="region"
          aria-label={`${t.overviewCaption}: ${t.tableRegion}`}
          tabIndex={0}
          className={`overflow-x-auto ${focus}`}
        >
          <table className="w-full min-w-[28rem] border-collapse text-left text-sm">
            <caption className="sr-only">{t.overviewCaption}</caption>
            <thead>
              <tr>
                <th scope="col" className={cell}>{t.method}</th>
                <th scope="col" className={cell}>{t.path}</th>
              </tr>
            </thead>
            <tbody>
              {data.endpoints.map((e) => (
                <tr key={`${e.method} ${e.path}`}>
                  <th scope="row" className={cell}>{e.method}</th>
                  <td className={cell}>
                    <a href={`#${e.anchor}`} className={`break-all underline ${focus}`}>
                      {e.path}
                    </a>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
      {data.docs.map((doc) => (
        <section key={doc.file} aria-labelledby={`doc-${doc.file}`} className="space-y-6">
          <h2 id={`doc-${doc.file}`} className="text-2xl font-semibold">
            {doc.title}
          </h2>
          {doc.sections.map((s) => {
            const Heading = s.level === 2 ? "h3" : "h4";
            return (
              <article key={s.anchor} aria-labelledby={s.anchor} className="space-y-3">
                <Heading
                  id={s.anchor}
                  className={`break-words font-semibold ${s.level === 2 ? "text-xl" : "text-lg"}`}
                >
                  {s.heading.replaceAll("`", "")}
                </Heading>
                <Body body={s.body} />
              </article>
            );
          })}
        </section>
      ))}
    </main>
  );
}
