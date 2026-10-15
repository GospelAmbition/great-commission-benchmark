#!/usr/bin/env bash
set -euo pipefail
umask 077

usage() {
  cat <<'EOF'
Usage: ./sync [--help]

Replace the local Docker Compose PostgreSQL database `gcb` with a read-only
Railway dump. This is destructive to LOCAL data and requires typing:
  overwrite local gcb

Source: process RAILWAY_DATABASE_URL, or gcb-platform/backend/.env.
Destination: this repository's gcb-platform Compose postgres container only.
A private local backup is saved before import. Production is never restored to.
Requires Docker Compose and Python 3. After confirmation, macOS starts Docker
Desktop if needed; other systems require a running Docker daemon.
EOF
}
if [[ $# -gt 0 ]]; then
  if [[ $# -eq 1 && ( "$1" == "--help" || "$1" == "-h" ) ]]; then
    usage
    exit 0
  fi
  usage >&2
  exit 2
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLATFORM_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
BACKEND_ENV="${PLATFORM_DIR}/backend/.env"
for executable in docker python3; do
  if ! command -v "$executable" >/dev/null 2>&1; then
    echo "$executable is required. Aborting." >&2
    exit 1
  fi
done
# Hold the same advisory lock as ./launch throughout the operation, including
# confirmation. A Python parent retains the lock while the shell does the work.
if [[ "${_GCB_SYNC_LOCK_HELD:-}" != 1 ]]; then
  exec python3 - "$0" "${PLATFORM_DIR}/../.local-run/launch.lock" 3<&0 <<'PYLOCK'
import fcntl
import os
from pathlib import Path
import subprocess
import sys

lock_path = Path(sys.argv[2])
lock_path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
with lock_path.open("a") as lock:
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        print("Local launch or sync is active. Stop ./launch before refreshing its database.", file=sys.stderr)
        sys.exit(1)
    environment = dict(os.environ, _GCB_SYNC_LOCK_HELD="1")
    try:
        sys.exit(subprocess.call(["bash", sys.argv[1]], env=environment, stdin=3, pass_fds=(lock.fileno(),)))
    except KeyboardInterrupt:
        sys.exit(130)
PYLOCK
fi
unset _GCB_SYNC_LOCK_HELD

# Docker contexts can target remote machines. Resolve CLI precedence explicitly,
# allow only a local Unix socket, and pin it for every subsequent command.
if [[ -n "${DOCKER_CONTEXT:-}" ]]; then
  docker_endpoint="$(docker context inspect "$DOCKER_CONTEXT" --format '{{.Endpoints.docker.Host}}' 2>/dev/null)" || {
    echo "Cannot inspect the selected Docker context." >&2; exit 1;
  }
elif [[ -n "${DOCKER_HOST:-}" ]]; then
  docker_endpoint="$DOCKER_HOST"
else
  docker_endpoint="$(docker context inspect --format '{{.Endpoints.docker.Host}}' 2>/dev/null)" || {
    echo "Cannot inspect the current Docker context." >&2; exit 1;
  }
fi
if [[ "$docker_endpoint" != unix:///* || "$docker_endpoint" == *$'\n'* || "$docker_endpoint" == *$'\r'* ]]; then
  echo "Refusing sync: Docker must use a local Unix socket, not a remote TCP/SSH endpoint." >&2
  exit 1
fi
unset DOCKER_CONTEXT DOCKER_TLS_VERIFY DOCKER_CERT_PATH
export DOCKER_HOST="$docker_endpoint"

daemon_ready=false
if docker info >/dev/null 2>&1; then
  daemon_ready=true
fi
if ! docker compose version >/dev/null 2>&1; then
  echo "Docker Compose is not available." >&2
  exit 1
fi

# Pin the compose file/project and use explicit localhost connection arguments
# inside its postgres container. Never use the Railway URL for the destination.
compose=(docker compose --project-directory "$PLATFORM_DIR" --project-name gcb-platform -f "$PLATFORM_DIR/docker-compose.yml")
backup_dir="$(mktemp -d "${TMPDIR:-/tmp}/gcb-local-refresh.XXXXXXXX")"
credential_file="$backup_dir/source.env"
private_log="$backup_dir/operation.log"
confirmed=false
cleanup() {
  rm -f "$credential_file"
  if [[ "$confirmed" == false ]]; then
    rm -f "$private_log"
    rmdir "$backup_dir" 2>/dev/null || true
  fi
}
trap cleanup EXIT
trap 'exit 130' INT TERM

# Parse data, never source/eval dotenv contents. Secret values stay out of argv
# and terminal output. Docker receives a private environment file for pg_dump.
if ! python3 - "$BACKEND_ENV" "$credential_file" <<'PY'
import os
import re
import sys
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlsplit

try:
    value = os.environ.get("RAILWAY_DATABASE_URL")
    if value is None:
        value = ""
        for line in Path(sys.argv[1]).read_text().splitlines():
            match = re.match(r"^\s*(?:export\s+)?RAILWAY_DATABASE_URL\s*=\s*(.*)$", line)
            if not match:
                continue
            raw = match.group(1).strip()
            if raw.startswith(("'", '"')):
                quote = raw[0]
                quoted = re.fullmatch(r"(['\"])(.*?)\1\s*(?:#.*)?", raw)
                if not quoted:
                    raise ValueError("Malformed quoted setting")
                value = quoted.group(2)
                if quote == '"':
                    value = value.replace('\\"', '"').replace('\\\\', '\\')
            else:
                value = re.split(r"\s+#", raw, maxsplit=1)[0].strip()
    parsed = urlsplit(value or "")
    if parsed.scheme not in ("postgres", "postgresql") or not parsed.hostname or not parsed.username or not parsed.path.strip("/"):
        raise ValueError("Invalid database URL")
    query = parse_qs(parsed.query)
    sslmode = query.get("sslmode", ["require"])[0]
    if sslmode not in ("disable", "allow", "prefer", "require", "verify-ca", "verify-full"):
        raise ValueError("Invalid SSL mode")
    fields = {
        "PGHOST": parsed.hostname,
        "PGPORT": str(parsed.port or 5432),
        "PGUSER": unquote(parsed.username),
        "PGPASSWORD": unquote(parsed.password or ""),
        "PGDATABASE": unquote(parsed.path[1:]),
        "PGSSLMODE": sslmode,
        "PGCONNECT_TIMEOUT": "10",
        "PGOPTIONS": "-c default_transaction_read_only=on",
    }
    if any("\n" in item or "\r" in item or "\0" in item for item in fields.values()):
        raise ValueError("Invalid credential encoding")
    Path(sys.argv[2]).write_text("".join(f"{key}={item}\n" for key, item in fields.items()))
except Exception:
    print("Cannot read a valid RAILWAY_DATABASE_URL from the process or backend/.env. No data changed.", file=sys.stderr)
    sys.exit(1)
PY
then
  exit 1
fi

printf "This will OVERWRITE the LOCAL Compose database 'gcb'. Type 'overwrite local gcb' to continue: "
if ! IFS= read -r confirm || [[ "$confirm" != "overwrite local gcb" ]]; then
  echo "Cancelled. No database changed."
  exit 0
fi
confirmed=true
fail() {
  echo "$1 See private diagnostics: $private_log" >&2
  echo "Backup directory: $backup_dir" >&2
  exit 1
}

if [[ "$daemon_ready" != true ]]; then
  if [[ "$(uname -s)" != Darwin ]] || ! command -v open >/dev/null 2>&1; then
    fail "Docker daemon is unavailable. Start Docker and retry."
  fi
  echo "Starting Docker Desktop; waiting up to two minutes..."
  if ! open -a Docker >>"$private_log" 2>&1; then
    fail "Could not start Docker Desktop."
  fi
  for ((attempt=0; attempt<60; attempt++)); do
    if docker info >/dev/null 2>&1; then
      daemon_ready=true
      break
    fi
    sleep 2
  done
  [[ "$daemon_ready" == true ]] || fail "Docker Desktop did not become ready within two minutes."
fi

if ! "${compose[@]}" up -d postgres >"$private_log" 2>&1; then
  fail "Could not start local Postgres."
fi
ready=false
for ((attempt=0; attempt<30; attempt++)); do
  if "${compose[@]}" exec -T postgres pg_isready -h 127.0.0.1 -p 5432 -U postgres -d gcb >>"$private_log" 2>&1; then
    ready=true
    break
  fi
  sleep 1
done
[[ "$ready" == true ]] || fail "Local Postgres did not become ready within 30 attempts."

# Match the production major version instead of rewriting SQL for an older server.
if ! local_version="$("${compose[@]}" exec -T postgres psql -X -h 127.0.0.1 -p 5432 -U postgres -d gcb -At -c 'SHOW server_version_num' 2>>"$private_log")"; then
  fail "Could not verify the local PostgreSQL version."
fi
if [[ ! "$local_version" =~ ^17[0-9]{4}$ ]]; then
  fail "Local PostgreSQL must be major version 17; import was not attempted."
fi

backup_file="$backup_dir/local-backup.sql"
remote_dump="$backup_dir/railway.sql"
echo "Creating private local backup..."
if ! "${compose[@]}" exec -T postgres pg_dump -h 127.0.0.1 -p 5432 -U postgres -d gcb --no-owner --no-privileges >"$backup_file" 2>>"$private_log"; then
  fail "Local backup failed; import was not attempted."
fi
[[ -s "$backup_file" ]] || fail "Local backup was empty; import was not attempted."

echo "Reading Railway with PostgreSQL 17 pg_dump..."
if ! docker run --rm --env-file "$credential_file" postgres:17 pg_dump --no-owner --no-privileges --clean --if-exists >"$remote_dump" 2>>"$private_log"; then
  fail "Railway dump failed; local data has not been replaced."
fi
rm -f "$credential_file"
[[ -s "$remote_dump" ]] || fail "Railway dump was empty; import was not attempted."

# GCB application tables live in public. Refuse unknown schema layouts instead
# of partially replacing a database; preserve COPY data verbatim while removing
# public schema commands that conflict with the reset. Retain all PG17 settings.
restore_file="$backup_dir/restore.sql"
if ! python3 - "$backup_file" "$remote_dump" "$restore_file" "$backup_dir/local-recovery.sql" <<'PYRESTORE' 2>>"$private_log"
import re
import sys
from pathlib import Path

public_schema_commands = {
    "CREATE SCHEMA public;", 'CREATE SCHEMA "public";',
    "DROP SCHEMA public;", 'DROP SCHEMA "public";',
    "DROP SCHEMA IF EXISTS public;", 'DROP SCHEMA IF EXISTS "public";',
}

def sql_lines(path):
    in_copy = False
    with Path(path).open() as source:
        for line in source:
            data_line = in_copy
            if in_copy and line.rstrip("\n") == r"\.":
                in_copy = False
            elif not in_copy and line.startswith("COPY ") and line.rstrip().endswith(" FROM stdin;"):
                in_copy = True
            if not data_line and line.startswith("CREATE SCHEMA ") and line.strip() not in public_schema_commands:
                raise ValueError("Unsupported non-public schema; local data has not been replaced")
            yield line, data_line

def prepare(source_path, destination_path):
    source_major = None
    with Path(destination_path).open("w") as target:
        target.write("DROP SCHEMA public CASCADE;\nCREATE SCHEMA public;\nCOMMENT ON SCHEMA public IS 'standard public schema';\n")
        for line, data_line in sql_lines(source_path):
            if not data_line:
                version = re.match(r"-- Dumped from database version (\d+)(?:\.|\s|$)", line)
                if version:
                    source_major = int(version.group(1))
                if line.strip() in public_schema_commands:
                    continue
            target.write(line)
    if source_major != 17:
        raise ValueError("Dump source must be PostgreSQL major version 17; import was not attempted")

# Validate the local backup too: unrelated schemas must not be silently retained
# or destroyed. A prepared recovery file can restore the backup transactionally.
prepare(sys.argv[1], sys.argv[4])
prepare(sys.argv[2], sys.argv[3])
PYRESTORE
then
  fail "Dump preparation failed; local data has not been replaced."
fi

echo "Restoring LOCAL data in a single transaction..."
# Replacing public also removes local-only objects absent from the source dump.
if ! "${compose[@]}" exec -T postgres psql -X -h 127.0.0.1 -p 5432 -U postgres -d gcb --single-transaction -v ON_ERROR_STOP=1 <"$restore_file" >>"$private_log" 2>&1; then
  fail "Local restore failed and its transaction was rolled back."
fi

echo "Local refresh complete."
echo "Local backup: $backup_file"
echo "Prepared local recovery: $backup_dir/local-recovery.sql"
echo "Imported dump: $remote_dump"
