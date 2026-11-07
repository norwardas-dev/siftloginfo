import gzip

from logsift.reader import iter_entries, read_lines
from logsift.stats import summarize


def load(directory, name):
    return list(iter_entries(read_lines(str(directory / name))))


def test_summary_of_access_log(fixtures):
    summary = summarize(load(fixtures, "access.log"), top=2)
    assert summary.total == 8
    assert summary.levels == {"INFO": 3, "WARNING": 3, "ERROR": 2}
    assert summary.statuses[401] == 2
    assert summary.error_rate == 0.25

    data = summary.to_dict()
    assert data["first_seen"] == "2026-11-07T10:00:01+00:00"
    assert data["last_seen"] == "2026-11-07T10:12:31+00:00"
    assert len(data["top_paths"]) == 2


def test_jsonl_skips_invalid_lines(fixtures):
    entries = load(fixtures, "app.jsonl")
    assert len(entries) == 5
    assert entries[1].level == "DEBUG"


def test_empty_summary():
    summary = summarize([])
    assert summary.total == 0
    assert summary.error_rate == 0.0
    assert summary.to_dict()["first_seen"] is None


def test_gzip_input(tmp_path, fixtures):
    target = tmp_path / "access.log.gz"
    target.write_bytes(gzip.compress((fixtures / "access.log").read_bytes()))
    assert len(load(tmp_path, "access.log.gz")) == 8
