---
status: accepted
date: 2026-10-12
deciders: edouard
---

# ADR-018: One-Week Lag on Dependency Updates

## Context and Problem Statement

Taking every dependency update the moment it is published exposes the project to
compromised or broken releases before the ecosystem has reacted. How fresh
should dependencies be?

## Decision Drivers

- Supply-chain safety.
- Avoiding freshly published regressions.
- Still receiving security fixes reasonably promptly.

## Considered Options

1. A seven-day publication lag (`uv lock --upgrade --exclude-newer`).
2. Always take the latest version.
3. Pin exact versions indefinitely.

## Decision Outcome

Chosen option: "One-week lag", following the sibling projects. `make update-deps`
locks to versions published at least seven days ago, then syncs and re-runs
`pip-audit`. Ordinary `uv sync` is unaffected.

### Consequences

- Good, because a malicious or broken release is usually caught within a week.
- Good, because the update path re-audits dependencies.
- Bad, because a critical security fix can be delayed by up to a week unless it
  is taken explicitly.

## More Information

- `make update-deps`
- Related: [ADR-015](015-composed-quality-gates.md)
