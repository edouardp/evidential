#!/usr/bin/env bash
# Publish the current committed version. Never bump or tag here.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/publish-guard.sh"
cd "$ROOT"

"$SCRIPT_DIR/check-keyring.sh"
make readme-check
make check

echo "==> Fetching PyPI token (approve Keychain access if prompted)..."
UV_PUBLISH_TOKEN=$(uv run --frozen python -m keyring get https://upload.pypi.org/legacy/ __token__)
if [[ -z "$UV_PUBLISH_TOKEN" ]]; then
    echo "ERROR: The production PyPI keyring token is empty." >&2
    exit 1
fi
export UV_PUBLISH_TOKEN

echo "==> Publishing to PyPI"
uv publish dist/*
