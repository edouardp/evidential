---
status: accepted
date: 2026-10-25
deciders: edouard
---

# ADR-074: Readable Scientific Formatting

## Context and Problem Statement

The `sci` preset displayed spreadsheet notation such as `1.23E+5`. The requested
report style uses a multiplication sign, base ten and an HTML superscript for
the exponent. Cells, annotations, statistics and axes need the same treatment;
native tooltips and SVG titles require plain text rather than HTML markup.

## Decision Drivers

- Preserve the string-returning formatter contract.
- Show two mantissa decimal places with correct rounding and signed exponents.
- Construct safe DOM nodes and preserve prefixes, suffixes and accounting style.
- Keep label fitting and compact row height working with raised exponents.
- Retain explicit SSF formatting as the precision and notation escape hatch.

## Considered Options

1. Return HTML strings from `formatValue` and insert them into every consumer.
2. Use Unicode superscripts on every surface.
3. Return readable plain text and render canonical scientific runs as HTML.

## Decision Outcome

Chosen option: **3**. The `sci` preset retains SSF's `0.00E+0` numeric formatting
and rounding, then converts its result into text such as `1.23 × 10⁵` or
`1.23 × 10⁻⁴`. Positive exponents omit their redundant plus sign. Missing and
invalid inputs retain their existing fallback behavior. Explicit SSF codes,
including `0.000E+0`, continue to use their requested notation.

A shared `formattedText` helper recognizes canonical scientific runs and builds
DOM fragments with real `sup` elements. It preserves surrounding text, including
accounting brackets and label affixes, using text nodes instead of parsing HTML.
Each scientific run has a math role and a descriptive accessible name. Dedicated
exponent styling controls its size and rise without increasing row line height
or sharing footnote positioning.

Ordinary cells, chips, merged templates, media labels, mark and stack labels,
statistics, axes and display-row values use the helper. Formatter outputs remain
strings, so native tooltips, SVG titles and other plain-text consumers receive
readable Unicode superscripts. Data and CSV export remain based on raw values.

### Consequences

Reports gain consistent scientific typography without exposing arbitrary HTML
through numeric formatting. New formatted text surfaces can reuse one DOM
helper. The helper recognizes numeric scientific runs within supplied text;
ordinary markup-like text remains literal. Custom SSF output remains unchanged.

## More Information

- `frontend/src/scientific.js`, `frontend/src/formatted-text.js`, formatter and
  presentation consumers.
- `frontend/test_scientific.js`, browser conformance and notebook smoke tests.
- `notebooks/08_column_options.py` compares decimal, scientific and custom SSF.
