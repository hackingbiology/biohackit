// SPDX-License-Identifier: AGPL-3.0-or-later
import { test, expect, jest } from "@jest/globals";
import "@testing-library/jest-dom/jest-globals";
import { render, screen, within } from "@testing-library/react";
import data from "@/content/architecture.json";
import { architectureStrings } from "@/lib/i18n";

jest.doMock("next/headers", () => ({
  headers: async () => ({ get: () => null }),
}));

const t = architectureStrings.en;

// scenario: dev-process::architecture-page-in-sync
test("both tables render every row from the generated data", async () => {
  const { default: Page } = await import("@/app/docs/architecture/page");
  render(await Page());
  const [built, specified] = screen.getAllByRole("table");
  for (const h of [t.component, t.layer, t.path, t.purpose]) {
    expect(within(built).getByRole("columnheader", { name: h })).toBeInTheDocument();
  }
  for (const h of [t.component, t.requirement]) {
    expect(within(specified).getByRole("columnheader", { name: h })).toBeInTheDocument();
  }
  for (const r of data.built) {
    const row = within(built).getByRole("rowheader", { name: r.component }).closest("tr") as HTMLElement;
    const cells = within(row).getAllByRole("cell").map((c) => c.textContent);
    expect(cells).toEqual([t.layerLabels[r.layer], r.path, r.purpose]);
  }
  for (const r of data.specified) {
    const row = within(specified).getByRole("rowheader", { name: r.component }).closest("tr") as HTMLElement;
    expect(within(row).getByRole("cell")).toHaveTextContent(r.requirement);
  }
});

// scenario: dev-process::architecture-page-in-sync
test("the docs index links to the architecture page", async () => {
  const { default: Docs } = await import("@/app/docs/page");
  render(await Docs());
  expect(screen.getByRole("link", { name: t.title })).toHaveAttribute(
    "href",
    "/docs/architecture",
  );
});
