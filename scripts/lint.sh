#!/usr/bin/env bash
#
# Run every lint/format/security gate for evidential.
#
# Usage:
#   ./scripts/lint.sh          # check only (CI, pre-commit parity)
#   ./scripts/lint.sh --fix    # auto-fix formatting and lint issues
#
# Mirrors .pre-commit-config.yaml so the two never drift.
set -euo pipefail

FIX=""
[[ "${1:-}" == "--fix" ]] && FIX="1"

echo "=== ruff lint ==="
if [[ -n "$FIX" ]]; then
    uv run ruff check . --fix
    uv run ruff format .
else
    uv run ruff check .
    uv run ruff format --check .
fi

echo "=== bandit ==="
uv run bandit -r -c .bandit -q src/evidential

echo "=== pip-audit ==="
uv run pip-audit

echo "=== pyrefly ==="
uv run pyrefly check

echo "=== shellcheck ==="
find scripts -name '*.sh' -exec shellcheck -x -e SC2016 -e SC1091 {} +

echo "=== checkmake ==="
checkmake --config=.checkmake Makefile

echo "=== rumdl ==="
if [[ -n "$FIX" ]]; then
    uvx rumdl fmt README.md docs notebooks
else
    uvx rumdl check README.md docs notebooks
fi

echo "All lints passed"
