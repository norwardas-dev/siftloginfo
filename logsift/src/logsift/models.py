"""Core data model shared by parsers, filters and formatters."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any


@dataclass(slots=True)
class LogEntry:
    """A single log record, normalized regardless of the source format."""

    timestamp: datetime | None
    level: str = "INFO"
    message: str = ""
    source: str | None = None
    status: int | None = None
    method: str | None = None
    path: str | None = None
    extra: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat() if self.timestamp else None
        return data
