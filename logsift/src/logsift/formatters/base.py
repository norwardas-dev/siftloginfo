"""Formatter interface and helpers shared by all output formats."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable, Sequence

from logsift.levels import level_rank
from logsift.models import LogEntry
from logsift.stats import Summary
from logsift.timeutil import format_ts

COLUMNS: tuple[str, ...] = ("time", "level", "source", "status", "message")
Section = tuple[str, list[tuple[str, str]]]


class Formatter(ABC):
    """Renders entries or a summary into a printable string."""

    name: str = ""

    @abstractmethod
    def render_entries(self, entries: Sequence[LogEntry]) -> str:
        """Render a list of log entries."""

    @abstractmethod
    def render_summary(self, summary: Summary) -> str:
        """Render aggregated statistics."""


def entry_row(entry: LogEntry) -> list[str]:
    return [
        format_ts(entry.timestamp),
        entry.level,
        entry.source or "-",
        "-" if entry.status is None else str(entry.status),
        entry.message,
    ]


def summary_sections(summary: Summary) -> list[Section]:
    """Flatten a summary into titled key/value sections for tabular formats."""
    levels = sorted(summary.levels.items(), key=lambda item: level_rank(item[0]))
    sections: list[Section] = [
        (
            "Overview",
            [
                ("Total entries", str(summary.total)),
                ("First seen", format_ts(summary.first_seen)),
                ("Last seen", format_ts(summary.last_seen)),
                ("Error rate", f"{summary.error_rate:.1%}"),
            ],
        ),
        ("Levels", _counts(levels)),
    ]
    if summary.statuses:
        sections.append(("Status codes", _counts(sorted(summary.statuses.items()))))
    if summary.paths:
        sections.append(("Top paths", _counts(summary.paths.most_common(summary.top))))
    if summary.sources:
        sections.append(("Top sources", _counts(summary.sources.most_common(summary.top))))
    return sections


def _counts(pairs: Iterable[tuple[object, int]]) -> list[tuple[str, str]]:
    return [(str(key), str(count)) for key, count in pairs]
