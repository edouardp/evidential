---
status: accepted
date: 2026-10-13
deciders: edouard
---

# ADR-034: `uv_build` as the Build Backend

## Context and Problem Statement

The wheel may only contain the `evidential` import package — including the
committed JS/CSS bundle from [ADR-014](014-committed-frontend-bundle.md) — and
the sdist must stay free of `tests/`, `notebooks/` and `frontend/` (the
`check_artifact.py` gate). We need a PEP 517 backend that ships package data and
produces a narrow source distribution, ideally without hand-written file lists.
The other projects in this workspace (`galaga`, `gamr`, `wigglystuff`) use
`hatchling`.

## Decision Drivers

- One import package, standard `src/` layout.
- The renderer assets live **inside** the package and must be installed with it.
- A narrow, reviewable sdist with no development files.
- Minimal configuration and a fast build.
- No custom build steps or generated-at-build-time files.

## Considered Options

1. `uv_build`, Astral's Rust build backend (shipped with `uv`).
2. `hatchling`, the pure-Python backend the other projects use.
3. `setuptools` with `package-data` / `MANIFEST.in`.

## Decision Outcome

Chosen option: "`uv_build`". It auto-detects `src/evidential`, ships the `.py`
files, `py.typed` and `static/` as package data (so anywidget finds the renderer
next to the module), and its default sdist is exactly the package plus metadata —
which is what the artifact gate asserts, with no `exclude` rules to maintain.
`uv build` also takes a PEP 517 fast path for this backend, so builds are
milliseconds with no throwaway environment. `[tool.uv] package = true` marks the
project as a package for `uv sync`/editable installs.

The `uv_build` build requirement is a bounded range (`>=0.11.7,<0.12.0`) because
the backend versions in lockstep with `uv`; keep it in step when bumping `uv`.

Option 2 was rejected as more configuration for the same result here: hatchling's
default sdist is VCS-wide, so it would need an `include`/`exclude` list to satisfy
the gate, and `only-packages` + `artifacts` (wigglystuff's belt-and-braces for
its bundle) is unnecessary when the bundle is already package data. Option 3 was
rejected: a hand-maintained file list is the drift risk the committed bundle was
meant to avoid.

### Consequences

- Good, because file inclusion is right by default — the wheel and sdist are
  correct with no build config.
- Good, because builds are fast and need no Python build environment.
- Good, because the same gate (`check_artifact.py`) verifies the result.
- Bad, because it is opinionated: exactly one import package, no build hooks and
  no arbitrary include/exclude beyond `[tool.uv.build-backend]`'s knobs. If the
  project is split into several import packages, or needs build-time file
  selection, it should move to hatchling.
- Note: the `uv_build` pin tracks `uv`, so upgrading `uv` may require widening it.

## More Information

- [AGENTS.md § Packaging](../../AGENTS.md)
- `scripts/check_artifact.py`
- Related: [ADR-014](014-committed-frontend-bundle.md),
  [ADR-017](017-release-workflow-tests.md)
