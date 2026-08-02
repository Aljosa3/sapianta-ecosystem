#!/bin/sh

set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
DEFAULT_ROOT=$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)
REPOSITORY_ROOT=${1:-$DEFAULT_ROOT}

install_hook() {
    source_path=$1
    target_path=$2

    if [ ! -f "$source_path" ]; then
        echo "Governance hook installation failed closed: missing $source_path" >&2
        exit 1
    fi
    if [ ! -d "$(dirname -- "$target_path")" ]; then
        echo "Governance hook installation failed closed: missing target directory for $target_path" >&2
        exit 1
    fi

    cp "$source_path" "$target_path"
    chmod 0755 "$target_path"

    if ! cmp -s "$source_path" "$target_path"; then
        echo "Governance hook installation failed closed: byte mismatch at $target_path" >&2
        exit 1
    fi
}

install_hook \
    "$REPOSITORY_ROOT/scripts/hooks/pre-commit" \
    "$REPOSITORY_ROOT/.git/hooks/pre-commit"
install_hook \
    "$REPOSITORY_ROOT/sapianta_system/scripts/hooks/pre-commit" \
    "$REPOSITORY_ROOT/sapianta_system/.git/hooks/pre-commit"

echo "Governance hooks installed with exact canonical bytes."
