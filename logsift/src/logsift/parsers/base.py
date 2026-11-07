from __future__ import annotations

from abc import ABC, abstractmethod

from logsift.models import LogEntry


class Parser(ABC):
    """Turns one raw line into a :class:`LogEntry`, or ``None`` if the line doesn't match."""

    name: str = ""
    description: str = ""

    @abstractmethod
    def parse_line(self, line: str) -> LogEntry | None:
        """Parse a single line. Must never raise on malformed input."""
