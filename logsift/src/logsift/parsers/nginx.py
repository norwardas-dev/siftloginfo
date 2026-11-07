"""Nginx / Apache access logs in the common or combined format."""

from __future__ import annotations

import re
from datetime import datetime

from logsift.models import LogEntry
from logsift.parsers.base import Parser

_PATTERN = re.compile(
    r"(?P<ip>\S+) \S+ (?P<user>\S+) \[(?P<time>[^\]]+)\] "
    r'"(?P<method>[A-Z]+) (?P<path>\S+)[^"]*" '
    r"(?P<status>\d{3}) (?P<size>\d+|-)"
    r'(?: "(?P<referer>[^"]*)" "(?P<agent>[^"]*)")?'
)
_TIME_FORMAT = "%d/%b/%Y:%H:%M:%S %z"


def _level_for_status(status: int) -> str:
    if status >= 500:
        return "ERROR"
    if status >= 400:
        return "WARNING"
    return "INFO"


class NginxParser(Parser):
    name = "nginx"
    description = "Nginx / Apache access log (common or combined format)"

    def parse_line(self, line: str) -> LogEntry | None:
        match = _PATTERN.match(line)
        if match is None:
            return None
        try:
            timestamp = datetime.strptime(match["time"], _TIME_FORMAT)
        except ValueError:
            return None

        status = int(match["status"])
        size = match["size"]
        return LogEntry(
            timestamp=timestamp,
            level=_level_for_status(status),
            message=f"{match['method']} {match['path']}",
            source=match["ip"],
            status=status,
            method=match["method"],
            path=match["path"],
            extra={
                "bytes": 0 if size == "-" else int(size),
                "referer": match["referer"],
                "user_agent": match["agent"],
            },
        )
