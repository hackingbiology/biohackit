# SPDX-License-Identifier: AGPL-3.0-or-later
"""get-based archive preview (X01 part 2a). A pure classifier: it reads the uploaded bytes
and the stored mapping table, stores nothing and logs nothing. Format facts:
docs/ecosystem/getbased-archive-format.md. Markers are matched only through a stored,
cited `GetbasedMarkerMapping` row, never by name. The output is built field by field from
an allow-list, so profile identity, chat, nutrition, wallet and credentials are never
copied (the archive content is not logged either)."""

import json
import re
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Any, NoReturn

from .models import (
    GETBASED_CALCULATED_PREFIX,
    GetbasedMarkerKind,
    GetbasedMarkerMapping,
)

SUPPORTED_VERSION = 2
MAX_KEY_CHARS = 200
MAX_TEXT_CHARS = 200
MAX_ENTRIES = 1000
MAX_ROWS = 5000
DATE_PATTERN = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}")
SUPPORTED_TEXT = (
    "Supported: a single-client export (no 'type', has 'entries', version 2) and an "
    "all-clients bundle ('type': 'database', has 'profiles', version 2)."
)
QUALIFIER = "last import into this date; the model for this value is unknown"

DELETED = "not imported: deleted in get-based"
CALCULATED = "not imported: calculated"
DERIVED = "not imported: calculated by get-based from other markers, not measured"
NO_MAPPING = "not recognised: no mapping stored for this get-based marker"
UNIT_NOT_VERIFIED = "not recognised: unit not verified"
BAD_DATE = "not recognised: date not in YYYY-MM-DD form"
NOT_A_NUMBER = "not recognised: the value is not a number"

MATCHED = "matched"
NOT_RECOGNISED = "not_recognised"
NOT_IMPORTED = "not_imported"


class GetbasedImportError(ValueError):
    """A refusal with a plain message that is safe to show: it never repeats file content
    beyond the short format and version labels."""


@dataclass(frozen=True)
class Container:
    kind: str  # "single-client export" | "all-clients bundle"
    profiles: list[dict[str, Any]]  # one dict per profile, holding `entries`
    ids: list[str]  # profile ids (bundle only)


def _short(value: Any) -> str:
    text = value if isinstance(value, str) else json.dumps(value, default=str)
    return text[:40]


def _refuse(message: str) -> NoReturn:
    raise GetbasedImportError(message)


def _parse(raw: bytes) -> Any:
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        _refuse("The file is not UTF-8 text, so it is not a get-based export.")

    def no_constant(_: str) -> NoReturn:
        raise ValueError("non-finite number")

    try:
        return json.loads(text, parse_float=Decimal, parse_constant=no_constant)
    except (ValueError, RecursionError):
        _refuse("The file is not valid JSON, so it is not a get-based export.")


def _is_version_2(version: Any) -> bool:
    return (
        isinstance(version, int)
        and not isinstance(version, bool)
        and version == SUPPORTED_VERSION
    )


def _found(top: dict[str, Any]) -> str:
    label = top.get("format") if "format" in top else top.get("type")
    version = top.get("version", "missing")
    return f"found format/type {_short(label) if label is not None else 'none'}, version {_short(version)}"


def detect(top: Any) -> Container:
    """Identify the container from the cited markers or refuse it."""
    if not isinstance(top, dict):
        _refuse(f"The top level of the file is not an object. {SUPPORTED_TEXT}")
    fmt = top.get("format")
    if fmt in ("labcharts-backup", "getbased-migration"):
        _refuse(
            f"The format '{fmt}' is not supported yet ({_found(top)}). {SUPPORTED_TEXT}"
        )
    unsupported = f"Unsupported file ({_found(top)}). {SUPPORTED_TEXT}"
    profiles = top.get("profiles")
    if top.get("type") == "database" and isinstance(profiles, list):
        if not _is_version_2(top.get("version")):
            _refuse(unsupported)
        if not profiles or not all(isinstance(p, dict) for p in profiles):
            _refuse("The bundle holds no readable profiles.")
        ids = [p["id"] for p in profiles if isinstance(p.get("id"), str)]
        return Container("all-clients bundle", profiles, ids)
    if "type" not in top and isinstance(top.get("entries"), list):
        if not _is_version_2(top.get("version")):
            _refuse(unsupported)
        return Container("single-client export", [top], [])
    _refuse(unsupported)


