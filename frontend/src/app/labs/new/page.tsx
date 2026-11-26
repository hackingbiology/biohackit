// SPDX-License-Identifier: AGPL-3.0-or-later
// biohack.it — open-source biohacking platform
// Copyright (C) HackingBiology 2026 — https://biohack.it
// Full license text: https://www.gnu.org/licenses/agpl-3.0.html

"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useRef, useState } from "react";
import {
  createReport,
  withOffset,
  type FieldErrors,
  type ManualResultInput,
} from "@/lib/labs";
import { labStrings, pickLocale } from "@/lib/i18n";

const button =
  "inline-flex items-center justify-center rounded-lg bg-slate-900 dark:bg-slate-100 px-5 py-3 text-sm font-semibold text-white dark:text-slate-900 disabled:opacity-50";
const input = "block w-full rounded border border-slate-500 p-2 text-sm";

type Field = keyof ManualResultInput;
type Draft = Record<Field, string> & { key: number };

const REQUIRED: Field[] = ["loinc_code", "reported_value", "reported_unit"];
const OPTIONAL: Field[] = ["laboratory", "method", "device"];
const DATES: Field[] = ["collected_at", "reported_at"];

const blank = (key: number): Draft => ({
  key,
  loinc_code: "",
  reported_value: "",
  reported_unit: "",
  laboratory: "",
  method: "",
  device: "",
  collected_at: "",
  reported_at: "",
});

function toInput(d: Draft): ManualResultInput {
  const out: ManualResultInput = {
    loinc_code: d.loinc_code.trim(),
    reported_value: d.reported_value,
    reported_unit: d.reported_unit.trim(),
  };
  for (const f of OPTIONAL) if (d[f].trim()) out[f] = d[f].trim();
  for (const f of DATES) if (d[f]) out[f] = withOffset(d[f]);
  return out;
}

