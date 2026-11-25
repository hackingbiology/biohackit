// SPDX-License-Identifier: AGPL-3.0-or-later
import { test, expect, jest } from "@jest/globals";
import "@testing-library/jest-dom/jest-globals";
import { render, screen, within } from "@testing-library/react";
import data from "@/content/changelog.json";
import { changelogStrings } from "@/lib/i18n";

jest.doMock("next/headers", () => ({
  headers: async () => ({ get: () => null }),
}));

const t = changelogStrings.en;

// scenario: dev-process::changelog-page-in-sync
test("headings and every entry render from the generated data", async () => {
  const { default: Page } = await import("@/app/docs/changelog/page");
  render(await Page());
  expect(screen.getByRole("heading", { level: 1, name: t.title })).toBeInTheDocument();
  const tables = screen.getAllByRole("table");
  expect(tables).toHaveLength(data.days.length);
  data.days.forEach((day, i) => {
    expect(screen.getByRole("heading", { level: 2, name: day.date })).toBeInTheDocument();
    for (const e of day.entries) {
      const row = within(tables[i]).getByRole("rowheader", { name: e.summary }).closest("tr") as HTMLElement;
      expect(within(row).getAllByRole("cell").map((c) => c.textContent)).toEqual([e.change, e.commit]);
    }
  });
});

// scenario: dev-process::changelog-page-in-sync
test("the docs index links to the changelog", async () => {
  const { default: Docs } = await import("@/app/docs/page");
  render(await Docs());
  expect(screen.getByRole("link", { name: t.title })).toHaveAttribute("href", "/docs/changelog");
});
