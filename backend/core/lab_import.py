# SPDX-License-Identifier: AGPL-3.0-or-later
"""CSV lab import in two steps (M02 TG-c part 1). Preview stores nothing; confirm stores one
`LabReport(origin=import)` with its results in one transaction. Rows go through the same
`_create_result` / `LabResult.save` rules as manual entry: nothing is validated twice or
differently, and nothing is guessed (no name matching, no unit inference)."""

import csv
import io
from dataclasses import dataclass
from typing import Any

from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from rest_framework import status  # type: ignore[import-untyped]  # DRF ships no stubs
from rest_framework.exceptions import ValidationError  # type: ignore[import-untyped]  # DRF ships no stubs
from rest_framework.request import Request  # type: ignore[import-untyped]  # DRF ships no stubs
from rest_framework.response import Response  # type: ignore[import-untyped]  # DRF ships no stubs
from rest_framework.views import APIView  # type: ignore[import-untyped]  # DRF ships no stubs

from .models import LabReport, LabReportOrigin, LabResultValidation
from .views import (
    MAX_REPORTED_VALUE_CHARS,
    _create_result,
    _field_errors,
    _plausibility,
    _report_data,
    _text,
)

REQUIRED_COLUMNS = ("loinc_code", "value", "unit")
OPTIONAL_COLUMNS = ("collected_at", "reported_at", "laboratory", "method")
HEADER = REQUIRED_COLUMNS + OPTIONAL_COLUMNS
# Abuse protection (Q71), consistent with Q70.
MAX_FILE_BYTES = 1024 * 1024
MAX_ROWS = 200
FIELD_LIMITS = {
    "loinc_code": 64,
    "value": MAX_REPORTED_VALUE_CHARS,
    "unit": 64,
    "collected_at": 64,
    "reported_at": 64,
    "laboratory": 200,
    "method": 200,
}
# CSV column -> name used by the shared manual-entry rules
FIELD_OF = {"value": "reported_value", "unit": "reported_unit"}
COLUMN_OF = {v: k for k, v in FIELD_OF.items()}
IMPORT_NAME_MAX = 200


@dataclass(frozen=True)
class CsvLine:
    number: int  # 1-based data line (the header is not counted)
    cells: dict[str, str]
    ragged: bool  # the line has a different number of cells than the header


def _file_error(message: str) -> ValidationError:
    return ValidationError({"file": message})


def upload_name(request: Request) -> str:
    name = str(request.FILES["file"].name)
    if len(name) > IMPORT_NAME_MAX:
        raise _file_error(f"The file name is longer than {IMPORT_NAME_MAX} characters.")
    return name


def _check_header(header: list[str]) -> None:
    if (
        len(set(header)) != len(header)
        or any(h not in HEADER for h in header)
        or any(c not in header for c in REQUIRED_COLUMNS)
    ):
        raise _file_error(
            f"Unexpected header {','.join(header)!r}. Use columns from "
            f"{','.join(HEADER)}; the first three are required."
        )


def _check_bounds(lines: list[CsvLine]) -> None:
    if len(lines) > MAX_ROWS:
        raise _file_error(f"The file has more than {MAX_ROWS} data rows.")
    for line in lines:
        for column, limit in FIELD_LIMITS.items():
            if len(line.cells.get(column, "").strip()) > limit:
                raise _file_error(
                    f"Row {line.number}: {column} is longer than {limit} characters."
                )


def read_lines(request: Request) -> list[CsvLine]:
    """The data lines of the uploaded file. A file-level problem (size, encoding, header,
    row count, field length) raises a 400 naming it, before anything is evaluated."""
    upload = request.FILES.get("file")
    if upload is None:
        raise _file_error("Send the CSV as the multipart field 'file'.")
    if upload.size > MAX_FILE_BYTES:
        raise _file_error(f"The file is larger than {MAX_FILE_BYTES} bytes (1 MiB).")
    try:
        text = upload.read().decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise _file_error("The file must be UTF-8 text.") from exc
    try:
        reader = csv.reader(io.StringIO(text, newline=""))
        header = [h.strip() for h in next(reader, [])]
        _check_header(header)
        lines = [
            CsvLine(
                n, dict(zip(header, cells, strict=False)), len(cells) != len(header)
            )
            for n, cells in enumerate(reader, start=1)
            if any(cell.strip() for cell in cells)
        ]
    except csv.Error as exc:
        raise _file_error(f"The file is not valid CSV: {exc}") from exc
    _check_bounds(lines)
    return lines


