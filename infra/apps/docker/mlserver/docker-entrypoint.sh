#!/usr/bin/env bash

set -e

# shellcheck source=/dev/null
. .venv/bin/activate

dlctl ml server "$@"
