# Table composition

## Column and format choices

Use `col.text`, `integer`, `number`, `currency`, `percent`, `date`, `chip` or a
mark factory for the cell's meaning. Builders return new specifications; retain
the result of refinements. Automatic headings derive from column names.

| Requirement | API or convention |
| --- | --- |
| Whole numbers / explicit decimals | `.fmt("num0")`, `.fmt("num2")` |
| Fraction displayed as a percentage | `col.percent("rate", decimals=1)`; `0.125` displays `12.5%` |
| Currency with fixed precision | `.fmt("usd0")`, `.fmt("eur2")` |
| Per-value K/M/B/T | `.fmt("compact")` uses one decimal place |
| Up to four significant figures | `.fmt("compact4")`: `1.148T`, `877.1B`; supported suffixes are 1–21 |
| Readable scientific notation | `.fmt("sci")` renders a mantissa and superscript exponent |
| Custom spreadsheet format | `.fmt('#,##0.00" kg"')` |
| Negative styling | `.neg(color="red", bracket=True)` |
| Adjacent repeated group labels | `.repeat_values(False)` suppresses display text, not source data |
| Shared table options | `settings(...)`, overridden by explicit table keywords |
| Unformatted inspection | `table.raw`, or `wrapped.widget.raw` |

`num` infers precision and a common unit from the column range. `compact`
chooses a unit separately for each value; `compact4` caps significant figures,
not decimal places, and omits unnecessary trailing zeros. Check availability
against the installed version before using recently added presets.

Nulls should remain nulls, with `.null_text(...)` if a different placeholder is
needed. Avoid turning missing values into zero or formatting them in SQL just
to draw a table. `.raw` is a detached normalized snapshot; it does not reflect
browser search, sorting or pagination, and does not rerun a live query.

## Hierarchy and annotations

`col.group` adds a spanner above its children and can nest to multiple levels.
`col.subcolumns` gives several physical columns one shared leaf heading. Each
sub-column still has its own alignment, sorting data and statistics; statistics
can cycle among members. A value/period/status combination looks like this:

```python
from evidential import EvidentialTable, col

header_table = EvidentialTable(
    [{"country": "Example", "value": 2.9, "period": "Q3", "status": "Estimate"}],
    columns=[
        col.text("country"),
        col.group("Economy", [
            col.subcolumns("Latest", [
                col.number("value").fmt("num1").align("right"),
                col.text("period").align("left").font_color("#6b7280"),
                col.chip("status").align("center"),
            ]),
        ]),
    ],
    column_stats=True,
    search=False,
)
```

Group headings, per-group summaries and a grand summary are independent display
options. Keep input records at their detail grain and specify aggregation
columns explicitly, especially when identifiers or ratios are numeric:

```python
from evidential import EvidentialTable, col, rows

orders = [
    {"region": "North", "product": "Lamp", "units": 12, "sales": 1200, "note": "Launch month."},
    {"region": "North", "product": "Chair", "units": 9, "sales": 1800, "note": None},
    {"region": "South", "product": "Desk", "units": 4, "sales": 2400, "note": None},
]
grouped_report = EvidentialTable(
    orders,
    columns=[
        col.text("product").footnote("note"),
        col.integer("units"),
        col.currency("sales", decimals=0),
    ],
    row_layout=rows.group_by("region")
        .section(values={"product": rows.count(suffix=" products")})
        .summary("Region total", values={"units": "sum", "sales": "sum"})
        .grand_summary("All regions", values={"units": "sum", "sales": "sum"}),
    section_indent=1,
    title="Orders by region",
    subtitle="Three products",
    caption="Illustrative orders · US dollars",
    page_size=10,
    row_shading=True,
    row_lines=False,
    border=False,
)
```

Portable reducers (`"sum"`, `"mean"`, `rows.count(...)`,
`rows.aggregate(...)`) recalculate over browser search matches. Python callable
summaries retain their source scope until a Python refresh. Page size counts
details, with continuation headings as needed. Summary rows do not participate
in detail statistics, scale inference, raw snapshots or CSV data.

Use `.summary(position="top")` for a summary before a group, or
`.section(align="center")` for a centered heading without value cells. Use a
bold ordinary group column with `.repeat_values(False)` when the group label
belongs in its own column. `row_shading=False`, `True`, or an integer such as
`3` controls no shading, alternating rows, or bands of three rows.

Footnotes come from source fields through `.footnote("note")`. The default
symbol sequence and lowered superscript styling are handled by the renderer.
Keep titles, subtitles, captions and source notes as table metadata.

## Other data shapes

For a DuckDB-backed pivot or comparison, inspect the installed signatures of
`pivot_table` and `comparison_table` rather than guessing their measure schema.
`grouped_records` supports plain in-memory records; `grouped_table` aggregates
SQL-backed data. These helpers return tables, with their resulting detail data
available through `.raw`. A report's displayed row layout is separate from
those upstream data transformations.
