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

`src/evidential/static/table.js` and `table.css` are **committed** so the
Python package needs no JS toolchain. After editing anything under
`frontend/src/`, run `make frontend-build` and commit the rebuilt bundle
together with the source change.

## Packaging

The build uses `uv_build` (`[tool.uv] package = true`). `make check-artifact`
builds the wheel and sdist and verifies they contain every runtime module plus
`static/table.js` and `static/table.css`, and that no `tests/`, `notebooks/` or
`frontend/` files leak into a release.

## Releasing

Releases follow the house flow (`../galaga`, `../gamr`):

1. `make release` (or `make release-patch` / `release-minor` / `release-major`)
   prompts for the bump type, then [`scripts/release.sh`](scripts/release.sh):
   - guards that you are on `main` with a clean tree,
   - bumps `version` in `pyproject.toml` and refreshes `uv.lock`,
   - prepends a `CHANGELOG.md` entry and opens `$EDITOR` for the notes,
   - commits, runs `make validate`, builds and `twine check`s the artifacts,
   - publishes with `uv publish` (token via keyring) and tags `vX.Y.Z`.
2. `make check` runs `twine check` on an existing `dist/`; `make pypi` builds and
   publishes without bumping.
3. CI ([`.github/workflows/tests.yml`](.github/workflows/tests.yml)) runs the
   lint gate, `marimo check`, the Python/frontend tests and the artifact check on
   every push and pull request.

`tests/release/test_release.py` keeps the metadata, changelog entry, release
script and CI in place — in particular, the `version` in `pyproject.toml` must
have a matching `CHANGELOG.md` section.

## Marimo notebooks

- The cell that creates a widget must **not** reference controls; a separate
  reactive cell should call `set_controls(...)`. Referencing a control makes
  Marimo recreate the widget on every change. See
  [docs/design-and-dx.md](docs/design-and-dx.md).
- Notebooks are checked with `make check-notebooks`.

## marimo Studio views

- The Studio dashboard demo lives in `notebooks/21_studio_dashboard.py` with a
  committed view in `notebooks/studio/21_studio_dashboard/dashboard/`.
- Run it with `make studio-serve` (Server runtime) and validate the committed
  view with `make studio-validate`.
- Keep cells used as projection targets **named**; anonymous cells only get
  positional `cell-N` aliases. `tests/release/test_studio_views.py` checks that
  every `<marimo-cell>` / `mo-value` target resolves against the notebook.
- See [docs/marimo-studio.md](docs/marimo-studio.md) and
  [ADR-021](docs/adr/021-marimo-studio-projections.md).

## Commits

Commit as work progresses, with a descriptive message explaining the change and
the reason. Never `git commit --amend` or force-push.

## Architecture decisions

Significant design decisions are recorded as ADRs in
[`docs/adr/`](docs/adr/README.md) using the [MADR](https://adr.github.io/madr/)
format.

- Write a new ADR for a new design decision, and update the relevant ADR when
  you change an existing one. A decision is not finished until its ADR is
  written.
- Number sequentially, fill in every section, and add a row to the
  [index](docs/adr/README.md#adr-index). `tests/release/test_adrs.py` checks the
  numbering, frontmatter and index stay consistent.
