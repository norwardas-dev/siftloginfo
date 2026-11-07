import json

import pytest

from logsift import __version__
from logsift.cli import main


def run(capsys, *args):
    code = main(list(args))
    out, err = capsys.readouterr()
    return code, out, err


def test_view_auto_detects_format(capsys, fixtures):
    code, out, _ = run(capsys, "view", str(fixtures / "access.log"), "--status", "5xx")
    assert code == 0
    assert "/api/report" in out
    assert "/api/login" not in out


def test_view_limit_with_tail(capsys, fixtures):
    _, out, _ = run(capsys, "view", str(fixtures / "auth.log"), "-n", "1", "--tail", "-o", "json")
    data = json.loads(out)
    assert len(data) == 1
    assert data[0]["extra"]["app"] == "kernel"


def test_stats_json(capsys, fixtures):
    code, out, _ = run(capsys, "stats", str(fixtures / "app.jsonl"), "-o", "json", "-l", "warning")
    assert code == 0
    assert json.loads(out)["total"] == 2


def test_formats_command(capsys):
    code, out, _ = run(capsys, "formats")
    assert code == 0
    assert "nginx" in out
    assert "syslog" in out


def test_missing_file_is_reported(capsys, tmp_path):
    code, _, err = run(capsys, "view", str(tmp_path / "missing.log"))
    assert code == 2
    assert "error" in err


def test_invalid_timestamp_is_rejected(fixtures):
    with pytest.raises(SystemExit):
        main(["view", str(fixtures / "access.log"), "--since", "yesterday"])


def test_version(capsys):
    with pytest.raises(SystemExit):
        main(["--version"])
    assert __version__ in capsys.readouterr().out
