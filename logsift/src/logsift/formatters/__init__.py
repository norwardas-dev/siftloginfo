"""Output formats. To add one, subclass :class:`Formatter` and append it to ``_BUILTIN``."""

from __future__ import annotations

from logsift.formatters.base import Formatter
from logsift.formatters.csv_fmt import CsvFormatter
from logsift.formatters.json_fmt import JsonFormatter
from logsift.formatters.markdown import MarkdownFormatter
from logsift.formatters.table import TableFormatter

__all__ = ["FORMATTERS", "Formatter", "get_formatter"]

_BUILTIN: tuple[type[Formatter], ...] = (
    TableFormatter,
    JsonFormatter,
    CsvFormatter,
    MarkdownFormatter,
)
FORMATTERS: dict[str, type[Formatter]] = {cls.name: cls for cls in _BUILTIN}


def get_formatter(name: str, *, color: bool = False) -> Formatter:
    if name not in FORMATTERS:
        raise ValueError(f"unknown output format {name!r}; choose from: {', '.join(FORMATTERS)}")
    if name == TableFormatter.name:
        return TableFormatter(color=color)
    return FORMATTERS[name]()
