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

docker run -p 8000:8000 --rm -v "${kuzudb_path}:/database" kuzudb/explorer:latest
