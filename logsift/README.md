# logsift

**Filter, explore and summarize log files from the command line.**

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-3776AB?logo=python&logoColor=white)](pyproject.toml)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Ruff](https://img.shields.io/badge/lint-ruff-D7FF64)](https://github.com/astral-sh/ruff)
[![mypy: strict](https://img.shields.io/badge/mypy-strict-blue)](pyproject.toml)
[![Dependencies: none](https://img.shields.io/badge/dependencies-none-brightgreen)](pyproject.toml)

logsift reads Nginx/Apache access logs, structured JSON logs and syslog, **detects the format
automatically**, and lets you slice them by level, time, status code or regex. Output goes to
a readable colored table, or to JSON, CSV and Markdown for further processing.

```console
$ logsift stats access.log --top 3
OVERVIEW
  Total entries  8
  First seen     2026-11-07 10:00:01
  Last seen      2026-11-07 10:12:31
  Error rate     25.0%

LEVELS
  INFO     3
  WARNING  3
  ERROR    2

STATUS CODES
  200  3
  401  2
  404  1
  500  1
  502  1

TOP PATHS
  /api/login   2
  /api/report  2
  /            1
```

```console
$ logsift view access.log --status 4xx
TIME                 LEVEL    SOURCE      STATUS  MESSAGE
-------------------  -------  ----------  ------  -----------------
2026-11-07 10:01:15  WARNING  10.0.0.7    401     POST /api/login
2026-11-07 10:01:16  WARNING  10.0.0.7    401     POST /api/login
2026-11-07 10:06:03  WARNING  172.16.4.2  404     GET /api/orders/9
```

## Features

- **Zero dependencies**: pure Python standard library, works on any server with Python 3.10+
- **Format auto-detection** for Nginx/Apache, JSON Lines and syslog
- **Streaming**: constant memory, handles multi-gigabyte files and `.gz` archives
- **Filters**: minimum level, `--since`/`--until` time window, regex, HTTP status (`404`, `5xx`)
- **Four output formats**: colored table, JSON, CSV, Markdown
- **Unix-friendly**: reads stdin, meaningful exit codes, pipes nicely into `jq`
- **Fully typed** (`mypy --strict`) and tested

## Installation

```sh
git clone <repository-url> logsift
cd logsift
pip install .            # or: pipx install .
```

Or with Docker:

```sh
docker build -t logsift .
docker run --rm -v /var/log/nginx:/logs:ro logsift stats access.log
```

## Usage

```text
logsift view  [FILE ...] [filters] [-n N [--tail]] [-o FORMAT]
logsift stats [FILE ...] [filters] [--top N]       [-o FORMAT]
logsift formats
```

| Option | Description |
| --- | --- |
| `-f, --format` | Input format: `auto` (default), `nginx`, `jsonl`, `syslog` |
| `-l, --level` | Minimum severity: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL` |
| `--since`, `--until` | ISO 8601 time bounds, e.g. `2026-11-07T10:00:00Z` |
| `-g, --grep` | Case-insensitive regex matched against the message |
| `-s, --status` | HTTP status code or class: `404`, `5xx` |
| `-o, --output` | `table` (default), `json`, `csv`, `markdown` |
| `-n, --limit` / `--tail` | Show the first (or last) N entries |
| `--top` | Number of rows in the top paths / sources lists |

More examples in [docs/usage.md](docs/usage.md).

### Supported input formats

| Name | Example source | Level derived from |
| --- | --- | --- |
| `nginx` | Nginx / Apache access logs (common & combined) | HTTP status (4xx = warning, 5xx = error) |
| `jsonl` | pino, structlog, zap, Docker JSON logs | `level` / `severity` field |
| `syslog` | `/var/log/syslog`, `/var/log/auth.log` | Keywords in the message |

## Project structure

```text
src/logsift/
├── cli.py            # argument parsing and wiring
├── reader.py         # files, .gz and stdin -> lines -> entries
├── models.py         # LogEntry dataclass
├── filters.py        # FilterSpec
├── stats.py          # Summary (streaming counters)
├── levels.py         # level normalization
├── parsers/          # nginx, jsonl, syslog + auto-detection
└── formatters/       # table, json, csv, markdown
```

See [docs/architecture.md](docs/architecture.md) for the data flow and how to add a new format.

## Development

```sh
make install   # editable install with dev tools
make check     # ruff + mypy --strict + pytest
make cov       # tests with coverage report
```

## Roadmap

- [ ] `logfmt` parser
- [ ] `--follow` mode (like `tail -f`)
- [ ] Requests-per-minute histogram in `stats`
- [ ] Publish to PyPI

Contributions are welcome. Please read [CONTRIBUTING.md](CONTRIBUTING.md) first.

## License

[MIT](LICENSE)
