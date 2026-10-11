---
status: accepted
date: 2026-10-12
deciders: edouard
---

# ADR-015: Composed Quality Gates Mirrored in Pre-commit and a Script

## Context and Problem Statement

The project has Python, JavaScript, shell and Markdown. Quality checks must run
both on commit (fast, local) and in CI (authoritative), and the two must not
drift apart.

## Decision Drivers

- One definition of "clean" for the whole repository.
- Same checks locally and in CI.
- Fail fast, with the failing tool's output preserved.

## Considered Options

1. A composed gate defined once and invoked from both pre-commit and a script.
2. A different, ad hoc check list in each place.
3. Rely on CI only.

## Decision Outcome

Chosen option: "Composed gate", following the sibling projects. The stages are:
**ruff** (lint + format), **bandit**, **pip-audit**, **pyrefly** (types),
**shellcheck**, **checkmake** (Makefile) and **rumdl** (markdown, including the
ADRs). They are defined in `.pre-commit-config.yaml` and mirrored by
`scripts/lint.sh`, which fails fast. `make validate` runs the gate plus
`marimo check`, the tests and a build.

### Consequences

- Good, because contributors and CI agree on what "clean" means.
- Good, because a failure stops the run and keeps the diagnostic.
- Good, because the checks are exercised by tests
  ([ADR-017](017-release-workflow-tests.md)).
- Bad, because seven tools must be kept configured and in sync.
- Bad, because the gate is slower than any single tool.

## More Information

- [Design & DX §3](../design-and-dx.md)
- [`.pre-commit-config.yaml`](../../.pre-commit-config.yaml), [`scripts/lint.sh`](../../scripts/lint.sh)
