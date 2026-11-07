# Contributing

Thanks for taking the time to contribute! Bug reports, new log formats and documentation fixes are all welcome.

## Development setup

```sh
python -m venv .venv && source .venv/bin/activate
make install          # editable install + pytest, ruff, mypy
pre-commit install    # optional: run ruff on every commit
```

## Before opening a pull request

```sh
make check            # ruff + mypy --strict + pytest
```

- Keep the runtime dependency-free: logsift only uses the standard library.
- Add tests for every behavior change. Sample log lines go in `tests/fixtures/`.
- Add a line to `CHANGELOG.md` under **Unreleased**.
- Commit messages follow [Conventional Commits](https://www.conventionalcommits.org/)
  (`feat:`, `fix:`, `docs:`, `test:`, `refactor:`, `chore:`).

## Adding a log format or output format

See [docs/architecture.md](docs/architecture.md). A new parser is usually one small file
plus a fixture and a few tests.
