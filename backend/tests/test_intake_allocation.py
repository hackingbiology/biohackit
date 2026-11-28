# SPDX-License-Identifier: AGPL-3.0-or-later
"""Deterministic daily allocation (M04 TG-c). Synthetic values only."""

import random
from pathlib import Path

import pytest
from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.db import IntegrityError, transaction

from accounts.models import User
from protocols.allocation import (
    Constraint,
    ConstraintKind,
    FlagCode,
    Intake,
    MealRequirement,
    Slot,
    allocate,
)
from protocols.constraints import load_owner_constraints
from protocols.models import IntakeConstraint
from substances.models import Substance

BREAKFAST = Slot("breakfast", 480, is_meal=True)
FATTY_LUNCH = Slot("lunch", 750, is_meal=True, marked_has_fat=True)
EVENING = Slot("evening", 1260)
SLOTS = [BREAKFAST, FATTY_LUNCH, EVENING]

CITE = "synthetic citation"


def sep(cid: int, a: int, b: int | None, source: str = CITE) -> Constraint:
    return Constraint(cid, ConstraintKind.SEPARATE_SLOTS, a, b, None, source)


def dist(
    cid: int, a: int, b: int | None, minutes: int, source: str = CITE
) -> Constraint:
    return Constraint(cid, ConstraintKind.MIN_DISTANCE_MINUTES, a, b, minutes, source)


def slot_of(result, key: str) -> str | None:
    return next((a.slot_key for a in result.assignments if a.intake_key == key), None)


def test_same_input_same_schedule() -> None:
    # scenario: pills-management::same-input-same-schedule
    intakes = [
        Intake("c", 3),
        Intake("a", 1, MealRequirement.WITH_MEAL),
        Intake("b", 2, MealRequirement.AWAY_FROM_MEALS),
    ]
    rules = [sep(2, 1, 3), dist(1, 2, 3, 120)]
    first = allocate(intakes, SLOTS, rules)
    assert first == allocate(intakes, SLOTS, rules)
    for seed in range(5):
        rng = random.Random(seed)
        i2, s2, r2 = intakes[:], SLOTS[:], rules[:]
        rng.shuffle(i2)
        rng.shuffle(s2)
        rng.shuffle(r2)
        assert allocate(i2, s2, r2) == first
    assert first.separations
    assert all(s.constraint_id is not None for s in first.separations)


def test_unsourced_constraint_is_listed_not_enforced() -> None:
    # scenario: pills-management::unsourced-constraint-is-listed-not-enforced
    intakes = [Intake("a", 1), Intake("b", 2)]
    without = allocate(intakes, SLOTS, [])
    for blank in ("", "   \n\t"):
        result = allocate(intakes, SLOTS, [sep(7, 1, 2, blank)])
        assert result.unsourced == (7,)
        assert result.assignments == without.assignments
        assert result.separations == ()
    assert slot_of(without, "a") == slot_of(without, "b")


def test_no_constraint_is_seeded(db) -> None:
    # scenario: pills-management::no-constraint-is-seeded
    assert IntakeConstraint.objects.count() == 0
    call_command("seed_reference")
    call_command("seed_demo")
    assert IntakeConstraint.objects.count() == 0
    root = Path(__file__).resolve().parents[2]
    backend = root / "backend"
    sources = [
        *(backend / "protocols/migrations").glob("*.py"),
        *backend.glob("*/management/commands/*.py"),
    ]
    assert sources
    for base in (backend / "tests/fixtures", root / "fixtures"):
        if base.exists():
            sources.extend(p for p in base.rglob("*") if p.is_file())
    for path in sources:
        text = path.read_text(errors="ignore").lower()
        if path.parent.name == "migrations" and path.name.startswith("0007"):
            assert "runpython" not in text and "bulk_create" not in text
        else:
            assert "intakeconstraint" not in text, path


def test_no_meal_marked_as_containing_fat() -> None:
    # scenario: pills-management::no-meal-marked-as-containing-fat
    slots = [BREAKFAST, EVENING]
    result = allocate([Intake("d", 1, MealRequirement.NEEDS_FAT)], slots, [])
    assert result.assignments == ()
    assert [(f.code, f.intake_key) for f in result.flags] == [
        (FlagCode.MISSING_FATTY_MEAL, "d")
    ]


def test_fat_soluble_compound_with_a_fatty_meal() -> None:
    # scenario: pills-management::fat-soluble-compound-with-a-fatty-meal
    intakes = [
        Intake("d", 1, MealRequirement.NEEDS_FAT),
        Intake("e", 2, MealRequirement.AWAY_FROM_MEALS),
    ]
    result = allocate(intakes, SLOTS, [])
    assert slot_of(result, "d") == "lunch"
    assert slot_of(result, "e") == "evening"
    assert result.flags == ()


