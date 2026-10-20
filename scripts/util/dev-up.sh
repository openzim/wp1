#!/usr/bin/env bash
# Build and start the dev stack (docker-compose-dev.yml), print the host URL
# of every running service, then follow the logs. Ctrl-C stops the stack,
# like an attached `docker compose up`.
#
# Usage: ./scripts/util/dev-up.sh [docker compose up args...]
#   -d / --detach   start, print URLs, and return without following logs
# Profiles are enabled through COMPOSE_PROFILES, e.g.
#   COMPOSE_PROFILES=zimfarm ./scripts/util/dev-up.sh
set -euo pipefail

cd "$(dirname "$0")/../.."

compose=(docker compose -f docker-compose-dev.yml)

detach=0
up_args=()
for a in "$@"; do
  case "$a" in
    -d | --detach) detach=1 ;;
    *) up_args+=("$a") ;;
  esac
done

"${compose[@]}" up --build -d "${up_args[@]}"

# Ports come from `docker compose ps`, so worktree port remaps and profiles
# are reflected; services that aren't running are omitted.
echo
echo "Dev stack URLs:"
"${compose[@]}" ps --format json | jq -rs '
  [flatten[] | .Service as $s | .Publishers[]? | select(.PublishedPort > 0)
    | {key: "\($s):\(.TargetPort)", value: .PublishedPort}] | from_entries as $p
  | [
      ["dev-frontend:5173", "Frontend",          "http://localhost:"],
      ["dev-web:5000",      "API",               "http://localhost:"],
      ["minio:9001",        "MinIO console",     "http://localhost:"],
      ["minio:9000",        "MinIO S3 API",      "http://localhost:"],
      ["zimfarm-ui:80",     "Zimfarm UI",        "http://localhost:"],
      ["zimfarm-api:80",    "Zimfarm API",       "http://localhost:"],
      ["dev-database:3306", "Dev DB (MariaDB)",  "localhost:"],
      ["redis:6379",        "Redis",             "localhost:"],
      ["zimfarm-db:5432",   "Zimfarm DB (Postgres)", "localhost:"]
    ][]
  | select($p[.[0]])
  | "  \(.[1] + ":" + (" " * (24 - (.[1] | length))))\(.[2])\($p[.[0]])"'
echo

if [ "$detach" = 0 ]; then
  trap 'echo; "${compose[@]}" stop' INT
  "${compose[@]}" logs -f || true
fi
