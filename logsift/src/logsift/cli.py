"""Command line interface: ``logsift view | stats | formats``."""

from __future__ import annotations

import argparse
import re
import sys
from collections import deque
from collections.abc import Iterator, Sequence
from datetime import datetime
from itertools import islice

from logsift import __version__
from logsift.filters import FilterSpec, apply_filters
from logsift.formatters import FORMATTERS, get_formatter
from logsift.levels import LEVELS
from logsift.models import LogEntry
from logsift.parsers import PARSERS, get_parser
from logsift.reader import iter_entries, read_lines
from logsift.stats import summarize
from logsift.timeutil import parse_iso


def _timestamp(value: str) -> datetime:
    try:
        return parse_iso(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"invalid ISO 8601 timestamp: {value!r}") from None


def _regex(value: str) -> re.Pattern[str]:
    try:
        return re.compile(value, re.IGNORECASE)
    except re.error as exc:
        raise argparse.ArgumentTypeError(f"invalid regex {value!r}: {exc}") from None


def _positive_int(value: str) -> int:
    number = int(value)
    if number < 1:
        raise argparse.ArgumentTypeError("must be a positive integer")
    return number


def _add_common_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "files",
        nargs="*",
        default=["-"],
        metavar="FILE",
        help="log files to read (.gz supported); reads stdin when omitted",
    )
    parser.add_argument(
        "-f",
        "--format",
        choices=["auto", *PARSERS],
        default="auto",
        help="input format (default: auto-detect)",
    )

    filters = parser.add_argument_group("filters")
    filters.add_argument("-l", "--level", type=str.upper, choices=LEVELS, help="minimum severity")
    filters.add_argument("--since", type=_timestamp, metavar="TIME", help="ISO 8601 lower bound")
    filters.add_argument("--until", type=_timestamp, metavar="TIME", help="ISO 8601 upper bound")
    filters.add_argument(
        "-g", "--grep", type=_regex, metavar="REGEX", help="case-insensitive message regex"
    )
    filters.add_argument("-s", "--status", metavar="CODE", help="HTTP status, e.g. 404 or 5xx")

    output = parser.add_argument_group("output")
    output.add_argument(
        "-o",
        "--output",
        choices=list(FORMATTERS),
        default="table",
        help="output format (default: table)",
    )
    output.add_argument("--no-color", action="store_true", help="disable colored output")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="logsift",
        description="Filter, explore and summarize log files from the command line.",
    )
    parser.add_argument("-V", "--version", action="version", version=f"%(prog)s {__version__}")
    commands = parser.add_subparsers(dest="command", required=True, metavar="COMMAND")

    view = commands.add_parser("view", help="print matching log entries")
    _add_common_options(view)
    view.add_argument("-n", "--limit", type=_positive_int, help="show at most N entries")
    view.add_argument("--tail", action="store_true", help="with --limit, keep the last N entries")

    stats = commands.add_parser("stats", help="summarize matching log entries")
    _add_common_options(stats)
    stats.add_argument("--top", type=_positive_int, default=10, help="rows in top-N lists")

    commands.add_parser("formats", help="list supported input formats")
    return parser


def _entries(args: argparse.Namespace) -> Iterator[LogEntry]:
    spec = FilterSpec(
        min_level=args.level,
        since=args.since,
        until=args.until,
        pattern=args.grep,
        status=args.status,
    )
    for path in args.files:
        parser = None if args.format == "auto" else get_parser(args.format)
        yield from apply_filters(iter_entries(read_lines(path), parser), spec)


def _use_color(args: argparse.Namespace) -> bool:
    return bool(args.output == "table" and not args.no_color and sys.stdout.isatty())


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.command == "formats":
        for name, parser_cls in PARSERS.items():
            print(f"{name:<8} {parser_cls.description}")
        return 0

    formatter = get_formatter(args.output, color=_use_color(args))
    try:
        entries = _entries(args)
        if args.command == "view":
            if args.limit is None:
                selected = list(entries)
            elif args.tail:
                selected = list(deque(entries, maxlen=args.limit))
            else:
                selected = list(islice(entries, args.limit))
            output = formatter.render_entries(selected)
        else:
            output = formatter.render_summary(summarize(entries, top=args.top))
    except (OSError, ValueError) as exc:
        print(f"logsift: error: {exc}", file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        return 130

    print(output)
    return 0
