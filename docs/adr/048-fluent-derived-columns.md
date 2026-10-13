---
status: accepted
date: 2026-10-13
deciders: edouard
---

# ADR-048: Fluent Construction of Derived Columns

## Context and Problem Statement

Migrating the notebooks to `columns=[...]` surfaced two shapes the fluent API
could not express:

- `cols_merge_range` / `cols_merge_uncert` / `cols_merge_n_pct` return a
  **nameless** partial definition (a template plus the formats of its fields),
  meant to be a `column_config` value whose key is the name. In a
  `columns=[...]` list there is no key, so it failed with "missing a name".
- `comparison_table` builds `<measure>_prior` / `_delta` / `_pct` from a measure.
  Its delta options (`neutral_range`, `down_is_good`) were set as **top-level**
  keys of the measure config and inherited by the derived columns. A fluent
  `col.currency("sales").delta(...)` sets `delta_options` and a `viz`, which the
  helper would have applied to the measure itself.

## Decision Drivers

- One fluent way to declare every column, including derived ones.
- Derived columns should inherit the delta options that describe them.
- Keep the existing dict/`cols_merge_*` constructs working.

## Decision Outcome

Chosen option: "name merge specs; treat a measure's delta options as its
change columns'".

- **`col.merge(name, spec)`** wraps a `cols_merge_*` result (or any nameless
  column spec) with a name so it can join `columns=[...]`:

  ```python
  columns=[
      col.auto("low").hide(),
      col.auto("high").hide(),
      col.merge("range", cols_merge_range("low", "high", fmt="num0", title="Range")),
  ]
  ```

- **`comparison_table`** now reads a measure's `delta_options` (and any
  top-level `neutral_range` / `down_is_good` / `chip` / …) and applies them to
  the derived `<measure>_delta` and `<measure>_pct` columns. A measure whose
  `viz` is `"delta"` (from a `.delta(...)` chain) has that viz dropped from the
  measure. So `col.currency("sales", decimals=0).delta(neutral_range="-0.25:0.25")`
  reads as "format the measure as currency; give its change columns this neutral
  band".

Also fixed while converting: `col.sparkline(...)` now routes `x` / `y` /
`color` / `fit_to_data` / `y_fmt` / `width` / `height` into `sparkline_options`
(previously they fell to the top level, where `color` became `font_color` and
`fit_to_data` landed in `bar_options`), and `Column.chip(...)` /
`col.chip(...)` gained the colour-range options (`stops`, `scale_column`,
`min`, `max`, `midpoint`).

### Consequences

- Good, because derived columns (merged, compared) are declared in the same
  fluent list as everything else.
- Good, because a measure's delta styling is stated once and reaches the change
  columns.
- Good, because the dict form and `cols_merge_*` are unchanged for callers who
  prefer them.
- Note: `col.merge` takes the merge helper's output, not the individual source
  columns; the sources are still hidden with `col.auto(...).hide()`.

## More Information

- `src/evidential/_column.py` (`merge`), `src/evidential/comparison.py`,
  `src/evidential/_column_options.py`.
- `tests/test_column_builder.py`, `notebooks/18_great_tables.py`,
  `notebooks/11_comparisons.py`.
- Relates to [ADR-042](042-column-builder-and-settings.md),
  [ADR-043](043-column-kinds.md) and
  [ADR-047](047-inference-preserving-column-specs.md).
