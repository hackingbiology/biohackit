# SPDX-License-Identifier: AGPL-3.0-or-later
"""Typed cadence and due dates (M04 TG-a). Synthetic dates only."""

import json
from datetime import date, timedelta

import pytest

from core.cadence import Cadence, due_dates, due_events

START = date(2026, 1, 1)


def test_every_second_day() -> None:
    # scenario: pills-management::every-second-day
    cadence = Cadence(mode="interval", interval_days=2)
    window = (START, date(2026, 1, 7))
    expected = [date(2026, 1, d) for d in (1, 3, 5, 7)]
    assert due_dates(cadence, START, *window) == expected
    assert due_dates(cadence, START, *window) == expected
    later = due_dates(cadence, START, date(2026, 1, 4), date(2026, 1, 10))
    assert later == [date(2026, 1, d) for d in (5, 7, 9)]


def test_weekly_sessions() -> None:
    # scenario: therapeutics-management::weekly-sessions
    cadence = Cadence(mode="days_of_week", days_of_week=(2, 4))
    end = date(2026, 1, 14)
    got = due_dates(cadence, START, START, end)
    assert got == [
        d for d in (START + timedelta(i) for i in range(14)) if d.isoweekday() in (2, 4)
    ]
    assert got == [date(2026, 1, d) for d in (1, 6, 8, 13)]


def test_daily_events_and_bounds() -> None:
    cadence = Cadence(mode="daily", times_per_day=2)
    assert due_dates(cadence, START, date(2025, 12, 30), date(2026, 1, 2)) == [
        START,
        date(2026, 1, 2),
    ]
    assert due_events(cadence, START, START, START) == [(START, 1), (START, 2)]
    assert due_dates(cadence, START, date(2026, 1, 5), date(2026, 1, 4)) == []
    assert due_dates(cadence, START, date(2025, 1, 1), date(2025, 12, 31)) == []


def test_window_cap() -> None:
    cadence = Cadence(mode="daily")
    assert len(due_dates(cadence, START, START, START + timedelta(days=365))) == 366
    with pytest.raises(ValueError, match="window"):
        due_dates(cadence, START, START, START + timedelta(days=366))


@pytest.mark.parametrize(
    ("kwargs", "field"),
    [
        ({"mode": "interval", "interval_days": 0}, "interval_days"),
        ({"mode": "interval"}, "interval_days"),
        ({"mode": "daily", "times_per_day": 0}, "times_per_day"),
        ({"mode": "daily", "times_per_day": True}, "times_per_day"),
        ({"mode": "daily", "times_per_day": 25}, "times_per_day"),
        ({"mode": "interval", "interval_days": True}, "interval_days"),
        ({"mode": "days_of_week", "days_of_week": ()}, "days_of_week"),
        ({"mode": "days_of_week", "days_of_week": (2, 2)}, "days_of_week"),
        ({"mode": "days_of_week", "days_of_week": (0,)}, "days_of_week"),
        ({"mode": "days_of_week", "days_of_week": (True,)}, "days_of_week"),
        (
            {"mode": "days_of_week", "days_of_week": (1,), "interval_days": 2},
            "interval_days",
        ),
        ({"mode": "daily", "days_of_week": (1,)}, "days_of_week"),
        ({"mode": "monthly"}, "mode"),
    ],
)
def test_validation_names_the_field(kwargs: dict[str, object], field: str) -> None:
    with pytest.raises(ValueError, match=field):
        Cadence(**kwargs)  # type: ignore[arg-type]


def test_round_trip_plain_json() -> None:
    for cadence in (
        Cadence(mode="daily", times_per_day=3),
        Cadence(mode="days_of_week", days_of_week=(2, 4)),
        Cadence(mode="interval", interval_days=2),
    ):
        data = json.loads(json.dumps(cadence.to_dict()))
        assert Cadence.from_dict(data) == cadence
    with pytest.raises(ValueError, match="days_of_week"):
        Cadence.from_dict({"mode": "days_of_week", "days_of_week": "24"})


def test_from_dict_refuses_unknown_key_and_non_dict() -> None:
    with pytest.raises(ValueError, match="timesPerDay"):
        Cadence.from_dict({"mode": "daily", "timesPerDay": 3})
    with pytest.raises(ValueError, match="object"):
        Cadence.from_dict([])  # type: ignore[arg-type]
