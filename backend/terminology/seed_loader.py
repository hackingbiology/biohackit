# SPDX-License-Identifier: AGPL-3.0-or-later
"""Seed-file loader and inspector (M01 TG5 part A). Format: seed/README.md."""

import json
import re
from dataclasses import dataclass
from datetime import date
from decimal import Decimal, InvalidOperation
from fnmatch import fnmatch
from pathlib import Path
from typing import Any

from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.db import DatabaseError, transaction

from core.models import (
    GETBASED_CALCULATED_PREFIX,
    GETBASED_COMMIT_PATTERN,
    Biomarker,
    GetbasedMarkerKind,
    GetbasedMarkerMapping,
)
from terminology.models import Source, Unit, UnitConversion

SEED_DIR = Path(__file__).resolve().parent / "seed"
REQUIRED_SOURCE = ("name", "licence", "url", "retrieved_at")
FIELDS = {
    "unit": {"ucum_code", "display"},
    "unit_conversion": {"from_unit", "to_unit", "factor", "biomarker"},
    "getbased_marker_mapping": {
        "getbased_key",
        "kind",
        "biomarker",
        "unit",
        "unit_source_path",
        "unit_source_commit",
    },
}
MAX_LEN = {
    "ucum_code": 64,
    "display": 100,
    "from_unit": 64,
    "to_unit": 64,
    "biomarker": 64,
    "getbased_key": 200,
    "unit_source_path": 300,
}
MAPPING_CITATION = ("unit", "unit_source_path", "unit_source_commit")
SOURCE_MAX = {"name": 200, "version": 64, "licence": 200, "url": 500}
FACTOR_DECIMALS = 12
FACTOR_INT_DIGITS = 18
RESTRICTED_PATTERNS = ("loinc.csv", "loinctable*", "*snomed*", "sct2_*", "der2_*")


_URL_VALIDATOR = URLValidator(schemes=["http", "https"])


class SeedError(Exception):
    """A seed file or row is invalid; the message names the file and row."""


@dataclass(frozen=True)
class SeedRow:
    model: str
    source: dict[str, Any]
    fields: dict[str, Any]


