// SPDX-License-Identifier: AGPL-3.0-or-later
import { test, expect, jest, beforeEach } from "@jest/globals";
import "@testing-library/jest-dom/jest-globals";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import LabImportPage from "@/app/labs/import/page";

interface Reply {
  status: number;
  body: unknown;
}

const row = (n: number, status: string, reason = "") => ({
  row: n,
  status,
  reason,
  loinc_code: "0000-0",
  value: "1",
  unit: "xa/L",
  plausibility: null,
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

async function checkFile() {
  const user = userEvent.setup();
  render(<LabImportPage />);
  const file = new File(["loinc_code,value,unit\n"], "labs.csv", {
    type: "text/csv",
  });
  await user.upload(screen.getByLabelText("Lab results file (.csv)"), file);
  await user.click(screen.getByRole("button", { name: "Check file" }));
  return { user, file };
}

const okRows = { rows: [row(1, "recognised"), row(2, "recognised")] };

test("choosing another file clears the old preview so it cannot be saved unseen", async () => {
  replies = [{ status: 200, body: okRows }];
  const { user } = await checkFile();
  expect(
    await screen.findByRole("button", { name: "Save report" }),
  ).toBeEnabled();
  const other = new File(["loinc_code,value,unit\n"], "other.csv", {
    type: "text/csv",
  });
  await user.upload(screen.getByLabelText("Lab results file (.csv)"), other);
  expect(
    screen.queryByRole("button", { name: "Save report" }),
  ).not.toBeInTheDocument();
});

// scenario: biomarkers-and-labs::unrecognised-line-item
test("a not recognised row is shown as text with its reason and blocks Save", async () => {
  replies = [
    {
      status: 200,
      body: {
        rows: [
          row(1, "recognised"),
          row(2, "not_recognised", "loinc_code: unknown code"),
        ],
      },
    },
  ];
  await checkFile();
  expect(await screen.findByText("Not recognised")).toBeInTheDocument();
  expect(screen.getByText("loinc_code: unknown code")).toBeInTheDocument();
  expect(
    screen.getByRole("heading", { name: "1 of 2 rows recognised" }),
  ).toBeInTheDocument();
  expect(screen.getByRole("table")).toHaveAccessibleName(
    "Rows of your file and whether each one is recognised",
  );
  const save = screen.getByRole("button", { name: "Save report" });
  expect(save).toBeDisabled();
  expect(save).toHaveAccessibleDescription(/at least one row is not recognised/);
});

test("all rows recognised enables Save, confirm sends the same file", async () => {
  replies = [
    { status: 200, body: okRows },
    { status: 201, body: { id: 7, original_retained: true } },
  ];
  const { user, file } = await checkFile();
  const save = await screen.findByRole("button", { name: "Save report" });
  expect(save).toBeEnabled();
  await user.click(save);
  expect(await screen.findByText("Report number 7 was saved.")).toBeVisible();
  expect(screen.getByText("The original file was kept privately.")).toBeVisible();
  const [url, init] = fetchMock.mock.calls[1];
  expect(String(url)).toMatch(/\/api\/labs\/imports\/csv\/confirm\/$/);
  expect(((init as RequestInit).body as FormData).get("file")).toBe(file);
});

// scenario: biomarkers-and-labs::undo-an-import
test("Undo deletes the report only after confirmation", async () => {
  replies = [
    { status: 200, body: okRows },
    { status: 201, body: { id: 7, original_retained: false } },
    { status: 204, body: {} },
  ];
  const confirm = jest.spyOn(window, "confirm");
  const { user } = await checkFile();
  await user.click(await screen.findByRole("button", { name: "Save report" }));
  expect(await screen.findByText("The original file was not kept.")).toBeVisible();

  confirm.mockReturnValueOnce(false);
  await user.click(screen.getByRole("button", { name: "Undo this import" }));
  expect(fetchMock).toHaveBeenCalledTimes(2);

  confirm.mockReturnValueOnce(true);
  await user.click(screen.getByRole("button", { name: "Undo this import" }));
  await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(3));
  const [url, init] = fetchMock.mock.calls[2];
  expect(String(url)).toMatch(/\/api\/labs\/reports\/7\/$/);
  expect((init as RequestInit).method).toBe("DELETE");
  expect(
    await screen.findByRole("heading", {
      name: "Import undone. The report was deleted.",
    }),
  ).toBeInTheDocument();
});

test("a 400 from confirm shows the returned rows again", async () => {
  replies = [
    { status: 200, body: okRows },
    {
      status: 400,
      body: {
        detail: "Some rows are not recognised.",
        rows: [row(2, "not_recognised", "unit: empty")],
      },
    },
  ];
  const { user } = await checkFile();
  await user.click(await screen.findByRole("button", { name: "Save report" }));
  expect(await screen.findByText("unit: empty")).toBeInTheDocument();
  expect(
    screen.getByRole("heading", { name: "1 of 2 rows recognised" }),
  ).toBeInTheDocument();
  expect(screen.getByRole("alert")).toHaveTextContent(
    "The file was not saved because some rows are not recognised.",
  );
  expect(screen.getByRole("button", { name: "Save report" })).toBeDisabled();
});

test("a file-level 400 shows the file message", async () => {
  replies = [{ status: 400, body: { file: ["The file is not valid CSV."] } }];
  await checkFile();
  expect(await screen.findByRole("alert")).toHaveTextContent(
    "The file is not valid CSV.",
  );
});

test("a failed undo says the report is still saved", async () => {
  replies = [
    { status: 200, body: okRows },
    { status: 201, body: { id: 7, original_retained: true } },
    { status: 500, body: {} },
  ];
  jest.spyOn(window, "confirm").mockReturnValue(true);
  const { user } = await checkFile();
  await user.click(await screen.findByRole("button", { name: "Save report" }));
  await user.click(
    await screen.findByRole("button", { name: "Undo this import" }),
  );
  expect(await screen.findByRole("alert")).toHaveTextContent(
    "The report is still saved",
  );
});

test("a 401 shows the sign-in link in an alert", async () => {
  replies = [{ status: 401, body: { detail: "no" } }];
  await checkFile();
  const alert = await screen.findByRole("alert");
  expect(alert).toHaveTextContent("Please sign in");
  expect(screen.getByRole("link", { name: "Go to sign in" })).toHaveAttribute(
    "href",
    "/sign-in",
  );
});

test("every request carries credentials and the CSRF header", async () => {
  replies = [
    { status: 200, body: okRows },
    { status: 201, body: { id: 3, original_retained: true } },
    { status: 204, body: {} },
  ];
  jest.spyOn(window, "confirm").mockReturnValue(true);
  const { user } = await checkFile();
  await user.click(await screen.findByRole("button", { name: "Save report" }));
  await user.click(
    await screen.findByRole("button", { name: "Undo this import" }),
  );
  await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(3));
  for (const [, init] of fetchMock.mock.calls) {
    const req = init as RequestInit;
    expect(req.credentials).toBe("include");
    expect((req.headers as Record<string, string>)["X-CSRFToken"]).toBe(
      "tok123",
    );
  }
});

