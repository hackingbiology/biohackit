// SPDX-License-Identifier: AGPL-3.0-or-later
// biohack.it — open-source biohacking platform
// Copyright (C) HackingBiology 2026 — https://biohack.it
// Full license text: https://www.gnu.org/licenses/agpl-3.0.html

// Client for the lab API documented in docs/api-labs.md (CSV import part).
// The browser session cookie plus the X-CSRFToken header authenticate it.

import { csrfToken } from "@/lib/allauth";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export type RowStatus = "recognised" | "not_recognised" | "inferred";

export interface RangeSource {
  name: string;
  version: string;
  licence: string;
  url: string;
  retrieved_at: string;
}

export interface Plausibility {
  status: "within" | "outside" | "not_checked";
  range_source: RangeSource | null;
}

export interface PreviewRow {
  row: number;
  status: RowStatus;
  reason: string;
  loinc_code: string;
  value: string | number | null;
  unit: string;
  plausibility: Plausibility | null;
}

export interface PreviewResult {
  status: number;
  rows: PreviewRow[];
  detail: string;
}

export interface ConfirmedReport {
  id: number;
  original_retained: boolean;
}

export interface ConfirmResult {
  status: number;
  rows: PreviewRow[];
  detail: string;
  report: ConfirmedReport | null;
}

export interface RollbackResult {
  status: number;
  detail: string;
}

async function readJson(res: Response): Promise<Record<string, unknown>> {
  try {
    const body: unknown = await res.json();
    return typeof body === "object" && body !== null
      ? (body as Record<string, unknown>)
      : {};
  } catch {
    return {};
  }
}

function request(
  method: "POST" | "DELETE",
  path: string,
  body?: FormData,
): Promise<Response> {
  return fetch(`${API_URL}${path}`, {
    method,
    credentials: "include",
    headers: { Accept: "application/json", "X-CSRFToken": csrfToken() },
    body,
  });
}

function rowsOf(body: Record<string, unknown>): PreviewRow[] {
  return Array.isArray(body.rows) ? (body.rows as PreviewRow[]) : [];
}

function detailOf(body: Record<string, unknown>): string {
  if (typeof body.detail === "string") return body.detail;
  for (const value of Object.values(body)) {
    if (typeof value === "string") return value;
    if (Array.isArray(value) && typeof value[0] === "string") return value[0];
  }
  return "";
}

export async function previewCsv(
  file: File,
  redactTerms?: string[],
): Promise<PreviewResult> {
  const form = new FormData();
  form.append("file", file);
  for (const term of redactTerms ?? []) form.append("redact_terms", term);
  const res = await request("POST", "/api/labs/imports/csv/preview/", form);
  const body = await readJson(res);
  return { status: res.status, rows: rowsOf(body), detail: detailOf(body) };
}

export async function confirmCsv(
  file: File,
  laboratory?: string,
): Promise<ConfirmResult> {
  const form = new FormData();
  form.append("file", file);
  if (laboratory) form.append("laboratory", laboratory);
  const res = await request("POST", "/api/labs/imports/csv/confirm/", form);
  const body = await readJson(res);
  const report =
    res.status === 201 && typeof body.id === "number"
      ? { id: body.id, original_retained: body.original_retained === true }
      : null;
  return {
    status: res.status,
    rows: rowsOf(body),
    detail: detailOf(body),
    report,
  };
}

/** DELETE answers 204 with no body when the import is rolled back. */
export async function rollbackReport(id: number): Promise<RollbackResult> {
  const res = await request("DELETE", `/api/labs/reports/${id}/`);
  const body = await readJson(res);
  return { status: res.status, detail: detailOf(body) };
}
