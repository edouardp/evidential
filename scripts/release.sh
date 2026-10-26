#!/usr/bin/env bash
# Release with the same chooser, version requests, keyring and GitHub flow as Galaga.
set -euo pipefail

if [[ $# -eq 0 ]]; then
    echo "Usage: $0 <patch|minor|major>" >&2
    echo "       $0 --version <X.Y.Z|X.Y.ZaN|X.Y.ZbN|X.Y.ZrcN>" >&2
    exit 2
fi

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/publish-guard.sh"
cd "$ROOT"

CURRENT=$(grep '^version' pyproject.toml | head -1 | sed 's/.*"\(.*\)"/\1/')
RESOLVED=$(python3 "$SCRIPT_DIR/release_version.py" "$CURRENT" "$@")
read -r NEW RELEASE_KIND <<< "$RESOLVED"

if git show-ref --verify --quiet "refs/tags/v$NEW"; then
    echo "ERROR: Tag v$NEW already exists." >&2
    exit 1
fi

# Fail before changing the version, opening an editor or creating a commit.
echo "==> Checking notebook-generated README and images"
make readme-check

echo "==> Bumping $CURRENT -> $NEW"
python3 - "$CURRENT" "$NEW" <<'PY'
import sys
from pathlib import Path

path = Path("pyproject.toml")
path.write_text(path.read_text().replace(f'version = "{sys.argv[1]}"', f'version = "{sys.argv[2]}"', 1))
PY
uv lock

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
    echo "ERROR: Changelog not edited. No release was committed or published." >&2
    echo "Review the version and changelog edits before retrying." >&2
    exit 1
fi
uvx rumdl fmt CHANGELOG.md

git add -- pyproject.toml uv.lock CHANGELOG.md
git commit -m "Release v$NEW"

echo "==> Running the full local validation gate"
make validate

# Guard the committed state again, rebuild clean artifacts, check metadata and
# retrieve the token through the same explicit keyring command as Galaga.
make pypi

echo "==> Tagging v$NEW"
git push
git tag "v$NEW"
git push origin "v$NEW"

echo "==> Creating GitHub release"
GH_RELEASE_ARGS=(release create "v$NEW" --title "v$NEW" --notes-file CHANGELOG.md)
if [[ "$RELEASE_KIND" == "prerelease" ]]; then
    GH_RELEASE_ARGS+=(--prerelease)
fi
gh "${GH_RELEASE_ARGS[@]}"

echo "==> Released evidential v$NEW"
