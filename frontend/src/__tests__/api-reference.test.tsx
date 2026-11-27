// SPDX-License-Identifier: AGPL-3.0-or-later
import { test, expect, jest } from "@jest/globals";
import "@testing-library/jest-dom/jest-globals";
import { render, screen, within } from "@testing-library/react";
import data from "@/content/api-reference.json";
import { apiReferenceStrings } from "@/lib/i18n";

jest.doMock("next/headers", () => ({
  headers: async () => ({ get: () => null }),
}));

const t = apiReferenceStrings.en;

// scenario: dev-process::api-reference-page-in-sync
test("heading, every endpoint row and every section render from the generated data", async () => {
  const { default: Page } = await import("@/app/docs/api/page");
  render(await Page());
  expect(screen.getByRole("heading", { level: 1, name: t.title })).toBeInTheDocument();
  const table = screen.getByRole("table", { name: t.overviewCaption });
  const rows = within(table).getAllByRole("row").slice(1);
  expect(rows).toHaveLength(data.endpoints.length);
  const links = within(table).getAllByRole("link");
  expect(links.map((l) => [l.textContent, l.getAttribute("href")])).toEqual(
    data.endpoints.map((e) => [e.path, `#${e.anchor}`]),
  );
  for (const doc of data.docs) {
    expect(screen.getByRole("heading", { level: 2, name: doc.title })).toBeInTheDocument();
    for (const s of doc.sections) {
      const h = document.getElementById(s.anchor);
      expect(h?.tagName).toBe(s.level === 2 ? "H3" : "H4");
    }
  }
});

// scenario: dev-process::api-reference-page-in-sync
test("a Markdown table in a body renders as a real table with column headers", async () => {
  const { default: Page } = await import("@/app/docs/api/page");
  render(await Page());
  const tables = screen.getAllByRole("table");
  expect(tables.length).toBeGreaterThan(1);
  expect(within(tables[1]).getAllByRole("columnheader").length).toBeGreaterThan(0);
});

// scenario: dev-process::api-reference-page-in-sync
test("the docs index links to the API reference", async () => {
  const { default: Docs } = await import("@/app/docs/page");
  render(await Docs());
  expect(screen.getByRole("link", { name: t.title })).toHaveAttribute("href", "/docs/api");
});
