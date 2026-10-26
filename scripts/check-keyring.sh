#!/usr/bin/env bash
# Verify the managed CLI starts without requesting or retrieving credentials.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
if ! uv run --frozen python -m keyring --help >/dev/null; then
    echo "ERROR: The project keyring CLI cannot start. Run uv sync before releasing." >&2
    exit 1
fi