def test_competing_compounds_separated() -> None:
    # scenario: pills-management::competing-compounds-separated
    result = allocate([Intake("a", 1), Intake("b", 2)], SLOTS, [sep(5, 1, 2)])
    assert slot_of(result, "a") != slot_of(result, "b")
    assert [
        (s.constraint_id, s.intake_key, s.other_intake_key) for s in result.separations
    ] == [(5, "a", "b")]


def test_separation_needs_different_time_not_just_different_key() -> None:
    # scenario: pills-management::competing-compounds-separated
    twins = [Slot("x", 600), Slot("y", 600)]
    result = allocate([Intake("a", 1), Intake("b", 2)], twins, [sep(5, 1, 2)])
    assert result.assignments == ()
    assert [f.code for f in result.flags] == [FlagCode.CONFLICT]
    assert result.flags[0].constraint_ids == (5,)


def test_distance_respected_or_flagged() -> None:
    # scenario: pills-management::distance-respected-or-flagged
    intakes = [Intake("a", 1), Intake("b", 2)]
    ok = allocate(intakes, SLOTS, [dist(1, 1, 2, 600)])
    times = {s.key: s.minute_of_day for s in SLOTS}
    assert abs(times[slot_of(ok, "a")] - times[slot_of(ok, "b")]) >= 600
    bad = allocate(
        intakes, SLOTS, [dist(1, 1, 2, 600), dist(2, 1, 2, 1000), dist(3, 9, 8, 5)]
    )
    assert bad.assignments == ()
    conflict = [f for f in bad.flags if f.code == FlagCode.CONFLICT]
    assert len(conflict) == 1
    assert conflict[0].constraint_ids == (2,)


def test_distance_wraps_midnight() -> None:
    slots = [Slot("late", 1410), Slot("early", 30), Slot("noon", 720)]
    intakes = [Intake("a", 1), Intake("b", 2)]
    result = allocate(intakes, slots, [dist(1, 1, 2, 240)])
    assert {slot_of(result, "a"), slot_of(result, "b")} != {"late", "early"}
    assert "noon" in {slot_of(result, "a"), slot_of(result, "b")}
    only = allocate(intakes, slots[:2], [dist(1, 1, 2, 240)])
    assert only.assignments == ()
    assert only.flags[0].constraint_ids == (1,)


def test_food_distance_and_away_from_meals() -> None:
    result = allocate(
        [Intake("a", 1), Intake("m", 2, MealRequirement.AWAY_FROM_MEALS)],
        SLOTS,
        [dist(4, 1, None, 480)],
    )
    assert slot_of(result, "a") == "evening"
    assert slot_of(result, "m") not in {"breakfast", "lunch"}
    assert {s.other_slot_key for s in result.separations} == {"breakfast", "lunch"}


def test_invalid_inputs_refused() -> None:
    with pytest.raises(ValueError):
        allocate([Intake("a", 1), Intake("a", 2)], SLOTS, [])
    with pytest.raises(ValueError):
        dist(1, 1, 2, 0)
    with pytest.raises(ValueError):
        Slot("x", 2000)


@pytest.fixture
def owner(db) -> User:
    return User.objects.create_user(email="o@example.com", password="correct-horse-9")


def make(
    owner: User, a: Substance, b: Substance | None, kind: str, minutes, source: str
):
    return IntakeConstraint(
        owner=owner,
        created_by=owner,
        substance_a=a,
        substance_b=b,
        kind=kind,
        minutes=minutes,
        source=source,
    )


def test_model_validation_and_split(owner) -> None:
    a = Substance.objects.create(name="Synthetic A")
    b = Substance.objects.create(name="Synthetic B")
    for bad in (
        make(owner, a, b, "min_distance_minutes", 0, CITE),
        make(owner, a, b, "separate_slots", 30, CITE),
        make(owner, a, b, "min_distance_minutes", None, CITE),
        make(owner, a, None, "separate_slots", None, CITE),
    ):
        with pytest.raises(ValidationError):
            bad.full_clean()
        with pytest.raises(IntegrityError), transaction.atomic():
            bad.save()
    make(owner, a, b, "separate_slots", None, CITE).save()
    make(owner, a, None, "min_distance_minutes", 60, "  ").save()
    other = User.objects.create_user(email="p@example.com", password="correct-horse-9")
    make(other, a, b, "separate_slots", None, CITE).save()
    split = load_owner_constraints(owner)
    assert len(split.enforced) == 1 and len(split.unsourced) == 1
    assert split.enforced[0].source == CITE
