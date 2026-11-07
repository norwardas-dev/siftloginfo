from __future__ import annotations

import csv
import io
from collections.abc import Iterable, Sequence

from logsift.formatters.base import COLUMNS, Formatter, entry_row, summary_sections
from logsift.models import LogEntry
from logsift.stats import Summary


class CsvFormatter(Formatter):
    name = "csv"

    def render_entries(self, entries: Sequence[LogEntry]) -> str:
        return _to_csv(COLUMNS, (entry_row(entry) for entry in entries))

    def render_summary(self, summary: Summary) -> str:
        rows = (
            (title, key, value)
            for title, pairs in summary_sections(summary)
            for key, value in pairs
        )
        return _to_csv(("section", "key", "value"), rows)


def _to_csv(header: Sequence[str], rows: Iterable[Sequence[str]]) -> str:
    buffer = io.StringIO()
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerow(header)
    writer.writerows(rows)
    return buffer.getvalue().rstrip("\n")
