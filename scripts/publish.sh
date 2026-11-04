#!/usr/bin/env bash
# Publish the current committed version. Never bump or tag here.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/publish-guard.sh"
cd "$ROOT"

VERSION=$(grep '^version' pyproject.toml | head -1 | sed 's/.*"\(.*\)"/\1/')
COMMIT=$(git rev-parse HEAD)
RECEIPT=$(git rev-parse --git-path evidential-release.json)
python3 "$SCRIPT_DIR/release_state.py" publish "$RECEIPT" "$VERSION"

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
unset UV_PUBLISH_TOKEN
python3 "$SCRIPT_DIR/release_state.py" record "$RECEIPT" "$VERSION" "$COMMIT"
