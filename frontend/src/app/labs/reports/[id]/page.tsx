// SPDX-License-Identifier: AGPL-3.0-or-later
// biohack.it — open-source biohacking platform
// Copyright (C) HackingBiology 2026 — https://biohack.it
// Full license text: https://www.gnu.org/licenses/agpl-3.0.html

"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useRef, useState } from "react";
import { RangeCheck } from "@/components/RangeCheck";
import {
  fetchReport,
  rollbackReport,
  type StoredReport,
} from "@/lib/labs";
import {
  labImportStrings,
  labStrings,
  pickLocale,
  type LabStrings,
} from "@/lib/i18n";

const button =
  "inline-flex items-center justify-center rounded-lg bg-slate-900 dark:bg-slate-100 px-5 py-3 text-sm font-semibold text-white dark:text-slate-900 disabled:opacity-50";

type Load = "loading" | "ok" | "notFound" | "signIn" | "error";
type Message = "" | "signIn" | "undoFailed" | "undoConflict";

function stateText(state: string, t: LabStrings): string {
  switch (state) {
    case "entered":
      return t.stateEntered;
    case "user_confirmed":
      return t.stateUserConfirmed;
    case "source_verified":
      return t.stateSourceVerified;
    case "disputed":
      return t.stateDisputed;
    case "retracted":
      return t.stateRetracted;
    default:
      return state;
  }
}

export default function LabReportPage() {
  const params = useParams<{ id: string }>();
  const id = params.id;
  const locale = pickLocale(
    typeof document === "undefined" ? undefined : document.documentElement.lang,
  );
  const t = labStrings[locale];
  const imp = labImportStrings[locale];
  const [load, setLoad] = useState<Load>("loading");
  const [report, setReport] = useState<StoredReport | null>(null);
  const [undone, setUndone] = useState(false);
  const [message, setMessage] = useState<Message>("");
  const [busy, setBusy] = useState(false);
  const undoneHeading = useRef<HTMLHeadingElement>(null);

  useEffect(() => {
    let live = true;
    fetchReport(id)
      .then((res) => {
        if (!live) return;
        if (res.report) {
          setReport(res.report);
          setLoad("ok");
        } else if (res.status === 404) setLoad("notFound");
        else if (res.status === 401 || res.status === 403) setLoad("signIn");
        else setLoad("error");
      })
      .catch(() => live && setLoad("error"));
    return () => {
      live = false;
    };
  }, [id]);

  useEffect(() => {
    if (undone) undoneHeading.current?.focus();
  }, [undone]);

  async function onUndo() {
    if (!window.confirm(t.undoConfirm)) return;
    setBusy(true);
    setMessage("");
    try {
      const res = await rollbackReport(Number(id));
      if (res.status === 204) setUndone(true);
      else if (res.status === 409) setMessage("undoConflict");
      else setMessage(res.status === 401 || res.status === 403 ? "signIn" : "undoFailed");
    } catch {
      setMessage("undoFailed");
    } finally {
      setBusy(false);
    }
  }

  const originText = (origin: string) =>
    origin === "manual"
      ? t.originManual
      : origin === "import"
        ? t.originCsv
        : `${t.originUnknown}: ${origin}`;
  const given = (v: string | null) => (v ? v : t.notGiven);
  const signInLink = (
    <Link href="/sign-in" className="underline">
      {t.signInLink}
    </Link>
  );

  if (load !== "ok" || !report) {
    return (
      <main className="mx-auto max-w-3xl space-y-4 p-4 sm:p-8">
        <div role="alert" aria-live="assertive">
          {load === "notFound" && <h1 className="text-2xl font-bold">{t.notFound}</h1>}
          {load === "signIn" && (
            <p>
              {t.signIn} {signInLink}
            </p>
          )}
          {load === "error" && <p>{t.genericError}</p>}
        </div>
        {load === "loading" && <p>{t.loading}</p>}
        <p>
          <Link href="/labs/import" className="underline">
            {t.importLink}
          </Link>{" "}
          <Link href="/labs/new" className="underline">
            {t.newLink}
          </Link>
        </p>
      </main>
    );
  }

  if (undone) {
    return (
      <main className="mx-auto max-w-3xl space-y-4 p-4 sm:p-8">
        <h1 ref={undoneHeading} tabIndex={-1} className="text-2xl font-bold">
          {t.undone}
        </h1>
        <p>
          <Link href="/labs/new" className="underline">
            {t.newLink}
          </Link>
        </p>
      </main>
    );
  }

  return (
    <main className="mx-auto max-w-5xl space-y-6 p-4 sm:p-8">
      <h1 className="text-2xl font-bold">
        {t.reportTitle.replace("{id}", String(report.id))}
      </h1>
      <ul className="space-y-1">
        <li>
          {t.origin} {originText(report.origin)}
        </li>
        <li>
          {t.laboratoryLabel} {given(report.laboratory)}
        </li>
        <li>
          {report.original_retained ? t.originRetainedYes : t.originRetainedNo}
        </li>
      </ul>

      <div role="alert" aria-live="assertive">
        {message !== "" && (
          <p className="rounded border border-red-700 p-3">
            {message === "signIn"
              ? t.signIn
              : message === "undoConflict"
                ? t.undoConflict
                : t.undoFailed}{" "}
            {message === "signIn" && signInLink}
          </p>
        )}
      </div>

      <div
        className="overflow-x-auto"
        role="region"
        aria-label={t.tableRegion}
        tabIndex={0}
      >
        <table className="w-full border-collapse text-left text-sm">
          <caption className="pb-2 text-left font-semibold">
            {t.tableCaption}
          </caption>
          <thead>
            <tr>
              <th scope="col">{t.colLoinc}</th>
              <th scope="col">{t.colValue}</th>
              <th scope="col">{t.colUnit}</th>
              <th scope="col">{t.colNormalised}</th>
              <th scope="col">{t.colLaboratory}</th>
              <th scope="col">{t.colMethod}</th>
              <th scope="col">{t.colDevice}</th>
              <th scope="col">{t.colCollected}</th>
              <th scope="col">{t.colReported}</th>
              <th scope="col">{t.colState}</th>
              <th scope="col">{t.colAggregation}</th>
              <th scope="col">{t.colRange}</th>
            </tr>
          </thead>
          <tbody>
            {report.results.map((r) => (
              <tr key={r.id} className="border-t align-top">
                <th scope="row">{r.loinc_code}</th>
                <td>{r.reported_value}</td>
                <td>{r.reported_unit}</td>
                <td>
                  {r.normalised_value !== null && r.normalised_unit !== ""
                    ? `${r.normalised_value} ${r.normalised_unit}`
                    : t.notGiven}
                </td>
                <td>{given(r.laboratory)}</td>
                <td>{given(r.method)}</td>
                <td>{given(r.device)}</td>
                <td>{given(r.collected_at)}</td>
                <td>{given(r.reported_at)}</td>
                <td>{stateText(r.validation_state, t)}</td>
                <td>{r.aggregation_eligible ? t.aggregationYes : t.aggregationNo}</td>
                <td>
                  <RangeCheck plausibility={r.plausibility} t={imp} />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {report.origin === "import" ? (
        <button type="button" className={button} disabled={busy} onClick={onUndo}>
          {t.undo}
        </button>
      ) : (
        <p>{t.undoManualNote}</p>
      )}
      <p>
        <Link href="/labs/import" className="underline">
          {t.importLink}
        </Link>{" "}
        <Link href="/labs/new" className="underline">
          {t.newLink}
        </Link>
      </p>
    </main>
  );
}
