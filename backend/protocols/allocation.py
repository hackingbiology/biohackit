# SPDX-License-Identifier: AGPL-3.0-or-later
"""Deterministic daily allocation of intakes into day slots (M04 TG-c).

Plain backtracking written here: no solver, no randomness, no database. Inputs are sorted
canonically, so the same input in any order gives the same result. A constraint without
a cited source is listed in `unsourced` and is never enforced (Q154). A slot counts as
having fat only when `marked_has_fat` is True; nothing is inferred.
"""

from dataclasses import dataclass
from enum import StrEnum

MINUTES_PER_DAY = 24 * 60


class MealRequirement(StrEnum):
    WITH_MEAL = "with_meal"
    AWAY_FROM_MEALS = "away_from_meals"
    NEEDS_FAT = "needs_fat"
    NONE = "none"


class ConstraintKind(StrEnum):
    SEPARATE_SLOTS = "separate_slots"
    MIN_DISTANCE_MINUTES = "min_distance_minutes"


class FlagCode(StrEnum):
    MISSING_FATTY_MEAL = "missing_fatty_meal"
    MISSING_MEAL = "missing_meal"
    NO_SLOT = "no_slot"
    CONFLICT = "conflict"


@dataclass(frozen=True)
class Intake:
    key: str
    substance_id: int
    meal_requirement: MealRequirement = MealRequirement.NONE


@dataclass(frozen=True)
class Slot:
    key: str
    minute_of_day: int
    is_meal: bool = False
    marked_has_fat: bool = False

    def __post_init__(self) -> None:
        if not 0 <= self.minute_of_day < MINUTES_PER_DAY:
            raise ValueError(f"slot {self.key!r}: minute_of_day out of range")


@dataclass(frozen=True)
class Constraint:
    """`substance_b` None means food: the distance is measured from meal slots."""

    id: int
    kind: ConstraintKind
    substance_a: int
    substance_b: int | None
    minutes: int | None
    source: str

    def __post_init__(self) -> None:
        if self.kind == ConstraintKind.SEPARATE_SLOTS:
            if self.minutes is not None or self.substance_b is None:
                raise ValueError(
                    f"constraint {self.id}: separate_slots needs substance_b, no minutes"
                )
        elif self.minutes is None or self.minutes <= 0:
            raise ValueError(f"constraint {self.id}: minutes must be positive")


@dataclass(frozen=True)
class Assignment:
    intake_key: str
    slot_key: str


@dataclass(frozen=True)
class Separation:
    """Two placements kept apart by `constraint_id`; `other_intake_key` None = a meal slot."""

    constraint_id: int
    intake_key: str
    slot_key: str
    other_intake_key: str | None
    other_slot_key: str


@dataclass(frozen=True)
class Flag:
    code: FlagCode
    intake_key: str | None = None
    constraint_ids: tuple[int, ...] = ()


@dataclass(frozen=True)
class AllocationResult:
    assignments: tuple[Assignment, ...]
    separations: tuple[Separation, ...]
    unsourced: tuple[int, ...]
    flags: tuple[Flag, ...]


def is_sourced(constraint: Constraint) -> bool:
    return bool(constraint.source.strip())


def _unique(keys: list[object], what: str) -> None:
    if len(set(keys)) != len(keys):
        raise ValueError(f"duplicate {what}")


def _candidates(
    intake: Intake, slots: list[Slot]
) -> tuple[list[Slot], FlagCode | None]:
    req = intake.meal_requirement
    if not slots:
        return [], FlagCode.NO_SLOT
    if req == MealRequirement.NEEDS_FAT:
        fatty = [s for s in slots if s.is_meal and s.marked_has_fat]
        return fatty, None if fatty else FlagCode.MISSING_FATTY_MEAL
    if req == MealRequirement.WITH_MEAL:
        meals = [s for s in slots if s.is_meal]
        return meals, None if meals else FlagCode.MISSING_MEAL
    if req == MealRequirement.AWAY_FROM_MEALS:
        away = [s for s in slots if not s.is_meal]
        return away, None if away else FlagCode.NO_SLOT
    return list(slots), None


def _distance(x: Slot, y: Slot) -> int:
    """Circular minutes between two slots: the schedule repeats daily, so 23:30 and 00:30 are 60 apart."""
    d = abs(x.minute_of_day - y.minute_of_day)
    return min(d, MINUTES_PER_DAY - d)


def _pair_applies(c: Constraint, a: Intake, b: Intake) -> bool:
    if c.substance_b is None:
        return False
    return {a.substance_id, b.substance_id} == {c.substance_a, c.substance_b}


