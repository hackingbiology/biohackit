# SPDX-License-Identifier: AGPL-3.0-or-later
"""`manage.py import_loinc [dir] --release-version V`: import Loinc.csv (M01 TG-LOINC A)."""

from pathlib import Path
from typing import Any

from django.core.management.base import BaseCommand, CommandError, CommandParser

from terminology.loinc_importer import DEFAULT_DIR, LoincImportError, import_release


class Command(BaseCommand):
    help = "Idempotently import the user-supplied LOINC core table (Loinc.csv)."

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("dir", nargs="?", default=str(DEFAULT_DIR))
        parser.add_argument("--release-version", default="")

    def handle(self, *args: Any, **options: Any) -> None:
        try:
            summary = import_release(Path(options["dir"]), options["release_version"])
        except LoincImportError as exc:
            raise CommandError(str(exc)) from exc
        self.stdout.write(
            f"LoincTerm: created {summary.created}, updated {summary.updated}"
        )
