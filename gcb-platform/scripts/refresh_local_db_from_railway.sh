#!/usr/bin/env bash
set -euo pipefail

# Refresh local gcb-platform Postgres database from Railway.
# This overwrites local data in database "gcb".

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLATFORM_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
BACKEND_ENV="${PLATFORM_DIR}/backend/.env"

if [[ ! -f "${BACKEND_ENV}" ]]; then
  echo "Missing ${BACKEND_ENV}. Aborting."
  exit 1
fi

if ! command -v docker >/dev/null 2>&1; then
  echo "Docker is required but not installed."
  exit 1
fi

if ! docker compose version >/dev/null 2>&1; then
  echo "Docker Compose is required but not available."
  exit 1
fi

cd "${PLATFORM_DIR}"

if ! docker compose ps postgres | rg -q "Up"; then
  echo "Postgres container is not running. Starting it now..."
  docker compose up -d postgres
fi

RAILWAY_DATABASE_URL="$(rg '^RAILWAY_DATABASE_URL=' "${BACKEND_ENV}" | sed 's/^RAILWAY_DATABASE_URL=//')"

if [[ -z "${RAILWAY_DATABASE_URL}" ]]; then
  echo "RAILWAY_DATABASE_URL is empty in ${BACKEND_ENV}. Aborting."
  exit 1
fi

read -r -p "This will OVERWRITE local database 'gcb'. Continue? [y/N] " confirm
if [[ "${confirm}" != "y" && "${confirm}" != "Y" ]]; then
  echo "Cancelled."
  exit 0
fi

timestamp="$(date +%Y%m%d_%H%M%S)"
backup_file="/tmp/gcb_local_backup_${timestamp}.sql"
remote_dump="/tmp/gcb_railway_dump_${timestamp}.sql"

echo "Creating local backup at ${backup_file} ..."
docker compose exec -T postgres pg_dump -U postgres -d gcb --no-owner --no-privileges > "${backup_file}"

echo "Dumping Railway database ..."
# Use Postgres 17 client for Railway compatibility (Railway runs PG 17).
docker run --rm postgres:17 pg_dump "${RAILWAY_DATABASE_URL}" --no-owner --no-privileges --clean --if-exists > "${remote_dump}"

echo "Restoring dump to local database ..."
# PG 17 dumps include transaction_timeout, unknown on PG 15.
sed '/^SET transaction_timeout =/d' "${remote_dump}" | docker compose exec -T postgres psql -v ON_ERROR_STOP=1 -U postgres -d gcb

echo "Done."
echo "Local backup: ${backup_file}"
echo "Imported dump: ${remote_dump}"
