"""BSD syslog (RFC 3164), as found in /var/log/syslog or /var/log/auth.log."""

from __future__ import annotations

import re
from datetime import datetime, timezone

from logsift.models import LogEntry
from logsift.parsers.base import Parser

_PATTERN = re.compile(
    r"(?P<time>[A-Z][a-z]{2} [ \d]\d \d{2}:\d{2}:\d{2}) "
    r"(?P<host>\S+) (?P<app>[^\s:\[]+)(?:\[(?P<pid>\d+)\])?: (?P<msg>.*)"
)
_ERROR_HINTS = re.compile(r"\b(error|fail(ed|ure)?|denied|fatal|panic)\b", re.IGNORECASE)
_WARNING_HINTS = re.compile(r"\b(warn(ing)?|invalid|timeout|retry(ing)?)\b", re.IGNORECASE)


def _infer_level(message: str) -> str:
    if _ERROR_HINTS.search(message):
        return "ERROR"
    if _WARNING_HINTS.search(message):
        return "WARNING"
    return "INFO"


class SyslogParser(Parser):
    name = "syslog"
    description = "BSD syslog (RFC 3164), e.g. /var/log/auth.log"

    def __init__(self, year: int | None = None) -> None:
        # RFC 3164 timestamps carry no year, so we assume the current one.
        self.year = year or datetime.now(timezone.utc).year

    def parse_line(self, line: str) -> LogEntry | None:
        match = _PATTERN.match(line)
        if match is None:
            return None
        try:
            timestamp = datetime.strptime(f"{self.year} {match['time']}", "%Y %b %d %H:%M:%S")
        except ValueError:
            return None

        message = match["msg"]
        return LogEntry(
            timestamp=timestamp.replace(tzinfo=timezone.utc),
            level=_infer_level(message),
            message=message,
            source=match["host"],
            extra={"app": match["app"], "pid": int(match["pid"]) if match["pid"] else None},
        )
