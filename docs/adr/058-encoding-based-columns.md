---
status: accepted
date: 2026-10-20
deciders: edouard
---

# ADR-058: Encoding-Based Columns (Declarative Marks)

## Context and Problem Statement

The current column builder (§ADR-042, ADR-043) binds a column to exactly one
data field and gives it at most one visualisation: `col.number("sales").bar()`.
That model cannot express several of the tables the *Tabular Design System* and
the v1.1 API specification call for:

- a bar whose **label** is a different field (`col.bar('votes',
  label='@candidate')`) — today label text comes from the column itself;
- **two bars in one column** with independent thickness and colour
  (`col.bar('current').bar('previous')`), e.g. a this-year / last-year league
  table;
- a bar plus an independent **target marker** (`col.bar('current').point('target')`);
- a **range** (dumbbell / confidence interval) plus a point
  (`col.range('low', 'high').point('estimate')`).

In all of these one cell contains several **encodings**, each bound to its own
field and sharing one coordinate system. The field + single-viz model has no
place to put them.

## Decision Drivers

- A column is a *presentation slot*, not a data field; encodings are the unit
  that binds data and owns its label and geometry.
- Marks composed in a cell share one horizontal scale, so their lengths are
  comparable.
- The label belongs to the mark (`col.bar('value', label='@name')`), not to a
  separate text column that the renderer must know to pair up.
- Many working notebooks use `.bar()`, `.color()`, `.sparkline()` on a single
  field; the redesign must not break them.
- The renderer must consume a validated, serialisable spec — it never runs
  Python callables.

## Decision Outcome

Chosen option: add a declarative **encoding** layer alongside the existing
single-viz column, and migrate to it incrementally (specification §12:
"Keep a migration guide rather than changing all signatures at once").

**`col.bar(source, ...)`** and its siblings `col.point`, `col.range`,
`col.stacked_bar` return a `MarkColumn` — still an immutable `Mapping`, still the
same object that drops into `columns=[...]`, but able to hold an ordered list of
**encodings**:

```python
col.bar('current', color='navy', size=0.8).bar('previous', color='#d1d5db', size=0.2)
col.bar('votes', label='@candidate', color='@party_colour')
col.bar('current').point('target')
col.range('low', 'high', cap='line').point('estimate').scale(domain=(0, 100), unit='%')
```

Each encoding is a `(kind, sources, style, label)` record. Column-wide knobs —
`.scale(...)`, `.reference_line(...)`, `.cell_style(...)` — are named methods so
chaining never changes their meaning. `.label(...)` annotates the **most
recently declared** encoding.

The wire format gains three optional keys on a column:

| key | meaning |
| --- | --- |
| `encodings` | the ordered marks: `kind`, `source`, style, an owned `label` |
| `scale` | `domain`, `include_zero`, `unit` shared by the encodings |
| `references` | column-wide reference lines/bands |

**Compatibility.** When a `MarkColumn` holds a single plain bar over the
column's own field with no label, size, side, scale or references, it serialises
to the existing `viz="bar"` + `bar_options` shape. Existing notebooks and tests
are unchanged. The multi-mark keys are only emitted when the new features are
used, and the browser falls back to the legacy path when `encodings` is absent.

## Consequences

- Good, because one cell can now carry an overlaid league-table pair, a
  bar-plus-target, or a point-plus-interval, with a shared scale.
- Good, because labels are mark-owned and may name any field.
- Good, because the legacy single-viz path keeps working unchanged.
- Note: sources may be field names, the `@field` reference convention, or
  `Callable[[Row], T]`. A callable is evaluated Python-side into a generated
  hidden helper column (ADR-006), so the browser only ever sees field names;
  exports and untrusted data never execute Python.
- Note: this phase ships `bar`, `point`, `range`, `stacked_bar` (raw,
  `normalize="percent"`, or `diverge_at=…`), `strip` (equal-width, positioned
  runs and change-points), `boxplot` and `distribution`, plus the `shapes`
  alias for repeated symbols.
- Note: composition validity (ADR-058 §5.2) is enforced in Python where cheap
  (e.g. a sparkline beside a scalar bar is rejected) and reported with a clear
  message.
- Note: the TypeScript-free renderer renders `encodings` in `cells.js` /
  `visualizations.js`; the committed bundle must be rebuilt with
  `make frontend-build`.

## More Information

- `src/evidential/marks.py` (the `MarkColumn` builder and serialisation),
  `src/evidential/col.py`, `src/evidential/configuration.py`
  (`EncodingSpec`, `ScaleSpec`, `ReferenceSpec`).
- `frontend/src/visualizations.js` (`renderMarks`), `frontend/src/cells.js`,
  `frontend/src/color.js` (`calculateVizRanges`), `frontend/src/table.css`.
- `tests/test_marks.py`, `frontend/test_table.js`.
- Implements `evidential_table_api_spec_v1.1.md` §3–§6 and the
  *Tabular Design System* cell-visualisation model.
- Extends [ADR-020](020-bar-visualisation-geometry.md),
  [ADR-042](042-column-builder-and-settings.md) and
  [ADR-043](043-column-kinds.md).
