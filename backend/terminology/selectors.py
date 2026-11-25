# SPDX-License-Identifier: AGPL-3.0-or-later
from typing import TYPE_CHECKING

from .models import OptimalRange

if TYPE_CHECKING:
    from core.models import Biomarker


def _present(value: str | None) -> bool:
    return bool((value or "").strip())


def _complete(row: OptimalRange, biomarker: "Biomarker") -> bool:
    return (
        row.source_id is not None
        and row.unit_id == biomarker.unit_id
        and _present(row.population)
        and _present(row.endpoint)
        and _present(row.evidence_grade)
        and row.last_reviewed is not None
    )


def displayable_optimal_range(biomarker: "Biomarker") -> OptimalRange | None:
    """The optimal range only if its provenance is complete; None if none is complete
    or if several are (we never guess, Q49)."""
    rows = OptimalRange.objects.filter(biomarker=biomarker)
    complete = [r for r in rows if _complete(r, biomarker)]
    return complete[0] if len(complete) == 1 else None
