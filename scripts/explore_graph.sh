#!/bin/bash

KUZUDB_EXPLORER_VERSION=0.11.0
CONTAINER_NAME=datalab-kuzudb-explorer-1
PROJECT_NAME=datalab

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
    echo "==> Stopping docker container for $CONTAINER_NAME"
    docker stop $CONTAINER_NAME >/dev/null
}

container_exists() {
    docker ps -a --format '{{.Names}}' |
        awk '$0 == "'$CONTAINER_NAME'" { found=1 } END { exit !found }' >/dev/null
}

kuzudb_container_mode() {
    local mode

    mode=$(docker inspect $CONTAINER_NAME \
        --format='{{range .Config.Env}}{{println .}}{{end}}' |
        awk '{ if (match($0, /MODE=(.*)/, m)) print m[1] }')

    if [ -z "$mode" ]; then
        # default
        mode=READ_WRITE
    fi

    echo "$mode"
}

kuzudb_container_db_path_cmp() {
    local new_db_path
    local cur_db_path

    if [ $# -lt 1 ]; then
        exit 3
    fi

    new_db_path=$(readlink -f "$1")

    fmt='{{range .Mounts}}{{if eq .Destination "/database"}}{{.Source}}{{end}}{{end}}'
    cur_db_path=$(docker inspect $CONTAINER_NAME --format "$fmt")

    [ "$cur_db_path" = "$new_db_path" ]
}

trap cleanup SIGINT SIGTERM

export MODE=READ_WRITE

while [[ $# -gt 0 ]]; do
    case "$1" in
    --reset)
        if container_exists; then
            echo "==> Removing existing $CONTAINER_NAME container"
            docker rm -f $CONTAINER_NAME >/dev/null
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

kuzudb_path=$(readlink -f "$1")
kuzudb_file=${kuzudb_path##*/}

if container_exists; then
    current_mode=$(kuzudb_container_mode)

    if [ "$current_mode" != $MODE ]; then
        echo "==> Removing existing $current_mode $CONTAINER_NAME container"
        docker rm -f $CONTAINER_NAME >/dev/null
    fi

    if ! kuzudb_container_db_path_cmp "$kuzudb_path"; then
        echo "==> Removing existing $CONTAINER_NAME container for $kuzudb_path"
        docker rm -f $CONTAINER_NAME >/dev/null
    fi
fi

if container_exists; then
    echo "==> Starting existing docker container: $CONTAINER_NAME"
    docker start $CONTAINER_NAME >/dev/null
else
    echo "==> Creating and starting docker container: $CONTAINER_NAME"
    docker run -d -p 8000:8000 \
        --name $CONTAINER_NAME \
        --network ${PROJECT_NAME}_default \
        --label com.docker.compose.project=$PROJECT_NAME \
        -v "$kuzudb_path:/database/$kuzudb_file" \
        -e KUZU_FILE="$kuzudb_file" -e MODE=$MODE \
        kuzudb/explorer:$KUZUDB_EXPLORER_VERSION >/dev/null
fi

echo "==> Opening browser at http://localhost:8000..."
open http://localhost:8000

docker logs -n 4 -f $CONTAINER_NAME
