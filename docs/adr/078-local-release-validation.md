---
status: accepted
date: 2026-10-26
deciders: edouard
---

# ADR-078: Local Release Validation

## Context and Problem Statement

The repository initially configured GitHub Actions to validate pushes and pull
requests. During the first release, the maintainer confirmed that releases
should follow the sibling Galaga and Gamr workflows: validate, build and publish
on the local machine. Future CI/CD, if introduced, should use Buildkite.

## Decision Drivers

- Match the maintainer's established local release workflow.
- Validate the exact committed release snapshot before publishing.
- Retain all quality, browser, packaging and metadata checks.
- Keep credentials inside the publishing tool's keyring integration.

## Considered Options

1. Keep GitHub Actions as a required release gate.
2. Add a Buildkite pipeline immediately.
3. Use local release gates and reserve Buildkite for future automation.

## Decision Outcome

Chosen option: **3**. Remove GitHub Actions workflows and their README badge.
`make validate` runs lint/security/type checks, notebook validation, Python and
frontend tests, committed asset freshness, required-browser Playwright tests,
and a build. `make check` verifies runtime artifact contents and PyPI metadata.
Run both from a clean tracked checkout of the release commit.

The initial release publishes the existing 0.1.0 version after merging to
`main`. Later releases use the local release script. Following
[ADR-080](080-house-release-commands.md), publishing retrieves the token via
the project-managed `python -m keyring get`, exports `UV_PUBLISH_TOKEN` and
runs `uv publish`, followed by
Git pushes, a version tag and automatic GitHub release notes. GitHub hosts the source and
release metadata; it does not build or publish the package.

No CI/CD pipeline is required for release. If automation is requested later,
implement it in Buildkite rather than GitHub Actions. This decision supersedes
the CI-specific parts of ADR-014, ADR-015, ADR-016 and ADR-034, while retaining
their bundle, quality, testing and packaging decisions.

### Consequences

Release validation remains reproducible through committed commands and locked
dependencies, with the maintainer responsible for running and recording the
gates. A missing browser fails release validation instead of skipping tests.
Pushing to GitHub triggers no build jobs. Future automated validation requires
a separate Buildkite decision and implementation.

## More Information

- [Release process](../RELEASE_PROCESS.md).
- `Makefile`, `scripts/release.sh`, `tests/release/test_release.py`.
