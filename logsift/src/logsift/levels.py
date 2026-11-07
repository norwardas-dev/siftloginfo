"""Log level normalization shared by every parser and filter."""

from __future__ import annotations

LEVELS: tuple[str, ...] = ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")

_ALIASES = {
    "TRACE": "DEBUG",
    "NOTICE": "INFO",
    "WARN": "WARNING",
    "ERR": "ERROR",
    "FATAL": "CRITICAL",
    "CRIT": "CRITICAL",
    "ALERT": "CRITICAL",
    "EMERG": "CRITICAL",
}


def normalize_level(value: object) -> str:
    """Map any level-like value ("warn", "Err", None, ...) to a canonical name."""
    if value is None:
        return "INFO"
    name = str(value).strip().upper()
    name = _ALIASES.get(name, name)
    return name if name in LEVELS else "INFO"


def level_rank(level: str) -> int:
    """Return the severity of ``level`` as an integer (DEBUG=0 ... CRITICAL=4)."""
    return LEVELS.index(normalize_level(level))
