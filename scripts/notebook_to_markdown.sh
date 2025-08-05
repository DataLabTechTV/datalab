#!/bin/bash

SCRIPT_DIR="$(dirname "${BASH_SOURCE[0]}")"

if [ $# -lt 1 ]; then
    echo "Usage: $0 PATH"
    exit 1
fi

while [[ $# -gt 0 ]]; do
    case "$1" in
        --clear|-c)
            clear=1
            shift
            ;;
        *)
            break
            ;;
    esac
done

notebook_path=$1
output_dir=$(readlink -f "$SCRIPT_DIR/../local/nbmarkdown")

if [[ "$clear" -eq 1 ]]; then
    nb_basename=$(basename "$notebook_path")
    nb_basename=${nb_basename%.*}
    md_path="${output_dir}/${nb_basename}.md"
    assets_path="${output_dir}/${nb_basename}_files"
    rm -vf "$md_path"
    rm -vrf "$assets_path"
    exit
fi

uv run jupyter nbconvert "$notebook_path" \
    --to markdown \
    --output-dir "$output_dir"
