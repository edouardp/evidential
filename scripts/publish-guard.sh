#!/usr/bin/env bash
# Shared guards for publish scripts. Source this, don't run it.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT="$SCRIPT_DIR/.."

# Must be on a branch whose release commit can be pushed
if ! BRANCH=$(git -C "$ROOT" symbolic-ref --quiet --short HEAD); then
    echo "ERROR: Releases require an attached branch; detached HEAD is not supported." >&2
    exit 1
fi

if ! UPSTREAM=$(git -C "$ROOT" rev-parse --abbrev-ref --symbolic-full-name '@{upstream}' 2>/dev/null); then
    echo "ERROR: Release branch '$BRANCH' has no configured upstream." >&2
    exit 1
fi

# Must be clean
if [[ -n "$(git -C "$ROOT" status --porcelain)" ]]; then
    echo "ERROR: Working tree is dirty. Commit or stash changes first." >&2
    exit 1
fi

echo "==> Release branch: $BRANCH -> $UPSTREAM"
