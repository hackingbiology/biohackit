# SPDX-License-Identifier: AGPL-3.0-or-later
"""Import of the LOINC core table (Loinc.csv) and the optional ConsumerName and
LinguisticVariants accessory files from user-supplied files (M01 TG-LOINC A, C1).

Column names and file paths were verified from fetched sources, see
docs/ecosystem/m01-terminology.md. Nothing from LOINC is stored in the repository.
"""

import csv
import re
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

from django.conf import settings
from django.db import transaction
from django.db.models import CharField, Model

from terminology.models import (
    LoincConsumerName,
    LoincLinguisticVariant,
    LoincTerm,
    Source,
)

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

CONSUMER_FILE = Path("AccessoryFiles/ConsumerName/ConsumerName.csv")
CONSUMER_KEY = "LoincNumber"
CONSUMER_COLUMNS = {"ConsumerName": "consumer_name"}

VARIANT_DIR = Path("AccessoryFiles/LinguisticVariants")
VARIANT_FILE_PATTERN = re.compile(r"([a-z]{2})([A-Z]{2})[0-9]+LinguisticVariant\.csv")
VARIANT_LANGUAGES = frozenset({"it-IT", "zh-CN"})
VARIANT_COLUMNS = {
    "COMPONENT": "component",
    "SYSTEM": "system",
    "SHORTNAME": "short_name",
    "LONG_COMMON_NAME": "long_common_name",
    "RELATEDNAMES2": "related_names",
    "LinguisticVariantDisplayName": "display_name",
}

ABSENT_HELP = (
    "LOINC release not found in {directory}. Obtain the LOINC release yourself "
    "(licence: https://loinc.org/license/), unpack it, and place Loinc.csv in "
    "data/vendor/loinc/ (git-ignored), or pass the directory: "
    "manage.py import_loinc <dir> --release-version <version>."
)


class LoincImportError(Exception):
    """The release is absent or malformed; nothing was written."""


@dataclass(frozen=True)
class Counts:
    created: int = 0
    updated: int = 0


@dataclass(frozen=True)
class ImportSummary:
    created: int
    updated: int
    consumer_names: Counts = Counts()
    linguistic_variants: Counts = Counts()
    missing_optional: tuple[str, ...] = ()
    skipped_languages: dict[str, int] = field(default_factory=dict)


@dataclass(frozen=True)
class Row:
    line: str
    key: str
    values: dict[str, str]


def find_table(directory: Path) -> Path:
    for candidate in (directory / FILENAME, directory / "LoincTable" / FILENAME):
        if candidate.is_file():
            return candidate
    raise LoincImportError(ABSENT_HELP.format(directory=directory))


def parse_csv(
    path: Path, key_column: str, columns: dict[str, str], model: type[Model]
) -> list[Row]:
    """Return validated rows; raise LoincImportError naming file and line."""
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        header = reader.fieldnames or []
        missing = [c for c in (key_column, *columns) if c not in header]
        if missing:
            raise LoincImportError(f"{path.name} line 1: missing column(s) {missing}")
        rows: list[Row] = []
        for record in reader:
            where = f"{path.name} line {reader.line_num}"
            if None in record or any(v is None for v in record.values()):
                raise LoincImportError(f"{where}: expected {len(header)} fields")
            key = record[key_column].strip()
            if not key:
                raise LoincImportError(f"{where}: empty {key_column}")
            values = {name: record[col].strip() for col, name in columns.items()}
            check_lengths(model, values, where)
            rows.append(Row(where, key, values))
    return rows


def char_limit(model: type[Model], field: str) -> int | None:
    column = model._meta.get_field(field)
    return column.max_length if isinstance(column, CharField) else None


def check_lengths(model: type[Model], values: dict[str, str], where: str) -> None:
    for name, value in values.items():
        limit = char_limit(model, name)
        if limit is not None and len(value) > limit:
            raise LoincImportError(
                f"{where}: {name} is {len(value)} characters, maximum {limit}"
            )


def parse_term_rows(path: Path) -> list[Row]:
    rows = parse_csv(path, KEY, COLUMNS, LoincTerm)
    for row in rows:
        limit = char_limit(LoincTerm, "loinc_num")
        if limit is not None and len(row.key) > limit:
            raise LoincImportError(
                f"{row.line}: loinc_num is {len(row.key)} characters, maximum {limit}"
            )
    return rows


