// SPDX-License-Identifier: AGPL-3.0-or-later
import { test, expect, jest, beforeEach } from "@jest/globals";
import "@testing-library/jest-dom/jest-globals";
import { render as plainRender, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { PathParamsContext } from "next/dist/shared/lib/hooks-client-context.shared-runtime";
import LabReportPage from "@/app/labs/reports/[id]/page";

// The page reads its id from the route; supply it through Next's own context.
function render(ui: React.ReactElement) {
  return plainRender(
    <PathParamsContext.Provider value={{ id: "9" }}>
      {ui}
    </PathParamsContext.Provider>,
  );
}

interface Reply {
  status: number;
  body: unknown;
}

const result = (id: number, extra: Record<string, unknown> = {}) => ({
  id,
  loinc_code: "0000-0",
  laboratory: "Lab A",
  method: "Method M",
  device: "",
  collected_at: "2026-01-02T03:04:05Z",
  reported_at: null,
  reported_value: "5.10",
  reported_unit: "xa/L",
  normalised_value: null,
  normalised_unit: "",
  validation_state: "entered",
  aggregation_eligible: false,
  plausibility: { status: "not_checked", range_source: null },
  ...extra,
});

let replies: Reply[] = [];
let fetchMock: jest.Mock<typeof fetch>;

beforeEach(() => {
  replies = [];
  document.cookie = "csrftoken=tok123";
  fetchMock = jest.fn(async () => {
    const r = replies.shift() ?? { status: 500, body: {} };
    return {
      status: r.status,
      json: async () => r.body,
    } as unknown as Response;
  }) as unknown as jest.Mock<typeof fetch>;
  global.fetch = fetchMock as unknown as typeof fetch;
});

function report(origin: string) {
  return {
    id: 9,
    origin,
    laboratory: "Lab A",
    original_retained: origin === "import",
    results: [
      result(1),
      result(2, {
        validation_state: "user_confirmed",
        aggregation_eligible: true,
        normalised_value: "5.1",
        normalised_unit: "ya/L",
        plausibility: {
          status: "outside",
          range_source: {
            name: "Source X",
            version: "1",
            licence: "CC0",
            url: "https://example.org/x",
            retrieved_at: "2026-01-01",
          },
        },
      }),
    ],
  };
}

test("a manual and a csv report show the same columns in words", async () => {
  // scenario: biomarkers-and-labs::typed-value-gets-the-same-treatment
  for (const origin of ["manual", "import"]) {
    replies = [{ status: 200, body: report(origin) }];
    const { unmount } = render(<LabReportPage />);
    const table = await screen.findByRole("table");
    const headers = within(table)
      .getAllByRole("columnheader")
      .map((h) => h.textContent);
    expect(headers).toEqual([
      "LOINC code",
      "Reported value",
      "Reported unit",
      "Normalised value",
      "Laboratory",
      "Method",
      "Device",
      "Collected at",
      "Reported at",
      "Validation state",
      "Used in aggregations",
      "Range check",
    ]);
    const rows = within(table).getAllByRole("row");
    expect(rows).toHaveLength(3);
    expect(rows[1]).toHaveTextContent("5.10");
    expect(rows[1]).toHaveTextContent("Entered, not yet confirmed");
    expect(rows[1]).toHaveTextContent("No, not counted in aggregations");
    expect(rows[1]).toHaveTextContent("Not checked");
    expect(rows[1]).toHaveTextContent("Lab A");
    expect(rows[2]).toHaveTextContent("Confirmed by the user");
    expect(rows[2]).toHaveTextContent("Yes, counted in aggregations");
    expect(rows[2]).toHaveTextContent("5.1 ya/L");
    expect(rows[2]).toHaveTextContent("Outside the cited reference range");
    expect(
      within(rows[2]).getByRole("link", { name: /Source X/ }),
    ).toHaveAttribute("href", "https://example.org/x");
    expect(
      screen.getByText(origin === "manual" ? /Typed by hand/ : /Imported from a CSV/),
    ).toBeInTheDocument();
    unmount();
  }
});

test("a 404 says Report not found", async () => {
  // scenario: biomarkers-and-labs::typed-value-gets-the-same-treatment
  replies = [{ status: 404, body: { detail: "Not found." } }];
  render(<LabReportPage />);
  expect(await screen.findByText("Report not found")).toBeInTheDocument();
  expect(screen.queryByText(/another user/i)).toBeNull();
});

test("undo calls DELETE only after confirm", async () => {
  // scenario: biomarkers-and-labs::typed-value-gets-the-same-treatment
  replies = [
    { status: 200, body: report("import") },
    { status: 204, body: {} },
  ];
  const confirm = jest.spyOn(window, "confirm");
  confirm.mockReturnValueOnce(false).mockReturnValueOnce(true);
  const user = userEvent.setup();
  render(<LabReportPage />);
  const undo = await screen.findByRole("button", { name: "Undo this report" });
  await user.click(undo);
  expect(fetchMock).toHaveBeenCalledTimes(1);
  await user.click(undo);
  const heading = await screen.findByRole("heading", { name: /Report undone/ });
  expect(heading).toHaveFocus();
  const [url, init] = fetchMock.mock.calls[1];
  expect(String(url)).toContain("/api/labs/reports/9/");
  expect(init?.method).toBe("DELETE");
  confirm.mockRestore();
});

test("a typed report has no undo button and says why", async () => {
  // scenario: biomarkers-and-labs::typed-value-gets-the-same-treatment
  replies = [{ status: 200, body: report("manual") }];
  render(<LabReportPage />);
  await screen.findByRole("table");
  expect(screen.queryByRole("button", { name: "Undo this report" })).toBeNull();
  expect(screen.getByText(/cannot be undone/)).toBeInTheDocument();
});

test("an unexpected origin is shown as unknown", async () => {
  // scenario: biomarkers-and-labs::typed-value-gets-the-same-treatment
  replies = [{ status: 200, body: report("csv") }];
  render(<LabReportPage />);
  await screen.findByRole("table");
  expect(screen.getByText(/Unknown origin: csv/)).toBeInTheDocument();
  expect(screen.queryByText(/Imported from a CSV/)).toBeNull();
});

test("a 409 on undo says a typed report cannot be undone", async () => {
  // scenario: biomarkers-and-labs::typed-value-gets-the-same-treatment
  replies = [
    { status: 200, body: report("import") },
    { status: 409, body: { detail: "x" } },
  ];
  jest.spyOn(window, "confirm").mockReturnValue(true);
  const user = userEvent.setup();
  render(<LabReportPage />);
  await user.click(await screen.findByRole("button", { name: "Undo this report" }));
  expect(await screen.findByText(/typed by hand\. It is still saved/)).toBeInTheDocument();
});
