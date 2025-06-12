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
    trap - SIGINT SIGTERM
    echo "==> Stopping ephemeral docker container for kuzudb-explorer"
    docker stop kuzudb-explorer >/dev/null
}

trap cleanup SIGINT SIGTERM

echo "==> Starting ephemeral docker container for kuzudb-explorer..."
docker run -d --name kuzudb-explorer \
    -p 8000:8000 -v "${kuzudb_path}:/database" \
    -e MODE=READ_ONLY \
    --rm kuzudb/explorer:latest >/dev/null

echo "==> Opening browser at http://localhost:8000..."
open http://localhost:8000

docker logs -f kuzudb-explorer