def _pair_ok(c: Constraint, s: Slot, t: Slot) -> bool:
    if c.kind == ConstraintKind.SEPARATE_SLOTS:
        return s.key != t.key and _distance(s, t) > 0
    assert c.minutes is not None
    return _distance(s, t) >= c.minutes


def _meal_distance_ok(c: Constraint, s: Slot, slots: list[Slot]) -> bool:
    assert c.minutes is not None
    return all(_distance(s, m) >= c.minutes for m in slots if m.is_meal)


def _solve(
    intakes: list[Intake],
    cands: dict[str, list[Slot]],
    slots: list[Slot],
    rules: list[Constraint],
) -> dict[str, Slot] | None:
    food = [c for c in rules if c.substance_b is None]
    placed: dict[str, Slot] = {}
    by_key = {i.key: i for i in intakes}

    def fits(intake: Intake, slot: Slot) -> bool:
        for c in food:
            if c.substance_a == intake.substance_id and not _meal_distance_ok(
                c, slot, slots
            ):
                return False
        for other_key, other_slot in placed.items():
            other = by_key[other_key]
            for c in rules:
                if _pair_applies(c, intake, other) and not _pair_ok(
                    c, slot, other_slot
                ):
                    return False
        return True

    def step(index: int) -> bool:
        if index == len(intakes):
            return True
        intake = intakes[index]
        for slot in cands[intake.key]:
            if fits(intake, slot):
                placed[intake.key] = slot
                if step(index + 1):
                    return True
                del placed[intake.key]
        return False

    return placed if step(0) else None


def _minimal_conflict(
    intakes: list[Intake],
    cands: dict[str, list[Slot]],
    slots: list[Slot],
    rules: list[Constraint],
) -> tuple[int, ...]:
    """Deletion filter: drop each rule in id order unless the rest then becomes solvable."""
    kept = list(rules)
    for c in rules:
        rest = [r for r in kept if r is not c]
        if _solve(intakes, cands, slots, rest) is None:
            kept = rest
    return tuple(c.id for c in kept)


def _separations(
    placed: dict[str, Slot],
    intakes: list[Intake],
    rules: list[Constraint],
    slots: list[Slot],
) -> tuple[Separation, ...]:
    found: list[Separation] = []
    for c in rules:
        if c.substance_b is None:
            for i in intakes:
                if i.substance_id == c.substance_a:
                    found.extend(
                        Separation(c.id, i.key, placed[i.key].key, None, m.key)
                        for m in slots
                        if m.is_meal
                    )
            continue
        for n, i in enumerate(intakes):
            for j in intakes[n + 1 :]:
                if _pair_applies(c, i, j):
                    found.append(
                        Separation(
                            c.id, i.key, placed[i.key].key, j.key, placed[j.key].key
                        )
                    )
    return tuple(found)


def allocate(
    intakes: list[Intake] | tuple[Intake, ...],
    slots: list[Slot] | tuple[Slot, ...],
    constraints: list[Constraint] | tuple[Constraint, ...],
) -> AllocationResult:
    """Place intakes into slots. On an unresolvable conflict nothing is placed."""
    _unique([i.key for i in intakes], "intake key")
    _unique([s.key for s in slots], "slot key")
    _unique([c.id for c in constraints], "constraint id")
    ordered_intakes = sorted(intakes, key=lambda i: i.key)
    ordered_slots = sorted(slots, key=lambda s: (s.minute_of_day, s.key))
    ordered_rules = sorted(constraints, key=lambda c: c.id)
    unsourced = tuple(c.id for c in ordered_rules if not is_sourced(c))
    rules = [c for c in ordered_rules if is_sourced(c)]

    flags: list[Flag] = []
    cands: dict[str, list[Slot]] = {}
    placeable: list[Intake] = []
    for intake in ordered_intakes:
        found, flag = _candidates(intake, ordered_slots)
        if flag is not None:
            flags.append(Flag(flag, intake.key))
        else:
            cands[intake.key] = found
            placeable.append(intake)

    placed = _solve(placeable, cands, ordered_slots, rules)
    if placed is None:
        ids = _minimal_conflict(placeable, cands, ordered_slots, rules)
        flags.append(Flag(FlagCode.CONFLICT, None, ids))
        return AllocationResult((), (), unsourced, tuple(flags))
    return AllocationResult(
        tuple(Assignment(i.key, placed[i.key].key) for i in placeable),
        _separations(placed, placeable, rules, ordered_slots),
        unsourced,
        tuple(flags),
    )
