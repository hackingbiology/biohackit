# SPDX-License-Identifier: AGPL-3.0-or-later
"""CSV lab import in two steps (M02 TG-c part 1). Preview stores nothing; confirm stores one
`LabReport(origin=import)` with its results in one transaction. Rows go through the same
`_create_result` / `LabResult.save` rules as manual entry: nothing is validated twice or
differently, and nothing is guessed (no name matching, no unit inference)."""

import csv
import io
import json
from dataclasses import asdict, dataclass
from typing import Any

from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from rest_framework import status  # type: ignore[import-untyped]  # DRF ships no stubs
from rest_framework.exceptions import ValidationError  # type: ignore[import-untyped]  # DRF ships no stubs
from rest_framework.request import Request  # type: ignore[import-untyped]  # DRF ships no stubs
from rest_framework.response import Response  # type: ignore[import-untyped]  # DRF ships no stubs
from rest_framework.views import APIView  # type: ignore[import-untyped]  # DRF ships no stubs

from .models import LabReport, LabReportOrigin, LabResultValidation
from .redaction import redact_text
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
LABORATORY_MAX = 200
# Opt-in redaction (TG-d part 1). Redacting these columns would change a stored value.
MAX_REDACT_TERMS = 20
MAX_REDACT_TERM_CHARS = 200
MAX_REMOVALS = 1000
STRUCTURED_COLUMNS = ("loinc_code", "value", "unit", "collected_at", "reported_at")


@dataclass(frozen=True)
class CsvLine:
    number: int  # 1-based data line (the header is not counted)
    cells: dict[str, str]
    ragged: bool  # the line has a different number of cells than the header
    blocked: str | None = None  # structured column hit by a redaction term


def _file_error(message: str) -> ValidationError:
    return ValidationError({"file": message})


def upload_name(request: Request) -> str:
    name = str(request.FILES["file"].name)
    if len(name) > IMPORT_NAME_MAX:
        raise _file_error(f"The file name is longer than {IMPORT_NAME_MAX} characters.")
    return name


def _terms_error(message: str) -> ValidationError:
    return ValidationError({"redact_terms": message})


def redact_terms(request: Request) -> list[str]:
    """The optional `redact_terms`: repeated multipart fields, a JSON list in one field, or
    a JSON array in a JSON body. Absent or empty means no redaction."""
    data = request.data
    raw: Any = (
        data.getlist("redact_terms")
        if hasattr(data, "getlist")
        else data.get("redact_terms")
    )
    if (
        isinstance(raw, list)
        and len(raw) == 1
        and isinstance(raw[0], str)
        and raw[0].startswith("[")
    ):
        try:
            raw = json.loads(raw[0])
        except ValueError as exc:
            raise _terms_error("Send a list of strings.") from exc
    if raw is None:
        return []
    if not isinstance(raw, list) or not all(isinstance(t, str) for t in raw):
        raise _terms_error("Send a list of strings.")
    if len(raw) > MAX_REDACT_TERMS:
        raise _terms_error(f"Use at most {MAX_REDACT_TERMS} terms.")
    if any(not t.strip() for t in raw):
        raise _terms_error("A term must not be empty or whitespace-only.")
    if any(len(t) > MAX_REDACT_TERM_CHARS for t in raw):
        raise _terms_error(f"A term is longer than {MAX_REDACT_TERM_CHARS} characters.")
    return list(raw)


def _redact(
    value: str, terms: list[str], where: dict[str, Any], removals: list[dict[str, Any]]
) -> str:
    """Redact one field; the removals (offsets relative to the field) join `removals`."""
    result = redact_text(value, terms)
    removals.extend({**where, **asdict(r)} for r in result.removals)
    if len(removals) > MAX_REMOVALS:
        raise _terms_error(
            f"The terms match more than {MAX_REMOVALS} places in the file."
        )
    return result.redacted


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


def _check_redacted_bounds(lines: list[CsvLine]) -> None:
    """Same limits after redaction: the placeholder can be longer than the term, so the
    overflow is caused by `redact_terms`, not by the file."""
    for line in lines:
        for column, limit in FIELD_LIMITS.items():
            if len(line.cells.get(column, "").strip()) > limit:
                raise _terms_error(
                    f"After redaction row {line.number}: {column} is longer than "
                    f"{limit} characters."
                )


def _redact_line(
    number: int,
    header: list[str],
    cells: list[str],
    terms: list[str],
    removals: list[dict[str, Any]],
) -> CsvLine:
    """Redact each cell of a data line. A hit in a structured column blocks the row: the
    value is never silently changed."""
    out = list(cells)
    blocked: str | None = None
    for i, column in enumerate(header[: len(cells)]):
        before = len(removals)
        # The stripped cell is what the bounds check measures and the rules store, so it is
        # also what is scanned (offsets are relative to it).
        out[i] = _redact(
            cells[i].strip(), terms, {"row": number, "column": column}, removals
        )
        if len(removals) > before and column in STRUCTURED_COLUMNS and blocked is None:
            blocked = column
    return CsvLine(
        number, dict(zip(header, out, strict=False)), len(cells) != len(header), blocked
    )


