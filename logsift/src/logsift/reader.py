"""Reading raw lines from files, gzip archives or stdin and turning them into entries."""

from __future__ import annotations

import gzip
import sys
from collections.abc import Iterable, Iterator
from itertools import chain, islice
from typing import IO

from logsift.models import LogEntry
from logsift.parsers import Parser, detect_parser


def read_lines(path: str) -> Iterator[str]:
    """Yield lines without trailing newlines. ``-`` means stdin, ``.gz`` is decompressed."""
    if path == "-":
        for line in sys.stdin:
            yield line.rstrip("\r\n")
        return

    handle: IO[str]
    if path.endswith(".gz"):
        handle = gzip.open(path, "rt", encoding="utf-8", errors="replace")  # noqa: SIM115
    else:
        handle = open(path, encoding="utf-8", errors="replace")  # noqa: SIM115
    with handle:
        for line in handle:
            yield line.rstrip("\r\n")


def iter_entries(
    lines: Iterable[str],
    parser: Parser | None = None,
    *,
    sample_size: int = 50,
) -> Iterator[LogEntry]:
    """Parse ``lines`` lazily. Without a parser, the format is detected from the first lines."""
    iterator = iter(lines)
    if parser is None:
        head = list(islice(iterator, sample_size))
        parser = detect_parser(head)
        iterator = chain(head, iterator)

    for line in iterator:
        if not line.strip():
            continue
        entry = parser.parse_line(line)
        if entry is not None:
            yield entry