export default function LabNewPage() {
  const router = useRouter();
  const t =
    labStrings[
      pickLocale(
        typeof document === "undefined"
          ? undefined
          : document.documentElement.lang,
      )
    ];
  const [laboratory, setLaboratory] = useState("");
  const [drafts, setDrafts] = useState<Draft[]>([blank(0)]);
  const [nextKey, setNextKey] = useState(1);
  const [errors, setErrors] = useState<FieldErrors>({});
  const [summary, setSummary] = useState<"" | "fix" | "signIn" | "generic">("");
  const [reportErrors, setReportErrors] = useState<Record<string, string[]>>({});
  const [detail, setDetail] = useState("");
  const [busy, setBusy] = useState(false);
  const [removed, setRemoved] = useState<{ n: number; at: number; count: number } | null>(null);
  const addRef = useRef<HTMLButtonElement>(null);

  const fieldLabel: Record<Field, string> = {
    loinc_code: t.loincCode,
    reported_value: t.reportedValue,
    reported_unit: t.reportedUnit,
    laboratory: t.laboratory,
    method: t.method,
    device: t.device,
    collected_at: t.collectedAt,
    reported_at: t.reportedAt,
  };

  function edit(index: number, field: Field, value: string) {
    setDrafts((prev) =>
      prev.map((d, i) => (i === index ? { ...d, [field]: value } : d)),
    );
  }

  function addRow() {
    setDrafts((prev) => [...prev, blank(nextKey)]);
    setNextKey(nextKey + 1);
    setErrors({});
  }

  function removeRow(index: number) {
    setDrafts((prev) => prev.filter((_, i) => i !== index));
    setErrors({});
    setRemoved((prev) => ({ n: index + 1, at: index, count: (prev?.count ?? 0) + 1 }));
  }

  // After a removal the focused Remove button is gone: move focus to the first
  // input of the row now at that index, else the previous row, else "Add".
  useEffect(() => {
    if (removed === null) return;
    const target =
      document.getElementById(`r${removed.at}-loinc_code`) ??
      document.getElementById(`r${removed.at - 1}-loinc_code`) ??
      addRef.current;
    target?.focus();
  }, [removed]);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    const missing: FieldErrors = {};
    drafts.forEach((d, i) => {
      for (const f of REQUIRED) {
        if (d[f].trim() === "") missing[i] = { ...missing[i], [f]: [t.required] };
      }
    });
    if (Object.keys(missing).length > 0) {
      setErrors(missing);
      setSummary("fix");
      setDetail("");
      return;
    }
    setBusy(true);
    setErrors({});
    setReportErrors({});
    setSummary("");
    setDetail("");
    try {
      const res = await createReport(laboratory.trim(), drafts.map(toInput));
      if (res.status === 201 && res.id !== null) {
        router.push(`/labs/reports/${res.id}`);
        return;
      }
      if (res.status === 400) {
        setErrors(res.errors);
        setReportErrors(res.reportErrors);
        setSummary("fix");
        setDetail(
          [
            ...(res.errors[-1]?.results ?? []),
            ...(res.reportErrors.detail ?? []),
          ].join(" "),
        );
      } else if (res.status === 401 || res.status === 403) setSummary("signIn");
      else {
        setSummary("generic");
        setDetail(res.detail);
      }
    } catch {
      setSummary("generic");
    } finally {
      setBusy(false);
    }
  }

  const messageText =
    summary === "fix"
      ? t.fixErrors
      : summary === "signIn"
        ? t.signIn
        : summary === "generic"
          ? t.genericError
          : "";

  const labErrs = reportErrors.laboratory ?? [];
  const known: string[] = [...REQUIRED, ...OPTIONAL, ...DATES];

  function rowErrors(i: number): string[] {
    return Object.entries(errors[i] ?? {})
      .filter(([f]) => !known.includes(f))
      .flatMap(([, msgs]) => msgs);
  }

  function renderField(d: Draft, i: number, f: Field, type = "text") {
    const id = `r${i}-${f}`;
    const errs = errors[i]?.[f] ?? [];
    const required = REQUIRED.includes(f);
    return (
      <div key={f} className="space-y-1">
        <label htmlFor={id} className="block text-sm font-semibold">
          {fieldLabel[f]}
        </label>
        <input
          id={id}
          type={type}
          value={d[f]}
          required={required}
          aria-required={required}
          aria-invalid={errs.length > 0}
          aria-describedby={errs.length > 0 ? `${id}-err` : undefined}
          autoComplete="off"
          inputMode={f === "reported_value" ? "decimal" : undefined}
          onChange={(e) => edit(i, f, e.target.value)}
          className={input}
        />
        {errs.length > 0 && (
          <p id={`${id}-err`} className="text-sm font-medium text-red-800 dark:text-red-300">
            <span aria-hidden="true">⚠ </span>
            {errs.join(" ")}
          </p>
        )}
      </div>
    );
  }

  return (
    <main className="mx-auto max-w-3xl space-y-6 p-4 sm:p-8">
      <h1 className="text-2xl font-bold">{t.newTitle}</h1>
      <p>{t.newIntro}</p>
      <p>
        <Link href="/labs/import" className="underline">
          {t.importLink}
        </Link>
      </p>

      <div role="alert" aria-live="assertive">
        {messageText !== "" && (
          <p className="rounded border border-red-700 p-3">
            {messageText}
            {detail !== "" && ` ${detail}`}{" "}
            {summary === "signIn" && (
              <Link href="/sign-in" className="underline">
                {t.signInLink}
              </Link>
            )}
          </p>
        )}
      </div>

      <p role="status" aria-live="polite">
        {removed !== null && (
          <span key={removed.count}>
            {t.rowRemoved.replace("{n}", String(removed.n))}
          </span>
        )}
      </p>

      <form onSubmit={onSubmit} noValidate className="space-y-6">
        <div className="space-y-1">
          <label htmlFor="report-laboratory" className="block font-semibold">
            {t.reportLaboratory}
          </label>
          <input
            id="report-laboratory"
            type="text"
            aria-invalid={labErrs.length > 0}
            aria-describedby={labErrs.length > 0 ? "report-laboratory-err" : undefined}
            value={laboratory}
            onChange={(e) => setLaboratory(e.target.value)}
            className={input}
          />
          {labErrs.length > 0 && (
            <p id="report-laboratory-err" className="text-sm font-medium text-red-800 dark:text-red-300">
              <span aria-hidden="true">⚠ </span>
              {labErrs.join(" ")}
            </p>
          )}
        </div>
        <p id="date-help" className="text-sm">
          {t.dateHelp}
        </p>

        {drafts.map((d, i) => (
          <fieldset
            key={d.key}
            aria-describedby={rowErrors(i).length > 0 ? `r${i}-row-err` : undefined}
            className="space-y-3 rounded border border-slate-500 p-3">
            <legend className="px-1 font-semibold">
              {t.resultHeading.replace("{n}", String(i + 1))}
            </legend>
            {rowErrors(i).length > 0 && (
              <p id={`r${i}-row-err`} className="text-sm font-medium text-red-800 dark:text-red-300">
                <span aria-hidden="true">⚠ </span>
                {t.rowProblem} {rowErrors(i).join(" ")}
              </p>
            )}
            {REQUIRED.map((f) => renderField(d, i, f))}
            {OPTIONAL.map((f) => renderField(d, i, f))}
            {DATES.map((f) => renderField(d, i, f, "datetime-local"))}
            {drafts.length > 1 && (
              <button type="button" className={button} onClick={() => removeRow(i)}>
                {t.removeRow.replace("{n}", String(i + 1))}
              </button>
            )}
          </fieldset>
        ))}

        <div className="flex flex-wrap gap-3">
          <button type="button" ref={addRef} className={button} onClick={addRow}>
            {t.addRow}
          </button>
          <button type="submit" className={button} disabled={busy}>
            {busy ? t.submitting : t.submit}
          </button>
        </div>
      </form>
    </main>
  );
}
