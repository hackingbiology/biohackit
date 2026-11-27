# SPDX-License-Identifier: AGPL-3.0-or-later
"""Deterministic field-level comparison of protocol snapshots (stdlib `difflib`, no AI)."""

import difflib
import json
from typing import Any

POSOLOGY_KEYS = ("basis", "provenance", "provenance_source")
PRODUCT_KEYS = ("route", "formulation", "product_id", "units_per_day")
DIFF_FACETS = ("interventions", "doses", "cycles", "measures")


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False)


def changed_fields(old: Any, new: Any, path: str) -> list[dict[str, Any]]:
    """[{field, old, new}] for every leaf that differs; lists compare by position."""
    if isinstance(old, dict) and isinstance(new, dict):
        out: list[dict[str, Any]] = []
        for key in sorted(old.keys() | new.keys()):
            out += changed_fields(old.get(key), new.get(key), f"{path}.{key}")
        return out
    if isinstance(old, list) and isinstance(new, list):
        out = []
        for i in range(max(len(old), len(new))):
            a = old[i] if i < len(old) else None
            b = new[i] if i < len(new) else None
            out += changed_fields(a, b, f"{path}[{i}]")
        return out
    return [] if old == new else [{"field": path, "old": old, "new": new}]


def _facets_of(snapshot: dict[str, Any]) -> dict[str, Any]:
    interventions = snapshot["interventions"]
    return {
        "interventions": [
            {
                "name": i["name"],
                "schedule": i["schedule"],
                **{k: i[k] for k in PRODUCT_KEYS if k in i},
            }
            for i in interventions
        ],
        "doses": [
            {
                "name": i["name"],
                "amount": i["amount"],
                "unit": i["unit"],
                **{k: i[k] for k in POSOLOGY_KEYS if k in i},
            }
            for i in interventions
        ],
        "cycles": snapshot["cycles"],
        "measures": snapshot["measures"],
    }


def diff_snapshots(
    old: dict[str, Any], new: dict[str, Any], old_label: str, new_label: str
) -> dict[str, Any]:
    before, after = _facets_of(old), _facets_of(new)
    facets: dict[str, Any] = {}
    changes: list[dict[str, Any]] = []
    for name in DIFF_FACETS:
        text = list(
            difflib.unified_diff(
                canonical(before[name]).splitlines(),
                canonical(after[name]).splitlines(),
                fromfile=old_label,
                tofile=new_label,
                lineterm="",
            )
        )
        facets[name] = {"changed": bool(text), "unified": text}
        changes += changed_fields(before[name], after[name], name)
    return {"facets": facets, "changes": changes}
