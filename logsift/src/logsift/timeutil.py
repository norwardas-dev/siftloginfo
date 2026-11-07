"""Timestamp helpers. All timestamps inside logsift are timezone-aware."""

from __future__ import annotations

from datetime import datetime, timezone


def ensure_aware(value: datetime) -> datetime:
    """Treat naive datetimes as UTC so they can be compared safely."""
    return value if value.tzinfo else value.replace(tzinfo=timezone.utc)


def parse_iso(value: str) -> datetime:
    """Parse an ISO 8601 timestamp, accepting a trailing ``Z`` on Python 3.10."""
    text = value.strip()
    if text.endswith(("Z", "z")):
        text = text[:-1] + "+00:00"
    return ensure_aware(datetime.fromisoformat(text))


def format_ts(value: datetime | None) -> str:
    return value.strftime("%Y-%m-%d %H:%M:%S") if value else "-"
