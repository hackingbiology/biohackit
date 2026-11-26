// SPDX-License-Identifier: AGPL-3.0-or-later
// biohack.it — open-source biohacking platform
// Copyright (C) HackingBiology 2026 — https://biohack.it
// Full license text: https://www.gnu.org/licenses/agpl-3.0.html

"use client";

// One stored result against its three ranges (docs/api-labs.md, GET
// /api/labs/results/<id>/ranges/). The ranges are shown separately and never
// merged. Every number shown is a string from the API; nothing is computed here.

import { useEffect, useId, useState } from "react";
import {
  fetchResultRanges,
  type RangeObject,
  type RangeSourceRef,
  type ResultRanges as Ranges,
} from "@/lib/labs";
import type { LabStrings } from "@/lib/i18n";

type Load = "loading" | "ok" | "notFound" | "signIn" | "error";

function isHttpUrl(url: string | undefined): url is string {
  return typeof url === "string" && /^https?:\/\/\S+$/i.test(url);
}

function sourceName(source: RangeSourceRef | null | undefined): string {
  if (!source || !source.name) return "";
  return source.version ? `${source.name} ${source.version}` : source.name;
}

function present(v: string | null | undefined): v is string {
  return typeof v === "string" && v !== "";
}

/** Bounds, source and provenance are shown whenever the API sent a bound. */
function hasBounds(range: RangeObject | null | undefined): boolean {
  return !!range && (present(range.low) || present(range.high));
}

function statusText(range: RangeObject | null | undefined, t: LabStrings): string {
  if (range?.status === "not_comparable") return t.statusNotComparable;
  if (hasBounds(range)) {
    if (range?.status === "inside") return t.statusInside;
    if (range?.status === "below") return t.statusBelow;
    if (range?.status === "above") return t.statusAbove;
  }
  if (range?.reason === "ambiguous_several_thresholds") return t.statusAmbiguous;
  return t.statusNoRange;
}

function SourceLine({
  source,
  t,
}: {
  source: RangeSourceRef | null | undefined;
  t: LabStrings;
}) {
  const name = sourceName(source);
  return (
    <p>
      {t.sourceLabel}{" "}
      {name === "" ? (
        t.notGiven
      ) : isHttpUrl(source?.url) ? (
        <a href={source.url} className="underline" rel="noopener noreferrer">
          {name}
        </a>
      ) : (
        name
      )}
    </p>
  );
}

function OptimalDetails({ range, t }: { range: RangeObject; t: LabStrings }) {
  return (
    <details>
      <summary className="cursor-pointer underline">{t.aboutOptimal}</summary>
      <ul className="mt-1 space-y-1">
        <li>
          {t.sourceLabel} {sourceName(range.source) || t.notGiven}
        </li>
        <li>
          {t.populationLabel} {range.population || t.notGiven}
        </li>
        <li>
          {t.endpointLabel} {range.endpoint || t.notGiven}
        </li>
        <li>
          {t.evidenceLabel} {range.evidence_grade || t.notGiven}
        </li>
        <li>
          {t.reviewedLabel} {range.last_reviewed || t.notGiven}
        </li>
      </ul>
    </details>
  );
}

function RangeSection({
  title,
  range,
  kind,
  t,
}: {
  title: string;
  range: RangeObject | null | undefined;
  kind: "reference" | "optimal" | "safety";
  t: LabStrings;
}) {
  const headingId = useId();
  const shown = hasBounds(range);
  const status =
    kind === "optimal" && !shown && range?.status === "no_range"
      ? t.noOptimal
      : statusText(range, t);
  const unit = range?.unit ? ` ${range.unit}` : "";
  return (
    <section aria-labelledby={headingId} className="rounded border p-3">
      <h4 id={headingId} className="font-semibold">
        {title}
      </h4>
      <p>{status}</p>
      {shown && range && (
        <>
          <p>
            {t.boundsLine
              .replace("{low}", present(range.low) ? `${range.low}${unit}` : t.noLowerLimit)
              .replace("{high}", present(range.high) ? `${range.high}${unit}` : t.noUpperLimit)}
          </p>
          <SourceLine source={range.source} t={t} />
          {kind === "optimal" && <OptimalDetails range={range} t={t} />}
        </>
      )}
    </section>
  );
}

export function ResultRanges({
  resultId,
  loinc,
  value,
  unit,
  t,
}: {
  resultId: number;
  loinc: string;
  value: string;
  unit: string;
  t: LabStrings;
}) {
  const [load, setLoad] = useState<Load>("loading");
  const [ranges, setRanges] = useState<Ranges | null>(null);

  useEffect(() => {
    let live = true;
    fetchResultRanges(resultId)
      .then((res) => {
        if (!live) return;
        if (res.kind === "ok") {
          setRanges(res.ranges);
          setLoad("ok");
        } else {
          setLoad(
            res.kind === "not_found"
              ? "notFound"
              : res.kind === "unauthorised"
                ? "signIn"
                : "error",
          );
        }
      })
      .catch(() => live && setLoad("error"));
    return () => {
      live = false;
    };
  }, [resultId]);

  const message =
    load === "loading"
      ? t.rangesLoading
      : load === "notFound"
        ? t.rangesNotFound
        : load === "signIn"
          ? t.rangesSignIn
          : load === "error"
            ? t.rangesError
            : "";

  return (
    <div className="space-y-2">
      <h3 className="font-semibold">
        {t.compareFor
          .replace("{loinc}", loinc)
          .replace("{value}", value)
          .replace("{unit}", unit)}
      </h3>
      <div role="status" aria-live="polite">
        {message !== "" && <p>{message}</p>}
      </div>
      {load === "ok" && ranges && (
        <div className="grid gap-3 sm:grid-cols-3">
          <RangeSection title={t.rangeReference} range={ranges.reference_range} kind="reference" t={t} />
          <RangeSection title={t.rangeOptimal} range={ranges.optimal_range} kind="optimal" t={t} />
          <RangeSection title={t.rangeSafety} range={ranges.safety_threshold} kind="safety" t={t} />
          {ranges.converted === true && (
            <p className="sm:col-span-3">
              {t.convertedLine
                .replace("{value}", ranges.comparison_value ?? "")
                .replace("{unit}", ranges.comparison_unit ?? "")
                .replace("{source}", sourceName(ranges.conversion_source) || t.notGiven)}
            </p>
          )}
        </div>
      )}
    </div>
  );
}
