---
status: accepted
date: 2026-11-04
deciders: edouard
---

# ADR-092: Frontend Quality Gates and Browser Measurements

## Context and Problem Statement

The Python gates did not check JavaScript semantics or types. High line coverage
missed boundary mismatches, and jsdom benchmarks excluded label fitting, point
clustering, ResizeObserver callbacks and browser layout. Functional tests exercised
only Chromium and assumed its subpixel pointer rounding and event scheduling.

## Decision Drivers

- Keep release validation local and reproducible.
- Introduce useful static contracts without a wholesale TypeScript migration.
- Exercise invariants and browser behavior as well as individual code paths.
- Separate processing measurements from frame-inclusive browser measurements.

## Considered Options

1. Continue relying on Python checks, line coverage and Chromium alone.
2. Add JavaScript linting, gradual strict checking, branch coverage and a local browser matrix.
3. Rewrite the frontend in TypeScript before adding further gates.

## Decision Outcome

Choose option 2. ESLint checks all maintained frontend JavaScript. TypeScript
strictly checks JSDoc contracts in URL, CSV, aggregate and scale modules; compile-only
negative examples verify the contracts reject invalid inputs. Other JavaScript
remains unchecked until its boundary is explicitly typed. Dependencies are locked;
the minimatch override selects a patched version used successfully by these gates.

The shell lint entry point and pre-commit run the same frontend checks. Ruff caps
maintained Python function complexity at 20. Python coverage includes branches
and requires 90%; frontend source coverage requires 95% lines and 85% branches.
Shared Python/JavaScript fixtures and exhaustive small pagination cases verify
behavioral contracts rather than repeating implementation details.

Chromium remains the default screenshot engine. `make test-browser-matrix` also
runs WebKit, failing if the requested engine is unavailable. Tests allow fractional
layout rounding, await virtual-list changes and use keyboard access for segments
too narrow for reliable physical pointer targeting.

`make benchmark-browser` measures actual bundled tables through three animation
frames per operation, with automatic labels, pixel clusters and observers enabled.
Preparation/data transfer is outside its timer. Frame waits and layout are included;
the result is not a GPU paint measurement or a machine-independent timing gate.

### Consequences

- Additional npm development tools and a WebKit installation are required for the matrix.
- Existing JavaScript can gain contracts incrementally without implicit `any` in checked modules.
- Coverage remains a floor; invariant and browser tests provide independent evidence.
- Performance reports identify their included and excluded work explicitly.

## More Information

- [ADR-037](037-renderer-module-boundaries.md)
- [ADR-039](039-derived-data-cache-and-group-index.md)
- [ADR-091](091-runtime-boundary-contracts.md)
- [Performance measurements](../performance.md)
