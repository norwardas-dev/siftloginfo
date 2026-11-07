"""Human-friendly aligned table output, optionally colorized."""

from __future__ import annotations

from collections.abc import Sequence

from logsift.formatters.base import COLUMNS, Formatter, entry_row, summary_sections
from logsift.models import LogEntry
from logsift.stats import Summary

_RESET = "\033[0m"
_BOLD = "\033[1m"
_LEVEL_COLORS = {
    "DEBUG": "\033[2m",
    "INFO": "\033[36m",
    "WARNING": "\033[33m",
    "ERROR": "\033[31m",
    "CRITICAL": "\033[1;31m",
}


class TableFormatter(Formatter):
    name = "table"

    def __init__(self, *, color: bool = False, max_width: int = 80) -> None:
        self.color = color
        self.max_width = max_width

    def render_entries(self, entries: Sequence[LogEntry]) -> str:
        if not entries:
            return "(no matching entries)"
        rows = [entry_row(entry) for entry in entries]
        for row in rows:
            row[-1] = _truncate(row[-1], self.max_width)
        header = [column.upper() for column in COLUMNS]
        widths = [max(len(cell) for cell in column) for column in zip(header, *rows, strict=True)]
        lines = [self._row(header, widths), "  ".join("-" * width for width in widths)]
        lines.extend(self._row(row, widths, level_col=1) for row in rows)
        return "\n".join(lines)

    def render_summary(self, summary: Summary) -> str:
        blocks: list[str] = []
        for title, rows in summary_sections(summary):
            width = max((len(key) for key, _ in rows), default=0)
            body = [f"  {key.ljust(width)}  {value}" for key, value in rows] or ["  -"]
            blocks.append("\n".join([self._paint(title.upper(), _BOLD), *body]))
        return "\n\n".join(blocks)

    def _row(self, cells: list[str], widths: list[int], level_col: int | None = None) -> str:
        out: list[str] = []
        for index, (cell, width) in enumerate(zip(cells, widths, strict=True)):
            text = cell if index == len(cells) - 1 else cell.ljust(width)
            if index == level_col:
                text = self._paint(text, _LEVEL_COLORS.get(cell, ""))
            out.append(text)
        return "  ".join(out)

    def _paint(self, text: str, code: str) -> str:
        return f"{code}{text}{_RESET}" if self.color and code else text


def _truncate(text: str, width: int) -> str:
    return text if len(text) <= width else text[: width - 3] + "..."
