// SPDX-License-Identifier: AGPL-3.0-or-later
// biohack.it — open-source biohacking platform
// Copyright (C) HackingBiology 2026 — https://biohack.it
// Full license text: https://www.gnu.org/licenses/agpl-3.0.html

"use client";

import Link from "next/link";
import { useEffect, useRef, useState } from "react";
import {
  confirmCsv,
  previewCsv,
  rollbackReport,
  type ConfirmedReport,
  type PreviewRow,
} from "@/lib/labs";
import { labImportStrings, pickLocale } from "@/lib/i18n";

const button =
  "inline-flex items-center justify-center rounded-lg bg-slate-900 dark:bg-slate-100 px-5 py-3 text-sm font-semibold text-white dark:text-slate-900 disabled:opacity-50";

type Message = "" | "signIn" | "genericError" | "confirmRefused" | "noFile" | "undoFailed";

export default function LabImportPage() {
  const t =
    labImportStrings[
      pickLocale(
        typeof document === "undefined"
          ? undefined
          : document.documentElement.lang,
      )
    ];
  const [file, setFile] = useState<File | null>(null);
  const [rows, setRows] = useState<PreviewRow[] | null>(null);
  const [report, setReport] = useState<ConfirmedReport | null>(null);
  const [undone, setUndone] = useState(false);
  const [message, setMessage] = useState<Message>("");
  const [detail, setDetail] = useState("");
  const [busy, setBusy] = useState(false);
  const summaryRef = useRef<HTMLHeadingElement>(null);
  const savedRef = useRef<HTMLHeadingElement>(null);

  useEffect(() => {
    if (report) savedRef.current?.focus();
    else if (rows) summaryRef.current?.focus();
  }, [rows, report, undone]);

  const unrecognised = rows ? rows.filter((r) => r.status !== "recognised") : [];
  const canSave = rows !== null && rows.length > 0 && unrecognised.length === 0;

  function fail(status: number, text: string) {
    setMessage(status === 401 || status === 403 ? "signIn" : "genericError");
    setDetail(status === 401 || status === 403 ? "" : text);
  }

  async function onCheck() {
    if (!file) {
      setMessage("noFile");
      return;
    }
    setBusy(true);
    setMessage("");
    setDetail("");
    setReport(null);
    setUndone(false);
    try {
      const res = await previewCsv(file);
      if (res.status === 200) setRows(res.rows);
      else {
        setRows(null);
        fail(res.status, res.detail);
      }
    } catch {
      setRows(null);
      setMessage("genericError");
    } finally {
      setBusy(false);
    }
  }

  async function onSave() {
    if (!file || !canSave) return;
    setBusy(true);
    setMessage("");
    setDetail("");
    try {
      const res = await confirmCsv(file);
      if (res.status === 201 && res.report) setReport(res.report);
      else if (res.status === 400) {
        // The 400 body lists only the refused rows: merge them by row number.
        setRows((prev) => {
          const base = prev ?? [];
          const bad = new Map(res.rows.map((r) => [r.row, r]));
          const merged = base.map((r) => bad.get(r.row) ?? r);
          const known = new Set(base.map((r) => r.row));
          return merged.concat(res.rows.filter((r) => !known.has(r.row)));
        });
        setMessage("confirmRefused");
        setDetail(res.detail);
      } else fail(res.status, res.detail);
    } catch {
      setMessage("genericError");
    } finally {
      setBusy(false);
    }
  }

  async function onUndo() {
    if (!report || !window.confirm(t.undoConfirm)) return;
    setBusy(true);
    setMessage("");
    setDetail("");
    try {
      const res = await rollbackReport(report.id);
      if (res.status === 204) setUndone(true);
      else if (res.status === 401 || res.status === 403) fail(res.status, "");
      else {
        setMessage("undoFailed");
        setDetail(res.detail);
      }
    } catch {
      setMessage("undoFailed");
    } finally {
      setBusy(false);
    }
  }

  const statusText = (s: PreviewRow["status"]) =>
    s === "recognised"
      ? t.recognised
      : s === "inferred"
        ? t.inferred
        : t.notRecognised;

  return (
    <main className="mx-auto max-w-3xl space-y-6 p-4 sm:p-8">
      <h1 className="text-2xl font-bold">{t.title}</h1>
      <p>{t.intro}</p>

      <div role="alert" aria-live="assertive">
        {message !== "" && (
          <p className="rounded border border-red-700 p-3">
            {t[message]}
            {detail !== "" && ` ${detail}`}{" "}
            {message === "signIn" && (
              <Link href="/sign-in" className="underline">
                {t.signInLink}
              </Link>
            )}
          </p>
        )}
      </div>

      <div className="space-y-2">
        <label htmlFor="lab-file" className="block font-semibold">
          {t.fileLabel}
        </label>
        <input
          id="lab-file"
          type="file"
          accept=".csv,text/csv"
          aria-describedby="lab-file-help"
          onChange={(e) => {
            setFile(e.target.files?.[0] ?? null);
            setRows(null);
            setMessage("");
            setDetail("");
          }}
          className="block w-full text-sm"
        />
        <p id="lab-file-help" className="text-sm">
          {t.headerHelp}
        </p>
        <button type="button" className={button} disabled={busy} onClick={onCheck}>
          {busy && !report ? t.checking : t.check}
        </button>
      </div>

      {rows !== null && !report && (
        <section aria-labelledby="summary-heading" className="space-y-4">
          <h2
            id="summary-heading"
            tabIndex={-1}
            ref={summaryRef}
            className="text-lg font-semibold"
          >
            {t.summary
              .replace("{recognised}", String(rows.length - unrecognised.length))
              .replace("{total}", String(rows.length))}
          </h2>
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
                  <th scope="col">{t.colRow}</th>
                  <th scope="col">{t.colLoinc}</th>
                  <th scope="col">{t.colValue}</th>
                  <th scope="col">{t.colUnit}</th>
                  <th scope="col">{t.colStatus}</th>
                  <th scope="col">{t.colReason}</th>
                </tr>
              </thead>
              <tbody>
                {rows.map((r) => (
                  <tr key={r.row} className="border-t">
                    <th scope="row">{r.row}</th>
                    <td>{r.loinc_code}</td>
                    <td>{r.value ?? ""}</td>
                    <td>{r.unit}</td>
                    <td>{statusText(r.status)}</td>
                    <td>{r.reason}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {!canSave && (
            <p id="save-blocked" className="font-medium">
              {t.saveBlocked}
            </p>
          )}
          <button
            type="button"
            className={button}
            disabled={!canSave || busy}
            aria-describedby={canSave ? undefined : "save-blocked"}
            onClick={onSave}
          >
            {busy ? t.saving : t.save}
          </button>
        </section>
      )}

      {report && (
        <section aria-labelledby="saved-heading" className="space-y-3">
          <h2
            id="saved-heading"
            tabIndex={-1}
            ref={savedRef}
            className="text-lg font-semibold"
          >
            {undone ? t.undone : t.savedTitle}
          </h2>
          {!undone && (
            <>
              <p>{t.savedBody.replace("{id}", String(report.id))}</p>
              <p>
                {report.original_retained ? t.originalKept : t.originalNotKept}
              </p>
              <button
                type="button"
                className={button}
                disabled={busy}
                onClick={onUndo}
              >
                {t.undo}
              </button>
            </>
          )}
        </section>
      )}
    </main>
  );
}
