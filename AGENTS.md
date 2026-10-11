# Contributor guide

## Quality gates

Every check is defined twice, and the two must stay in sync:

- [`.pre-commit-config.yaml`](.pre-commit-config.yaml) — runs on `git commit`
  (install with `make install-hooks`).
- [`scripts/lint.sh`](scripts/lint.sh) — the same stages, runnable with
  `make lint` (or `make format` to auto-fix).

The gates are: **ruff** (lint + format), **bandit**, **pip-audit**, **pyrefly**
(types), **shellcheck**, **checkmake** (Makefile) and **rumdl** (markdown).
`make validate` runs the gates plus `marimo check`, the test suites and a build.

## Tests

- Add a unit test whenever you add code.
- Add a regression test whenever you fix a bug — the test should fail before the
  fix and pass after.
- Layers, from cheapest to slowest:
  - `frontend/test_*.js` — jsdom unit tests (`make frontend-test`).
  - `tests/` — Python unit tests (`make test-python`).
  - `tests/browser/` — Playwright functional tests (`make test-browser`).
  - `tests/release/` — repository/workflow tests: the Makefile help, that the
    lint gate fails fast, that the wheel contains the renderer assets, and that
    documentation examples stay valid.

## Frontend

`src/evidence_tables/static/table.js` and `table.css` are **committed** so the
Python package needs no JS toolchain. After editing anything under
`frontend/src/`, run `make frontend-build` and commit the rebuilt bundle
together with the source change.

## Packaging

The build uses `uv_build` (`[tool.uv] package = true`). `make check-artifact`
builds the wheel and sdist and verifies they contain every runtime module plus
`static/table.js` and `static/table.css`, and that no `tests/`, `notebooks/` or
`frontend/` files leak into a release.

## Marimo notebooks

- The cell that creates a widget must **not** reference controls; a separate
  reactive cell should call `set_controls(...)`. Referencing a control makes
  Marimo recreate the widget on every change. See
  [docs/design-and-dx.md](docs/design-and-dx.md).
- Notebooks are checked with `make check-notebooks`.

## Commits

Commit as work progresses, with a descriptive message explaining the change and
the reason. Never `git commit --amend` or force-push.
