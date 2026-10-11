---
status: accepted
date: 2026-10-12
deciders: edouard
---

# ADR-017: Repository Release-Workflow Tests and Artifact Check

## Context and Problem Statement

The lint gate, the Makefile, the packaging configuration and the documentation
are themselves code. They can silently rot — a renamed Make target, a lint stage
that no longer fails, or a wheel that no longer contains the committed renderer
assets.

## Decision Drivers

- Catch tooling regressions before a release.
- Assert the wheel is complete without shipping the repo.
- Keep the documentation honest (executable-looking examples, real images).

## Considered Options

1. `tests/release/` tests plus `scripts/check_artifact.py`.
2. Trust manual review of the tooling.
3. A full CI pipeline only.

## Decision Outcome

Chosen option: "Release-workflow tests". `tests/release/` asserts that:

- `scripts/check_artifact.py` detects missing runtime files, leaked dev files
  and empty renderer assets, and the committed assets are substantial;
- `make help` stays grouped, ordered and colour-free when piped;
- `scripts/lint.sh` fails fast on every stage and preserves the diagnostic;
- the README and docs keep valid-looking Python examples, existing local images
  and balanced code fences.

### Consequences

- Good, because a broken gate or Make target fails the suite.
- Good, because `make check-artifact` can be trusted to gate a release.
- Good, because documentation drift is caught mechanically.
- Bad, because the tests are meta: they test the project's tooling rather than
  its features.

## More Information

- [Technical architecture §9](../technical-architecture.md)
- Related: [ADR-014](014-committed-frontend-bundle.md), [ADR-015](015-composed-quality-gates.md)
