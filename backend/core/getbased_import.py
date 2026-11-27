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

from django.core.exceptions import ValidationError as DjangoValidationError

from .models import (
    GETBASED_CALCULATED_PREFIX,
    GetbasedFlag,
    GetbasedMarkerKind,
    GetbasedMarkerMapping,
    LabReport,
    LabReportImportSource,
    LabReportOrigin,
    LabResult,
    LabResultGetbasedProvenance,
    LabResultValidation,
)

SUPPORTED_VERSION = 2
BACKUP_VERSION = 1
BACKUP_KIND = "browser backup"
MAX_KEY_CHARS = 200
MAX_TEXT_CHARS = 200
MAX_ENTRIES = 1000
MAX_ROWS = 5000
DATE_PATTERN = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}")
SUPPORTED_TEXT = (
    "Supported: a single-client export (no 'type', has 'entries', version 2) and an "
    "all-clients bundle ('type': 'database', has 'profiles', version 2). Also supported: "
    f"an unencrypted full browser backup ('format': 'labcharts-backup', version {BACKUP_VERSION})."
)
LOCKED = (
    "This backup is encrypted: its lab data is still locked with the get-based "
    "passphrase. Unlock or export it from get-based first (a single-client export or an "
    "all-clients bundle); nothing was stored."
)
QUALIFIER = "last import into this date; the model for this value is unknown"
FLAG_TEXT = {
    GetbasedFlag.ORIGIN_UNKNOWN: "origin unknown, check against your report",
    GetbasedFlag.ORIGIN_NOT_SHOWN: "origin not shown in get-based, check against your report",
    GetbasedFlag.AI_READ: "read by an AI model, check against your report",
    GetbasedFlag.MAY_BE_AI_READ: "may have been read by an AI model, check against your report",
}
EDITED_TEXT = "edited in get-based after import"
EDITED_CODE = "edited_after_import"
FORMAT_NAME = {
    "single-client export": "getbased-export",
    "all-clients bundle": "getbased-database",
    BACKUP_KIND: "getbased-labcharts-backup",
}
FORMAT_VERSION = {BACKUP_KIND: BACKUP_VERSION}

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
    return _loads(text, "The file is not valid JSON, so it is not a get-based export.")


def _loads(text: str, failure: str) -> Any:
    def no_constant(_: str) -> NoReturn:
        raise ValueError("non-finite number")

    try:
        return json.loads(text, parse_float=Decimal, parse_constant=no_constant)
    except (ValueError, RecursionError):
        _refuse(failure)


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
    if fmt == "labcharts-backup":
        return _detect_backup(top)
    if fmt == "getbased-migration":
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


def _is_locked(value: Any) -> bool:
    return isinstance(value, str) and value.startswith("v1:")


def _detect_backup(top: dict[str, Any]) -> Container:
    """A `labcharts-backup` v1 (M js/backup.ts:43-49). Only `profiles[].profileId` and
    `profiles[].keys.imported` are read; settings, `profileList`, `encryptionSalt` and the
    side stores are never read, stored or echoed. An encrypted backup is refused."""
    version = top.get("version")
    if not (
        isinstance(version, int)
        and not isinstance(version, bool)
        and version == BACKUP_VERSION
    ):
        _refuse(
            f"The browser backup is version {_short(version) if 'version' in top else 'missing'}; "
            f"the only supported backup version is {BACKUP_VERSION}. {SUPPORTED_TEXT}"
        )
    backup_profiles = top.get("profiles")
    if top.get("encrypted") is True or _is_locked(top.get("profileList")):
        _refuse(LOCKED)
    if (
        not isinstance(backup_profiles, list)
        or not backup_profiles
        or not all(
            isinstance(p, dict)
            and isinstance(p.get("profileId"), str)
            and isinstance(p.get("keys"), dict)
            for p in backup_profiles
        )
    ):
        _refuse(
            "The browser backup ('labcharts-backup') holds no readable profiles. "
            f"{SUPPORTED_TEXT}"
        )
    profiles = [
        {"id": p["profileId"], "imported": p["keys"].get("imported")}
        for p in backup_profiles
    ]
    if any(_is_locked(p["imported"]) for p in profiles):
        _refuse(LOCKED)
    return Container(BACKUP_KIND, profiles, [p["id"] for p in profiles])


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
    if (
        "imported" in profile
    ):  # a browser backup: the raw stored JSON text (M js/data-core.ts:303)
        raw = profile["imported"]
        if raw is None:
            return {}
        if not isinstance(raw, str):
            _refuse("The lab data of this profile in the backup is not readable.")
        data = _loads(
            raw, "The lab data of this profile in the backup is not readable."
        )
        return data if isinstance(data, dict) else {}
    data = profile.get("data")
    return data if isinstance(data, dict) else {}


