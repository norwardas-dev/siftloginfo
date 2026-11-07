"""GitHub-flavored Markdown tables, handy for issues and incident reports."""

from __future__ import annotations

from collections.abc import Iterable, Sequence

from logsift.formatters.base import COLUMNS, Formatter, entry_row, summary_sections
from logsift.models import LogEntry
from logsift.stats import Summary


class MarkdownFormatter(Formatter):
    name = "markdown"

    def render_entries(self, entries: Sequence[LogEntry]) -> str:
        header = [column.capitalize() for column in COLUMNS]
        return _table(header, (entry_row(entry) for entry in entries))

    def render_summary(self, summary: Summary) -> str:
        blocks = [
            f"### {title}\n\n{_table(('Key', 'Value'), rows)}"
            for title, rows in summary_sections(summary)
        ]
        return "\n\n".join(blocks)


def _escape(text: str) -> str:
    return text.replace("|", "\\|")


def _table(header: Sequence[str], rows: Iterable[Sequence[str]]) -> str:
    lines = [
        "| " + " | ".join(header) + " |",
        "|" + "|".join(" --- " for _ in header) + "|",
    ]
    lines.extend("| " + " | ".join(_escape(cell) for cell in row) + " |" for row in rows)
    return "\n".join(lines)