def _choose(container: Container, profile_id: str | None) -> dict[str, Any] | None:
    """The one chosen profile's data dict, or None when the user must still choose."""
    if container.kind == "single-client export":
        if profile_id:
            _refuse("A single-client export has no profile ids; send no profile_id.")
        return container.profiles[0]
    if profile_id is None or profile_id == "":
        if len(container.profiles) == 1:
            return _profile_data(container.profiles[0])
        return None
    matches = [p for p in container.profiles if p.get("id") == profile_id]
    if len(matches) != 1:
        _refuse("The profile_id is not one of the profiles in this bundle.")
    return _profile_data(matches[0])


def _profile_data(profile: dict[str, Any]) -> dict[str, Any]:
    data = profile.get("data")
    return data if isinstance(data, dict) else {}


def _text(value: Any) -> str:
    if isinstance(value, str) and value.strip():
        return value[:MAX_TEXT_CHARS]
    return "unknown"


def _flags(source: Any, entry: dict[str, Any]) -> list[dict[str, str]]:
    """Per-value provenance flags, fail closed (Q92). Computed here, stored nowhere."""
    if not isinstance(source, dict):
        return [
            {
                "code": "origin_unknown",
                "text": "origin unknown, check against your report",
            }
        ]
    flags: list[dict[str, str]] = []
    if not (source.get("snapshotId") or source.get("file")):
        flags.append(
            {
                "code": "origin_not_shown",
                "text": "origin not shown in get-based, check against your report",
            }
        )
    elif isinstance(entry.get("importedWith"), dict):
        imported = entry["importedWith"]
        flags.append(
            {
                "code": "ai_read",
                "text": "read by an AI model, check against your report",
                "model_id": _text(imported.get("modelId")),
                "provider": _text(imported.get("provider")),
                "qualifier": QUALIFIER,
            }
        )
    else:
        flags.append(
            {
                "code": "may_be_ai_read",
                "text": "may have been read by an AI model, check against your report",
            }
        )
    if source.get("manuallyEdited") is True:
        flags.append(
            {"code": "edited_after_import", "text": "edited in get-based after import"}
        )
    return flags


def _valid_date(value: Any) -> str | None:
    if not isinstance(value, str) or not DATE_PATTERN.fullmatch(value):
        return None
    try:
        date.fromisoformat(value)
    except ValueError:
        return None
    return value


def _citation(mapping: GetbasedMarkerMapping) -> dict[str, str]:
    source = mapping.source
    return {
        "source": str(source),
        "source_url": source.url,
        "unit_source": f"{mapping.unit_source_path}@{mapping.unit_source_commit}",
    }


def _classify(
    value: Any,
    day: str | None,
    left_out: str | None,
    mapping: GetbasedMarkerMapping | None,
) -> tuple[str, str, dict[str, Any]]:
    """(status, reason, matched details). The rules run in the order of the spec."""
    if left_out is not None:
        return NOT_IMPORTED, left_out, {}
    if day is None:
        return NOT_RECOGNISED, BAD_DATE, {}
    if isinstance(value, bool) or not isinstance(value, int | Decimal):
        return NOT_RECOGNISED, NOT_A_NUMBER, {}
    if mapping is None:
        return NOT_RECOGNISED, NO_MAPPING, {}
    if mapping.unit is None or mapping.biomarker is None:
        return NOT_RECOGNISED, UNIT_NOT_VERIFIED, {}
    details = {
        "loinc_code": mapping.biomarker.loinc_code,
        "unit": mapping.unit.ucum_code,
        **_citation(mapping),
    }
    return MATCHED, "matched through a cited mapping", details


