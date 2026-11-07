# Usage recipes

## Web server logs

```sh
# Every server error in the last rotated logs
logsift view /var/log/nginx/access.log* --status 5xx

# Which endpoints get the most 404s?
logsift stats /var/log/nginx/access.log --status 404 --top 5

# Errors during an incident window, as a Markdown table for the postmortem
logsift view access.log --level error \
  --since 2026-11-07T10:00:00Z --until 2026-11-07T10:30:00Z -o markdown
```

## Application logs (JSON Lines)

```sh
# Warnings and errors mentioning a timeout
logsift view app.jsonl -l warning -g timeout

# Pipe from another tool
kubectl logs deploy/api | logsift stats -f jsonl
docker logs my-container 2>&1 | logsift view -l error
```

## System logs

```sh
# Failed SSH logins
logsift view /var/log/auth.log -g "failed password"

# Last 20 problems on the box
logsift view /var/log/syslog -l warning -n 20 --tail
```

## Exporting

```sh
logsift view access.log -o csv  > requests.csv
logsift stats access.log -o json | jq '.top_paths'
```

## Docker

```sh
docker build -t logsift .
docker run --rm -v /var/log/nginx:/logs:ro logsift stats access.log
```

## Exit codes

| Code | Meaning |
| --- | --- |
| `0` | Success (also when no entries matched) |
| `2` | Invalid arguments, unreadable file or undetectable format |
| `130` | Interrupted with Ctrl+C |
