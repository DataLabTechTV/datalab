#!/bin/bash

if ! which docker >/dev/null; then
    echo "docker: not found"
    exit 1
fi

if [ $# -lt 1 ]; then
    echo "Usage: $0 KUZUDB_PATH"
    exit 2
fi

kuzudb_path=$1

if [[ "$kuzudb_path" != /* && "$kuzudb_path" != ./* ]]; then
    kuzudb_path="./$kuzudb_path"
fi

cleanup() {
    echo "==> Cleaning up kuzudb-explorer..."
    trap - SIGINT SIGTERM

    echo "Stopping kuzudb-explorer"
    docker stop kuzudb-explorer >/dev/null

    echo "Removing kuzudb-explorer"
    docker rm kuzudb-explorer >/dev/null

    if [ -e "$kuzudb_path/.lock" ]; then
        echo "Removing database lock"
        rm -f "$kuzudb_path/.lock"
    fi
}

trap cleanup SIGINT SIGTERM

if [ -e "$kuzudb_path/.lock" ]; then
    echo "error: database is locked"
    exit 3
fi

echo "==> Starting kuzudb-explorer..."
docker run -q -d --name kuzudb-explorer -p 8000:8000 \
    -v "${kuzudb_path}:/database" kuzudb/explorer:latest \
    >/dev/null

echo "==> Opening browser..."
open http://localhost:8000

echo "==> Following logs..."
docker logs -f kuzudb-explorer
