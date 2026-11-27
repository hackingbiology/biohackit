// SPDX-License-Identifier: AGPL-3.0-or-later
// biohack.it — open-source biohacking platform
// Copyright (C) HackingBiology 2026 — https://biohack.it
// Full license text: https://www.gnu.org/licenses/agpl-3.0.html

export type Block =
  | { kind: "code"; text: string }
  | { kind: "list"; items: string[] }
  | { kind: "table"; head: string[]; rows: string[][] }
  | { kind: "text"; text: string };

const separator = /^\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)*\|?$/;

function cells(line: string): string[] {
  return line
    .trim()
    .replace(/^\|/, "")
    .replace(/\|$/, "")
    .split("|")
    .map((c) => c.trim());
}

// Splits a Markdown body into fenced code, tables, bullet lists and paragraphs.
export function blocks(body: string): Block[] {
  const out: Block[] = [];
  let fence: string[] | null = null;
  for (const part of body.split("\n")) {
    const last = out[out.length - 1];
    if (part.startsWith("```")) {
      if (fence) {
        out.push({ kind: "code", text: fence.join("\n") });
        fence = null;
      } else fence = [];
    } else if (fence) fence.push(part);
    else if (part.startsWith("|")) {
      if (separator.test(part.trim())) continue;
      if (last?.kind === "table") last.rows.push(cells(part));
      else out.push({ kind: "table", head: cells(part), rows: [] });
    } else if (part.startsWith("- ")) {
      if (last?.kind === "list") last.items.push(part.slice(2));
      else out.push({ kind: "list", items: [part.slice(2)] });
    } else if (part.trim() === "") out.push({ kind: "text", text: "" });
    else if (last?.kind === "list" && /^\s/.test(part)) {
      last.items[last.items.length - 1] += ` ${part.trim()}`;
    } else if (last?.kind === "text" && last.text) last.text += ` ${part.trim()}`;
    else out.push({ kind: "text", text: part.trim() });
  }
  return out.filter((b) => b.kind !== "text" || b.text);
}
