// SPDX-License-Identifier: AGPL-3.0-or-later
import { test, expect } from "@jest/globals";
import { blocks } from "@/lib/markdown-blocks";

// scenario: dev-process::api-reference-page-in-sync
test("a pipe table becomes one table block without its separator row", () => {
  const out = blocks("| State | Meaning |\n|---|---|\n| `a` | first |\n| `b` | second |");
  expect(out).toEqual([
    { kind: "table", head: ["State", "Meaning"], rows: [["`a`", "first"], ["`b`", "second"]] },
  ]);
});

// scenario: dev-process::api-reference-page-in-sync
test("an indented continuation stays inside its bullet and the list stays whole", () => {
  const out = blocks("- one that wraps\n  onto a second line\n- two");
  expect(out).toEqual([{ kind: "list", items: ["one that wraps onto a second line", "two"] }]);
});
