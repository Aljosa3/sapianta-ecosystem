#!/bin/sh

set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
DEFAULT_ROOT=$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)
REPOSITORY_ROOT=${1:-$DEFAULT_ROOT}

resolve_hook_path() {
    repository_path=$1

    if ! hook_path=$(git -C "$repository_path" rev-parse \
        --path-format=absolute --git-path hooks/pre-commit 2>/dev/null); then
        echo "Governance hook installation failed closed: Git metadata unavailable for $repository_path" >&2
        exit 1
    fi
    if [ -z "$hook_path" ]; then
        echo "Governance hook installation failed closed: empty hook path for $repository_path" >&2
        exit 1
    fi

    printf '%s\n' "$hook_path"
}

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

    if [ "$source_path" != "$target_path" ]; then
        cp "$source_path" "$target_path"
    fi
    chmod 0755 "$target_path"

    if ! cmp -s "$source_path" "$target_path"; then
        echo "Governance hook installation failed closed: byte mismatch at $target_path" >&2
        exit 1
    fi
}

install_hook \
    "$REPOSITORY_ROOT/scripts/hooks/pre-commit" \
    "$(resolve_hook_path "$REPOSITORY_ROOT")"
install_hook \
    "$REPOSITORY_ROOT/sapianta_system/scripts/hooks/pre-commit" \
    "$(resolve_hook_path "$REPOSITORY_ROOT/sapianta_system")"

echo "Governance hooks installed with exact canonical bytes."
