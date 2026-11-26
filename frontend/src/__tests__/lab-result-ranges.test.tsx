// SPDX-License-Identifier: AGPL-3.0-or-later
import { test, expect, jest, beforeEach } from "@jest/globals";
import "@testing-library/jest-dom/jest-globals";
import { render as plainRender, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { PathParamsContext } from "next/dist/shared/lib/hooks-client-context.shared-runtime";
import LabReportPage from "@/app/labs/reports/[id]/page";

function render(ui: React.ReactElement) {
  return plainRender(
    <PathParamsContext.Provider value={{ id: "9" }}>{ui}</PathParamsContext.Provider>,
  );
}

const result = (id: number) => ({
  id,
  loinc_code: `code-${id}`,
  laboratory: "Lab A",
  method: "",
  device: "",
  collected_at: null,
  reported_at: null,
  reported_value: "5.10",
  reported_unit: "xa/L",
  normalised_value: null,
  normalised_unit: "",
  validation_state: "entered",
  aggregation_eligible: false,
  plausibility: { status: "not_checked", range_source: null },
});

const report = (ids: number[]) => ({
  id: 9,
  origin: "manual",
  laboratory: "Lab A",
  original_retained: false,
  results: ids.map(result),
});

const refSource = { name: "Ref Source", version: "2", url: "https://example.org/ref" };
const optSource = { name: "Opt Source", version: "1", url: "https://example.org/opt" };

const ranges = (extra: Record<string, unknown> = {}) => ({
  result_id: 1,
  reported_value: "5.10",
  reported_unit: "xa/L",
  reference_range: {
    status: "inside",
    low: "3.0",
    high: "6.0",
    unit: "xa/L",
    source: refSource,
    lab: "",
    method: "",
    population: "adults",
    evidence_grade: "B",
  },
  optimal_range: {
    status: "above",
    low: "3.5",
    high: "4.5",
    unit: "xa/L",
    source: optSource,
    population: "healthy adults",
    endpoint: "all-cause mortality",
    evidence_grade: "A",
    last_reviewed: "2026-05-01",
  },
  safety_threshold: { status: "no_range" },
  comparison_value: "5.10",
  comparison_unit: "xa/L",
  converted: false,
  conversion_source: null,
  ...extra,
});

type Reply = { status: number; body: unknown };
let byResult: Record<number, Reply> = {};
let reportReply: Reply;

beforeEach(() => {
  document.cookie = "csrftoken=tok123";
  byResult = {};
  reportReply = { status: 200, body: report([1]) };
  global.fetch = jest.fn(async (url: unknown) => {
    const u = String(url);
    const m = u.match(/results\/(\d+)\/ranges\//);
    const r = m ? (byResult[Number(m[1])] ?? { status: 500, body: {} }) : reportReply;
    return { status: r.status, json: async () => r.body } as unknown as Response;
  }) as unknown as typeof fetch;
});

async function section(title: string, index = 0) {
  const headings = await screen.findAllByRole("heading", { name: title });
  const region = headings[index].closest("section");
  if (!region) throw new Error("no section");
  return region as HTMLElement;
}

test("reference and optimal show different words in separate sections", async () => {
  // scenario: biomarkers-and-labs::a-value-near-the-optimal-edge-but-within-reference
  byResult[1] = { status: 200, body: ranges() };
  render(<LabReportPage />);
  const ref = await section("Laboratory reference range");
  const opt = await section("Longevity-optimal range");
  expect(within(ref).getByText("Inside the range")).toBeInTheDocument();
  expect(within(ref).queryByText("Above the range")).toBeNull();
  expect(within(opt).getByText("Above the range")).toBeInTheDocument();
  expect(within(opt).queryByText("Inside the range")).toBeNull();
  expect(within(opt).getByText(/From 3\.5 xa\/L to 4\.5 xa\/L/)).toBeInTheDocument();
  expect(within(opt).getByRole("link", { name: "Opt Source 1" })).toHaveAttribute(
    "href",
    "https://example.org/opt",
  );
  expect(await section("Safety threshold")).toHaveTextContent("No range available");
});

test("opening About this optimal range shows its provenance", async () => {
  // scenario: biomarkers-and-labs::inspecting-an-optimal-range
  byResult[1] = { status: 200, body: ranges() };
  render(<LabReportPage />);
  const opt = await section("Longevity-optimal range");
  await userEvent.click(within(opt).getByText("About this optimal range"));
  const details = opt.querySelector("details") as HTMLDetailsElement;
  expect(details.open).toBe(true);
  expect(details).toHaveTextContent("Source: Opt Source 1");
  expect(details).toHaveTextContent("Population: healthy adults");
  expect(details).toHaveTextContent("Endpoint: all-cause mortality");
  expect(details).toHaveTextContent("Evidence grade: A");
  expect(details).toHaveTextContent("Last reviewed: 2026-05-01");
});

test("no optimal range shows no bounds and no provenance control", async () => {
  byResult[1] = {
    status: 200,
    body: ranges({ optimal_range: { status: "no_range" } }),
  };
  render(<LabReportPage />);
  const opt = await section("Longevity-optimal range");
  expect(within(opt).getByText("No optimal range available")).toBeInTheDocument();
  expect(within(opt).queryByText(/From /)).toBeNull();
  expect(screen.queryByText("About this optimal range")).toBeNull();
});

test("several safety thresholds are reported as none chosen", async () => {
  byResult[1] = {
    status: 200,
    body: ranges({
      safety_threshold: { status: "no_range", reason: "ambiguous_several_thresholds" },
    }),
  };
  render(<LabReportPage />);
  const safety = await section("Safety threshold");
  expect(safety).toHaveTextContent("Several thresholds exist, none chosen");
});

test("not comparable is said in words and keeps bounds, source and provenance", async () => {
  const base = ranges();
  byResult[1] = {
    status: 200,
    body: ranges({
      reference_range: {
        ...base.reference_range,
        status: "not_comparable",
        reason: "no_value_in_analyte_unit",
      },
      optimal_range: {
        ...base.optimal_range,
        status: "not_comparable",
        reason: "no_value_in_analyte_unit",
      },
    }),
  };
  render(<LabReportPage />);
  const ref = await section("Laboratory reference range");
  expect(ref).toHaveTextContent("Cannot compare: no value in the analyte's unit");
  expect(within(ref).getByText(/From 3\.0 xa\/L to 6\.0 xa\/L/)).toBeInTheDocument();
  expect(within(ref).getByRole("link", { name: "Ref Source 2" })).toBeInTheDocument();
  const opt = await section("Longevity-optimal range");
  expect(opt).toHaveTextContent("Cannot compare: no value in the analyte's unit");
  expect(within(opt).getByText("About this optimal range")).toBeInTheDocument();
});

test("a converted comparison names the stored value and its source", async () => {
  byResult[1] = {
    status: 200,
    body: ranges({
      converted: true,
      comparison_value: "5.1",
      comparison_unit: "ya/L",
      conversion_source: { name: "Conv Source", version: "3", url: "https://example.org/c" },
    }),
  };
  render(<LabReportPage />);
  expect(
    await screen.findByText(
      "Compared using the stored normalised value 5.1 ya/L (conversion source: Conv Source 3)",
    ),
  ).toBeInTheDocument();
});

test("a null bound is worded as no limit", async () => {
  byResult[1] = {
    status: 200,
    body: ranges({
      reference_range: {
        status: "inside",
        low: null,
        high: "6.0",
        unit: "xa/L",
        source: refSource,
      },
    }),
  };
  render(<LabReportPage />);
  const ref = await section("Laboratory reference range");
  expect(ref).toHaveTextContent("From no lower limit to 6.0 xa/L");
});

test("a failed ranges call for one result keeps the others", async () => {
  reportReply = { status: 200, body: report([1, 2]) };
  byResult[1] = { status: 404, body: {} };
  byResult[2] = { status: 200, body: ranges() };
  render(<LabReportPage />);
  expect(await screen.findByText("Ranges for this result were not found.")).toBeInTheDocument();
  const ref = await section("Laboratory reference range");
  expect(within(ref).getByText("Inside the range")).toBeInTheDocument();
  expect(screen.getByRole("heading", { name: "Lab report 9" })).toBeInTheDocument();
});

test("a source url that is not http(s) is not a link", async () => {
  byResult[1] = {
    status: 200,
    body: ranges({
      reference_range: {
        status: "inside",
        low: "3.0",
        high: "6.0",
        unit: "xa/L",
        source: { name: "Bad Source", version: "1", url: "javascript:alert(1)" },
      },
    }),
  };
  render(<LabReportPage />);
  const ref = await section("Laboratory reference range");
  expect(within(ref).getByText(/Bad Source 1/)).toBeInTheDocument();
  expect(within(ref).queryByRole("link")).toBeNull();
  expect(ref.querySelector("a")).toBeNull();
});
