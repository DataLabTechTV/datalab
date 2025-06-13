#!/bin/bash

if ! which docker >/dev/null; then
    echo "docker: not found"
    exit 1
fi

if [ $# -lt 1 ]; then
    echo "Usage: $0 [--reset] [--read-only] KUZUDB_PATH"
    exit 2
fi

cleanup() {
    trap - SIGINT SIGTERM
    echo "==> Stopping docker container for kuzudb-explorer"
    docker stop kuzudb-explorer >/dev/null
}

container_exists() {
    docker ps -a --format '{{.Names}}' |
        awk '$0 == "kuzudb-explorer" { found=1 } END { exit !found }' >/dev/null
}

kuzudb_container_mode() {
    mode=$(docker inspect kuzudb-explorer \
        --format='{{range .Config.Env}}{{println .}}{{end}}' |
        awk '{ if (match($0, /MODE=(.*)/, m)) print m[1] }')

    if [ -z "$mode" ]; then
        # default
        mode=READ_WRITE
    fi

    echo "$mode"
}

trap cleanup SIGINT SIGTERM

export MODE=READ_WRITE

while [[ $# -gt 0 ]]; do
    case "$1" in
    --reset)
        if container_exists; then
            echo "==> Removing existing kuzudb-explorer container"
            docker rm -f kuzudb-explorer >/dev/null
        fi

        shift
        ;;
    --read-only)
        export MODE=READ_ONLY
        shift
        ;;
    *)
        break
        ;;
    esac
done

kuzudb_path=$1

if [[ "$kuzudb_path" != /* && "$kuzudb_path" != ./* ]]; then
    kuzudb_path="./$kuzudb_path"
fi

if container_exists; then
    current_mode=$(kuzudb_container_mode)
    echo $current_mode
    echo $MODE

    if [ "$current_mode" != $MODE ]; then
        echo "==> Removing existing $current_mode kuzudb-explorer container"
        docker rm -f kuzudb-explorer >/dev/null
    fi
fi

if container_exists; then
    echo "==> Starting existing docker container for kuzudb-explorer..."
    docker start kuzudb-explorer >/dev/null
else
    echo "==> Creating and starting docker container for kuzudb-explorer..."
    docker run -d --name kuzudb-explorer \
        -p 8000:8000 -v "${kuzudb_path}:/database" \
        -e MODE=$MODE \
        kuzudb/explorer:latest >/dev/null
fi

echo "==> Opening browser at http://localhost:8000..."
open http://localhost:8000

docker logs -n 4 -f kuzudb-explorer
