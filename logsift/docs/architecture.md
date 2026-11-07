# Architecture

logsift is a small streaming pipeline. Every stage is a plain generator, so memory use stays
constant no matter how large the input is (except `view` without `--limit`, which has to
collect results before rendering a table).

```
 files / stdin            parsers/              filters.py           stats.py        formatters/
┌─────────────┐   lines  ┌──────────┐ LogEntry ┌────────────┐       ┌─────────┐      ┌─────────┐
│ read_lines()│ ───────▶ │ Parser   │ ───────▶ │ FilterSpec │ ────▶ │ Summary │ ───▶ │Formatter│ ──▶ stdout
└─────────────┘          └──────────┘          └────────────┘       └─────────┘      └─────────┘
   reader.py          auto-detected from                           (stats only)    table/json/csv/md
                       the first 50 lines
```

| Module | Responsibility |
| --- | --- |
| `models.py` | `LogEntry`, the normalized record every stage works with |
| `reader.py` | Reads files, `.gz` archives and stdin; drives the parser |
| `parsers/` | One class per input format plus `detect_parser()` |
| `levels.py` | Maps `warn`, `ERR`, `fatal`, ... onto five canonical levels |
| `filters.py` | `FilterSpec`: level, time window, regex, HTTP status |
| `stats.py` | `Summary`: counters updated one entry at a time |
| `formatters/` | Render entries or a summary as table, JSON, CSV or Markdown |
| `cli.py` | Argument parsing and wiring of the stages above |

## Adding an input format

1. Create `src/logsift/parsers/<name>.py`:

   ```python
   from logsift.models import LogEntry
   from logsift.parsers.base import Parser


   class LogfmtParser(Parser):
       name = "logfmt"
       description = "key=value pairs (Heroku / Go style)"

       def parse_line(self, line: str) -> LogEntry | None:
           ...  # return None for lines that don't match, never raise
   ```

2. Append the class to `_BUILTIN` in `src/logsift/parsers/__init__.py`.
   It is now available via `--format logfmt` and takes part in auto-detection.
3. Add a fixture in `tests/fixtures/` and tests in `tests/test_parsers.py`.

## Adding an output format

Subclass `Formatter` from `formatters/base.py`, implement `render_entries()` and
`render_summary()`, and register it in `formatters/__init__.py`. The helpers
`entry_row()` and `summary_sections()` give you ready-made rows, so most formatters
are under 30 lines.

## Design decisions

- **No runtime dependencies.** logsift should work on any server that has Python 3.10+.
- **Parsers never raise.** Malformed lines are skipped, because real-world logs are messy.
- **Timezone-aware timestamps everywhere.** Naive values are treated as UTC so that
  `--since` / `--until` comparisons can't crash.
