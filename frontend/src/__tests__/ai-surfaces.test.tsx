// SPDX-License-Identifier: AGPL-3.0-or-later
import { test, expect, jest } from "@jest/globals";
import "@testing-library/jest-dom/jest-globals";
import { render, screen, within } from "@testing-library/react";
import data from "@/content/ai-surfaces.json";
import { aiSurfacesStrings } from "@/lib/i18n";

jest.doMock("next/headers", () => ({
  headers: async () => ({ get: () => null }),
}));

const t = aiSurfacesStrings.en;

// scenario: ai-uses-and-attribution::the-numbers-are-not-ai
test("both tables render with headers and every row labelled AI or deterministic", async () => {
  const { default: Page } = await import("@/app/docs/ai-surfaces/page");
  render(await Page());
  const tables = screen.getAllByRole("table");
  expect(tables).toHaveLength(2);
  for (const table of tables) {
    for (const h of [t.surface, t.kind, t.where, t.status]) {
      expect(within(table).getByRole("columnheader", { name: h })).toBeInTheDocument();
    }
  }
  const [ai, det] = tables;
  for (const r of data.ai) {
    const row = within(ai).getByRole("rowheader", { name: r.surface }).closest("tr") as HTMLElement;
    const cells = within(row).getAllByRole("cell").map((c) => c.textContent);
    expect(cells).toEqual([t.kindLabels[r.kind], r.where, t.statusLabels[r.status]]);
  }
  for (const r of data.deterministic) {
    const row = within(det).getByRole("rowheader", { name: r.surface }).closest("tr") as HTMLElement;
    const cells = within(row).getAllByRole("cell").map((c) => c.textContent);
    expect(cells).toEqual([t.kindLabels[r.kind], r.where, t.statusLabels[r.status]]);
  }
});

// scenario: ai-uses-and-attribution::the-numbers-are-not-ai
test("the docs index links to the AI surfaces map", async () => {
  const { default: Docs } = await import("@/app/docs/page");
  render(await Docs());
  expect(screen.getByRole("link", { name: t.title })).toHaveAttribute(
    "href",
    "/docs/ai-surfaces",
  );
});