def read_lines(
    request: Request, terms: list[str] | None = None
) -> tuple[list[CsvLine], list[dict[str, Any]]]:
    """The data lines of the uploaded file and the redaction removals (none without
    `terms`). A file-level problem (size, encoding, header, row count, field length)
    raises a 400 naming it, before anything is evaluated."""
    terms = terms or []
    removals: list[dict[str, Any]] = []
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
        raw = [
            (n, cells)
            for n, cells in enumerate(reader, start=1)
            if any(cell.strip() for cell in cells)
        ]
    except csv.Error as exc:
        raise _file_error(f"The file is not valid CSV: {exc}") from exc
    # Bounds on the raw lines first, so redaction never runs on an oversized file.
    _check_bounds(
        [CsvLine(n, dict(zip(header, c, strict=False)), False) for n, c in raw]
    )
    lines = [_redact_line(n, header, c, terms, removals) for n, c in raw]
    if terms:
        _check_redacted_bounds(lines)
    return lines, removals


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
    if line.blocked:
        row["reason"] = (
            f"{line.blocked}: matches a redaction term; the value is not changed. "
            "Remove the term from the list or fix the file."
        )
        return row
    if line.ragged:
        row["reason"] = "row: the number of cells differs from the header."
        return row
    try:
        with transaction.atomic():
            result = _create_result(
                report, _item(line), LabResultValidation.USER_CONFIRMED
            )
    except (DjangoValidationError, ValidationError) as exc:
        row["reason"] = _reason(exc)
        return row
    row["status"] = "recognised"
    row["plausibility"] = _plausibility(result)
    return row


def _report_laboratory(request: Request) -> str | None:
    return _text(request.data.get("laboratory"), "laboratory")


def _evaluate_all(
    request: Request, lines: list[CsvLine], name: str, laboratory: str | None
) -> tuple[LabReport, list[dict[str, Any]]]:
    """Must run inside `transaction.atomic`; the caller decides to keep or discard."""
    report = LabReport(
        owner=request.user,
        origin=LabReportOrigin.IMPORT,
        import_name=name,
        laboratory=laboratory,
    )
    report.save()
    return report, [_evaluate(report, line) for line in lines]


def _prepare(
    request: Request,
) -> tuple[list[CsvLine], str, str | None, list[dict[str, Any]]]:
    """Lines, file name and report laboratory with the opt-in redaction applied, plus every
    removal. Without `redact_terms` nothing changes."""
    terms = redact_terms(request)
    lines, removals = read_lines(request, terms)
    name = upload_name(request)
    laboratory = _report_laboratory(request)
    name = _redact(name, terms, {"row": None, "column": "import_name"}, removals)
    if laboratory is not None:
        laboratory = _redact(
            laboratory, terms, {"row": None, "column": "laboratory"}, removals
        )
    if terms and len(name) > IMPORT_NAME_MAX:
        raise _terms_error(
            f"After redaction the file name is longer than {IMPORT_NAME_MAX} characters."
        )
    if terms and laboratory is not None and len(laboratory) > LABORATORY_MAX:
        raise _terms_error(
            f"After redaction the laboratory is longer than {LABORATORY_MAX} characters."
        )
    return lines, name, laboratory, removals


class CsvPreviewView(APIView):  # type: ignore[misc]  # base is Any: DRF untyped
    """POST: every row with its status. Nothing is stored: the evaluation runs in a
    transaction that is always rolled back."""

    http_method_names = ["post", "options"]

    def post(self, request: Request) -> Response:
        lines, name, laboratory, removals = _prepare(request)
        with transaction.atomic():
            _, rows = _evaluate_all(request, lines, name, laboratory)
            transaction.set_rollback(True)
        body: dict[str, Any] = {"rows": rows}
        if redact_terms(request):
            body["redaction"] = {"applied": True, "removals": removals}
        else:
            body["redaction"] = {"applied": False, "removals": []}
        return Response(body)


class CsvConfirmView(APIView):  # type: ignore[misc]  # base is Any: DRF untyped
    """POST: the same file again. 400 with the not-recognised rows, storing nothing, or
    201 with one `LabReport(origin=import)` and its results, stored in one transaction."""

    http_method_names = ["post", "options"]

    def post(self, request: Request) -> Response:
        lines, name, laboratory, _ = _prepare(request)
        with transaction.atomic():
            report, rows = _evaluate_all(request, lines, name, laboratory)
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
