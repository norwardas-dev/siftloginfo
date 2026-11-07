"""Aggregate statistics over a stream of log entries."""

from __future__ import annotations

from collections import Counter
from collections.abc import Iterable
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from logsift.models import LogEntry
from logsift.timeutil import ensure_aware

_ERROR_LEVELS = ("ERROR", "CRITICAL")


@dataclass(slots=True)
class Summary:
    """Running totals that are updated one entry at a time (constant memory)."""

    top: int = 10
    total: int = 0
    levels: Counter[str] = field(default_factory=Counter)
    statuses: Counter[int] = field(default_factory=Counter)
    paths: Counter[str] = field(default_factory=Counter)
    sources: Counter[str] = field(default_factory=Counter)
    first_seen: datetime | None = None
    last_seen: datetime | None = None

    def add(self, entry: LogEntry) -> None:
        self.total += 1
        self.levels[entry.level] += 1
        if entry.status is not None:
            self.statuses[entry.status] += 1
        if entry.path:
            self.paths[entry.path] += 1
        if entry.source:
            self.sources[entry.source] += 1
        if entry.timestamp:
            timestamp = ensure_aware(entry.timestamp)
            if self.first_seen is None or timestamp < self.first_seen:
                self.first_seen = timestamp
            if self.last_seen is None or timestamp > self.last_seen:
                self.last_seen = timestamp

    @property
    def error_rate(self) -> float:
        if not self.total:
            return 0.0
        return sum(self.levels[level] for level in _ERROR_LEVELS) / self.total

    def to_dict(self) -> dict[str, Any]:
        return {
            "total": self.total,
            "first_seen": self.first_seen.isoformat() if self.first_seen else None,
            "last_seen": self.last_seen.isoformat() if self.last_seen else None,
            "error_rate": round(self.error_rate, 4),
            "levels": dict(self.levels),
            "statuses": {str(code): count for code, count in sorted(self.statuses.items())},
            "top_paths": _top(self.paths, self.top),
            "top_sources": _top(self.sources, self.top),
        }


def _top(counter: Counter[str], limit: int) -> list[dict[str, Any]]:
    return [{"value": value, "count": count} for value, count in counter.most_common(limit)]


def summarize(entries: Iterable[LogEntry], *, top: int = 10) -> Summary:
    summary = Summary(top=top)
    for entry in entries:
        summary.add(entry)
    return summary
