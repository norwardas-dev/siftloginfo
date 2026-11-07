"""Composable entry filters."""

from __future__ import annotations

import re
from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from datetime import datetime

from logsift.levels import level_rank
from logsift.models import LogEntry
from logsift.timeutil import ensure_aware


@dataclass(slots=True)
class FilterSpec:
    """Criteria an entry must satisfy. Unset fields are ignored."""

    min_level: str | None = None
    since: datetime | None = None
    until: datetime | None = None
    pattern: re.Pattern[str] | None = None
    status: str | None = None

    def matches(self, entry: LogEntry) -> bool:
        if self.min_level and level_rank(entry.level) < level_rank(self.min_level):
            return False
        if self.since or self.until:
            if entry.timestamp is None:
                return False
            timestamp = ensure_aware(entry.timestamp)
            if self.since and timestamp < self.since:
                return False
            if self.until and timestamp > self.until:
                return False
        if self.pattern and not self.pattern.search(entry.message):
            return False
        return not self.status or _status_matches(entry.status, self.status)


def _status_matches(status: int | None, spec: str) -> bool:
    """``spec`` is either an exact code ("404") or a class ("5xx")."""
    if status is None:
        return False
    spec = spec.strip().lower()
    if len(spec) == 3 and spec.endswith("xx"):
        return str(status)[0] == spec[0]
    return str(status) == spec


def apply_filters(entries: Iterable[LogEntry], spec: FilterSpec) -> Iterator[LogEntry]:
    return (entry for entry in entries if spec.matches(entry))
