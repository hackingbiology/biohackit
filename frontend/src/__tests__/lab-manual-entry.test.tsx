// SPDX-License-Identifier: AGPL-3.0-or-later
import { test, expect, jest, beforeEach } from "@jest/globals";
import "@testing-library/jest-dom/jest-globals";
import { render as plainRender, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { AppRouterContext } from "next/dist/shared/lib/app-router-context.shared-runtime";
import type { AppRouterInstance } from "next/dist/shared/lib/app-router-context.shared-runtime";
import LabNewPage from "@/app/labs/new/page";

const push = jest.fn();

// The page navigates with the app router; supply a router that records push.
function render(ui: React.ReactElement) {
  const router = { push } as unknown as AppRouterInstance;
  return plainRender(
    <AppRouterContext.Provider value={router}>{ui}</AppRouterContext.Provider>,
  );
}

interface Reply {
  status: number;
  body: unknown;
}

let replies: Reply[] = [];
let fetchMock: jest.Mock<typeof fetch>;

beforeEach(() => {
  replies = [];
  push.mockClear();
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

async function fillRow(
  user: ReturnType<typeof userEvent.setup>,
  n: number,
  code: string,
  value: string,
  unit: string,
) {
  const scope = within(
    screen.getByRole("group", { name: `Result ${n}` }),
  );
  await user.type(scope.getByLabelText("LOINC code"), code);
  await user.type(scope.getByLabelText("Reported value"), value);
  await user.type(scope.getByLabelText("Reported unit"), unit);
}

test("a typed row is posted with the exact typed string", async () => {
  // scenario: biomarkers-and-labs::typed-value-gets-the-same-treatment
  replies = [{ status: 201, body: { id: 7 } }];
  const user = userEvent.setup();
  render(<LabNewPage />);
  await fillRow(user, 1, "0000-0", "5.10", "xa/L");
  await user.click(screen.getByRole("button", { name: "Save report" }));
  await screen.findByRole("button", { name: "Save report" });
  const [url, init] = fetchMock.mock.calls[0];
  expect(String(url)).toContain("/api/labs/reports/");
  expect(init?.method).toBe("POST");
  expect(
    (init?.headers as Record<string, string>)["X-CSRFToken"],
  ).toBe("tok123");
  const body = JSON.parse(String(init?.body));
  expect(body.results[0].reported_value).toBe("5.10");
  expect(body.results[0].loinc_code).toBe("0000-0");
});

test("a 400 on result 1 is shown on row 2 and the inputs are kept", async () => {
  // scenario: biomarkers-and-labs::typed-value-gets-the-same-treatment
  replies = [
    {
      status: 400,
      body: { results: { "1": { reported_value: ["Too many decimals."] } } },
    },
  ];
  const user = userEvent.setup();
  render(<LabNewPage />);
  await fillRow(user, 1, "0000-0", "1", "xa/L");
  await user.click(screen.getByRole("button", { name: "Add another result" }));
  await fillRow(user, 2, "0000-1", "2.1234567", "xa/L");
  await user.click(screen.getByRole("button", { name: "Save report" }));
  const second = within(screen.getByRole("group", { name: "Result 2" }));
  expect(await second.findByText(/Too many decimals/)).toBeInTheDocument();
  const value = second.getByLabelText("Reported value");
  expect(value).toHaveValue("2.1234567");
  expect(value).toHaveAccessibleDescription(/Too many decimals/);
  expect(
    within(screen.getByRole("group", { name: "Result 1" })).queryByText(
      /Too many decimals/,
    ),
  ).toBeNull();
  expect(screen.getByRole("alert")).toHaveTextContent("was not saved");
});

test("a 201 sends the user to the report page", async () => {
  // scenario: biomarkers-and-labs::typed-value-gets-the-same-treatment
  replies = [{ status: 201, body: { id: 42 } }];
  const user = userEvent.setup();
  render(<LabNewPage />);
  await fillRow(user, 1, "0000-0", "1", "xa/L");
  await user.click(screen.getByRole("button", { name: "Save report" }));
  await screen.findByRole("button", { name: "Save report" });
  expect(push).toHaveBeenCalledWith("/labs/reports/42");
});

test("a missing required field blocks submit", async () => {
  // scenario: biomarkers-and-labs::typed-value-gets-the-same-treatment
  const user = userEvent.setup();
  render(<LabNewPage />);
  await user.type(screen.getByLabelText("LOINC code"), "0000-0");
  await user.click(screen.getByRole("button", { name: "Save report" }));
  expect(fetchMock).not.toHaveBeenCalled();
  expect(screen.getAllByText("This field is required.")).toHaveLength(2);
  expect(screen.getByLabelText("Reported value")).toHaveAccessibleDescription(
    "This field is required.",
  );
});

test("a 401 shows a sign-in link", async () => {
  // scenario: biomarkers-and-labs::typed-value-gets-the-same-treatment
  replies = [{ status: 401, body: {} }];
  const user = userEvent.setup();
  render(<LabNewPage />);
  await fillRow(user, 1, "0000-0", "1", "xa/L");
  await user.click(screen.getByRole("button", { name: "Save report" }));
  expect(await screen.findByRole("link", { name: "Go to sign in" })).toHaveAttribute(
    "href",
    "/sign-in",
  );
});

test("a row-level non_field_errors message and a laboratory error are shown", async () => {
  // scenario: biomarkers-and-labs::typed-value-gets-the-same-treatment
  replies = [
    {
      status: 400,
      body: {
        laboratory: ["Too long."],
        results: { "0": { non_field_errors: ["Row is inconsistent."] } },
      },
    },
  ];
  const user = userEvent.setup();
  render(<LabNewPage />);
  await fillRow(user, 1, "0000-0", "1", "xa/L");
  await user.click(screen.getByRole("button", { name: "Save report" }));
  expect(await screen.findByText(/Row is inconsistent/)).toBeInTheDocument();
  expect(screen.getByRole("group", { name: "Result 1" })).toHaveAccessibleDescription(
    /Row is inconsistent/,
  );
  const lab = screen.getByLabelText("Laboratory for the whole report (optional)");
  expect(lab).toHaveAccessibleDescription(/Too long/);
  expect(lab).toHaveAttribute("aria-invalid", "true");
});

test("the intro does not promise undo and says a typed report cannot be undone", () => {
  // scenario: biomarkers-and-labs::typed-value-gets-the-same-treatment
  render(<LabNewPage />);
  const main = screen.getByRole("main");
  expect(main).not.toHaveTextContent("you can undo");
  expect(main).toHaveTextContent("cannot be undone after saving");
});

test("removing a row keeps focus in the form and announces the removal", async () => {
  // scenario: biomarkers-and-labs::typed-value-gets-the-same-treatment
  const user = userEvent.setup();
  render(<LabNewPage />);
  await user.click(screen.getByRole("button", { name: "Add another result" }));
  await user.click(screen.getByRole("button", { name: "Add another result" }));
  await user.click(screen.getByRole("button", { name: "Remove result 2" }));
  const second = within(screen.getByRole("group", { name: "Result 2" }));
  expect(document.activeElement).toBe(second.getByLabelText("LOINC code"));
  expect(screen.getByRole("status")).toHaveTextContent("Result 2 removed.");
});

test("removing the last row moves focus to the previous row", async () => {
  // scenario: biomarkers-and-labs::typed-value-gets-the-same-treatment
  const user = userEvent.setup();
  render(<LabNewPage />);
  await user.click(screen.getByRole("button", { name: "Add another result" }));
  await user.click(screen.getByRole("button", { name: "Remove result 2" }));
  const first = within(screen.getByRole("group", { name: "Result 1" }));
  expect(document.activeElement).not.toBe(document.body);
  expect(document.activeElement).toBe(first.getByLabelText("LOINC code"));
  expect(screen.getByRole("status")).toHaveTextContent("Result 2 removed.");
});

test("removing result 2 twice replaces the announcement node each time", async () => {
  // scenario: biomarkers-and-labs::typed-value-gets-the-same-treatment
  const user = userEvent.setup();
  render(<LabNewPage />);
  for (let i = 0; i < 3; i++) {
    await user.click(screen.getByRole("button", { name: "Add another result" }));
  }
  await user.click(screen.getByRole("button", { name: "Remove result 2" }));
  const firstNode = screen.getByRole("status").firstElementChild;
  await user.click(screen.getByRole("button", { name: "Remove result 2" }));
  const secondNode = screen.getByRole("status").firstElementChild;
  expect(secondNode).not.toBeNull();
  expect(secondNode).not.toBe(firstNode);
  expect(screen.getByRole("status")).toHaveTextContent("Result 2 removed.");
});
