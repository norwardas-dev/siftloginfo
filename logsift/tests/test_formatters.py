import csv
import io
import json
from datetime import datetime, timezone

import pytest

from logsift.formatters import FORMATTERS, get_formatter
from logsift.models import LogEntry
from logsift.stats import summarize

ENTRIES = [
    LogEntry(
        timestamp=datetime(2026, 11, 7, 10, 0, tzinfo=timezone.utc),
        level="INFO",
        message="GET /",
        source="10.0.0.1",
        status=200,
        path="/",
    ),
    LogEntry(
        timestamp=datetime(2026, 11, 7, 10, 5, tzinfo=timezone.utc),
        level="ERROR",
        message="GET /a|b",
        source="10.0.0.2",
        status=500,
        path="/a|b",
    ),
]


@pytest.mark.parametrize("name", list(FORMATTERS))
def test_every_formatter_renders_entries_and_summary(name):
    formatter = get_formatter(name)
    assert formatter.render_entries(ENTRIES)
    assert formatter.render_summary(summarize(ENTRIES))


def test_json_roundtrip():
    data = json.loads(get_formatter("json").render_entries(ENTRIES))
    assert data[1]["status"] == 500
    assert data[0]["timestamp"] == "2026-11-07T10:00:00+00:00"


def test_csv_has_header_and_rows():
    rows = list(csv.reader(io.StringIO(get_formatter("csv").render_entries(ENTRIES))))
    assert rows[0] == ["time", "level", "source", "status", "message"]
    assert len(rows) == 3


def test_markdown_escapes_pipes():
    assert "/a\\|b" in get_formatter("markdown").render_entries(ENTRIES)


def test_table_color_is_opt_in():
    plain = get_formatter("table").render_entries(ENTRIES)
    colored = get_formatter("table", color=True).render_entries(ENTRIES)
    assert "\033[" not in plain
    assert "\033[31m" in colored


def test_table_handles_no_entries():
    assert "no matching entries" in get_formatter("table").render_entries([])


def test_unknown_formatter():
    with pytest.raises(ValueError, match="unknown output format"):
        get_formatter("xml")
