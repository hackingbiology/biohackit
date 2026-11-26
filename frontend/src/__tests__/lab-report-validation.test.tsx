// SPDX-License-Identifier: AGPL-3.0-or-later
import { test, expect, jest, beforeEach } from "@jest/globals";
import "@testing-library/jest-dom/jest-globals";
import { render as plainRender, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { PathParamsContext } from "next/dist/shared/lib/hooks-client-context.shared-runtime";
import LabReportPage from "@/app/labs/reports/[id]/page";

function render(ui: React.ReactElement) {
  return plainRender(
    <PathParamsContext.Provider value={{ id: "9" }}>{ui}</PathParamsContext.Provider>,
  );
}

interface Reply {
  status: number;
  body: unknown;
}

const result = (id: number, extra: Record<string, unknown> = {}) => ({
  id,
  loinc_code: `000${id}-0`,
  laboratory: "Lab A",
  method: "Method M",
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
  ...extra,
});

const report = {
  id: 9,
  origin: "manual",
  laboratory: "Lab A",
  original_retained: false,
  results: [
    result(1),
    result(2, { validation_state: "disputed" }),
    result(3, { validation_state: "retracted" }),
  ],
};

let replies: Reply[] = [];
let fetchMock: jest.Mock<typeof fetch>;

beforeEach(() => {
  replies = [];
  document.cookie = "csrftoken=tok123";
  fetchMock = jest.fn(async (url: unknown) => {
    const isRanges = String(url).includes("/ranges/");
    const r = (isRanges ? undefined : replies.shift()) ?? { status: 500, body: {} };
    return { status: r.status, json: async () => r.body } as unknown as Response;
  }) as unknown as jest.Mock<typeof fetch>;
  global.fetch = fetchMock as unknown as typeof fetch;
});

const patches = () =>
  fetchMock.mock.calls.filter(([, init]) => (init as RequestInit)?.method === "PATCH");

test("controls follow the state and never offer source_verified", async () => {
  // scenario: biomarkers-and-labs::source-verification-cannot-be-self-declared
  // scenario: biomarkers-and-labs::a-retracted-result-is-kept-but-excluded
  replies = [{ status: 200, body: report }];
  render(<LabReportPage />);
  await screen.findByText("Check each result");
  const names = screen.getAllByRole("button").map((b) => b.getAttribute("aria-label"));
  expect(names.filter((n) => n?.includes("(result 1,"))).toHaveLength(3);
  expect(names.filter((n) => n?.includes("(result 2,"))).toEqual([
    "I checked it against my report (result 2, 0002-0)",
    "Withdraw this result (result 2, 0002-0)",
  ]);
  expect(names.filter((n) => n?.includes("(result 3,"))).toHaveLength(0);
  expect(screen.getByText(/Withdrawn, kept for audit/)).toBeInTheDocument();
  expect(screen.queryByRole("button", { name: /verified/i })).toBeNull();
});

test("confirm sends PATCH with CSRF and updates the page", async () => {
  // scenario: biomarkers-and-labs::the-owner-confirms-a-result
  replies = [
    { status: 200, body: report },
    {
      status: 200,
      body: result(1, { validation_state: "user_confirmed", aggregation_eligible: true }),
    },
  ];
  render(<LabReportPage />);
  await userEvent.click(
    await screen.findByRole("button", { name: /I checked it against my report \(result 1,/ }),
  );
  await waitFor(() => expect(patches()).toHaveLength(1));
  const [url, init] = patches()[0] as [string, RequestInit];
  expect(url).toMatch(/\/api\/labs\/results\/1\/validation\/$/);
  expect(init.credentials).toBe("include");
  expect((init.headers as Record<string, string>)["X-CSRFToken"]).toBe("tok123");
  expect(JSON.parse(init.body as string)).toEqual({ validation_state: "user_confirmed" });
  const live = await screen.findByText("Result 1 is now: Confirmed by the user");
  expect(live).toHaveAttribute("aria-live", "polite");
  expect(screen.getAllByText("Yes, counted in aggregations")).toHaveLength(1);
});

test("dispute sends disputed", async () => {
  // scenario: biomarkers-and-labs::the-owner-confirms-a-result
  replies = [
    { status: 200, body: report },
    { status: 200, body: result(1, { validation_state: "disputed" }) },
  ];
  render(<LabReportPage />);
  await userEvent.click(
    await screen.findByRole("button", { name: /Mark as possibly wrong \(result 1,/ }),
  );
  await waitFor(() => expect(patches()).toHaveLength(1));
  const init = patches()[0][1] as RequestInit;
  expect(JSON.parse(init.body as string)).toEqual({ validation_state: "disputed" });
  expect(
    await screen.findByText(
      "Result 1 is now: Marked as possibly wrong, not counted in statistics",
    ),
  ).toBeTruthy();
});

test("retract asks first; cancel sends nothing; accept sends retracted", async () => {
  // scenario: biomarkers-and-labs::a-retracted-result-is-kept-but-excluded
  replies = [
    { status: 200, body: report },
    { status: 200, body: result(1, { validation_state: "retracted" }) },
  ];
  const confirm = jest.spyOn(window, "confirm").mockReturnValue(false);
  render(<LabReportPage />);
  const btn = await screen.findByRole("button", { name: /Withdraw this result \(result 1,/ });
  await userEvent.click(btn);
  expect(confirm).toHaveBeenCalledWith(expect.stringContaining("cannot be restored"));
  expect(patches()).toHaveLength(0);
  confirm.mockReturnValue(true);
  await userEvent.click(btn);
  await waitFor(() => expect(patches()).toHaveLength(1));
  const init = patches()[0][1] as RequestInit;
  expect(JSON.parse(init.body as string)).toEqual({ validation_state: "retracted" });
  expect(await screen.findAllByText(/Withdrawn, kept for audit/)).toHaveLength(2);
  expect(screen.getAllByText("5.10").length).toBeGreaterThan(0);
  confirm.mockRestore();
});

test("a 400 shows the API message next to the result and keeps the state", async () => {
  // scenario: biomarkers-and-labs::source-verification-cannot-be-self-declared
  replies = [
    { status: 200, body: report },
    { status: 400, body: { validation_state: ["Not allowed."] } },
  ];
  render(<LabReportPage />);
  const btn = await screen.findByRole("button", {
    name: /I checked it against my report \(result 1,/,
  });
  await userEvent.click(btn);
  const msg = await screen.findByText("Not allowed.");
  expect(btn).toHaveAttribute("aria-describedby", msg.id);
  expect(screen.getAllByText("Entered, not yet confirmed").length).toBeGreaterThan(0);
});

test("a failed request keeps the button enabled and focused, and the error is an alert", async () => {
  // scenario: biomarkers-and-labs::source-verification-cannot-be-self-declared
  replies = [
    { status: 200, body: report },
    { status: 400, body: { validation_state: ["Not allowed."] } },
  ];
  render(<LabReportPage />);
  const btn = await screen.findByRole("button", {
    name: /I checked it against my report \(result 1,/,
  });
  await userEvent.click(btn);
  const msg = await screen.findByText("Not allowed.");
  expect(msg).toHaveAttribute("role", "alert");
  expect(btn).not.toBeDisabled();
  expect(btn).toHaveFocus();
});

test("on an imported report the withdraw warning does not promise retention past Undo", async () => {
  // scenario: biomarkers-and-labs::a-retracted-result-is-kept-but-excluded
  replies = [{ status: 200, body: { ...report, origin: "import" } }];
  const confirm = jest.spyOn(window, "confirm").mockReturnValue(false);
  render(<LabReportPage />);
  await userEvent.click(
    await screen.findByRole("button", { name: /Withdraw this result \(result 1,/ }),
  );
  expect(confirm).toHaveBeenCalledWith(expect.stringContaining("undoing the import deletes"));
  confirm.mockRestore();
});

test("a 404 shows a not-found message", async () => {
  // scenario: biomarkers-and-labs::the-owner-confirms-a-result
  replies = [{ status: 200, body: report }, { status: 404, body: {} }];
  render(<LabReportPage />);
  await userEvent.click(
    await screen.findByRole("button", { name: /I checked it against my report \(result 1,/ }),
  );
  expect(await screen.findByText(/This result was not found/)).toBeInTheDocument();
});
