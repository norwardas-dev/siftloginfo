from __future__ import annotations

import json
from collections.abc import Sequence

from logsift.formatters.base import Formatter
from logsift.models import LogEntry
from logsift.stats import Summary


class JsonFormatter(Formatter):
    name = "json"

    def __init__(self, *, indent: int | None = 2) -> None:
        self.indent = indent

    def render_entries(self, entries: Sequence[LogEntry]) -> str:
        payload = [entry.to_dict() for entry in entries]
        return json.dumps(payload, indent=self.indent, ensure_ascii=False, default=str)

    def render_summary(self, summary: Summary) -> str:
        return json.dumps(summary.to_dict(), indent=self.indent, ensure_ascii=False)
