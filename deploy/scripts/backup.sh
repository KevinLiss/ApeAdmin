#!/usr/bin/env bash
# ApeAdmin daily backup: database + plugin runtime data.
#
# Usage:   bash backup.sh <project_root> [keep_days]
# Example: bash backup.sh /www/wwwroot/apeadmin 7
#
# Crontab (03:10 daily, server time):
#   10 3 * * * bash /www/wwwroot/apeadmin/scripts/backup.sh /www/wwwroot/apeadmin 7 >> /var/log/apeadmin/backup.log 2>&1
#
# What it does:
#   - MySQL: mysqldump --single-transaction | gzip   (InnoDB-consistent snapshot)
#   - SQLite: python sqlite3 .backup                  (safe online copy)
#   - src/uploads: tar.gz (plugin data home: release packages, marketplace files)
#   - Keeps the last <keep_days> days per artifact, prunes older ones.
#
# Restore:
#   MySQL:   gunzip -c db-YYYYmmdd.sql.gz | mysql -u<user> -p <db>
#   SQLite:  stop service; cp db.sqlite.gz-restore; start
#   Files:   tar -xzf files-YYYYmmdd.tar.gz -C <project_root>/src

set -euo pipefail

PROJECT_ROOT="${1:?usage: backup.sh <project_root> [keep_days]}"
KEEP_DAYS="${2:-7}"
STAMP="$(date +%Y%m%d-%H%M)"

# ---- locate the app -------------------------------------------------------
APP_DIR="$PROJECT_ROOT"
[ -d "$PROJECT_ROOT/backend" ] && APP_DIR="$PROJECT_ROOT/backend"
ENV_FILE="$APP_DIR/.env"
OUT_DIR="${BACKUP_DIR:-$PROJECT_ROOT.parent}"   # placeholder, fixed below
OUT_DIR="$(dirname "$PROJECT_ROOT")/apeadmin_backups"
LOG_TAG="[backup $STAMP]"

[ -f "$ENV_FILE" ] || { echo "$LOG_TAG .env not found at $ENV_FILE"; exit 1; }
mkdir -p "$OUT_DIR"

# ---- tiny .env reader -----------------------------------------------------
env_get() {
  grep -E "^$1=" "$ENV_FILE" | tail -1 | cut -d= -f2-
}
DB_TYPE="$(env_get DB_TYPE)"
DB_TYPE="${DB_TYPE:-sqlite}"

echo "$LOG_TAG start (type=$DB_TYPE keep=$KEEP_DAYS out=$OUT_DIR)"

# ---- database -------------------------------------------------------------
if [ "$DB_TYPE" = "mysql" ]; then
  DB_HOST="$(env_get DB_HOST)"; DB_PORT="$(env_get DB_PORT)"
  DB_USER="$(env_get DB_USER)"; DB_PASSWORD="$(env_get DB_PASSWORD)"
  DB_NAME="$(env_get DB_NAME)"
  OUT="$OUT_DIR/db-$STAMP.sql.gz"
  MYSQLDUMP_OPTS=(--single-transaction --quick --routines --host="$DB_HOST" --port="$DB_PORT" --user="$DB_USER")
  if [ -n "$DB_PASSWORD" ]; then MYSQLDUMP_OPTS+=(-p"$DB_PASSWORD"); fi
  if command -v mysqldump >/dev/null 2>&1; then
    mysqldump "${MYSQLDUMP_OPTS[@]}" "$DB_NAME" | gzip > "$OUT"
  else
    # Fall back to a python client when the CLI is absent (shared hosting).
    "$(dirname "$0")/../.venv/bin/python3" - "$DB_HOST" "$DB_PORT" "$DB_USER" "$DB_PASSWORD" "$DB_NAME" "$OUT" <<'PY'
import sys, gzip
import pymysql
host, port, user, pwd, name, out = sys.argv[1:7]
conn = pymysql.connect(host=host, port=int(port), user=user, password=pwd, database=name)
with gzip.open(out, "wt") as f:
    for line in conn.iter_dump():
        f.write(line if line.endswith("\n") else line + "\n")
PY
  fi
  echo "$LOG_TAG mysql -> $OUT ($(du -h "$OUT" | cut -f1))"
elif [ "$DB_TYPE" = "sqlite" ]; then
  DB_FILE="$(env_get DB_NAME)"
  case "$DB_FILE" in /*) ;; *) DB_FILE="$APP_DIR/$DB_FILE";; esac
  OUT="$OUT_DIR/db-$STAMP.sqlite.gz"
  "$(dirname "$0")/../.venv/bin/python3" - "$DB_FILE" "$OUT" <<'PY'
import sys, sqlite3, gzip
src, out = sys.argv[1], sys.argv[2]
backup = out[:-3]  # strip .gz for the temp raw copy
with sqlite3.connect(src) as s, sqlite3.connect(backup) as d:
    s.backup(d)
with open(backup, "rb") as fin, gzip.open(out, "wb") as fout:
    fout.write(fin.read())
import os; os.remove(backup)
PY
  echo "$LOG_TAG sqlite -> $OUT ($(du -h "$OUT" | cut -f1))"
else
  echo "$LOG_TAG unknown DB_TYPE=$DB_TYPE, skipping database"
fi

# ---- plugin runtime data (src/uploads) ------------------------------------
if [ -d "$APP_DIR/src/uploads" ]; then
  OUT="$OUT_DIR/files-$STAMP.tar.gz"
  tar -czf "$OUT" -C "$APP_DIR/src" uploads
  echo "$LOG_TAG files -> $OUT ($(du -h "$OUT" | cut -f1))"
fi

# ---- retention ------------------------------------------------------------
find "$OUT_DIR" -type f \( -name "db-*.sql.gz" -o -name "db-*.sqlite.gz" -o -name "files-*.tar.gz" \) -mtime +"$KEEP_DAYS" -print -delete | sed "s/^/$LOG_TAG pruned /"
echo "$LOG_TAG done"
