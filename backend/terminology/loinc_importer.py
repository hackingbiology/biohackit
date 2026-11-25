# SPDX-License-Identifier: AGPL-3.0-or-later
"""Import of the LOINC core table (Loinc.csv) from user-supplied files (M01 TG-LOINC A).

Column names were verified against the OHDSI Vocabulary-v5.0 staging DDL, see
docs/ecosystem/m01-terminology.md. Nothing from LOINC is stored in the repository.
"""

import csv
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from django.conf import settings
from django.db import transaction
from django.db.models import CharField, Model

from terminology.models import LoincTerm, Source

DEFAULT_DIR = Path(settings.BASE_DIR).parent / "data" / "vendor" / "loinc"
FILENAME = "Loinc.csv"
SOURCE_URL = "https://loinc.org/license/"
SOURCE_LICENCE = "LOINC licence terms unverified (Q10)"

# CSV column -> LoincTerm field
COLUMNS = {
    "COMPONENT": "component",
    "PROPERTY": "property",
    "TIME_ASPCT": "time_aspect",
    "SYSTEM": "system",
    "SCALE_TYP": "scale_type",
    "METHOD_TYP": "method_type",
    "CLASS": "loinc_class",
    "LONG_COMMON_NAME": "long_common_name",
    "SHORTNAME": "short_name",
    "STATUS": "status",
}
KEY = "LOINC_NUM"

ABSENT_HELP = (
    "LOINC release not found in {directory}. Obtain the LOINC release yourself "
    "(licence: https://loinc.org/license/), unpack it, and place Loinc.csv in "
    "data/vendor/loinc/ (git-ignored), or pass the directory: "
    "manage.py import_loinc <dir> --release-version <version>."
)


class LoincImportError(Exception):
    """The release is absent or malformed; nothing was written."""


@dataclass(frozen=True)
class ImportSummary:
    created: int
    updated: int


def find_table(directory: Path) -> Path:
    for candidate in (directory / FILENAME, directory / "LoincTable" / FILENAME):
        if candidate.is_file():
            return candidate
    raise LoincImportError(ABSENT_HELP.format(directory=directory))


def parse_table(path: Path) -> list[dict[str, str]]:
    """Return rows as {loinc_num, <field>: value}; raise on a malformed file."""
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        missing = [c for c in (KEY, *COLUMNS) if c not in (reader.fieldnames or [])]
        if missing:
            raise LoincImportError(f"{path.name} line 1: missing column(s) {missing}")
        width = len(reader.fieldnames or [])
        rows: list[dict[str, str]] = []
        for record in reader:
            where = f"{path.name} line {reader.line_num}"
            if None in record or any(v is None for v in record.values()):
                raise LoincImportError(f"{where}: expected {width} fields")
            loinc_num = record[KEY].strip()
            if not loinc_num:
                raise LoincImportError(f"{where}: empty {KEY}")
            row = {"loinc_num": loinc_num}
            for column, field in COLUMNS.items():
                row[field] = record[column].strip()
            check_lengths(row, where)
            rows.append(row)
    return rows


def char_limit(model: type[Model], field: str) -> int | None:
    column = model._meta.get_field(field)
    return column.max_length if isinstance(column, CharField) else None


def check_lengths(row: dict[str, str], where: str) -> None:
    for field, value in row.items():
        limit = char_limit(LoincTerm, field)
        if limit is not None and len(value) > limit:
            raise LoincImportError(
                f"{where}: {field} is {len(value)} characters, maximum {limit}"
            )


def import_release(directory: Path, release_version: str) -> ImportSummary:
    """Upsert every Loinc.csv row by loinc_num in one transaction."""
    table = find_table(directory)
    if not release_version.strip():
        raise LoincImportError(
            "--release-version is required (e.g. the LOINC release number)"
        )
    version_limit = char_limit(Source, "version")
    if version_limit is not None and len(release_version) > version_limit:
        raise LoincImportError(f"--release-version is longer than {version_limit}")
    rows = parse_table(table)
    created = updated = 0
    with transaction.atomic():
        source, _ = Source.objects.get_or_create(
            name="LOINC",
            version=release_version,
            defaults={
                "licence": SOURCE_LICENCE,
                "url": SOURCE_URL,
                "retrieved_at": date.today(),
            },
        )
        for row in rows:
            loinc_num = row.pop("loinc_num")
            _, was_created = LoincTerm.objects.update_or_create(
                loinc_num=loinc_num, defaults={**row, "source": source}
            )
            created += was_created
            updated += not was_created
    return ImportSummary(created=created, updated=updated)
