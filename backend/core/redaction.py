# SPDX-License-Identifier: AGPL-3.0-or-later
"""Deterministic, opt-in redaction (M02 TG-d part 1). Only exact, case-insensitive matches of
terms the user typed are replaced. There are no built-in PII patterns and no NER: any such
rule would be unverified (Q72). The removed text is never returned: the user knows what they
typed, so a removal names the term by its index only."""

import re
from dataclasses import dataclass

PLACEHOLDER = "[REDACTED]"


@dataclass(frozen=True)
class Removal:
    term_index: int
    start: int  # offsets in the original text
    end: int
    line: int  # 1-based line of the original text
    replacement: str = PLACEHOLDER


@dataclass(frozen=True)
class RedactionResult:
    redacted: str
    removals: list[Removal]


def _spans(text: str, terms: list[str]) -> list[tuple[int, int, int]]:
    """Every occurrence of every term as (start, end, term_index), overlaps included.
    Each term is compiled once with re.IGNORECASE (the engine's own case rules, so offsets stay
    on the original text) and searched from one past the previous hit: linear per term."""
    found: list[tuple[int, int, int]] = []
    for index, term in enumerate(terms):
        pattern = re.compile(re.escape(term), re.IGNORECASE)
        match = pattern.search(text)
        while match is not None:
            found.append((match.start(), match.end(), index))
            match = pattern.search(text, match.start() + 1)
    found.sort()
    return found


def redact_text(text: str, terms: list[str]) -> RedactionResult:
    """Replace every case-insensitive occurrence of each term. Overlapping or adjacent
    occurrences merge into one interval with one placeholder, so no part of a longer
    overlapping match survives. The interval names its longest term (first index on a tie).
    Raises ValueError for an empty or whitespace-only term."""
    if any(not term.strip() for term in terms):
        raise ValueError("A redaction term must not be empty or whitespace-only.")
    if not terms:
        return RedactionResult(text, [])
    merged: list[list[int]] = []  # [start, end, best_len, best_index]
    for start, end, index in _spans(text, terms):
        length = end - start
        if merged and start <= merged[-1][1]:
            current = merged[-1]
            current[1] = max(current[1], end)
            if length > current[2] or (length == current[2] and index < current[3]):
                current[2], current[3] = length, index
        else:
            merged.append([start, end, length, index])
    removals: list[Removal] = []
    parts: list[str] = []
    last = 0
    line = 1
    counted = 0
    for start, end, _, index in merged:
        line += text.count("\n", counted, start)
        counted = start
        removals.append(Removal(index, start, end, line))
        parts.append(text[last:start])
        parts.append(PLACEHOLDER)
        last = end
    parts.append(text[last:])
    return RedactionResult("".join(parts), removals)
