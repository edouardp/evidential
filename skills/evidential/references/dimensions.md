# Dimension slicers

Use `DimensionGrid` for ranked, searchable category lists driving linked
tables. It is a separate anywidget, not a table column or row selection mode.
Verify the installed package exports it before using these examples.

## Persistent widgets in marimo

Keep each of the following code blocks in a separate cell. This small example
uses illustrative product data; replace it with the user's actual source.

```python
import marimo as mo
from evidential import DimensionGrid, EvidentialTable, col, label

facts = [
    {"region": "North", "product": "Lamp", "sales": 1200},
    {"region": "North", "product": "Chair", "sales": 1800},
    {"region": "South", "product": "Lamp", "sales": 600},
]
slicer = mo.ui.anywidget(DimensionGrid(
    facts, dimensions=["region", "product"], metric="sales", format="usd0",
    title="Filter product sales",
))
slicer
```

```python
results = mo.ui.anywidget(EvidentialTable(
    [],
    columns=[
        col.text("region"), col.text("product"),
        col.bar("sales", label=label.fmt("usd0").auto_position("outside end")),
    ],
    title="Matching sales", border=False,
))
results
```

```python
selection = slicer.value["selected"]  # Reactive dependency; create neither widget here.
results.widget.set_data(slicer.widget.filtered)
```

The wrapper's `.value["selected"]` is `{field: [typed_values]}`. Values within
a dimension combine with OR; dimensions combine with AND. Empty selections
impose no restriction. Multi-select is the default; `multiple=False` opts into
one selection per dimension. `.clear()` removes selections. `.set_data(data)`
retains selected categories still present in the replacement source.

Each facet applies the other dimensions' selections, excluding its own. This
preserves alternatives and naturally constrains child categories: selecting a
service limits usage types to matching source records. No separate hierarchy
declaration is needed. Search narrows category choices, not the linked records.

## Data grain and SQL results

Accept the same records/dataframe/Arrow/DuckDB inputs as the table. Omitted
`dimensions` infers string fields; use a sequence for an intentional subset or
`{field: display_name}` for custom labels. A numeric `metric` defaults to sum;
without a metric, the grid counts records. Other `aggregate` values are
`count`, `mean`, `min` and `max`; a count with a metric counts non-null values.
`metric` is a field name, not a SQL expression.

For large fact tables, preaggregate additive cost at the complete chosen
dimension grain before constructing the slicer. Keep all combinations so
cross-filtering remains accurate. Do not sum precomputed means or mix
currencies and billing units. Python retains source records and aggregates;
the browser receives category totals and virtualizes visible rows.

Use `predicate, parameters = slicer.widget.where()` for linked SQL. It quotes
field identifiers, binds values and handles null selections with `IS NULL`.
Apply that predicate to a relation with the same dimension names using
`con.execute(statement, parameters)`. Filter the original facts before
computing grouped costs, shares or trends. Keep a detail-row display limit
separate from full matching totals. `.raw` and `.filtered` are detached
snapshots of the slicer's input grain, which may already be aggregated.

The real-data
[CUR explorer](https://github.com/edouardp/evidential/blob/main/notebooks/57_aws_cur_explorer.py)
demonstrates this split with a local processed product and external SQL files.
Use configurable dataset paths and an actionable missing-data message; do not
substitute made-up charges when a real source was requested.

## Layout and verification

The grid uses the table's default inherited font at `0.75rem`, compact 20px
rows, a white surface, a bold title and centered availability/selection counts.
Selected rows stay in ranked position with bold text and a full-height 6px dark
red strip. Selections remain in the list through searches; incompatible ones
show an unavailable metric and can still be removed.

The search icon replaces a heading with an input; blur restores the heading
with an active-search indicator. The × clears the search. Native thin vertical
scrollbars and mouse wheels navigate category lists. Horizontal scrolling and
arrow controls reveal additional dimensions; `dimension_width` is a minimum
width, and `height` includes the dimension header and footer.

Render `.edg-root` alongside `.et-root` with a live marimo kernel. Exercise
multi-select, search beyond the initial window, wheel scrolling, off-screen
dimensions and cleared/incompatible selections. Assert populated data or
specific values; empty table placeholders can have the same row count as a
filled page. Confirm linked widgets retain identity and query totals reconcile.
