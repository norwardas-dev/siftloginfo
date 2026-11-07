"""Structured JSON Lines logs (one JSON object per line)."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from logsift.levels import normalize_level
from logsift.models import LogEntry
from logsift.parsers.base import Parser
from logsift.timeutil import parse_iso

_TIME_KEYS = ("timestamp", "time", "ts", "@timestamp", "date")
_LEVEL_KEYS = ("level", "severity", "lvl", "loglevel")
_MESSAGE_KEYS = ("message", "msg", "event")
_SOURCE_KEYS = ("ip", "client", "host")
_KNOWN_KEYS = {
    *_TIME_KEYS,
    *_LEVEL_KEYS,
    *_MESSAGE_KEYS,
    *_SOURCE_KEYS,
    "status",
    "method",
    "path",
}


def _first(data: dict[str, Any], keys: tuple[str, ...]) -> Any:
    for key in keys:
        if data.get(key) is not None:
            return data[key]
    return None


def _parse_time(value: object) -> datetime | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        seconds = value / 1000 if value > 1e11 else value  # epoch millis vs seconds
        return datetime.fromtimestamp(seconds, tz=timezone.utc)
    if isinstance(value, str):
        try:
            return parse_iso(value)
        except ValueError:
            return None
    return None


def _as_int(value: object) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.isdigit():
        return int(value)
    return None


def _as_str(value: object) -> str | None:
    return None if value is None else str(value)


class JsonLinesParser(Parser):
    name = "jsonl"
    description = "JSON Lines: one JSON object per line (pino, structlog, zap, ...)"

    def parse_line(self, line: str) -> LogEntry | None:
        text = line.strip()
        if not text.startswith("{"):
            return None
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            return None
        if not isinstance(data, dict):
            return None

        return LogEntry(
            timestamp=_parse_time(_first(data, _TIME_KEYS)),
            level=normalize_level(_first(data, _LEVEL_KEYS)),
            message=str(_first(data, _MESSAGE_KEYS) or ""),
            source=_as_str(_first(data, _SOURCE_KEYS)),
            status=_as_int(data.get("status")),
            method=_as_str(data.get("method")),
            path=_as_str(data.get("path")),
            extra={key: value for key, value in data.items() if key not in _KNOWN_KEYS},
        )
