---
status: accepted
date: 2026-10-12
deciders: edouard
---

# ADR-016: Layered Testing Strategy

## Context and Problem Statement

Behaviour spans three runtimes: pure JavaScript (formatting, colour, DOM
rendering), Python (normalisation, SQL, rules) and the real browser
(interaction, layout, focus). Where should each behaviour be tested?

## Decision Drivers

- Test each behaviour at the cheapest layer that can observe it.
- Fast feedback for the bulk of the logic.
- Real-browser coverage for the things jsdom cannot see (layout, geometry,
  native dialogs).

## Considered Options

1. Layered: jsdom unit tests, Python unit tests, and Playwright browser tests.
2. Python tests only, with a JS-free renderer.
3. Browser tests only.

## Decision Outcome

Chosen option: "Layered":

- **jsdom** (`frontend/test_*.js`, `node --test`) for the pure JS: formatting,
  colour maths and renderer output against a fake model.
- **pytest** (`tests/`) for Python: normalisation, inference, SQL, rules,
  aggregations and live parameter binding.
- **Playwright** (`tests/browser/`) for real DOM behaviour: sorting, search,
  pagination, fullscreen round-trips, sparklines and exact bar geometry. It
  prefers installed Edge/Chrome locally and falls back to Playwright Chromium.
  CI installs Chromium with its system dependencies and requires a successful
  launch, so missing browsers cannot silently skip the suite.

CI separates quality/build checks from a Python 3.11–3.14 test matrix and the
browser suite. Tool versions are pinned and dependencies installed with
`uv sync --locked` and `npm ci`.

### Consequences

- Good, because the fast suites cover the bulk of the logic.
- Good, because jsdom cannot accidentally mask a layout bug — those are tested
  in a real browser.
- Good, because browser regressions run on every pull request.
- Bad, because behaviour can be duplicated across layers.
- Bad, because the browser suite is the slowest and the most environment
  sensitive.

## More Information

- [Technical architecture §9](../technical-architecture.md)
