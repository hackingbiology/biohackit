# SPDX-License-Identifier: AGPL-3.0-or-later
"""Shared fixtures: retained originals go to a temporary private store, never to the real one."""

from collections.abc import Iterator
from pathlib import Path

import pytest
from django.core.files.storage import FileSystemStorage

from core.models import LabReport


@pytest.fixture(autouse=True)
def private_root(tmp_path: Path) -> Iterator[Path]:
    root = tmp_path / "private"
    field = LabReport._meta.get_field("original_file")
    original = field.storage
    field.storage = FileSystemStorage(location=str(root), base_url=None)
    yield root
    field.storage = original