const outsideRow = {
  ...row(1, "recognised"),
  plausibility: {
    status: "outside",
    range_source: {
      name: "Synthetic source",
      version: "1",
      licence: "CC0-1.0",
      url: "https://example.org/range",
      retrieved_at: "2026-01-01T00:00:00+00:00",
    },
  },
};

// scenario: biomarkers-and-labs::unrecognised-line-item
test("an outside row shows the range check in words and Save stays enabled", async () => {
  replies = [{ status: 200, body: { rows: [outsideRow] } }];
  await checkFile();
  expect(
    await screen.findByText("Outside the cited reference range"),
  ).toBeInTheDocument();
  expect(
    screen.getByRole("link", { name: "Range source: Synthetic source" }),
  ).toHaveAttribute("href", "https://example.org/range");
  expect(screen.getByRole("columnheader", { name: "Range check" })).toBeInTheDocument();
  expect(screen.getByRole("button", { name: "Save report" })).toBeEnabled();
});

// scenario: biomarkers-and-labs::unrecognised-line-item
test("a null plausibility shows Not checked", async () => {
  replies = [{ status: 200, body: { rows: [row(1, "recognised")] } }];
  await checkFile();
  expect(await screen.findByText("Not checked")).toBeInTheDocument();
});

// scenario: biomarkers-and-labs::undo-an-import
test("after a save Check file is disabled and Undo stays; after Undo it is enabled", async () => {
  replies = [
    { status: 200, body: okRows },
    { status: 201, body: { id: 7, original_retained: true } },
    { status: 204, body: {} },
  ];
  jest.spyOn(window, "confirm").mockReturnValue(true);
  const { user } = await checkFile();
  await user.click(await screen.findByRole("button", { name: "Save report" }));
  const undo = await screen.findByRole("button", { name: "Undo this import" });
  expect(screen.getByRole("button", { name: "Check file" })).toBeDisabled();
  expect(
    screen.getByText("Report number 7 is saved. Undo it before you check another file."),
  ).toBeVisible();
  await user.click(undo);
  await screen.findByRole("heading", {
    name: "Import undone. The report was deleted.",
  });
  expect(screen.getByRole("button", { name: "Check file" })).toBeEnabled();
});