def _text(value: Any) -> str:
    if isinstance(value, str) and value.strip():
        return value[:MAX_TEXT_CHARS]
    return "unknown"


def _flag_code(source: Any, entry: dict[str, Any]) -> GetbasedFlag:
    """The one origin flag of a value, fail closed (Q92): exempt only when `importedWith`
    positively shows a non-AI path, which the archive cannot show, so none is exempt."""
    if not isinstance(source, dict):
        return GetbasedFlag.ORIGIN_UNKNOWN
    if not (source.get("snapshotId") or source.get("file")):
        return GetbasedFlag.ORIGIN_NOT_SHOWN
    if isinstance(entry.get("importedWith"), dict):
        return GetbasedFlag.AI_READ
    return GetbasedFlag.MAY_BE_AI_READ


def _flags(source: Any, entry: dict[str, Any]) -> list[dict[str, str]]:
    """Per-value provenance flags of the preview."""
    code = _flag_code(source, entry)
    flag = {"code": code.value, "text": FLAG_TEXT[code]}
    if code == GetbasedFlag.AI_READ:
        imported = entry["importedWith"]
        flag.update(
            model_id=_text(imported.get("modelId")),
            provider=_text(imported.get("provider")),
            qualifier=QUALIFIER,
        )
    flags = [flag]
    if isinstance(source, dict) and source.get("manuallyEdited") is True:
        flags.append({"code": EDITED_CODE, "text": EDITED_TEXT})
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


@dataclass(frozen=True)
class Candidate:
    """One matched value, with exactly the archive fields that are stored. Nothing else of
    the entry is carried."""

    value: int | Decimal
    day: date
    mapping: GetbasedMarkerMapping
    source: Any  # the markerSources record of this key, as found
    imported_with: Any  # the entry's importedWith, as found
    flag: GetbasedFlag


def _rows(
    data: dict[str, Any], mappings: dict[str, GetbasedMarkerMapping]
) -> tuple[list[dict[str, Any]], list[Candidate]]:
    rows: list[dict[str, Any]] = []
    candidates: list[Candidate] = []
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
            if status == MATCHED and day is not None:
                candidates.append(
                    Candidate(
                        value,
                        date.fromisoformat(day),
                        mappings[key],
                        sources.get(key),
                        entry.get("importedWith"),
                        _flag_code(sources.get(key), entry),
                    )
                )
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
    return rows, candidates


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