def _left_out_reason(
    key: str,
    entry: dict[str, Any],
    sources: dict[str, Any],
    mappings: dict[str, GetbasedMarkerMapping],
) -> str | None:
    deleted = entry.get("deletedMarkers")
    if isinstance(deleted, dict | list) and key in deleted:
        return DELETED
    mapping = mappings.get(key)
    if key.startswith(GETBASED_CALCULATED_PREFIX) or (
        mapping is not None and mapping.kind == GetbasedMarkerKind.CALCULATED
    ):
        return CALCULATED
    source = sources.get(key)
    if isinstance(source, dict) and source.get("derivedFrom") is not None:
        return DERIVED
    return None


def _rows(
    data: dict[str, Any], mappings: dict[str, GetbasedMarkerMapping]
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    entries = data.get("entries")
    entries = entries if isinstance(entries, list) else []
    if len(entries) > MAX_ENTRIES:
        _refuse(f"The profile has more than {MAX_ENTRIES} entries.")
    for entry in entries:
        markers = entry.get("markers") if isinstance(entry, dict) else None
        if not isinstance(markers, dict):
            continue  # get-based itself skips an entry without markers
        day = _valid_date(entry.get("date"))
        sources = entry.get("markerSources")
        sources = sources if isinstance(sources, dict) else {}
        if len(rows) + len(markers) > MAX_ROWS:
            _refuse(f"The profile has more than {MAX_ROWS} marker values.")
        for key, value in markers.items():
            left_out = _left_out_reason(key, entry, sources, mappings)
            status, reason, details = _classify(value, day, left_out, mappings.get(key))
            numeric = not isinstance(value, bool) and isinstance(value, int | Decimal)
            rows.append(
                {
                    "marker": key[:MAX_KEY_CHARS],
                    "value": str(value) if numeric else None,
                    "date": day,
                    "status": status,
                    "reason": reason,
                    "loinc_code": details.get("loinc_code"),
                    "unit": details.get("unit"),
                    "mapping_source": details.get("source"),
                    "mapping_source_url": details.get("source_url"),
                    "unit_source": details.get("unit_source"),
                    "flags": _flags(sources.get(key), entry),
                }
            )
    return rows


def _summary(rows: list[dict[str, Any]]) -> dict[str, int]:
    def count(status: str) -> int:
        return sum(1 for r in rows if r["status"] == status)

    return {
        "total": len(rows),
        "matched": count(MATCHED),
        "not_recognised": count(NOT_RECOGNISED),
        "left_out": count(NOT_IMPORTED),
        "left_out_deleted": sum(1 for r in rows if r["reason"] == DELETED),
        "left_out_calculated": sum(
            1 for r in rows if r["reason"] in (CALCULATED, DERIVED)
        ),
    }


def build_preview(raw: bytes, profile_id: str | None = None) -> dict[str, Any]:
    """The preview of one chosen profile, or the list of profile ids to choose from.
    Raises `GetbasedImportError` for anything unsupported. Stores nothing."""
    container = detect(_parse(raw))
    data = _choose(container, profile_id)
    if data is None:
        return {
            "status": "choose_profile",
            "container": container.kind,
            "profile_ids": container.ids,
            "detail": "Choose exactly one profile to preview.",
        }
    mappings = {
        m.getbased_key: m
        for m in GetbasedMarkerMapping.objects.select_related(
            "source", "unit", "biomarker"
        )
    }
    rows = _rows(data, mappings)
    summary = _summary(rows)
    return {
        "status": "preview",
        "container": container.kind,
        "version": SUPPORTED_VERSION,
        "rows": rows,
        "summary": summary,
        "can_confirm": summary["not_recognised"] == 0 and summary["matched"] > 0,
    }
