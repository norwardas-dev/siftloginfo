import re
from datetime import datetime, timezone

import pytest

from logsift.filters import FilterSpec, apply_filters
from logsift.models import LogEntry


def make(level="INFO", message="ok", status=None, hour=10):
    timestamp = datetime(2026, 11, 7, hour, tzinfo=timezone.utc)
    return LogEntry(timestamp=timestamp, level=level, message=message, status=status)


def test_empty_spec_keeps_everything():
    entries = [make(), make("ERROR")]
    assert list(apply_filters(entries, FilterSpec())) == entries


def test_min_level():
    entries = [make("DEBUG"), make("INFO"), make("WARNING"), make("ERROR")]
    kept = apply_filters(entries, FilterSpec(min_level="WARNING"))
    assert [entry.level for entry in kept] == ["WARNING", "ERROR"]


def test_time_window():
    entries = [make(hour=hour) for hour in (8, 10, 12)]
    spec = FilterSpec(
        since=datetime(2026, 11, 7, 9, tzinfo=timezone.utc),
        until=datetime(2026, 11, 7, 11, tzinfo=timezone.utc),
    )
    assert [entry.timestamp.hour for entry in apply_filters(entries, spec)] == [10]


def test_time_filters_drop_entries_without_timestamp():
    spec = FilterSpec(since=datetime(2026, 1, 1, tzinfo=timezone.utc))
    assert list(apply_filters([LogEntry(timestamp=None)], spec)) == []


def test_grep():
    entries = [make(message="user login"), make(message="cache miss")]
    kept = apply_filters(entries, FilterSpec(pattern=re.compile("LOGIN", re.IGNORECASE)))
    assert [entry.message for entry in kept] == ["user login"]


@pytest.mark.parametrize(
    ("status_spec", "expected"),
    [("404", [404]), ("5xx", [500, 503]), ("2XX", [200])],
)
def test_status(status_spec, expected):
    entries = [make(status=code) for code in (200, 404, 500, 503)] + [make()]
    kept = apply_filters(entries, FilterSpec(status=status_spec))
    assert [entry.status for entry in kept] == expected