def variant_files(directory: Path) -> tuple[dict[str, Path], dict[str, int]]:
    """Per-language files to import (by language tag) and counts of skipped languages."""
    wanted: dict[str, Path] = {}
    skipped: dict[str, int] = {}
    for path in sorted((directory / VARIANT_DIR).glob("*LinguisticVariant.csv")):
        match = VARIANT_FILE_PATTERN.fullmatch(path.name)
        if match is None:
            continue
        tag = f"{match.group(1)}-{match.group(2)}"
        if tag in VARIANT_LANGUAGES:
            wanted[tag] = path
        else:
            skipped[tag] = skipped.get(tag, 0) + 1
    return wanted, skipped


def resolve_term(row: Row, terms: dict[str, LoincTerm]) -> LoincTerm:
    term = terms.get(row.key)
    if term is None:
        raise LoincImportError(f"{row.line}: unknown LOINC code {row.key!r}")
    return term


def import_consumer_names(
    rows: list[Row], terms: dict[str, LoincTerm], source: Source, replace: bool
) -> Counts:
    """Upsert consumer names. With replace (the file is present), names of the
    release's terms that are not in the file any more are deleted, so a renamed
    consumer name does not leave the old one behind."""
    created = updated = 0
    kept: list[int] = []
    for row in rows:
        obj, was_created = LoincConsumerName.objects.update_or_create(
            term=resolve_term(row, terms),
            consumer_name=row.values["consumer_name"],
            defaults={"source": source},
        )
        kept.append(obj.pk)
        created += was_created
        updated += not was_created
    if replace:
        LoincConsumerName.objects.filter(term__in=terms.values()).exclude(
            pk__in=kept
        ).delete()
    return Counts(created, updated)


def import_variants(
    by_language: dict[str, list[Row]], terms: dict[str, LoincTerm], source: Source
) -> Counts:
    """Upsert variants. For each language file present, variants of the release's
    terms that the file no longer has are deleted (withdrawn labels do not linger)."""
    created = updated = 0
    for language, rows in by_language.items():
        kept: list[int] = []
        for row in rows:
            obj, was_created = LoincLinguisticVariant.objects.update_or_create(
                term=resolve_term(row, terms),
                language=language,
                defaults={**row.values, "source": source},
            )
            kept.append(obj.pk)
            created += was_created
            updated += not was_created
        LoincLinguisticVariant.objects.filter(
            language=language, term__in=terms.values()
        ).exclude(pk__in=kept).delete()
    return Counts(created, updated)


def import_release(directory: Path, release_version: str) -> ImportSummary:
    """Upsert Loinc.csv rows by loinc_num, then the optional accessory files, in one
    transaction. Absent accessory files are reported, not an error."""
    table = find_table(directory)
    if not release_version.strip():
        raise LoincImportError(
            "--release-version is required (e.g. the LOINC release number)"
        )
    version_limit = char_limit(Source, "version")
    if version_limit is not None and len(release_version) > version_limit:
        raise LoincImportError(f"--release-version is longer than {version_limit}")
    rows = parse_term_rows(table)
    missing: list[str] = []
    consumer_rows: list[Row] = []
    consumer_present = (directory / CONSUMER_FILE).is_file()
    if consumer_present:
        consumer_rows = parse_csv(
            directory / CONSUMER_FILE, CONSUMER_KEY, CONSUMER_COLUMNS, LoincConsumerName
        )
    else:
        missing.append(str(CONSUMER_FILE))
    files, skipped = variant_files(directory)
    variant_rows = {
        tag: parse_csv(path, KEY, VARIANT_COLUMNS, LoincLinguisticVariant)
        for tag, path in files.items()
    }
    missing.extend(
        f"{VARIANT_DIR}/{tag} LinguisticVariant file"
        for tag in sorted(VARIANT_LANGUAGES - files.keys())
    )
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
            _, was_created = LoincTerm.objects.update_or_create(
                loinc_num=row.key, defaults={**row.values, "source": source}
            )
            created += was_created
            updated += not was_created
        codes = {row.key for row in rows}
        terms = {t.loinc_num: t for t in LoincTerm.objects.filter(loinc_num__in=codes)}
        consumer = import_consumer_names(
            consumer_rows, terms, source, replace=consumer_present
        )
        variants = import_variants(variant_rows, terms, source)
    return ImportSummary(created, updated, consumer, variants, tuple(missing), skipped)
