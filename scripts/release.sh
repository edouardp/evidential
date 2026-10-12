#!/usr/bin/env bash
#
# Release evidential: bump the version, update the changelog, run the full
# validation gate, build, publish to PyPI, and tag the release.
#
# Usage:
#   ./scripts/release.sh patch   # bug fixes
#   ./scripts/release.sh minor   # new features
#   ./scripts/release.sh major   # breaking changes
#
# `make release` runs the interactive chooser and then calls this.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

# --- Guard: clean working tree on main ---
BRANCH=$(git branch --show-current)
if [[ "$BRANCH" != "main" ]]; then
    echo "ERROR: Must be on main branch (currently on '$BRANCH')" >&2
    exit 1
fi
if [[ -n "$(git status --porcelain)" ]]; then
    echo "ERROR: Working tree is not clean. Commit or stash changes." >&2
    exit 1
fi

BUMP_TYPE="${1:?Usage: $0 <patch|minor|major>}"

# --- Read current version ---
CURRENT=$(grep '^version' pyproject.toml | head -1 | sed 's/.*"\(.*\)"/\1/')
IFS='.' read -r MAJOR MINOR PATCH <<< "$CURRENT"

case "$BUMP_TYPE" in
    patch) NEW="$MAJOR.$MINOR.$((PATCH + 1))" ;;
    minor) NEW="$MAJOR.$((MINOR + 1)).0" ;;
    major) NEW="$((MAJOR + 1)).0.0" ;;
    *) echo "ERROR: bump type must be patch, minor, or major" >&2; exit 1 ;;
esac

echo "==> Bumping $CURRENT -> $NEW"

# --- Update version ---
sed -i '' "s/^version = \"$CURRENT\"/version = \"$NEW\"/" pyproject.toml
uv lock

# --- Update CHANGELOG ---
DATE=$(date +%Y-%m-%d)
TMPFILE=$(mktemp)
cat > "$TMPFILE" <<EOF
# Changelog

## $NEW ($DATE)

<!-- Fill in release notes, then save and close -->

EOF
tail -n +2 CHANGELOG.md >> "$TMPFILE"
cp "$TMPFILE" CHANGELOG.md
rm "$TMPFILE"

${EDITOR:-vim} CHANGELOG.md

if grep -q '<!-- Fill in release notes' CHANGELOG.md; then
    echo "ERROR: Changelog not edited. Aborting." >&2
    git checkout pyproject.toml uv.lock CHANGELOG.md
    exit 1
fi

# Keep the changelog in the house markdown style.
uvx rumdl fmt CHANGELOG.md

# --- Commit ---
git add -A
git commit -m "Release v$NEW"

# --- Tests ---
echo "==> Running the full validation gate"
make validate

# --- Build + metadata check ---
echo "==> Building"
rm -rf dist/
make build
uvx twine check dist/*

# --- Publish ---
echo "==> Publishing to PyPI"
uv publish --keyring-provider subprocess --username __token__

# --- Tag + push ---
echo "==> Tagging v$NEW"
git push
git tag "v$NEW"
git push origin "v$NEW"

echo "==> Released evidential v$NEW 🎉"
