from datetime import datetime, timezone

import pytest

from logsift.parsers import PARSERS, detect_parser, get_parser
from logsift.parsers.jsonl import JsonLinesParser
from logsift.parsers.nginx import NginxParser
from logsift.parsers.syslog import SyslogParser

NGINX_LINE = (
    '10.0.0.7 - - [07/Nov/2026:10:01:15 +0000] "POST /api/login HTTP/1.1" 401 52 "-" "curl/8.4.0"'
)


def test_nginx_parses_combined_format():
    entry = NginxParser().parse_line(NGINX_LINE)
    assert entry is not None
    assert entry.timestamp == datetime(2026, 11, 7, 10, 1, 15, tzinfo=timezone.utc)
    assert (entry.method, entry.path, entry.status) == ("POST", "/api/login", 401)
    assert entry.source == "10.0.0.7"
    assert entry.extra["user_agent"] == "curl/8.4.0"


@pytest.mark.parametrize(("status", "level"), [(200, "INFO"), (404, "WARNING"), (503, "ERROR")])
def test_nginx_level_follows_status(status, level):
    entry = NginxParser().parse_line(NGINX_LINE.replace(" 401 ", f" {status} "))
    assert entry is not None
    assert entry.level == level


def test_nginx_handles_missing_size():
    entry = NginxParser().parse_line(NGINX_LINE.replace(" 52 ", " - "))
    assert entry is not None
    assert entry.extra["bytes"] == 0


def test_jsonl_normalizes_key_aliases():
    line = '{"ts": 1794046500, "severity": "warn", "msg": "disk almost full", "disk": "/dev/sda1"}'
    entry = JsonLinesParser().parse_line(line)
    assert entry is not None
    assert entry.timestamp == datetime(2026, 11, 7, 10, 15, tzinfo=timezone.utc)
    assert entry.level == "WARNING"
    assert entry.message == "disk almost full"
    assert entry.extra == {"disk": "/dev/sda1"}


@pytest.mark.parametrize("line", ["", "plain text", "[1, 2, 3]", "{broken json"])
def test_jsonl_rejects_non_objects(line):
    assert JsonLinesParser().parse_line(line) is None


def test_syslog_infers_level_from_message():
    line = "Nov  7 10:02:17 web-01 sshd[2245]: Failed password for invalid user admin"
    entry = SyslogParser(year=2026).parse_line(line)
    assert entry is not None
    assert entry.timestamp == datetime(2026, 11, 7, 10, 2, 17, tzinfo=timezone.utc)
    assert entry.level == "ERROR"
    assert entry.source == "web-01"
    assert entry.extra == {"app": "sshd", "pid": 2245}


@pytest.mark.parametrize(
    ("fixture", "expected"),
    [("access.log", "nginx"), ("app.jsonl", "jsonl"), ("auth.log", "syslog")],
)
def test_detect_parser(fixtures, fixture, expected):
    lines = (fixtures / fixture).read_text().splitlines()
    assert detect_parser(lines).name == expected


def test_detect_parser_fails_on_unknown_input():
    with pytest.raises(ValueError, match="could not detect"):
        detect_parser(["hello", "world"])


def test_get_parser_rejects_unknown_name():
    with pytest.raises(ValueError, match="unknown format"):
        get_parser("nope")


def test_registry_keys_match_parser_names():
    assert all(cls.name == name for name, cls in PARSERS.items())
