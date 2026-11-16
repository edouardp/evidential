---
status: accepted
date: 2026-11-16
deciders: edouard
---

# ADR-101: Widget CSS Isolation in Embedded Documents

## Context and Problem Statement

A blog embedding a marimo island changed Evidential's table font sizes, borders,
header alignment and row backgrounds. The anywidget already lived in marimo's
shadow root, but the islands runtime copied host styles into that root. Host
rules included `table th { text-align: center !important }`, so increasing our
selector specificity could not reliably restore the intended presentation.

## Decision Drivers

- Work out of the box in notebooks and embedded marimo islands.
- Keep host table, control and SVG selectors outside the widget cascade.
- Preserve explicit theme settings and light/dark switching.
- Keep keyboard navigation, focus, tooltips, fullscreen and scrolling functional.
- Avoid changes to the embedding site or requiring an iframe.

## Considered Options

1. Increase selector specificity and reset known host table properties.
2. Require an iframe or site-specific exclusions in the blog stylesheet.
3. Mount both packaged widgets in their own nested shadow root.

## Decision Outcome

Chosen option: **3**. The packaged table and DimensionGrid entry points create
an open shadow root inside the anywidget view and install their CSS within it.
The bundle embeds its matching stylesheet at build time, so blob-backed anywidget
modules need no runtime CSS fetch. Python no longer injects a second stylesheet
into marimo's surrounding root. Standalone committed CSS files remain available
for tooling and compatibility. Disposal removes the mount and style; remounts
reuse the empty shadow root. CSS resets stay within this boundary. A small
foundation supplies box sizing, inherited table typography and explicit widget
font styling so rendering does not depend on Tailwind preflight.

CSS isolation is automatic. Authors style widgets using the public `theme`,
column and table options rather than reaching through a host stylesheet.
Custom CSS rules outside the widget no longer target its implementation DOM.
Advanced notebook-owned `css=` is installed as a second local stylesheet and
updates with the options trait. It accepts plain CSS without host ancestor
prefixes or HTML tags. The existing subcolumns recreation moves its local
styling to this option. Public theme/column options remain preferred because
implementation class selectors are not a stable styling API.
Inherited CSS custom properties still cross shadow boundaries intentionally.
The outer host retains loading and render diagnostics for integrations.

`theme_source="auto"` follows the surrounding document inside a
`<marimo-island>` and the nearest theme context elsewhere. Detection traverses
shadow hosts. `theme_source="nearest"` explicitly follows notebook/runtime
wrappers; `"host"` explicitly starts outside the surrounding shadow roots,
including in non-island embeds. These options apply equally to DimensionGrid.
An explicit `color_scheme="light"` or `"dark"` wins over theme-source selection.
This extends ADR-100 without requiring two palettes or a Python island-context
flag. The current marimo Python context API does not expose an island flag.

Focus reads use the local root's active element. Document-level pointer/key
handlers use composed event paths to distinguish widget interactions from
outside interactions after browser event retargeting. Playwright locators
traverse the boundary; browser scripts and benchmarks query the appropriate
shadow root instead of assuming all tables live in the document.

### Consequences

The widget layout survives even important host table rules and stylesheet load
order. Notebook-specific external CSS targeting `.et-*` implementation classes
must move to supported theme/column options. This is style encapsulation, not a
security boundary. Rem units continue to respect the document root font size.

Regression tests reproduce blog selectors copied into an outer shadow root,
verify unchanged table/control/SVG styling, and exercise automatic theme changes,
sorting, search and fullscreen keyboard behavior. Unit tests cover disposable
surfaces and theme-source overrides. The existing blog output is tested read-only
with the new renderer substituted only in browser memory after its original
island has loaded.

## More Information

- [ADR-100](100-light-dark-themes.md): light/dark theme and colour policy.
- [Marimo context API](https://docs.marimo.io/api/app/).
- [Marimo islands](https://docs.marimo.io/guides/exporting/webassembly_html/).
