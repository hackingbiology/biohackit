// SPDX-License-Identifier: AGPL-3.0-or-later
import { test, expect, jest } from "@jest/globals";
import "@testing-library/jest-dom/jest-globals";
import { render, screen, within } from "@testing-library/react";
import data from "@/content/user-guide.json";
import { userGuideStrings } from "@/lib/i18n";

jest.doMock("next/headers", () => ({
  headers: async () => ({ get: () => null }),
}));

const t = userGuideStrings.en;

// scenario: dev-process::user-guide-page-in-sync
test("headings and every row render from the generated data", async () => {
  const { default: Page } = await import("@/app/docs/user-guide/page");
  render(await Page());
  expect(screen.getByRole("heading", { level: 1, name: t.title })).toBeInTheDocument();
  for (const h of [t.stepsCaption, t.signinCaption, t.laterCaption]) {
    expect(screen.getByRole("heading", { level: 2, name: h })).toBeInTheDocument();
  }
  const [steps, signin, later] = screen.getAllByRole("table");
  for (const r of data.steps) {
    const row = within(steps).getByRole("rowheader", { name: r.step }).closest("tr") as HTMLElement;
    expect(within(row).getAllByRole("cell").map((c) => c.textContent)).toEqual([r.action, r.route]);
  }
  for (const r of data.signin) {
    const row = within(signin).getByRole("rowheader", { name: r.method }).closest("tr") as HTMLElement;
    expect(within(row).getAllByRole("cell").map((c) => c.textContent)).toEqual([r.availability, r.source]);
  }
  for (const r of data.later) {
    const row = within(later).getByRole("rowheader", { name: r.feature }).closest("tr") as HTMLElement;
    expect(within(row).getByRole("cell")).toHaveTextContent(r.requirement);
  }
});

// scenario: dev-process::user-guide-page-in-sync
test("the docs index links to the user guide", async () => {
  const { default: Docs } = await import("@/app/docs/page");
  render(await Docs());
  expect(screen.getByRole("link", { name: t.title })).toHaveAttribute("href", "/docs/user-guide");
});
