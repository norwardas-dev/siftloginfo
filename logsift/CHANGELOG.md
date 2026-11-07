# Changelog

All notable changes to this project are documented in this file.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)
and the project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [0.1.0] - 2026-11-07

### Added

- `view`, `stats` and `formats` commands.
- Parsers for Nginx/Apache access logs, JSON Lines and BSD syslog, with automatic format detection.
- Filters by minimum level, time window, regex and HTTP status (exact code or class like `5xx`).
- Table (colored), JSON, CSV and Markdown output.
- Transparent `.gz` decompression and stdin support.
- Docker image and GitHub Actions CI.
