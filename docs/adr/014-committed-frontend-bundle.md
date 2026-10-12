---
status: accepted
date: 2026-10-12
deciders: edouard
---

# ADR-014: Committed Frontend Bundle, No JS Toolchain for Users

## Context and Problem Statement

The widget is an anywidget: it needs a JavaScript module and a stylesheet in the
browser. Users install the Python package; they should not need Node, npm or
esbuild to render a table.

## Decision Drivers

- `pip install` (or `uv add`) is the whole install.
- Reproducible builds from source.
- A reviewable, testable frontend.

## Considered Options

1. Commit the esbuild bundle into `src/evidential/static/`.
2. Build the frontend as part of the Python build.
3. Load the module from a CDN.

## Decision Outcome

Chosen option: "Commit the bundle". `frontend/src/` is the source of truth;
`make frontend-build` bundles it with esbuild into
`src/evidential/static/table.js` and copies `table.css`, and both files are
committed. The wheel therefore contains the renderer with no build step.

### Consequences

- Good, because the Python package works with no JS toolchain.
- Good, because the bundle can be tested and reviewed like any other artifact.
- Bad, because a frontend change must rebuild and commit the bundle in the same
  change, or the source and the shipped asset drift.
- Bad, because generated code appears in the diff.

## More Information

- [Technical architecture §8](../technical-architecture.md)
- Related: [ADR-017](017-release-workflow-tests.md)
