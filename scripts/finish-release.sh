#!/usr/bin/env bash
# Resume only the idempotent post-upload steps. Never builds or retrieves tokens.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/publish-guard.sh"
cd "$ROOT"

VERSION="${1:?Usage: finish-release.sh VERSION}"
CURRENT=$(grep '^version' pyproject.toml | head -1 | sed 's/.*"\(.*\)"/\1/')
if [[ "$CURRENT" != "$VERSION" ]]; then
    echo "ERROR: Requested version must match pyproject.toml ($CURRENT)." >&2
    exit 1
fi
RECEIPT=$(git rev-parse --git-path evidential-release.json)
COMMIT=$(git rev-parse HEAD)
RELEASE_KIND=$(python3 "$SCRIPT_DIR/release_state.py" verify "$RECEIPT" "$VERSION" "$COMMIT")
TAG="v$VERSION"
REMOTE=$(git config --get "branch.$BRANCH.remote")
MERGE_REF=$(git config --get "branch.$BRANCH.merge")
if [[ "$REMOTE" == "." ]]; then
    echo "ERROR: Release upstream must be a pushable remote." >&2
    exit 1
fi

if git show-ref --verify --quiet "refs/tags/$TAG" && [[ "$(git rev-parse "$TAG^{commit}")" != "$COMMIT" ]]; then
    echo "ERROR: Tag $TAG points at another commit; refusing to replace it." >&2
    exit 1
fi
REMOTE_TAG=$(git ls-remote "$REMOTE" "refs/tags/$TAG" "refs/tags/$TAG^{}")
if [[ -n "$REMOTE_TAG" ]]; then
    REMOTE_COMMIT=$(printf '%s\n' "$REMOTE_TAG" | tail -1 | cut -f1)
    if [[ "$REMOTE_COMMIT" != "$COMMIT" ]]; then
        echo "ERROR: Remote tag $TAG points at another commit; refusing to replace it." >&2
        exit 1
    fi
fi

NOTES=$(mktemp)
trap 'rm -f "$NOTES"' EXIT
python3 "$SCRIPT_DIR/release_state.py" notes CHANGELOG.md "$VERSION" > "$NOTES"
git push "$REMOTE" "HEAD:$MERGE_REF"
if ! git show-ref --verify --quiet "refs/tags/$TAG"; then
    git tag "$TAG" "$COMMIT"
fi
if [[ -z "$REMOTE_TAG" ]]; then
    git push "$REMOTE" "refs/tags/$TAG"
fi

# Query once; failure to query is an error, not permission to duplicate a release.
# Explicit repo selection follows the upstream even when it isn't called origin.
REPO_URL=$(git remote get-url "$REMOTE")
RELEASES=$(gh release list --repo "$REPO_URL" --limit 1000 --json tagName --jq '.[].tagName')
if ! grep -Fxq "$TAG" <<< "$RELEASES"; then
    GH_RELEASE_ARGS=(release create "$TAG" --repo "$REPO_URL" --verify-tag --title "$TAG" --notes-file "$NOTES")
    if [[ "$RELEASE_KIND" == "prerelease" ]]; then
        GH_RELEASE_ARGS+=(--prerelease)
    fi
    gh "${GH_RELEASE_ARGS[@]}"
fi
python3 "$SCRIPT_DIR/release_state.py" complete "$RECEIPT" "$VERSION" "$COMMIT"
echo "==> Released evidential $TAG"
