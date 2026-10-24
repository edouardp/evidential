---
status: accepted
date: 2026-10-24
deciders: edouard
---

# ADR-066: Consistent Public API Preparation

## Context and Problem Statement

Factories, classic fluent columns, encoding columns and table mutations have
acquired different normalization and rendering paths. Equivalent declarations
could lose options, skip validation, evaluate callables before transforms, or
ignore formatting. The public review identified these as correctness defects
as well as maintenance costs.

## Decision Drivers

- Equivalent entry points must produce equivalent display values and settings.
- Preserve existing notebooks and accepted option spellings.
- Reject unsupported settings rather than silently ignoring them.
- Keep Python callables outside the browser configuration.
- Make changes transactional when validation or callable evaluation fails.

## Considered Options

1. Patch each factory, mutation and renderer independently.
2. Remove the classic configuration shape and require a breaking migration.
3. Share preparation and validation, retaining compatibility aliases and the
   classic dictionaries, with one encoding shape for mark factories.

## Decision Outcome

Chosen option: **3**.

- Prefer `format`, `format_column`, `total_format`, `subtotal_format`,
  `template_format` and `pct_format` in the public API. Retain their `fmt`
  spellings and the existing wire keys. Alias pairs reject conflicting values.
  Mark labels and row aggregates also accept `fmt` for compatibility.
- Mark factories accept common `title`, `format`/`fmt` and `align` metadata.
  Chained mark additions use the same metadata split and encoding validator.
- Prefer `negative_color` for bar style, accepting `color_negative` too. Both
  literal and `@field` colors use the same binding rules, including boxplots
  and negative bar fills. Python callables resolve to hidden fields.
- Bar and stack `height` is a fraction in `(0, 1]`; `size` remains an alias.
  Point diameter and range line thickness use positive pixel `size`. Density
  band height retains its existing fractional meaning.
- `to_config()` normalizes and validates every column and includes its name.
  Callables remain Python declarations until bound by a table; table columns
  contain only portable values after preparation.
- Constructors and mutations share the pipeline: retain normalized source
  records, apply blank predicates, apply Python transforms, coerce columns,
  resolve callable sources, and attach helper fields. Retain source inference
  metadata so updating columns does not discard Arrow/DuckDB information.
  Commit synced state and configuration only after preparation succeeds.
- Nested fluent options refine existing settings. No-argument `.label()` is a
  no-op, and `.label(False)` removes the annotation. Source-free `.bar(...)`
  refines only a last bar; it cannot silently restyle a point.
- All mark families have chain methods. A strip can share with other strips;
  it cannot share a scalar coordinate system. A column holds at most one
  cumulative stack; independent stacks belong in separate columns.
- Every mark uses the cell's resolved format, including per-row codes, format
  rules, decimal alignment, summary formats, accounting brackets and null text.
  An explicit label format overrides the code. Array points label observations
  individually; boxplots anchor at the median; band/strip captions anchor at
  the center. Stack labels honor start/center/end within their segment.
- The marks renderer honors accepted bar compatibility options when a scale,
  annotation or overlay is added. Mark factories always emit encodings and use explicit labels. ADR-067 removes
  the scalar bar decorator; raw classic dictionaries remain accepted.
  `hide_labels` suppresses bar labels, including explicit annotations.
- Bar direction mirrors the shared scale, overlays, axes and reference marks.
  Bars sharing a column must use the same direction. Centered bars use a
  symmetric domain and place unpositioned explicit labels opposite their bars.
- Fluent base methods return `Self`, preserving the encoding methods in type
  completion. The scale annotation includes its supported `"auto"` domain.

### Consequences

Existing short spellings and classic dictionaries remain accepted. Mark factory
serialization no longer changes from `viz="bar"` to `encodings` when a scale or
label is added; it always uses `encodings`. Add `label=True` to `col.bar(...)`
when a value annotation is wanted. ADR-067 subsequently removes the scalar `.bar()` decorator. Unsupported
options and contradictory aliases now fail early instead of doing nothing.
Retaining source records uses additional memory proportional to the dataset;
it prevents mutation paths from repeatedly transforming already prepared data.
The classic renderer remains for compatibility, but tests compare accepted
behavior against the encoding renderer and cover browser geometry.

## More Information

- Extends [ADR-058](058-encoding-based-columns.md).
- [Public API](../api/API.md#consistent-option-names-and-updates).
- `tests/test_api_consistency.py`, `frontend/test_spec_conformance.js`,
  `frontend/test_table.js`, `tests/browser/test_spec_conformance.py`.