def _mappings() -> dict[str, GetbasedMarkerMapping]:
    return {
        m.getbased_key: m
        for m in GetbasedMarkerMapping.objects.select_related(
            "source", "unit", "biomarker__unit"
        )
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
    rows, _ = _rows(data, _mappings())
    summary = _summary(rows)
    return {
        "status": "preview",
        "container": container.kind,
        "version": FORMAT_VERSION.get(container.kind, SUPPORTED_VERSION),
        "rows": rows,
        "summary": summary,
        "can_confirm": summary["not_recognised"] == 0 and summary["matched"] > 0,
    }


@dataclass(frozen=True)
class ConfirmPlan:
    """What a confirm would store: the matched values, the rows that block it and the
    counts of rows left out."""

    import_format: str
    import_format_version: int
    candidates: list[Candidate]
    not_recognised: list[dict[str, Any]]
    left_out_calculated: int
    left_out_deleted: int


def build_confirm_plan(raw: bytes, profile_id: str | None) -> ConfirmPlan:
    """Parse the upload again with the preview's rules. Raises `GetbasedImportError` for an
    unsupported file or while no profile is chosen. Stores nothing."""
    container = detect(_parse(raw))
    data = _choose(container, profile_id)
    if data is None:
        _refuse("Choose exactly one profile to import: send its profile_id.")
    rows, candidates = _rows(data, _mappings())
    summary = _summary(rows)
    return ConfirmPlan(
        FORMAT_NAME[container.kind],
        FORMAT_VERSION.get(container.kind, SUPPORTED_VERSION),
        candidates,
        [r for r in rows if r["status"] == NOT_RECOGNISED],
        summary["left_out_calculated"],
        summary["left_out_deleted"],
    )


# The archive's own file name can carry the client's name, so a fixed name is stored.
IMPORT_NAME = "getbased-export.json"


def _verbatim(value: Any) -> str | None:
    """Text or number as found (a number such as the `at` milliseconds is kept as its
    digits); booleans and other types are stored as empty."""
    if isinstance(value, bool):
        return None
    if isinstance(value, (str, int, Decimal)):
        return str(value)
    return None


def _known_text(imported: dict[str, Any] | None, key: str) -> str | None:
    text = _text(imported.get(key)) if imported else "unknown"
    return None if text == "unknown" else text


def _provenance(result: LabResult, c: Candidate) -> LabResultGetbasedProvenance:
    """The archive's provenance fields of one value, as found. Nothing is parsed or
    corrected; a field of another type than the format says is stored as empty."""
    source = c.source if isinstance(c.source, dict) else None
    imported = c.imported_with if isinstance(c.imported_with, dict) else None
    reported = source.get("reported") if source else None
    return LabResultGetbasedProvenance(
        result=result,
        has_marker_sources=source is not None,
        ms_reported=reported if isinstance(reported, bool) else None,
        ms_file=_verbatim(source.get("file")) if source else None,
        ms_at=_verbatim(source.get("at")) if source else None,
        ms_snapshot_id=_verbatim(source.get("snapshotId")) if source else None,
        manually_edited=bool(source) and source.get("manuallyEdited") is True,
        imported_with_present=imported is not None,
        imported_with_model_id=_known_text(imported, "modelId"),
        imported_with_provider=_known_text(imported, "provider"),
        flag=c.flag,
        entry_date=c.day,
    )


def store_plan(plan: ConfirmPlan, owner: Any) -> LabReport:
    """Store one report and one result per matched value. Must run inside
    `transaction.atomic`. Every result is `entered` and keeps its provenance; the unit is
    the mapping's cited unit, never read from the archive. `collected_at` stays empty
    (the sample date has no time zone, Q101). Raises `GetbasedImportError` when the shared
    result rules refuse a value, so the caller rolls everything back."""
    report = LabReport(
        owner=owner,
        origin=LabReportOrigin.IMPORT,
        import_name=IMPORT_NAME,
        import_source=LabReportImportSource.GETBASED,
        import_format=plan.import_format,
        import_format_version=plan.import_format_version,
    )
    report.save()
    for c in plan.candidates:
        unit = c.mapping.unit
        if unit is None:  # a matched row always has one
            _refuse("A mapped marker has no cited unit.")
        result = LabResult(
            report=report,
            biomarker=c.mapping.biomarker,
            reported_value=Decimal(str(c.value)),
            reported_unit=unit.ucum_code,
            validation_state=LabResultValidation.ENTERED,
        )
        try:
            result.save()
        except DjangoValidationError as exc:
            _refuse(f"{c.mapping.getbased_key}: {' '.join(exc.messages)}")
        _provenance(result, c).save()
    return report
