# SPDX-License-Identifier: AGPL-3.0-or-later
"""Load an owner's stored intake constraints for the allocator (M04 TG-c)."""

from dataclasses import dataclass

from accounts.models import User
from protocols.allocation import Constraint, ConstraintKind, is_sourced
from protocols.models import IntakeConstraint


@dataclass(frozen=True)
class OwnerConstraints:
    enforced: tuple[Constraint, ...]
    unsourced: tuple[Constraint, ...]


def to_allocation_constraint(row: IntakeConstraint) -> Constraint:
    return Constraint(
        id=row.pk,
        kind=ConstraintKind(row.kind),
        substance_a=row.substance_a_id,
        substance_b=row.substance_b_id,
        minutes=row.minutes,
        source=row.source,
    )


def load_owner_constraints(owner: User) -> OwnerConstraints:
    """Only a constraint with a non-blank source is enforced; the rest are listed."""
    rows = IntakeConstraint.objects.filter(owner=owner).order_by("id")
    converted = [to_allocation_constraint(r) for r in rows]
    return OwnerConstraints(
        enforced=tuple(c for c in converted if is_sourced(c)),
        unsourced=tuple(c for c in converted if not is_sourced(c)),
    )
