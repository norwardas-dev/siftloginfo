"""Input parsers and format auto-detection.

To add a format, subclass :class:`Parser` and append it to ``_BUILTIN``.
"""

from __future__ import annotations

from collections.abc import Iterable

from logsift.parsers.base import Parser
from logsift.parsers.jsonl import JsonLinesParser
from logsift.parsers.nginx import NginxParser
from logsift.parsers.syslog import SyslogParser

__all__ = ["PARSERS", "Parser", "detect_parser", "get_parser"]

_BUILTIN: tuple[type[Parser], ...] = (NginxParser, JsonLinesParser, SyslogParser)
PARSERS: dict[str, type[Parser]] = {cls.name: cls for cls in _BUILTIN}


def get_parser(name: str) -> Parser:
    try:
        return PARSERS[name]()
    except KeyError:
        choices = ", ".join(PARSERS)
        raise ValueError(f"unknown format {name!r}; choose from: {choices}") from None


def detect_parser(sample: Iterable[str]) -> Parser:
    """Pick the parser that understands the largest share of ``sample``."""
    lines = [line for line in sample if line.strip()]
    best: Parser | None = None
    best_hits = 0
    for cls in _BUILTIN:
        parser = cls()
        hits = sum(parser.parse_line(line) is not None for line in lines)
        if hits > best_hits:
            best, best_hits = parser, hits
    if best is None:
        raise ValueError("could not detect log format; pass --format explicitly")
    return best
