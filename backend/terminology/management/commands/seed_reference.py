# SPDX-License-Identifier: AGPL-3.0-or-later
"""`manage.py seed_reference [--dir PATH]`: load sourced JSON seed files (M01 TG5)."""

from pathlib import Path
from typing import Any

from django.core.management.base import BaseCommand, CommandError, CommandParser

from terminology.seed_loader import SEED_DIR, SeedError, load_dir


class Command(BaseCommand):
    help = "Idempotently load JSON seed files; every row must carry a complete Source."

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("--dir", default=str(SEED_DIR), help="seed directory")

    def handle(self, *args: Any, **options: Any) -> None:
        try:
            summary = load_dir(Path(options["dir"]))
        except SeedError as exc:
            raise CommandError(str(exc)) from exc
        for line in summary:
            self.stdout.write(line)
