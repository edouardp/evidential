---
status: accepted
date: 2026-11-04
deciders: edouard
---

# ADR-091: Explicit Runtime Boundary Contracts

## Context and Problem Statement

The repository review reproduced executable data URLs, shallow configuration
ownership, unquoted SQL field names, parameter replacement inside valid literals,
different Python/browser summaries, and CSV record corruption from carriage returns.
High line coverage did not establish consistent boundary behavior.

## Decision Drivers

- Preserve the public fluent and mapping APIs.
- Keep authored SQL expressions distinct from field identifiers and bound values.
- Make reusable columns own their nested configuration without copying callable state.
- Verify equivalent behavior across Python, JavaScript and real browser rendering.

## Considered Options

1. Patch each caller independently and retain its existing implicit rules.
2. Introduce small boundary helpers and shared behavioral fixtures.
3. Replace the public API and both renderers with a new schema framework.

## Decision Outcome

Choose option 2. Navigation uses one browser-parsed URL allowlist: HTTP, HTTPS,
mailto, telephone, and relative targets resolving to supported protocols.
Rejected cell/row/information links remain inert text. Trusted HTML is still an
explicit separate opt-in; image sources are not navigation URLs.

Column construction and mapping access copy configuration containers recursively;
callable source objects retain identity. SQL helpers quote field/alias identifiers
and preserve explicitly authored aggregate expressions. Live parameters are bound
only outside strings, quoted identifiers, dollar strings and nested comments.

Portable summaries have shared fixtures in `tests/fixtures/summary-contract.json`.
Nulls are excluded, counts are zero for empty inputs, other empty aggregates are
null, min/max support strings and ISO dates, and numeric aggregates require numeric
values. Distinctness separates booleans from numbers and compares JSON structures
by value. Frontend filtering recomputes the same operations as Python preparation.

CSV serialization is a pure helper that quotes both carriage returns and line
feeds, commas and double quotes, preserving raw source values and record boundaries.

### Consequences

- Public inputs remain convenient while executable navigation is rejected.
- Defensive copies cost proportional to configuration size, independent of row count.
- Shared fixtures catch semantic drift that independent line-coverage tests miss.
- Focused browser tests verify navigation safety and date summary filtering.

## More Information

- [ADR-038](038-typed-configuration-validation.md)
- [ADR-064](064-display-only-row-layout.md)
- `src/evidential/_sql.py`, `src/evidential/_spec.py`
- `frontend/src/urls.js`, `frontend/src/csv.js`, `frontend/src/aggregates.js`
