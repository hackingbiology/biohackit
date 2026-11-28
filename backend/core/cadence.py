# SPDX-License-Identifier: AGPL-3.0-or-later
"""Typed cadence shared by intakes and therapy sessions (M04 TG-a).

Shape follows get-based's schedule (mode, timesPerDay, daysOfWeek, intervalDays; see
docs/ecosystem/m03-interventions-protocols.md). The mode names are a default (Q156), the
window cap a default (Q157), the times-per-day bound a default (Q159). Pure and stdlib only: no recurrence library, no time zone.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Any

MODE_DAILY = "daily"
MODE_DAYS_OF_WEEK = "days_of_week"
MODE_INTERVAL = "interval"
MODES = (MODE_DAILY, MODE_DAYS_OF_WEEK, MODE_INTERVAL)
MAX_WINDOW_DAYS = 366
MAX_TIMES_PER_DAY = 24
KEYS = ("mode", "times_per_day", "days_of_week", "interval_days")


def _positive_int(value: object, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{field} must be an integer")
    if value < 1:
        raise ValueError(f"{field} must be >= 1")
    return value


@dataclass(frozen=True)
class Cadence:
    mode: str
    times_per_day: int = 1
    days_of_week: tuple[int, ...] | None = None
    interval_days: int | None = None

    def __post_init__(self) -> None:
        if self.mode not in MODES:
            raise ValueError(f"mode must be one of {', '.join(MODES)}")
        if _positive_int(self.times_per_day, "times_per_day") > MAX_TIMES_PER_DAY:
            raise ValueError(f"times_per_day must be <= {MAX_TIMES_PER_DAY}")
        if self.mode == MODE_INTERVAL:
            if self.interval_days is None:
                raise ValueError("interval_days is required in interval mode")
            _positive_int(self.interval_days, "interval_days")
        elif self.interval_days is not None:
            raise ValueError("interval_days is allowed only in interval mode")
        if self.mode == MODE_DAYS_OF_WEEK:
            self._check_days()
        elif self.days_of_week is not None:
            raise ValueError("days_of_week is allowed only in days_of_week mode")

    def _check_days(self) -> None:
        days = self.days_of_week
        if not days:
            raise ValueError("days_of_week must not be empty")
        for day in days:
            if isinstance(day, bool) or not isinstance(day, int) or not 1 <= day <= 7:
                raise ValueError("days_of_week must hold ISO weekday integers 1-7")
        if len(set(days)) != len(days):
            raise ValueError("days_of_week must not contain duplicates")

    def to_dict(self) -> dict[str, Any]:
        return {
            "mode": self.mode,
            "times_per_day": self.times_per_day,
            "days_of_week": None
            if self.days_of_week is None
            else list(self.days_of_week),
            "interval_days": self.interval_days,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Cadence:
        if not isinstance(data, dict):
            raise ValueError("cadence must be an object")
        for key in data:
            if key not in KEYS:
                raise ValueError(f"unknown cadence key: {key}")
        days = data.get("days_of_week")
        if days is not None and not isinstance(days, (list, tuple)):
            raise ValueError("days_of_week must be a list")
        return cls(
            mode=data.get("mode"),  # type: ignore[arg-type]
            times_per_day=data.get("times_per_day", 1),
            days_of_week=None if days is None else tuple(days),
            interval_days=data.get("interval_days"),
        )


def _is_due(cadence: Cadence, start: date, day: date) -> bool:
    if cadence.mode == MODE_DAYS_OF_WEEK:
        return day.isoweekday() in (cadence.days_of_week or ())
    if cadence.mode == MODE_INTERVAL:
        return (day - start).days % (cadence.interval_days or 1) == 0
    return True


def due_dates(
    cadence: Cadence, start: date, window_start: date, window_end: date
) -> list[date]:
    """Dates in the inclusive window on which the cadence is due, never before `start`."""
    if window_end < window_start:
        return []
    if (window_end - window_start).days + 1 > MAX_WINDOW_DAYS:
        raise ValueError(f"window must not exceed {MAX_WINDOW_DAYS} days")
    first = max(window_start, start)
    days = (window_end - first).days + 1
    return [
        day
        for day in (first + timedelta(days=i) for i in range(max(days, 0)))
        if _is_due(cadence, start, day)
    ]


def due_events(
    cadence: Cadence, start: date, window_start: date, window_end: date
) -> list[tuple[date, int]]:
    """(date, index 1..times_per_day) pairs; no clock times are invented."""
    return [
        (day, index)
        for day in due_dates(cadence, start, window_start, window_end)
        for index in range(1, cadence.times_per_day + 1)
    ]