def _text(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""


def _source_problem(source: Any) -> str | None:
    if not isinstance(source, dict):
        return "missing source"
    for key in REQUIRED_SOURCE:
        if not _text(source.get(key)):
            return f"missing source.{key}"
    try:
        _URL_VALIDATOR(source["url"].strip())
    except ValidationError:
        return "invalid source.url"
    return None


def _parse_factor(value: Any) -> Decimal | None:
    if not isinstance(value, str):
        return None
    try:
        factor = Decimal(value)
    except InvalidOperation:
        return None
    if not factor.is_finite() or factor <= 0:
        return None
    exponent = int(factor.as_tuple().exponent)
    if -exponent > FACTOR_DECIMALS:
        # trailing zeros beyond the column precision are harmless
        factor = factor.normalize()
        if -int(factor.as_tuple().exponent) > FACTOR_DECIMALS:
            return None
    if factor.adjusted() + 1 > FACTOR_INT_DIGITS:
        return None
    return factor


def _check_fields(model: str, fields: dict[str, Any]) -> str | None:
    """Type, blank and length checks on the string-valued fields."""
    for key, limit in MAX_LEN.items():
        if key not in fields:
            continue
        value = fields[key]
        if value is None and key in ("biomarker", *MAPPING_CITATION):
            continue
        if not isinstance(value, str) or not value.strip():
            return f"fields.{key} must be a non-blank string"
        if len(value) > limit:
            return f"fields.{key} is longer than {limit} characters"
    return None


def _mapping_problem(fields: dict[str, Any]) -> str | None:
    """The same rules as GetbasedMarkerMapping.clean() and its CheckConstraints."""
    kind = fields["kind"]
    if kind not in GetbasedMarkerKind.values:
        return "fields.kind must be measured or calculated"
    cited = [fields[key] for key in MAPPING_CITATION]
    if kind == GetbasedMarkerKind.CALCULATED:
        if fields["biomarker"] is not None or any(v is not None for v in cited):
            return (
                "a calculated row must have null biomarker, unit, "
                "unit_source_path and unit_source_commit"
            )
        return None
    if fields["biomarker"] is None:
        return "fields.biomarker is required for a measured row"
    if fields["getbased_key"].startswith(GETBASED_CALCULATED_PREFIX):
        return f"a {GETBASED_CALCULATED_PREFIX} key can only be a calculated row"
    if any(v is not None for v in cited) and any(v is None for v in cited):
        return "unit, unit_source_path and unit_source_commit are set together or not at all"
    commit = fields["unit_source_commit"]
    if commit is not None and not re.fullmatch(GETBASED_COMMIT_PATTERN, commit):
        return "fields.unit_source_commit must be 40 lowercase hex characters"
    return None


def _source_values(src: dict[str, Any]) -> dict[str, Any] | str:
    version = src.get("version")
    if version is not None and not isinstance(version, str):
        return "source.version must be a string"
    for key in REQUIRED_SOURCE:
        if not isinstance(src[key], str):
            return f"source.{key} must be a string"
    values: dict[str, Any] = {
        "name": src["name"].strip(),
        "version": _text(version),
        "licence": src["licence"].strip(),
        "url": src["url"].strip(),
    }
    for key, limit in SOURCE_MAX.items():
        if len(values[key]) > limit:
            return f"source.{key} is longer than {limit} characters"
    try:
        values["retrieved_at"] = date.fromisoformat(src["retrieved_at"].strip())
    except ValueError:
        return "invalid source.retrieved_at (expected ISO date)"
    return values


def _parse_row(raw: Any) -> SeedRow | str:
    """Return a SeedRow, or a message describing the first problem."""
    if not isinstance(raw, dict):
        return "row is not an object"
    problem = _source_problem(raw.get("source"))
    if problem:
        return problem
    src = raw["source"]
    source = _source_values(src)
    if isinstance(source, str):
        return source
    model = raw.get("model")
    if model not in FIELDS:
        return f"unknown model {model!r}"
    fields = raw.get("fields")
    if not isinstance(fields, dict):
        return "missing fields"
    if set(fields) != FIELDS[model]:
        names = sorted(set(fields) ^ FIELDS[model])
        return f"unknown or missing fields: {', '.join(names)}"
    problem = _check_fields(model, fields)
    if problem:
        return problem
    if model == "getbased_marker_mapping":
        problem = _mapping_problem(fields)
        if problem:
            return problem
    if model == "unit_conversion":
        factor = _parse_factor(fields["factor"])
        if factor is None:
            return "factor must be a finite decimal string"
        fields = {**fields, "factor": factor}
    return SeedRow(model, source, fields)


def _read_rows(path: Path) -> list[Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise SeedError(f"{path.name}: cannot read JSON: {exc}") from exc
    rows = data.get("rows") if isinstance(data, dict) else None
    if not isinstance(rows, list):
        raise SeedError(f"{path.name}: expected an object with a 'rows' list")
    return rows


def _parse_file(path: Path) -> list[SeedRow]:
    parsed: list[SeedRow] = []
    for index, raw in enumerate(_read_rows(path)):
        row = _parse_row(raw)
        if isinstance(row, str):
            raise SeedError(f"{path.name} row {index}: {row}")
        parsed.append(row)
    return parsed


def _upsert_source(src: dict[str, Any], where: str) -> Source:
    """Create the Source; refuse to change provenance of an existing (name, version)."""
    defaults = {k: src[k] for k in ("licence", "url", "retrieved_at")}
    source, created = Source.objects.get_or_create(
        name=src["name"], version=src["version"], defaults=defaults
    )
    if not created:
        changed = [k for k, v in defaults.items() if getattr(source, k) != v]
        if changed:
            raise SeedError(
                f"{where}: source {source} already exists with different "
                f"{', '.join(changed)}"
            )
    return source


def _unit(code: Any, where: str, role: str) -> Unit:
    try:
        return Unit.objects.get(ucum_code=code)
    except Unit.DoesNotExist:
        raise SeedError(f"{where}: {role} unit {code!r} does not exist") from None


def _biomarker(code: Any, where: str) -> Biomarker | None:
    if code is None:
        return None
    try:
        return Biomarker.objects.get(loinc_code=code)
    except Biomarker.DoesNotExist:
        raise SeedError(f"{where}: biomarker {code!r} does not exist") from None


def _apply_mapping(f: dict[str, Any], source: Source, where: str) -> bool:
    """Upsert by getbased_key; clean() runs before save, so a row the model refuses is
    never stored."""
    mapping = GetbasedMarkerMapping.objects.filter(
        getbased_key=f["getbased_key"]
    ).first()
    created = mapping is None
    if mapping is None:
        mapping = GetbasedMarkerMapping(getbased_key=f["getbased_key"])
    mapping.kind = f["kind"]
    mapping.source = source
    mapping.biomarker = _biomarker(f["biomarker"], where)
    mapping.unit = None if f["unit"] is None else _unit(f["unit"], where, "mapping")
    mapping.unit_source_path = f["unit_source_path"] or ""
    mapping.unit_source_commit = f["unit_source_commit"] or ""
    try:
        mapping.save()
    except ValidationError as exc:
        raise SeedError(f"{where}: {exc}") from exc
    return created


def _apply_row(row: SeedRow, where: str) -> bool:
    """Upsert one row; return True when it was created."""
    source = _upsert_source(row.source, where)
    f = row.fields
    if row.model == "unit":
        return Unit.objects.update_or_create(
            ucum_code=f["ucum_code"],
            defaults={"display": f["display"], "source": source},
        )[1]
    if row.model == "getbased_marker_mapping":
        return _apply_mapping(f, source, where)
    return UnitConversion.objects.update_or_create(
        from_unit=_unit(f["from_unit"], where, "from"),
        to_unit=_unit(f["to_unit"], where, "to"),
        biomarker=_biomarker(f["biomarker"], where),
        defaults={"factor": f["factor"], "source": source},
    )[1]


def _load_file(path: Path, counts: dict[str, list[int]]) -> None:
    rows = _parse_file(path)
    file_counts: dict[str, list[int]] = {m: [0, 0] for m in FIELDS}
    index = 0
    try:
        with transaction.atomic():
            for index, row in enumerate(rows):
                created = _apply_row(row, f"{path.name} row {index}")
                file_counts[row.model][0 if created else 1] += 1
    except DatabaseError as exc:
        raise SeedError(f"{path.name} row {index}: database error: {exc}") from exc
    for model, (made, updated) in file_counts.items():
        counts[model][0] += made
        counts[model][1] += updated


def _is_restricted(path: Path) -> bool:
    name = path.name.lower()
    return any(fnmatch(name, pattern) for pattern in RESTRICTED_PATTERNS)


def _restricted_files(directory: Path) -> list[str]:
    """Relative paths of restricted releases, at any depth."""
    return [
        p.relative_to(directory).as_posix()
        for p in sorted(directory.rglob("*"))
        if _is_restricted(p)
    ]


def load_dir(directory: Path) -> list[str]:
    """Load every *.json file (sorted); each file is all-or-nothing.

    A licence-restricted filename anywhere in the directory aborts before any write.
    """
    if not directory.is_dir():
        raise SeedError(f"{directory}: not a directory")
    restricted = _restricted_files(directory)
    if restricted:
        raise SeedError(
            f"{restricted[0]}: licence-restricted release must not be bundled"
        )
    counts: dict[str, list[int]] = {m: [0, 0] for m in FIELDS}
    for path in sorted(directory.glob("*.json")):
        _load_file(path, counts)
    return [
        f"{model}: created {c}, updated {u}" for model, (c, u) in sorted(counts.items())
    ]


def _unverified_unit_warnings(name: str, index: int, raw: Any) -> list[str]:
    fields = raw.get("fields") if isinstance(raw, dict) else None
    if (
        isinstance(raw, dict)
        and raw.get("model") == "getbased_marker_mapping"
        and isinstance(fields, dict)
        and fields.get("kind") == GetbasedMarkerKind.MEASURED
        and fields.get("unit") is None
    ):
        key = fields.get("getbased_key")
        return [
            f"{name} row {index}: warning: measured key {key!r} has no unit citation"
        ]
    return []


def inspect_seed_dir(directory: Path) -> list[str]:
    """List problems: restricted release filenames and rows without a complete source."""
    problems: list[str] = []
    for name in _restricted_files(directory):
        problems.append(f"{name}: licence-restricted release must not be bundled")
    for path in sorted(directory.iterdir()):
        if path.suffix != ".json":
            continue
        try:
            rows = _read_rows(path)
        except SeedError as exc:
            problems.append(str(exc))
            continue
        for index, raw in enumerate(rows):
            source = raw.get("source") if isinstance(raw, dict) else None
            problem = _source_problem(source)
            if problem:
                problems.append(f"{path.name} row {index}: {problem}")
            problems.extend(_unverified_unit_warnings(path.name, index, raw))
    return problems
