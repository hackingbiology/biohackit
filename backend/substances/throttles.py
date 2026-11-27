# SPDX-License-Identifier: AGPL-3.0-or-later
"""A scoped throttle that charges one request slot per submitted name (M03 TG-c).

An extraction resolves, and may queue for review, every entry it carries; counting only
requests would let one call do as much work as MAX_ENTRIES calls on /resolve/ (Q125).
"""

from typing import Any

from rest_framework.throttling import ScopedRateThrottle  # type: ignore[import-untyped]  # DRF ships no stubs


def _cost(request: Any) -> int:
    data = request.data
    entries = data.get("entries") if isinstance(data, dict) else None
    return max(1, len(entries)) if isinstance(entries, list) else 1


class PerEntryScopedRateThrottle(ScopedRateThrottle):  # type: ignore[misc]  # base is Any: DRF untyped
    def allow_request(self, request: Any, view: Any) -> bool:
        self.scope = getattr(view, "throttle_scope", None)
        if not self.scope:
            return True
        self.rate = self.get_rate()
        self.num_requests, self.duration = self.parse_rate(self.rate)
        key = self.get_cache_key(request, view)
        if key is None:
            return True
        self.key = key
        self.history = self.cache.get(self.key, [])
        self.now = self.timer()
        while self.history and self.history[-1] <= self.now - self.duration:
            self.history.pop()
        cost = _cost(request)
        if len(self.history) + cost > self.num_requests:
            return bool(self.throttle_failure())
        self.history[0:0] = [self.now] * cost
        self.cache.set(self.key, self.history, self.duration)
        return True
