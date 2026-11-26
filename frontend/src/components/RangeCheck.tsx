// SPDX-License-Identifier: AGPL-3.0-or-later
// biohack.it — open-source biohacking platform
// Copyright (C) HackingBiology 2026 — https://biohack.it
// Full license text: https://www.gnu.org/licenses/agpl-3.0.html

import type { Plausibility } from "@/lib/labs";
import type { LabImportStrings } from "@/lib/i18n";

type Words = Pick<
  LabImportStrings,
  "rangeWithin" | "rangeOutside" | "rangeNotChecked" | "rangeSource"
>;

/** The 'Range check' cell: the status in words plus the range source link. */
export function RangeCheck({
  plausibility,
  t,
}: {
  plausibility: Plausibility | null;
  t: Words;
}) {
  const text =
    plausibility?.status === "within"
      ? t.rangeWithin
      : plausibility?.status === "outside"
        ? t.rangeOutside
        : t.rangeNotChecked;
  return (
    <>
      {text}
      {plausibility?.range_source && (
        <>
          {" "}
          <a href={plausibility.range_source.url} className="underline">
            {t.rangeSource} {plausibility.range_source.name}
          </a>
        </>
      )}
    </>
  );
}
