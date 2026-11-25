# SPDX-License-Identifier: AGPL-3.0-or-later
"""`manage.py import_loinc [dir] --release-version V`: import Loinc.csv plus the optional
ConsumerName, it-IT/zh-CN LinguisticVariants, Part and primary part link files
(M01 TG-LOINC A, C1, D1)."""

from pathlib import Path
from typing import Any

from django.core.management.base import BaseCommand, CommandError, CommandParser

from terminology.loinc_importer import DEFAULT_DIR, LoincImportError, import_release


class Command(BaseCommand):
    help = (
        "Idempotently import the user-supplied LOINC core table (Loinc.csv) and the "
        "optional ConsumerName, LinguisticVariants (it-IT, zh-CN), Part and LoincPartLink_Primary "
        "files."
    )

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("dir", nargs="?", default=str(DEFAULT_DIR))
        parser.add_argument("--release-version", default="")

    def handle(self, *args: Any, **options: Any) -> None:
        try:
            summary = import_release(Path(options["dir"]), options["release_version"])
        except LoincImportError as exc:
            raise CommandError(str(exc)) from exc
        out = self.stdout.write
        out(f"LoincTerm: created {summary.created}, updated {summary.updated}")
        names = summary.consumer_names
        out(f"LoincConsumerName: created {names.created}, updated {names.updated}")
        variants = summary.linguistic_variants
        out(
            f"LoincLinguisticVariant: created {variants.created}, "
            f"updated {variants.updated}"
        )
        out(
            f"LoincPart: created {summary.parts.created}, updated {summary.parts.updated}"
        )
        links = summary.part_links
        out(f"LoincPartLink: created {links.created}, updated {links.updated}")
        for language, count in sorted(summary.skipped_languages.items()):
            out(f"Skipped language {language}: {count} file(s) not imported")
        for name in summary.missing_optional:
            out(f"Optional file not found, skipped: {name}")
