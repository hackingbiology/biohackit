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
  method: "GET" | "POST" | "DELETE" | "PATCH",
  path: string,
  body?: FormData | string,
): Promise<Response> {
  const headers: Record<string, string> = {
    Accept: "application/json",
    "X-CSRFToken": csrfToken(),
  };
  if (typeof body === "string") headers["Content-Type"] = "application/json";
  return fetch(`${API_URL}${path}`, {
    method,
    credentials: "include",
    headers,
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

/** One typed result. reported_value is a string and is sent unchanged. */
export interface ManualResultInput {
  loinc_code: string;
  reported_value: string;
  reported_unit: string;
  laboratory?: string;
  method?: string;
  device?: string;
  collected_at?: string;
  reported_at?: string;
}

/** Field messages by result index; index -1 holds messages about the list itself. */
export type FieldErrors = Record<number, Record<string, string[]>>;

export interface CreateResult {
  status: number;
  id: number | null;
  errors: FieldErrors;
  /** Messages about report-level fields such as laboratory. */
  reportErrors: Record<string, string[]>;
  detail: string;
}

function messages(value: unknown): string[] {
  if (typeof value === "string") return [value];
  return Array.isArray(value)
    ? value.filter((m): m is string => typeof m === "string")
    : [];
}

/** Reads {results: {<index>: {<field>: [msg]}}} or {results: [msg]}. */
function fieldErrorsOf(body: Record<string, unknown>): FieldErrors {
  const out: FieldErrors = {};
  const results = body.results;
  if (Array.isArray(results)) {
    const list = messages(results);
    if (list.length > 0) out[-1] = { results: list };
  } else if (typeof results === "object" && results !== null) {
    for (const [index, fields] of Object.entries(results)) {
      if (typeof fields !== "object" || fields === null) continue;
      const byField: Record<string, string[]> = {};
      for (const [field, msg] of Object.entries(fields)) {
        byField[field] = messages(msg);
      }
      out[Number(index)] = byField;
    }
  }
  return out;
}

/** Reads the report-level keys of a 400 body (everything except results). */
function reportErrorsOf(body: Record<string, unknown>): Record<string, string[]> {
  const out: Record<string, string[]> = {};
  for (const [key, value] of Object.entries(body)) {
    if (key === "results") continue;
    const list = messages(value);
    if (list.length > 0) out[key] = list;
  }
  return out;
}

export async function createReport(
  laboratory: string,
  results: ManualResultInput[],
): Promise<CreateResult> {
  const payload = laboratory ? { laboratory, results } : { results };
  const res = await request(
    "POST",
    "/api/labs/reports/",
    JSON.stringify(payload),
  );
  const body = await readJson(res);
  return {
    status: res.status,
    id: res.status === 201 && typeof body.id === "number" ? body.id : null,
    errors: res.status === 400 ? fieldErrorsOf(body) : {},
    reportErrors: res.status === 400 ? reportErrorsOf(body) : {},
    detail: detailOf(body),
  };
}

export interface ReportResult {
  id: number;
  loinc_code: string;
  laboratory: string;
  method: string;
  device: string;
  collected_at: string | null;
  reported_at: string | null;
  reported_value: string;
  reported_unit: string;
  normalised_value: string | null;
  normalised_unit: string;
  validation_state: string;
  aggregation_eligible: boolean;
  plausibility: Plausibility | null;
}

export interface StoredReport {
  id: number;
  origin: string;
  laboratory: string;
  original_retained: boolean;
  results: ReportResult[];
}

export interface FetchReportResult {
  status: number;
  report: StoredReport | null;
}

export async function fetchReport(id: string): Promise<FetchReportResult> {
  const res = await request(
    "GET",
    `/api/labs/reports/${encodeURIComponent(id)}/`,
  );
  const body = await readJson(res);
  const ok = res.status === 200 && Array.isArray(body.results);
  return {
    status: res.status,
    report: ok ? (body as unknown as StoredReport) : null,
  };
}

export type RangeStatus =
  | "inside"
  | "below"
  | "above"
  | "no_range"
  | "not_comparable";

export interface RangeSourceRef {
  name?: string;
  version?: string;
  url?: string;
}

/** One of the three ranges; every field except status may be absent. */
export interface RangeObject {
  status: RangeStatus;
  reason?: string;
  low?: string | null;
  high?: string | null;
  unit?: string;
  source?: RangeSourceRef | null;
  lab?: string;
  method?: string;
  population?: string;
  endpoint?: string;
  evidence_grade?: string;
  last_reviewed?: string;
}

export interface ResultRanges {
  result_id?: number;
  reported_value?: string;
  reported_unit?: string;
  reference_range?: RangeObject | null;
  optimal_range?: RangeObject | null;
  safety_threshold?: RangeObject | null;
  comparison_value?: string | null;
  comparison_unit?: string;
  converted?: boolean;
  conversion_source?: RangeSourceRef | null;
}

export type FetchRangesResult =
  | { kind: "ok"; ranges: ResultRanges }
  | { kind: "not_found" | "unauthorised" | "error" };

/** Placement of one stored result against its three ranges (docs/api-labs.md). */
export async function fetchResultRanges(id: number): Promise<FetchRangesResult> {
  const res = await request("GET", `/api/labs/results/${id}/ranges/`);
  if (res.status === 404) return { kind: "not_found" };
  if (res.status === 401 || res.status === 403) return { kind: "unauthorised" };
  const body = await readJson(res);
  if (res.status !== 200) return { kind: "error" };
  return { kind: "ok", ranges: body as ResultRanges };
}

/** A datetime-local value read as browser-local time, with its UTC offset. */
export function withOffset(local: string): string {
  const date = new Date(local);
  const offset = -date.getTimezoneOffset();
  const sign = offset < 0 ? "-" : "+";
  const pad = (n: number) => String(Math.floor(Math.abs(n))).padStart(2, "0");
  const base = local.length === 16 ? `${local}:00` : local;
  return `${base}${sign}${pad(offset / 60)}:${pad(offset % 60)}`;
}

export type OwnerValidationState = "user_confirmed" | "disputed" | "retracted";

export type ValidationOutcome =
  | { kind: "ok"; result: ReportResult }
  | { kind: "invalid"; detail: string }
  | { kind: "not_found" | "unauthorised" | "error" };

/** Owner changes one result's validation state (docs/api-labs.md). */
export async function setValidationState(
  id: number,
  state: OwnerValidationState,
): Promise<ValidationOutcome> {
  const res = await request(
    "PATCH",
    `/api/labs/results/${id}/validation/`,
    JSON.stringify({ validation_state: state }),
  );
  if (res.status === 404) return { kind: "not_found" };
  if (res.status === 401 || res.status === 403) return { kind: "unauthorised" };
  const body = await readJson(res);
  if (res.status === 400) {
    const list = messages(body.validation_state);
    return { kind: "invalid", detail: list[0] ?? detailOf(body) };
  }
  if (res.status !== 200 || typeof body.id !== "number") return { kind: "error" };
  return { kind: "ok", result: body as unknown as ReportResult };
}
