---
name: evidential
description: Build and refine interactive Python tables and dimension slicers with Evidential, including marimo reports, DuckDB explorers, cell graphics, grouped summaries, and linked drill-downs. Use when the user requests Evidential or is working in an existing Evidential notebook or application.
license: MIT
---

# Evidential

Turn a result set into a readable table using `evidential`. Keep data shaping in
SQL or Python, and presentation in the table configuration. Preserve the user's
chosen data source, host and project tooling.

## Start with the right scope

Inspect the environment and installed Evidential version before choosing APIs.
The library is alpha: these examples track the repository version containing
this skill, which may be ahead of PyPI. Check installed exports/signatures and
matching release documentation if an option is unavailable; do not silently
upgrade the project or invent a replacement API.

`evidential` alone accepts records; the `marimo` and `duckdb` extras support
those integrations. The renderer ships with the Python package, so consumers
do not need Node or a frontend build. Follow the project's dependency manager.

- For columns, formatting, nested headers, footnotes and row summaries, read
  [Table composition](references/tables.md).
- For marks, labels, shared scales, sparklines and distributions, read
  [Cell graphics](references/graphics.md).
- For reactive controls, selection and live queries, read
  [Marimo integration](references/marimo.md).
- For searchable category filters and linked results, read
  [Dimension slicers](references/dimensions.md). Check for the `DimensionGrid`
  export first; this addition may be newer than the installed release.

The bundled [report template](assets/report.py) and
[linked explorer template](assets/explorer.py) are executable marimo notebooks
with illustrative data. Copy only the template that fits the task, then replace
its data and prose. They do not depend on a clone of this repository.

## Shape and explain the data

Establish the row grain, units, null semantics and stable identifiers before
adding graphics. Query existing curated models when available. Avoid silently
combining overlapping extracts, duplicating rows through joins, or averaging
ratios that require weighted numerators and denominators. Keep numbers numeric;
formatting belongs in columns or labels. State coverage and partial periods in
the report when they affect interpretation.

Pass records, a dataframe, Arrow table or DuckDB relation to `EvidentialTable`.
Start with explicit columns when their order or presentation matters:

```python
from evidential import EvidentialTable, col, label

table = EvidentialTable(
    [{"product": "Lamp", "sales": 1200}, {"product": "Chair", "sales": 1800}],
    columns=[
        col.text("product").bold(),
        col.bar("sales", format="usd0", label=label.auto_position("outside end")),
    ],
    title="Product sales",
    caption="Illustrative data · US dollars",
    search=True,
    border=False,
)
```

## Compose the presentation

Use `col.<kind>(...)` and immutable fluent refinements. Add `title=` only for
wording or units that differ from the automatically derived title. Prefer
`format=` on factories and `.fmt(...)` on chains and fluent labels; `fmt=` is
also accepted. Use `col.bar(..., label=label.fmt(...).auto_position(...))` for
a labeled bar; the scalar `col.number(...).bar()` shortcut was removed.

Choose graphics by meaning: bars for magnitude, centered bars for signed
change, ranges/points for comparisons, stacks for composition, and sparklines
for ordered series. Comparable quantities need comparable domains. Do not give
different units the same scale merely because they share a header.

Keep hierarchy in `col.group`, shared leaf headings in `col.subcolumns`, and
display-only row annotations in `row_layout`. Do not insert total or heading
records into the detail data. Prefer ordinary footnote marks over link-like
custom HTML. Let the renderer handle numeric alignment and label contrast.

For marimo interactivity, create widgets independently of controls and update
their models in separate reactive cells. Read the integration reference before
adding live filters or linked tables; recreating the widget loses UI state.

## Check the result

Execute the data/table construction and check counts, totals, missing values
and units. For notebooks, run `marimo check` and execute the notebook with the
project's Python environment. Check reactive changes as well as initial output.

When a browser is available, render the actual marimo output and inspect the
target `.et-root` or `.edg-root`: headings, visible labels, alignment, missing values, chart
scales and scrolling at the intended width. Verify selection and controls keep
the existing table in place. Do not describe unrendered output as visually
verified. In this repository, follow its contributor checks and rebuild assets
only when changing renderer source.

For details beyond the bundled references, use the
[public API reference](https://github.com/edouardp/evidential/blob/main/docs/api/API.md)
and [runnable examples](https://github.com/edouardp/evidential/tree/main/notebooks),
matching their revision to the installed package when necessary.
