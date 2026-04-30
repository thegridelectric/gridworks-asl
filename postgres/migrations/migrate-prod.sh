#!/usr/bin/env bash
# ============================================================================
# postgres/migrations/migrate-prod.sh
# ============================================================================
# Forward-only migration runner for the prod sema base.
#
# Usage:
#   migrate-prod.sh <CONNECTION_STRING> [--allow-localhost]
#
# Behavior:
#   1. Refuses to run against localhost unless --allow-localhost is passed
#      (localhost is the domain of init-db.sh; running migrations against
#      it is only useful for testing the migration scripts themselves).
#   2. Ensures public.schema_migrations exists.
#   3. Iterates *.sql in this directory in lexicographic order.
#   4. For each file whose leading NNNN is NOT in schema_migrations:
#        - applies it inside a single transaction (psql -1, ON_ERROR_STOP=1)
#        - INSERTs the version on success, in the same transaction.
#   5. Idempotent — re-running applies nothing when up-to-date.
#
# Failure mode is FAIL-NOT-FALLBACK: any psql error halts the run with
# the offending file named. No retries, no skips, no auto-recovery.
# ============================================================================

set -euo pipefail

if [[ $# -lt 1 ]]; then
    echo "usage: $(basename "$0") <CONNECTION_STRING> [--allow-localhost]" >&2
    exit 2
fi

CONN="$1"; shift
ALLOW_LOCALHOST=0
for arg in "$@"; do
    case "$arg" in
        --allow-localhost) ALLOW_LOCALHOST=1 ;;
        *) echo "unknown arg: $arg" >&2; exit 2 ;;
    esac
done

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Guard against accidentally migrating localhost. Crude but effective.
if [[ "$CONN" == *localhost* || "$CONN" == *127.0.0.1* ]]; then
    if [[ $ALLOW_LOCALHOST -ne 1 ]]; then
        echo "ERROR: refusing to migrate a localhost conn string." >&2
        echo "  Use ./postgres/init-db.sh for local rebuilds, or pass" >&2
        echo "  --allow-localhost to test migration scripts." >&2
        exit 1
    fi
    echo "WARNING: --allow-localhost set; running migrations against localhost." >&2
fi

echo "Applying migrations against: $CONN"

# Bootstrap the tracking table. Safe to run repeatedly.
psql "$CONN" -v ON_ERROR_STOP=1 <<'SQL'
CREATE TABLE IF NOT EXISTS public.schema_migrations (
    version    text PRIMARY KEY,
    filename   text NOT NULL,
    applied_at timestamptz NOT NULL DEFAULT now()
);
SQL

shopt -s nullglob
applied_count=0
skipped_count=0

for sql_file in "$SCRIPT_DIR"/[0-9][0-9][0-9][0-9]_*.sql "$SCRIPT_DIR"/[0-9][0-9][0-9][0-9]-*.sql; do
    [[ -f "$sql_file" ]] || continue
    filename="$(basename "$sql_file")"
    # Extract leading NNNN from "0042_foo.sql" or "0042-foo.sql".
    version="${filename%%[_-]*}"
    if ! [[ "$version" =~ ^[0-9]{4}$ ]]; then
        echo "ERROR: $filename does not start with a 4-digit version" >&2
        exit 1
    fi

    already=$(psql "$CONN" -tAc \
        "SELECT 1 FROM public.schema_migrations WHERE version='$version' LIMIT 1" || true)

    if [[ "$already" == "1" ]]; then
        echo "  skip  $filename (version $version already applied)"
        skipped_count=$((skipped_count + 1))
        continue
    fi

    echo "  apply $filename"
    # -1 wraps the file in a single transaction; the INSERT below runs in
    # the SAME txn via -c so a failure in either rolls back together.
    psql "$CONN" -v ON_ERROR_STOP=1 --single-transaction \
        -f "$sql_file" \
        -c "INSERT INTO public.schema_migrations(version, filename) VALUES ('$version', '$filename');"
    applied_count=$((applied_count + 1))
done

echo ""
echo "Done. Applied $applied_count migration(s); skipped $skipped_count already-recorded."
