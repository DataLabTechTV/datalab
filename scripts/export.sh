#!/bin/bash

SCRIPT_PATH="$(readlink -f "${BASH_SOURCE[0]}")"
SCRIPT_DIR="$(dirname "$SCRIPT_PATH")"

INIT_SCRIPT=${SCRIPT_DIR}/init.sql

# shellcheck source=/dev/null
. "$SCRIPT_DIR"/../.env

LOCAL_DIR=$SCRIPT_DIR/../local

if [ ! -r "$INIT_SCRIPT" ]; then
    echo "init.sql: file not found or unreadable"
    exit 1
fi

if ! which duckdb >/dev/null; then
    echo "duckdb: not found in PATH"
    exit 2
fi

for export_script in "$SCRIPT_DIR"/export_*.sql; do
    echo "==> Running $export_script"
    duckdb -init "$INIT_SCRIPT" "${LOCAL_DIR}/${ENGINE_DB}" -f "$export_script"
done

echo "==> Done"
