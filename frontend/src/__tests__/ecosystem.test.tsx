// SPDX-License-Identifier: AGPL-3.0-or-later
import { test, expect, jest, beforeEach } from "@jest/globals";
import "@testing-library/jest-dom/jest-globals";
import { render, screen, within } from "@testing-library/react";
import data from "@/content/ecosystem.json";
import { ecosystemStrings } from "@/lib/i18n";

let mockAcceptLanguage: string | null = null;

beforeEach(() => {
  mockAcceptLanguage = null;
});

jest.doMock("next/headers", () => ({
  headers: async () => ({ get: () => mockAcceptLanguage }),
}));

async function renderPage() {
  const { default: EcosystemPage } = await import("@/app/ecosystem/page");
  render(await EcosystemPage());
}

// scenario: ecosystem-reuse::page-lists-every-scan-entry
test("every scan entry is a link to its URL with licence and decision", async () => {
  await renderPage();
  for (const scan of data.scans) {
    for (const e of scan.entries) {
      const region = screen.getByRole("region", {
        name: `${scan.title}: ${ecosystemStrings.en.tableRegion}`,
      });
      const links = within(region)
        .getAllByRole("link", { name: e.name })
        .filter((a) => a.getAttribute("href") === e.fields.URL);
      expect(links.length).toBeGreaterThan(0);
      const row = links[0].closest("tr") as HTMLElement;
      const f = e.fields as Record<string, string>;
      expect(row).toHaveTextContent(f["Licence"] ?? "unknown");
      expect(row).toHaveTextContent(f["Decision"] ?? "unknown");
      expect(row).toHaveTextContent(f["AGPL-compatible"] ?? "unknown");
      expect(row).toHaveTextContent(f["Verified"] ?? "unknown");
      if (f["Provisional"]) {
        expect(row).toHaveTextContent(f["Provisional"]);
      }
      if (f["Licence note"]) {
        expect(row).toHaveTextContent(f["Licence note"]);
      }
    }
  }
});

// scenario: ecosystem-reuse::page-lists-every-scan-entry
test("each table has a caption", async () => {
  await renderPage();
  const tables = screen.getAllByRole("table");
  expect(tables).toHaveLength(data.scans.length + 1);
  for (const table of tables) {
    expect(table.querySelector("caption")).not.toBeNull();
  }
});

// scenario: ecosystem-reuse::page-lists-give-back-proposals
test("give-back rows, statuses and the approval sentence are shown", async () => {
  await renderPage();
  expect(
    screen.getByText(ecosystemStrings.en.approval),
  ).toBeInTheDocument();
  for (const g of data.giveback) {
    const link = screen
      .getAllByRole("link", { name: g.upstream })
      .find((a) => a.getAttribute("href") === g.link);
    expect(link).toBeDefined();
    const row = link!.closest("tr") as HTMLElement;
    expect(row).toHaveTextContent(g.contribution);
    expect(row).toHaveTextContent(g.status);
  }
});

// scenario: ecosystem-reuse::page-lists-every-scan-entry
test("interface language follows Accept-Language", async () => {
  mockAcceptLanguage = "it-IT,it;q=0.9,en;q=0.8";
  await renderPage();
  expect(
    screen.getByRole("heading", { level: 1, name: ecosystemStrings.it.title }),
  ).toBeInTheDocument();
});