def _reason(exc: Any) -> str:
    """First field error as '<column>: <message>'."""
    errors = _field_errors(exc)
    key, messages = next(iter(errors.items()))
    column = COLUMN_OF.get(key, key)
    message = messages[0] if isinstance(messages, list) else messages
    return str(message) if key == "non_field_errors" else f"{column}: {message}"


def _item(line: CsvLine) -> dict[str, Any]:
    """The cells as the payload of the manual-entry rules; an empty cell is absent."""

    def cell(name: str) -> str | None:
        return line.cells.get(name, "").strip() or None

    return {
        "loinc_code": cell("loinc_code"),
        "reported_value": cell("value"),
        "reported_unit": cell("unit"),
        "laboratory": cell("laboratory"),
        "method": cell("method"),
        "collected_at": cell("collected_at"),
        "reported_at": cell("reported_at"),
    }


def _evaluate(report: LabReport, line: CsvLine) -> dict[str, Any]:
    """Store the line as a result of `report` inside a savepoint; the row dict says whether
    the shared rules accepted it. A rejected row leaves nothing behind."""
    row: dict[str, Any] = {
        "row": line.number,
        "status": "not_recognised",
        "reason": "",
        "loinc_code": line.cells.get("loinc_code", "").strip(),
        "value": line.cells.get("value", "").strip(),
        "unit": line.cells.get("unit", "").strip(),
        "plausibility": None,
    }
    if line.ragged:
        row["reason"] = "row: the number of cells differs from the header."
        return row
    try:
        with transaction.atomic():
            result = _create_result(report, _item(line), LabResultValidation.REVIEWED)
    except (DjangoValidationError, ValidationError) as exc:
        row["reason"] = _reason(exc)
        return row
    row["status"] = "recognised"
    row["plausibility"] = _plausibility(result)
    return row


def _report_laboratory(request: Request) -> str | None:
    return _text(request.data.get("laboratory"), "laboratory")


def _evaluate_all(
    request: Request, lines: list[CsvLine], name: str
) -> tuple[LabReport, list[dict[str, Any]]]:
    """Must run inside `transaction.atomic`; the caller decides to keep or discard."""
    report = LabReport(
        owner=request.user,
        origin=LabReportOrigin.IMPORT,
        import_name=name,
        laboratory=_report_laboratory(request),
    )
    report.save()
    return report, [_evaluate(report, line) for line in lines]


class CsvPreviewView(APIView):  # type: ignore[misc]  # base is Any: DRF untyped
    """POST: every row with its status. Nothing is stored: the evaluation runs in a
    transaction that is always rolled back."""

    http_method_names = ["post", "options"]

    def post(self, request: Request) -> Response:
        lines = read_lines(request)
        name = upload_name(request)
        with transaction.atomic():
            _, rows = _evaluate_all(request, lines, name)
            transaction.set_rollback(True)
        return Response({"rows": rows})


class CsvConfirmView(APIView):  # type: ignore[misc]  # base is Any: DRF untyped
    """POST: the same file again. 400 with the not-recognised rows, storing nothing, or
    201 with one `LabReport(origin=import)` and its results, stored in one transaction."""

    http_method_names = ["post", "options"]

    def post(self, request: Request) -> Response:
        lines = read_lines(request)
        name = upload_name(request)
        with transaction.atomic():
            report, rows = _evaluate_all(request, lines, name)
            bad = [r for r in rows if r["status"] != "recognised"]
            if bad or not rows:
                transaction.set_rollback(True)
        if bad:
            return Response(
                {
                    "detail": "Some rows are not recognised; nothing was stored. "
                    "Rows: " + ", ".join(str(r["row"]) for r in bad),
                    "rows": bad,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not rows:
            raise _file_error("The file has no data rows.")
        return Response(_report_data(report), status=status.HTTP_201_CREATED)
