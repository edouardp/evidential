# The `evidential` API

`evidential` gives you Evidence-style tables inside a Marimo notebook (or any
anywidget host). You point it at data, describe the columns you want with a
small fluent builder, and it renders a sortable, searchable, exportable table.

This is the reference for the **current** API. It is written around the three
things you actually compose:

1. **Columns** — `col.<kind>("name", ...)` and the chain that refines it.
2. **Header structures** — groups and sub-columns, built from columns.
3. **Derived values** — merged columns and the grouped / pivot / comparison
   helpers, which reuse the same column builder.

Every screenshot in this document comes from
[`notebooks/49_api_screenshots.py`](../../notebooks/49_api_screenshots.py) and is
captured with Playwright by
[`scripts/api_screenshots.py`](../../scripts/api_screenshots.py). Run
`make api-screenshots` after changing an example.

- [Quick start](#quick-start)
- [The fluent column builder](#the-fluent-column-builder)
  - [Kinds](#kinds-the-chain-entry-points)
  - [The chain](#the-chain)
  - [How a column composes](#how-a-column-composes)
- [Composing header structures](#composing-header-structures)
  - [Columns](#columns)
  - [Groups](#groups)
  - [Sub-columns](#sub-columns)
  - [Nesting](#nesting)
- [Composing merged values](#composing-merged-values)
- [Grouped, pivot and comparison tables](#grouped-pivot-and-comparison-tables)
- [Table settings](#table-settings)
- [Visualisations](#visualisations)
- [Formatting](#formatting)
- [Dimension slicers](#dimension-slicers)
- [Reference](#reference)

## Quick start

```bash
uv add evidential
```

```python
from evidential import EvidentialTable, col, settings

rows = [
    {"city": "Boston", "trips": 1284, "revenue": 48120.50, "tip_rate": 0.183},
    {"city": "New York", "trips": 3502, "revenue": 142880.25, "tip_rate": 0.171},
    {"city": "Chicago", "trips": 2118, "revenue": 76540.00, "tip_rate": 0.164},
    {"city": "San Francisco", "trips": 1907, "revenue": 98320.75, "tip_rate": 0.196},
    {"city": "Seattle", "trips": 1463, "revenue": 61140.10, "tip_rate": 0.188},
]

EvidentialTable(
    rows,
    columns=[
        col.text("city"),
        col.integer("trips"),
        col.currency("revenue"),
        col.percent("tip_rate", decimals=1, title="Tip rate"),
    ],
    settings=settings(
        title="Tipping by city",
        caption="Illustrative sample orders.",
        width="620px",
    ),
)
```

![Quick start](images/quickstart.png)

In Marimo, wrap it in a widget cell: `mo.ui.anywidget(EvidentialTable(...))`.
The cell that *creates* the widget must not read any control values — see
[`docs/design-and-dx.md`](../design-and-dx.md).

`EvidentialTable` accepts a pandas DataFrame, a PyArrow Table, a list of dicts
(via `rows=`), or a DuckDB connection with SQL (through the helpers below). You
can also pass `columns=` as an ordered list of names, or omit `columns` entirely
and let the renderer infer a column set from the data.

### Inspecting unformatted data

`table.raw` returns a detached `list[dict[str, Any]]` snapshot of all source
records, including hidden source fields. It precedes blank predicates, text
transforms and generated mark helpers, and excludes synthetic section/summary
rows. Browser search, sorting and pagination do not change the snapshot or its
source order. Editing a snapshot does not change the table.

For a standard Marimo data grid, pass the records directly to
[`mo.ui.table`](https://docs.marimo.io/api/inputs/table/):

```python
mo.ui.table(table.raw, selection=None, pagination=True)
```

For a table wrapped with `mo.ui.anywidget(...)`, use `table.widget.raw`.
If you prefer Marimo's automatic dataframe viewer, `pd.DataFrame(table.raw)`
works when pandas is installed. The property itself needs no dataframe library.

`LiveEvidentialTable.raw` exposes the latest successful query result without
running SQL. `set_data()` and successful live refreshes replace the snapshot;
failed updates preserve it. Pivot, grouping, comparison and query helpers share
the same property on their returned tables: it exposes their resulting detail
records, rather than rerunning or reversing their SQL transformations.

To refresh a raw grid with live controls, display it in the reactive cell that
updates the persistent table:

```python
live.set_controls(year=year)
mo.ui.table(live.raw, selection=None, pagination=True)
```

Values use the table's existing input normalization: numbers remain numbers,
dates/times are ISO strings, decimals become floats, and nonfinite values
become `None`. `.raw` returns data without table formatting, rather than the
original dataframe object or its native schema.

## The fluent column builder

A column is built in two moves:

```python
from evidential import col

(
    col.bar("growth", format="pct1", center=True, label=True)  # 1. declare the mark and label
    .neg(bracket=True)                                        # 2. refine its display
)
```

- The **factory** (`col.*`) names the column's *kind*: a number, a currency, a
  percentage, a date, a flag, a bar, a chip, a rating, … This is the first
  decision, so it is the first thing you write, and `col.` autocompletes to
  exactly these entry points.
- The **chain** (`.bar(...)`, `.neg(...)`, `.bold()`, `.fmt(...)`, …) refines the
  baseline the factory set.

The result is a `Column`: an immutable `Mapping[str, Any]` in the widget's wire
format. `dict(column)` or `column.to_config()` returns the plain dict, which is
what the classic (non-fluent) API accepted — the two are interchangeable.

### Consistent option names and updates

Use `format=` in factories, mark labels, formatting rules and row aggregates.
The existing `fmt=` spelling remains accepted. `.format(code)` and `.fmt(code)`
are equivalent; the browser configuration continues to use `fmt`.

| Preferred public spelling | Compatibility spelling |
| --- | --- |
| `format`, `.format(...)` | `fmt`, `.fmt(...)` |
| `format_column`, `.format_column(...)` | `fmt_column`, `.fmt_column(...)` |
| `total_format`, `.total_format(...)` | `total_fmt`, `.total_fmt(...)` |
| `subtotal_format`, `.subtotal_format(...)` | `subtotal_fmt`, `.subtotal_fmt(...)` |
| `template_format` in `cols_merge(...)` | `template_fmt` |
| `pct_format` in `cols_merge_n_pct(...)` | `pct_fmt` |
| `negative_color` in bar declarations | `color_negative` |
| `height` in bar/stack declarations | `size` |

Alias pairs may be supplied together only when their values agree. Bar and
stack `height` is a fraction in `(0, 1]`. Point `size` is diameter in pixels;
range `size` is line thickness in pixels. All mark factories accept `title`,
`format`/`fmt` and `align`; those options configure the whole column. Mark
color options accept literal colors, `@field` references, or row callables.

```python
col.bar("sales", format="usd0", height=0.7, negative_color="@loss_color")
col.points("samples", format="num1", align="right", label=True)
col.boxplot("low", "q1", "median", "q3", "high", color="@ink", format="num2")
```

`col.bar(...)` always serializes to `encodings`, with the same rendering path
before and after adding a scale, label or overlay.

`to_config()` includes the column name and validates the normalized definition,
so its result is accepted anywhere a column mapping is accepted. Callables are
resolved when the table binds the column to data. Dictionary definitions use
the same alias and encoding validation as factories.

Nested fluent options refine previous settings. `.label()` with no arguments
preserves the current annotation; `.label(False)` removes it. `.bar(...)`
without a source can refine the last bar, and raises if the last mark is another
kind. Pass a source to add a new bar. All mark kinds have chain methods;
coordinate compatibility is checked when the table binds the declarations.
A column can hold one cumulative stack, and strips can compose with strips.

Mark labels inherit per-row formatting, formatting rules, decimal alignment,
summary formats, negative brackets and null text. A label's explicit `format`
overrides the format code. Points arrays label each observation, boxplots place
their annotation at the median, and band/strip captions use the track center.
Stack label positions are `inside_start`, `center` and `inside_end`, within each
segment. Mark factories use explicit annotations (`label=True` for a value).
`label=False` or `hide_labels=True` suppresses a bar's label. Scalar builders
(`col.number`, `col.currency`, `col.percent`, etc.) do not expose `.bar()`: start
with `col.bar(...)` and set the numeric `format` on that mark column.

Constructing a table, calling `set_data()` and calling `set_column()` apply the
same preparation: blank predicates, Python transforms, then callable mark
bindings. Updates start from retained source records, so transforms do not
compound. Invalid updates leave the previous state intact. `update_options()`
uses constructor precedence, including `groups_open`/`collapsed` and link-column
visibility.

### Kinds (the chain entry points)

Each factory sets a sensible `type`, format and alignment for the kind. The
kind is the *starting point*; anything it sets can be overridden later.

| Factory | Kind | Baseline it sets |
| --- | --- | --- |
| `col.text(name)` | free text | `type="string"`, left |
| `col.number(name, fmt=, align=)` | a number | `type="number"`, auto-scaling |
| `col.integer(name)` | a whole number | `type="number"`, `num0` |
| `col.percent(name, whole=, decimals=)` | a percentage | `pct1` (or `0.0"%"` when `whole=True`) |
| `col.currency(name, code=, decimals=)` | money | `usd`, `eur`, `gbp`, … |
| `col.boolean(name)` | true/false | `type="boolean"` |
| `col.date(name)` | a date | `type="date"`, `yyyy-mm-dd` |
| `col.time(name)` | a time of day | `type="date"`, `hms` |
| `col.datetime(name)` | date and time | `type="date"`, `yyyy-mm-dd HH:MM:SS` |
| `col.flag(name)` | a country/region | `fmt="flag"` (alpha-3 codes) |
| `col.bar(name)` | a bar | a `bar` encoding; optional `label=True` |
| `col.color(name)` | a shaded cell | `viz="color"` |
| `col.chip(name)` | a pill | `viz="chip"` |
| `col.delta(name)` | a change indicator | `viz="delta"` |
| `col.sparkline(name)` | an array trend | `viz="sparkline"` |
| `col.symbols(name)` / `col.repeat` | repeated symbols | `viz="symbols"` |
| `col.rating(name, max=)` | a star rating | `viz="symbols"`, `★`/`☆` |
| `col.link(name)` / `col.url` | a hyperlink | `html` + link |
| `col.image(name)` / `col.logo` | an image | `html` + `<img>` |
| `col.markdown(name)` / `col.html` | rich text | `html` |
| `col.auto(name, **overrides)` | *inferred* | see [inference](#the-inferred-kind-colauto) |
| `col.merge(name, spec)` | a merged column | see [merged values](#composing-merged-values) |

`col.group(...)` and `col.subcolumns(...)` are **structures**, not leaf columns —
see [Composing header structures](#composing-header-structures).

### The chain

Every method returns a **new** `Column`; the original is never mutated. That is
what makes the chain safe to store, reuse and extend.

| Method | Effect |
| --- | --- |
| `.fmt(code)` / `.format(code)` | set the SSF format code (the escape hatch) |
| `.total_fmt(code)` / `.subtotal_fmt(code)` | a different format in the total / subtotal rows |
| `.align("left"\|"right"\|"center")` | horizontal alignment |
| `.align_decimals(bool)` | pad decimals so points line up |
| `.title(text)` / `.info(text)` / `.footnote(column)` | header text, tooltip, footnote mark |
| `.bold()` / `.italic()` / `.font_weight(v)` / `.font_style(v)` | body-cell font |
| `.font(family)` / `.font_color(color)` | body-cell family and colour |
| `.wrap(bool)` / `.rotate_title(deg)` | wrapping and rotated headers |
| `.neg(color=, bracket=)` / `.red_negatives()` | negative-number styling |
| `.highlight(color)` | tint the whole column |
| `.blank(pred)` / `.blank_below(v)` / `.blank_above(v)` / `.null_text(t)` | suppress values |
| `.repeat_values(bool)` / `.hide(bool)` / `.sort_by(column)` | grouping display, visibility, sort key |
| `.markdown()` / `.html()` / `.link(...)` / `.image(...)` / `.logo(...)` | rich cells |
| `.template(value, **formats)` | a fill-in-the-blanks cell |
| `.viz(kind, **options)` | set `viz` directly |
| `.color(...)` / `.chip(...)` / `.delta(...)` / `.sparkline(...)` / `.symbols(...)` | visualisations |
| `.relative(value)` / `.fmt_column(column)` / `.group(label)` / `.subcolumn(label)` | dates, references, header structure |

### How a column composes

Every factory call and every chain method merges a small dict of options into a
new `Column`. Options **accumulate** and the **last write wins**, so the chain
reads top-to-bottom as "start here, then…".

```python
col.bar("revenue", format='usd0', label=True).neg(bracket=True).bold()
```

builds up like this:

```python
step_1 = {"name": "revenue", "type": "number", "fmt": "usd0"}
step_2 = {**step_1, "encodings": [{"kind": "bar", "source": "revenue",
                                "label": {"value": True}}]}  # col.bar(..., label=True)
step_3 = {**step_2, "red_negatives": True, "bracket_negatives": True}     # .neg(bracket=True)
step_4 = {**step_3, "font_weight": "600"}                                  # .bold()
```

and `to_config()` returns the merged result:

```python
{
    "name": "revenue",
    "type": "number",
    "fmt": "usd0",
    "encodings": [{"kind": "bar", "source": "revenue", "label": {"value": True}}],
    "red_negatives": True,
    "bracket_negatives": True,
    "font_weight": "600",
}
```

Because a column is just a mapping, the reverse also works: build the dict
yourself and hand it to `columns=[...]` — the renderer treats the two
identically.

#### The inferred kind: `col.auto`

If a spec has **no `type`**, it does not retype the column — it takes the
*inferred* definition and then applies its own options on top. `col.auto` is the
explicit spelling of that:

```python
[col.auto("trips"), col.auto("revenue").font_color("#94a3b8")]
```

This is how you keep DuckDB/Arrow types and column metadata while still tweaking
alignment, colour or a visualisation. A bare name (`col.auto("x")` ≡ `"x"`) and
a mapping without a `type` behave the same way. Aliases are normalised *before*
the merge, so an inferred default (e.g. `redNegatives: false`) never shadows a
camelCase option you set.

## Composing header structures

Tables are trees, not just rows of columns. Three builders express the tree, and
they all flatten into the same flat `columns=[...]` list.

### Columns

A `col.*` leaf is the only thing that renders body cells. Its `name` is the data
column it reads; everything else is presentation.

### Groups

`col.group(label, columns, *, highlight=None)` puts a **spanner** header over a
run of columns:

```python
col.group("Financials", [
    col.currency("revenue"),
    col.currency("cost"),
    col.currency("profit"),
])
```

![Grouped headers](images/groups.png)

The label spans its members; the members keep their own headers and rendering.
`label` may be a list of strings to nest several levels at once, and `highlight`
tints the whole group.

### Sub-columns

`col.subcolumns(label, columns, *, group=None, highlight=None)` gives several
members **one shared leaf header**. This is for the reporting idiom of a value
beside its period — one right-aligned number, one muted left-aligned text, maybe
a chip — under a single heading:

```python
col.subcolumns("Latest", [
    col.number("gdp", fmt="num1", align="right").neg(),
    col.auto("quarter").align("left").font_color("#94a3b8"),
])
```

The shared header replaces the members' individual visible titles, and clicking
it sorts on the first visible member (`sort_by` on that member can pick a
different key). Each member is still its own data column for search, export,
statistics and runtime updates — only the header is shared.

### Nesting

Groups and sub-columns nest freely, which is how you get the two-level economic
table:

```python
col.group("Gross domestic product", [
    col.subcolumns("Latest", [
        col.number("gdp", fmt="num1", align="right").neg(),
        col.auto("quarter").align("left").font_color("#94a3b8"),
    ]),
    col.number("forecast", fmt="num1", align="right", title="Annual forecast"),
]),
col.group("Consumer prices", [
    col.subcolumns("Latest", [
        col.number("cpi", fmt="num1", align="right").neg(),
        col.auto("month").align("left").font_color("#94a3b8"),
    ]),
]),
```

![Sub-columns inside groups](images/subcolumns.png)

`col.group` and `col.subcolumns` both return a `ColumnGroup` — an immutable
`Sequence[Column]`. Because `columns=[...]` flattens nested sequences
recursively, a `ColumnGroup` can be dropped anywhere a list of columns is
expected, including inside another group.

## Composing merged values

A **merged column** is the opposite of a sub-column: instead of one header over
several cells, it is **one cell** built from several columns. The `cols_merge_*`
helpers describe the value; `col.merge(name, spec)` names the derived column:

```python
from evidential import col, cols_merge_n_pct, cols_merge_range, cols_merge_uncert

columns=[
    col.text("site"),
    col.merge("range", cols_merge_range("low", "high", fmt="num0", title="Range")),
    col.merge("measurement", cols_merge_uncert("value", "uncert", fmt="num1", title="Value")),
    col.merge("share", cols_merge_n_pct("n", "pct", title="Share")),
]
```

![Merged columns](images/merged.png)

| Helper | Result |
| --- | --- |
| `cols_merge(template, *, template_fmt=, **options)` | a template filled from other columns |
| `cols_merge_range(begin, end, *, sep="–", fmt=)` | `"begin–end"` |
| `cols_merge_uncert(value, uncert, *, sep=" ± ", fmt=)` | `"value ± uncert"` |
| `cols_merge_n_pct(n, pct, *, fmt=, pct_fmt="pct1")` | `"n (pct)"` |

The first argument to `col.merge` is the name of the new column; the helper's
`**options` (including `title`) are merged onto it like any other column option,
so you can chain on the result too.

## Grouped, pivot and comparison tables

The aggregate helpers accept the same `col.*` builders — through
`dimension_config` / `measure_config` — so everything above applies unchanged.
They run their aggregation in DuckDB (`GROUPING SETS`), then hand a flat table to
the renderer.

```python
from evidential import col, grouped_table, pivot_table, comparison_table

grouped_table(
    connection,
    "SELECT category, sales FROM needful_things.orders",
    dimensions=["category"],
    measures=["round(sum(sales), 0) AS sales", "count(*) AS orders"],
    dimension_config={"category": col.text("category")},
    measure_config={
        "sales": col.currency("sales", decimals=0),
        "orders": col.integer("orders"),
    },
)
```

![Grouped totals](images/grouped-table.png)

`pivot_table` turns a dimension into columns (each pivot value becomes its own
column per measure, under a shared header):

![Pivoted columns](images/pivot-table.png)

`comparison_table` computes each measure for the current and the matching prior
period, then adds `<measure>_prior`, `<measure>_delta` and `<measure>_pct`. The
percentage-change column is a `viz="delta"`; a measure's `delta_options` (or
top-level `neutral_range`, `down_is_good`) describe those derived columns. Use
`col.merge` when you want to name and style them explicitly.

![Prior-period comparison](images/comparison-table.png)

`query_table` runs ad-hoc SQL with optional `where` / `order` / `limit` /
`date_range` and lays the result out with your `columns`:

![Ad-hoc query](images/query-table.png)

`grouped_records` does the same grouping client-side, from plain rows. For
report-specific display rows, pass a separate `row_layout`. Headings and
summaries never become detail records:

```python
from evidential import EvidentialTable, rows

table = EvidentialTable(
    detail,
    row_layout=rows.group_by("region")
        .section(values={"country": rows.count(suffix=" products"), "arr": "sum"})
        .summary("Region average", values={"arr": "mean"})
        .grand_summary("All regions", values={"arr": "sum"}),
    page_size=10,
)
```

`.section()` adds a heading per group, optionally with numeric values or text in
named columns. `.summary()` and `.grand_summary()` are independently optional;
`.total()` aliases the latter. A summary without `values` sums numeric detail
fields, excluding internal metadata; use `values={}` for a label-only summary.
Multiple `group_by` fields create nested groups in first-appearance order.
Sorting reorders details within groups, without changing the source records.

A `values` entry may be a built-in aggregation name (`"sum"`, `"mean"`,
`"median"`, `"min"`, `"max"`, `"count"`, `"count_distinct"`), a portable
`rows.aggregate("sum", "source", prefix=, suffix=, format=)` expression, a
literal, or a Python callable receiving the group's detail records.
`rows.count(suffix=" products")` counts detail records rather than nonnull
values in a field. Named aggregations and portable expressions recalculate over
all search matches, across pages. Literals, callable values and callable labels
retain their source scope until a Python `set_data` refresh. Filter upstream to
recalculate an arbitrary Python function over a filtered dataset.

Page size counts details only. Every page repeats its active group headings as
`"<label> (cont.)"`, without repeating heading values. A bottom group summary
appears after its last matching detail; `summary(position="top")` puts it before
the first one. The grand summary appears once on the final nonempty page.
Empty search results have no annotations. CSV contains matching details in
display order, without annotations; statistics, marks and scale domains use
detail data exclusively.

Each annotation accepts `style={...}`, `rule="none" | "above" | "below" |
"both"`, and `label_column=`. A label and an explicit value in the same column
both remain visible. `section(align="center")` spans the table and rejects
value cells. Annotations participate in alternating shading; their rules and
styles are independent of detail cell styles, marks and row rules. Page
boundary rules remain visible. `section_indent=1` insets detail stubs below
left-aligned headings by one rem.

`set_data` preserves the layout, or replaces it with `row_layout=...`; pass
`row_layout=None` to clear it. The bound spelling
`rows.of(detail).group_by(...).section().build()` returns a `RowView`, containing
detail records and a separate layout, and can be passed directly to
`EvidentialTable`. Both iterating that view and reading `table.rows` return
details only. `table.display_rows` is an unfiltered inspection snapshot that
includes synthetic rows.

Historical `grouped_records`/SQL helpers, `section_row` and `spacer_row` inputs
are split at the table boundary before mark evaluation. They retain their
precomputed summaries and accordion/merged-cell behavior. Pass `combined=True`
to grouped helpers for combined labels and totals. Use `row_layout` for
filter-sensitive summaries and detail-based pagination.

## Table settings

`settings(**options)` validates a set of table-wide options and returns a
`TableOptions` mapping. Pass it with `settings=REPORT`, and let explicit keyword
arguments win over it:

```python
REPORT = settings(title="Monthly report", width="900px", row_shading=True)

EvidentialTable(rows, columns=[...], settings=REPORT, width="700px")  # width=700px
```

The same options can be passed directly to `EvidentialTable(...)`. The full set
is in the [Table options reference](#table-options).

In tables containing charts, text and numeric columns fit their content while
chart columns share the remaining width. Mark tracks have a minimum width of
`10rem`, or `18rem` for stacked bars. Fixed-size sparklines retain their specified
width. `stretch=False` sizes the whole table to its content and chart minimums;
`width=` caps the table container. If the minimum content cannot fit, the table
scrolls horizontally.

## Visualisations

A visualisation is a column option (`viz`) plus a bag of options, set through a
chain method. Most visualisations are **presentations of a value**: sorting,
search, statistics and CSV export keep using the underlying number.

```python
columns=[
    col.text("region"),
    col.bar("revenue", label=True),                    # a bar
    col.bar("growth", center=True, label=True),         # a centred (diverging) bar
    col.color("share"),                      # a shaded cell
    col.chip("region", title="Chip"),                       # a pill
    col.sparkline("trend", type="area"),     # a trend
    col.boolean("active", true_symbol="✓", false_symbol="✗"),  # ✓/✗
    col.percent("growth", decimals=0, title="Δ").delta(),   # a change indicator
]
```

![Visualisations](images/visualizations.png)

- **Bar** — `col.bar(source, label=True, color=, negative_color=, fit_to_data=, hide_labels=,
  background=, center=, pad=, direction=, reference=, reference_color=,
  reference_label=)`. With `center=True` the bar grows from a centre line
  (positive right, negative left) — a second geometry of the same cell. With
  `direction="left"` it fills from the right edge instead, and `reference=N`
  draws a vertical benchmark rule at a value. `color="@column"` colours each bar
  from a column (`@` marks the column reference).
- **Colour** — `.color(scale=, stops=, conditional_colors=, scale_column=, min=,
  max=, midpoint=)`. `scale` takes a preset (`"blues"`, `"viridis"`), any of the
  matplotlib colour maps (`"RdBu"`, `"plasma"`, …), a list of stops, or
  `"@column"` to take each row's colour from another column.
- **Chip** — `.chip(min_width=, conditional_colors=, scale=, …)`, on either a
  text or a numeric column.
- **Delta** — `.delta(down_is_good=, neutral_range=, chip=, show_value=,
  show_symbol=, symbol_position=)`. Green for up, red for down, a grey dash
  inside `neutral_range`.
- **Sparkline** — `.sparkline(type="line"|"area"|"bar"|"points"|"change", x=, y=,
  color=, fit_to_data=, y_fmt=, width=, height=, markers=, marker_color=, signed=,
  reference=, reference_color=, delta=, steady=, color_scale=, color_domain=)`
  over an array column. `type="points"` draws only markers; `markers=True` adds a
  dot at every point and `markers="ends"` only the endpoints; a per-point
  `color` key on the data overrides `marker_color`; `signed=True` splits an area
  fill at the zero baseline. For ordinary sparklines, `reference=1` draws a
  dashed 100% line (with `y_fmt="pct1"`) and anchors the area/bar origin there.
  `signed=True` then fills above it with `color` and below it with the negative
  theme color. `reference_color=` styles the rule. Inferred scales include the
  reference, including when `fit_to_data=True`; explicit shared domain bounds
  take precedence. Missing values leave gaps. For example:

  ```python
  col.sparkline(
      "trade_history", type="area", x="year", y="ratio", y_fmt="pct1",
      reference=1, signed=True, fit_to_data=True, color="#0f766e",
  )
  ```

  The public `SparklineType` literal alias lists the five supported styles and
  is shared by both builders and the configuration schema. Import it with
  `from evidential import SparklineType` when annotating your own helpers.

  `type="change"` draws one equal rectangle per observation, with an ordinal
  position even for structured/date input. Values are changes or signed outcomes:
  up above `steady`, down below it, centered within its inclusive range (default
  `(0, 0)`). Up/down shift by exactly half a rectangle height. Missing or invalid
  values leave empty slots; an entirely missing sequence shows the null marker.
  `x`/`y` bindings and `y_fmt` supply formatted, per-match tooltips. The SVG also
  exposes a summary of up/steady/down/missing counts.

  Add `delta=True` for absolute measurements: each observation is compared with
  its immediate predecessor. The first slot stays blank, and missing values
  break comparisons. State thresholds, tooltips, gradient colors and shared
  domains then use the computed differences. `delta` defaults to `False` and
  is only supported for `type="change"`. Original arrays remain unchanged.

  ```python
  # Win/loss/draw sequence: positive, negative and zero goal margins.
  col.sparkline("outcomes", type="change", width=160)
  # Absolute revenue: 5 → 4 is a decrease, even though both values are positive.
  col.sparkline("revenue", type="change", delta=True)
  # Continuous change: keep the whole neutral range gray, even on an asymmetric domain.
  col.sparkline(
      "changes", type="change", steady=(-0.5, 0.5),
      color_scale=["#b2182b", "#b8bcc2", "#2166ac"], color_domain=(-4, 8),
  )
  ```

  Default state colors are the theme's accent (up), negative (down), and gray
  (steady). `color=` gives every rectangle one color. Optional `color_scale=`
  accepts the existing named palettes or at least two colors. Its midpoint is
  anchored to the **whole steady interval**, with independent ramps below and
  above it; an odd palette makes the center color explicit. An even palette
  uses its interpolated midpoint. `color_domain=(low, high)` fixes the endpoints
  and must contain the steady interval. Colors outside it clamp to the endpoints.
  Otherwise matching rows share inferred endpoints before pagination; filtering
  recomputes them. Marks always retain their three positions and equal heights.
  Change-only settings are validated for factories, refinements and mappings.
  `color` and `color_scale` are mutually exclusive. Marker, signed-area and
  fit-to-data settings do not apply to change rectangles.

  [Notebook 46](../../notebooks/46_change_sparklines.py) queries the local
  football results dataset: search teams, select a year and competition, then
  click a team to update the second table with match details and labeled goal
  margin bars. A switch adds a goal-margin gradient to the top table's sparklines.
- **Symbols** — `.symbols(symbol=, shape=, empty=, max=, image=, color=,
  empty_color=, size=, gap=)`: repeat the value as glyphs, emoji, images, or
  font-independent CSS boxes. `max` is a *floor* (the row is filled to at least
  `max`, then the rest are empty). `col.rating` and `col.repeat` are shortcuts.

![Repeated symbols](images/symbols.png)

Two references are useful throughout: `@column` marks a column name wherever an
option names a column (`sort_by="@x"`, `scale="@color"`, `footnote="@note"`,
`link="@url"`, `color="@bar_colour"`, …), and colours accept matplotlib names
(`"tab:blue"`, `"C3"`, `"k"`) **wherever a colour is accepted** — marks,
`cell_style`, `highlight`, `font_color`, `negative_color`, theme options,
palette lists and colour stops.

### Shared numeric domains

Columns with `.domain("name")` pool their numeric values into one domain,
independently of column groups or sub-columns. For shared color settings too,
reuse an immutable domain specification:

```python
from evidential import col, domain

payments = domain.numeric("payments").include_zero().palette("Blues")
columns = [
    col.bar("credit_card").domain(payments),
    col.bar("cash").domain("payments"),
    col.number("no_charge").color().domain(payments),
]
```

All declarations with the same name belong to the same table-local domain.
A configured declaration supplies settings to name-only members. Values from
all member columns, including hidden ones and plain numeric columns, determine
inferred bounds. Mark contributions use their plotted coordinates (including
stack totals); sparkline contributions use their numeric observations. Synthetic
rows and missing values do not contribute. Matching rows are pooled before
pagination; filtering recomputes inferred bounds, while paging and hiding a
member preserve them.

- `.bounds(low, high)` fixes endpoints instead of inferring them.
- `.include_zero()` includes zero in inferred bounds; `.include_zero(False)`
  disables it. Without a setting, bars and zero-based area/bar sparklines
  include zero. Explicit bounds remain fixed.
- `.palette("Blues")` or `.palette(["red", "gray", "blue"])` shares the color
  mapping for heatmaps, numeric chips and change sparklines. Bar/line fill colors
  remain independent styling choices.
- `.midpoint(0)` anchors a diverging palette. A shared palette also shares any
  member's explicitly configured color midpoint.

Centered or diverging marks make the domain symmetric for all members. Fixed
bounds for these marks must be symmetric or expressed as `(0, magnitude)`.
Change sparklines contribute their steady interval; every shared color encoding
uses that whole interval as its neutral color, preserving equal colors for equal
values across a heatmap and a sparkline. Change members must agree on that
interval.

Conflicting shared settings raise an error during table construction or update.
Set shared bounds on the domain rather than individual scale/color options.
Shared palettes use the existing LCH interpolation; incompatible per-column
color overrides are rejected. Per-column axes and gridlines remain available.
Shared numeric domains currently
support linear scales. Reusing the same specification in separate tables shares
configuration; inference remains local to each table. Use fixed bounds for
comparisons across tables.

See [notebook 47](../../notebooks/47_shared_domains.py) for bars, heatmaps,
change sequences and independent header groups using shared domains.

### Composing marks in a column

A column is a *presentation slot*: it can hold an ordered list of **marks**
(encodings), each bound to its own field and sharing one horizontal scale. The
mark constructors — `col.bar`, `col.point`, `col.range`, `col.stacked_bar`,
`col.strip` — return a chainable column; `.bar(...)`/`.point(...)`/`.range(...)`
append a mark and `.label(...)` annotates the most recent one.

```python
columns=[
    # two overlaid bars, this year over last (size is the height fraction)
    col.bar("current", color="navy", size=0.8)
       .bar("previous", color="#d1d5db", size=0.2),
    # a bar whose label is another field, coloured per row
    col.bar("votes", label="@candidate", color="@party_colour"),
    # a value with an independent target marker
    col.bar("current").point("target"),
    # a point plus its interval, on a fixed 0–100% scale
    col.range("low", "high", cap="line").point("estimate").scale(domain=(0, 100), unit="%"),
    # a column-wide benchmark rule
    col.bar("debt").reference_line(55, label="Developing average"),
    # a five-part stack, labelled, normalised to percentages
    col.stacked_bar("ally", "friendly", "unknown", "unfriendly", "hostile",
                    colors=["#9333ea", "#c084fc", "#ddd", "#fb8b80", "#ef4444"],
                    labels=True, normalize="percent"),
    # an ordered categorical sequence (form / states)
    col.strip("form", colors={"W": "green", "D": "grey", "L": "red"}, labels=True),
    # a precomputed five-number summary with outliers
    col.boxplot("minimum", "q1", "median", "q3", "maximum", outliers="outliers", whisker="iqr"),
]
```

- **Marks** — `bar(source, color=, color_negative=, size=, side=, valign=, ...)`,
  `point(source, size=, color=, outline=)`, `points(source, size=, color=, outline=)` (one marker per
  array element), `range(low, high, cap="none"|"line"|"dot"|"arrow", fill=,
  color_negative=, direction_marker=)`.
  `fill=True` draws the interval as a translucent band instead of a line.
  For dumbbells, `color_negative="red"` colors a range when its second value
  is smaller than its first. `direction_marker=True` adds a centered chevron
  pointing from the first endpoint to the second; equal endpoints omit it.
  Both options preserve independent point colors. Negative colors also accept
  `"@column"` and callable bindings. See
  [`48_dumbbell_plots.py`](../../notebooks/48_dumbbell_plots.py).
  `side="left"`
  `|"right"` draws a nonnegative magnitude from the central origin; `size` is the
  bar height fraction or the point/range marker size; `valign="top"|"center"|
  "bottom"` places the mark vertically (top/bottom with small sizes gives
  side-by-side bars). `cap="arrow"` marks an endpoint that extends beyond the
  displayed scale. Points accept `outline=False` to remove their ring, or a
  color string such as `outline="#334155"` to recolor it independently of
  `color` (the fill). Omission, `None`, or `True` keeps the default one-pixel
  theme ring, without changing the marker's size or position.
- **Named point series** — `col.points(["actual", "target"], palette=,
  connect=True)` draws several scalar fields without repeated `.point(...)`
  calls. A field-to-name mapping, such as
  `col.points({"young": "0–9", "old": "80+"}, palette="viridis", connect=True)`,
  supplies both fields and legend names; `.legend()` picks those names up
  automatically. Omitting `palette` uses the categorical `tab10` sequence;
  named ranges such as `viridis` are sampled evenly in declared series order.
  A list supplies custom colour stops, and an explicit `color` overrides the
  palette. `size` and `outline` override the defaults of nine-pixel points
  without rings. `connect=True` draws a thin span across valid points as a
  display concern, without adding extrema fields or a legend entry. Missing
  values keep the remaining series' colour assignments; equal or singleton
  points have no span. `col.points("array_column")` retains its existing array
  semantics and defaults. Palette/connection options require the field-list or
  mapping form. The scale, axis and value format remain explicit choices.
- **Stacks** — `stacked_bar(*sources, colors=, labels=, label_align="begin"|
  "center"|"end", normalize="percent", size=, diverge_at=, neutral="split")`.
  `labels=True` writes each segment's value and `labels="percent"` its share;
  `size` is the stack height fraction. `diverge_at="neutral", neutral="split"`
  centres the named segment on the origin and grows the categories either side
  left and right (a Likert chart).
- **Legends** — append `.legend()` to a mark column for a compact color key
  above the table, to the right of the title and subtitle. A group for each
  opted-in column is named exactly like its rendered table heading. Column
  names default to hidden for one nonempty group and visible for two or more.
  `.legend(column_names=True)` forces this group's heading to show;
  `column_names=False` hides it, and `None` restores automatic behavior.
  Each group occupies its own `Column name: <keys>` row when named;
  complete swatch/label pairs wrap
  without splitting words. There is no extra visible legend heading.
  `.legend(outline=True)` draws a thin box around the combined key; any opted-in
  column can request the shared outline. On narrow displays the
  key moves below the title as needed. Column and key names use mid-dark grey;
  bar/stack swatches are square. Entries are separated by spacing, with no
  leading separator after a wrap, and stay inside the table's right edge.
  Stacks, bars, points, ranges and strips share this API. Names default to source
  headings (or strip category keys); `.legend(["Storage", "Requests"])` overrides
  all names in declaration order, while `.legend({"requests": "API calls"})`
  overrides selected names. A `None` label omits an entry, such as a connecting
  range behind coloured points. `.legend(False)` disables the column's key.
  Swatches resolve the same colors as their marks, including theme defaults
  and explicit negative colors. Per-row color references are rejected because
  a color field alone cannot identify categories. Keys do not change with row
  search, pagination or sorting. See
  [`54_legends.py`](../../notebooks/54_legends.py) for one stack, two stacks and
  nine age-band points using real population data.
- **Overlapping points** — opaque, differently coloured dots whose centres fit
  within one CSS pixel share a circle split into equal pie sectors. Halves
  divide vertically; thirds and larger groups meet at the centre. The entire
  group's span is bounded, so a chain of nearby points cannot collapse into
  one long cluster. A sorted sweep recalculates after layout and resize.
  Translucent and differently sized points keep their existing rendering.
  Source values, individual outline colours and tooltip identities are retained.
  See [`48_dumbbell_plots.py`](../../notebooks/48_dumbbell_plots.py).
- **Tooltips** — inspect full, comma-grouped values independently of painted
  labels. Dots under the pointer share a multiline tooltip with named series,
  sorted by numeric x-value (declaration order breaks ties);
  their invisible hit area is slightly larger than the visible dot. Stack
  segments report category, amount, share and total, including hidden labels
  and both halves of a split neutral category. Ranges report endpoints and
  change; box plots report their five-number summary and outliers. Object-backed
  observations can carry plain-text metadata such as date, opponent and score.
  Currency and percentage units are retained while abbreviated/scientific
  numbers expand to their available source precision.
  Every column supports `.tooltip(False)`, `.tooltip("@hover_text")` and literal
  multiline `.tooltip("First line\nSecond line")`; `.tooltip()` restores defaults.
  Overrides apply to the whole cell, including all child marks; text is never
  interpreted as HTML. Graphic cells provide one Tab stop; Left/Right cycles
  marks, Home/End jumps and Escape dismisses. Sparklines choose just one nearest
  x observation across the graphic's height; signed-area swatches follow the
  above/below-reference fill. Stacks and strips choose one segment at an edge.
  Hover timing is configured in seconds with
  `settings(tooltips={"delay": 0.8, "text_delay": 1.5})`; per-column
  `.tooltip(delay=0)` overrides the graphics delay. Defaults are 0s for graphics
  and 0.8s for text. Keyboard and touch inspection bypass hover delays. See the offline
  [`55_tooltips.py`](../../notebooks/55_tooltips.py) gallery.
- **Boxplot** — `boxplot(minimum, q1, median, q3, maximum, outliers=, whisker=`
  `"extrema"|"iqr")`. The renderer never computes statistics; the five numbers
  arrive from SQL or Python.
- **Distribution** — `distribution(source, x="position", y="density",
  style="band", height=0.5, density_max=None)` draws a flat uncertainty band.
  Density controls opacity, with pale tails and darker high-density regions;
  the height stays constant. Input is an ordered `LIST<STRUCT<x, y>>` of
  precomputed coordinates and nonnegative densities. Raw samples are rejected;
  the renderer never fits a density curve. Null samples or null fields leave
  gaps, and the band ends at the supplied support. Coordinates must be strictly
  increasing and positive on a log axis.
  `height` is a fraction of the row's mark track in `(0, 1]`. By default each
  row's peak maps to full opacity; this compares shape and uncertainty width,
  not absolute density heights. Set the same positive `density_max` across rows
  for a fixed intensity scale; opacity saturates at that value. Clipping and
  search do not renormalize the visible tail. Add `.point("median")` for a
  central estimate on the shared x-axis. See
  [ADR-065](../adr/065-distribution-uncertainty-bands.md).
  (ordered positions, not raw samples). Combine with `.point("median")`.
- **Strip input** — a list of categories (`LIST<category>`) is equal-width; a
  list of `{start, end, category}` structs is positioned on a shared x axis, and
  a list of `{position, category}` structs fills each state to the next.
- **Labels** — use the immutable `label` builder to format and style a mark's
  annotation. It shares `fmt`/`format`, `font`, `font_color`, `bold`, `italic`,
  `font_weight`, `font_style` and `figure_style` with text columns. For labels,
  `color` and `colour` are aliases of `font_color`.

  ```python
  from evidential import col, label

  annotation = label.fmt("num0").bold().auto_position("inside end").colour("black")
  col.bar("sales", label=annotation)
  col.bar("sales", label=annotation.auto_position("outside start"))
  col.point("target", label=label.fmt("num1").position("above").italic())
  col.stacked_bar("cash", "card", labels=label.fmt("num0").bold().colour("black"))
  ```

  With no explicit binding, a label shows the mark's value. Use
  `label.source("other_field")` (or a callable) for another value,
  `label.text("literal")` for fixed text, and `.value()` to return to the mark's
  value. `.prefix(...)` and `.suffix(...)` surround the formatted text.
  `.align("begin"|"center"|"end")` aligns text within the mark; `left` and `right`
  are aliases for `begin` and `end`. Stacks also support `.share()` to label each
  segment with its share of the total (default format `pct0`).

  `.position(...)` fixes placement and turns automatic placement off.
  `.auto_position(...)` tries the preferred position, then swaps inside/outside
  at the same start/end edge, omitting the label if neither fits. Every fit,
  including resizing, retries the original preference. The four automatic
  preferences are `inside start`, `inside end`, `outside start` and `outside end`.
  Fixed labels also support `center`, `above` and `below`. Spaces, underscores
  and hyphens are accepted in positions. Automatic placement applies to bars.

  `label=True`, `label="@field"`, literal strings, dictionaries and
  `.label(...)` remain supported. Repeated `.label(...)` calls refine the latest
  mark's annotation, preserving its binding unless another is specified. The
  mapping form accepts `source`, `text`, `value`, `prefix`, `suffix`, `format`,
  `position`, `auto`, `align`, `overflow`, `min_width`, `color`, `font`,
  `font_weight`, `font_style` and `figure_style`. For example,
  `label={"format": "num0", "position": "inside_end", "auto": True}` is an
  automatic label. With no position, bars default to `outside_end`, centered
  bars to `outside_start`, points to `center`, and stack segments to `inside_end`.

  For bars, `outside_start` places the label across the origin from the bar:
  positive bars label left of zero, negative bars right of zero. Start/end
  follows the numeric origin/tip for both signs and mirrored bars.
  Labels that do not fit hide completely by default; the original values remain
  in the mark's accessibility text. `.overflow("show")` permits overflow for
  fixed labels; automatic labels always omit text when neither candidate fits.
  `.min_width(pixels)` adds a minimum available width. Inside and stacked labels
  choose light/dark text for contrast; an explicit color overrides this choice.
- **Scale** — `.scale(domain=(lo, hi), include_zero=, unit=, transform=`
  `"linear"|"log", axis=, axis_position="top"|"bottom", gridlines=)` fixes the
  shared quantitative axis; `.reference_line(value, label=, color=)` adds a rule
  and `.reference_band(low, high, label=, color=)` shades a zone (a target or
  equivalence range) through the cell height behind guides and marks. An explicit
  band color is used as supplied; use an alpha color for transparency. The
  default band remains subtle. `axis=True` draws tick labels for the column, and
  `gridlines=True` faint vertical lines through the cells. A top axis sits below
  its column label and above the first horizontal line of the row area, pushing
  the label upward; unscaled labels stay by that line. A bottom axis sits below
  the last horizontal line. Tick marks touch those lines from outside the rows.
  Axes belong to the header/footer, never synthetic body rows. A log scale needs a
  positive domain and labels powers of ten plus domain endpoints, with shorter
  unlabeled ticks at 2–9 within each decade. Their gaps shrink toward the next
  decade; major and minor tick marks are black. It is what a forest plot
  uses with `.reference_line(1)`.
  Repeated `.scale(...)` calls preserve earlier settings; `domain="auto"`
  explicitly clears fixed bounds. Missing data suppresses only its own mark.
  Automatic marks domains exclude synthetic rows and include all detail-row
  sources, interval endpoints and cumulative stack totals.
  For two-sided bars/Likert stacks, `(0, magnitude)` denotes the extent of
  each arm and displays a signed `-magnitude…+magnitude` axis. An explicit
  symmetric signed domain is also accepted; asymmetric signed bounds are rejected.
- **Cell chrome** — `.cell_style(background=, color=, border=, padding=)` styles
  the cell independently of the marks; `background="@column"` takes a per-row
  colour. Matching `rules` still win for the same property.
- **Sources** — a field name, `"@field"`, or a `lambda row: ...`. A callable is
  evaluated Python-side into a hidden helper column, so the browser (and any
  static export) only ever sees field names.

Every mark factory serializes to `encodings`, including a single plain bar.
Use `col.bar("revenue", label=True)` to annotate its value. Existing raw `viz="bar"`
dictionaries remain accepted. The scalar `.number(...).bar()` shortcut has been
removed; use the mark factory with an explicit format and label.

Display `.section(values=...)` rows use separate annotation cells, so a numeric
column can show a literal such as `"27 products"` in a heading without applying
its detail mark bindings. See the row-layout API above and
[`45_display_row_layout.py`](../../notebooks/45_display_row_layout.py).

`col.html(...)` and `.html()` explicitly opt into **trusted, unsanitized HTML**.
Only use them with content you control or have sanitized upstream. Ordinary text
columns escape source strings and never interpret them as HTML.

### Back-to-back bars

`direction="left"` mirrors the bar, so a leftward column and a rightward one
either side of a label column make a back-to-back ("tornado") league table.
`reference=N` draws a benchmark rule on the bar's own scale (mirrored with a
leftward bar), `reference_label` captions the benchmark, and
`color="@column"` keys both panels with one colour column:

```python
columns=[
    col.bar(
        "spend", format="usd1", direction="left", label=True,
        reference=4.3, reference_label="OECD median 4.3", color="@color", pad=3,
    ).align("left"),
    col.text("country"),
    col.bar(
        "rate", format="num2", label=True,
        reference=0.32, reference_label="OECD median 0.32", color="@color", pad=3,
    ).align("right"),
    col.auto("color").hide(),
]
```

![Back-to-back bars](images/back-to-back.png)

## Formatting

The kind factories cover the common cases; `.fmt()` is the escape hatch when you
need an exact SSF code.

`.fmt("compact")` chooses a unit for each value: **234.5B**, **1.7T**,
**1.2M** or **1.5K**, with one decimal place (zero displays as `0`). It works
with `label.fmt("compact")` and scale axes too. Values keep their signs and
remain numeric for sorting, statistics and export. The existing `num` preset
continues to choose one unit from the column's range.

Use `compactN` for **up to N significant figures**, from `compact1` through
`compact21`. For example, `.fmt("compact4")` displays `1147650000000` as
**1.148T** and `877123400000` as **877.1B**. The suffix controls significant
figures, not decimal places; unnecessary trailing zeros are omitted.
`label.fmt("compact4")`, statistics and scale axes use the same formatter.
Tooltips expand the underlying number with commas and retain its available
precision. Plain `compact` retains its one-decimal behavior.

`.fmt("sci")` displays scientific notation as **1.23 × 10⁵**, with two decimal
places in the mantissa. HTML cells, mark labels, statistics and axes use a real
superscript exponent; tooltips expand the full underlying value. Small values
use negative powers, for example `0.000123` becomes **1.23 × 10⁻⁴**. Explicit SSF
codes such as `.fmt("0.000E+0")` retain their requested `1.235E+5` notation.
See [the formatting demo](../../notebooks/08_column_options.py).

```python
columns=[
    col.text("item"),
    col.integer("count"),
    col.currency("price"),
    col.percent("share", decimals=0),
    col.date("day"),
    col.flag("origin"),
    col.boolean("active"),
]
```

![Column kinds](images/kinds.png)

Dates and times can print as **relative** time (`"2 hours ago"`) with
`relative=` on the factory or the `.relative()` chain method; the unit can be
`"auto"` or an explicit one:

```python
col.datetime("at", relative=True)
```

![Relative time](images/relative-time.png)

Body-cell styling — negatives, weight, italics, highlights — is also part of the
chain:

```python
columns=[
    col.text("metric").bold(),
    col.currency("q1", decimals=0).neg(),
    col.currency("q2", decimals=0).neg(bracket=True),
    col.percent("change", decimals=1).neg().italic(),
    col.percent("change", decimals=1, title="Δ %").bold().highlight("#fef3c7"),
]
```

![Body-cell styling](images/styling.png)

`.neg()` marks negative numbers (red by default; pass `color=`) and
`bracket=True` switches to accounting brackets (`-$1,234` → `($1,234)`) so the
column stays right-aligned. `font_size` on the table scales all content without
scaling the controls.

## Display rules

gt-style rules transform values at render time, leaving the data untouched. Each
is a `locations` dict from `cells_body(...)` plus an effect:

```python
from evidential import cells_body, tab_style, text_transform

rules=[
    text_transform(cells_body("category"), str.upper),
    tab_style(cells_body("sales"), color="#b45309"),
]
```

![Display rules](images/rules.png)

`tab_style` applies CSS to a location; `tab_format` overrides the format code
there; `text_transform` rewrites the displayed value with a Python callable; and
`sub_missing` / `sub_zero` / `sub_small_vals` / `sub_large_vals` / `sub_values`
substitute placeholder text. They run in order and can target columns, rows, or
a predicate.

## Dimension slicers

`DimensionGrid` is a separate anywidget input. It accepts the same data
containers as `EvidentialTable`, infers string dimensions, and displays ranked
category bars. See [notebook 56](../../notebooks/56_dimension_grid.py) for
Needful Things orders linked to monthly sales and a high-cardinality demo.

```python
from evidential import DimensionGrid

slicer = mo.ui.anywidget(
    DimensionGrid(
        con.sql("SELECT state, category, item, channel, sales FROM orders"),
        metric="sales",
        multiple=True,
        format="compact4",
    )
)
slicer
```

In a **separate reactive cell**, read `slicer.value["selected"]`. Then use
`slicer.widget.filtered` for detached matching records, or query the source:

```python
selection = slicer.value["selected"]  # Establish the marimo dependency.
predicate, parameters = slicer.widget.where()
result = con.execute(
    f"SELECT category, sum(sales) AS sales FROM orders WHERE {predicate} GROUP BY ALL",
    parameters,
).to_arrow_table()
linked_table.widget.set_data(result)
```

Create `linked_table` in its own cell; do not recreate either widget when
selections change. `.where()` quotes field identifiers and binds values,
including null categories. Apply it to a relation with the same field names.

| Parameter | Default | Meaning |
| --- | --- | --- |
| `dimensions` | Inferred string fields | Sequence of field names or `{field: display_name}`. Explicit scalar numeric/boolean dimensions are supported. |
| `metric` | `None` | Numeric field to aggregate; an omitted field counts records. |
| `aggregate` | `"sum"` with a metric, otherwise `"count"` | `"sum"`, `"count"`, `"mean"`, `"min"`, `"max"`. `count` with a metric counts non-null values; the other aggregates skip nulls. |
| `format` | `"compact"` | Existing Evidential numeric/SSF format code. |
| `multiple` | `True` | Toggle multiple selections within each dimension; `False` restricts each dimension to one. |
| `height` | `280` | Each dimension's height in pixels, including its header and footer. |
| `dimension_width` | `220` | Minimum dimension width in pixels; horizontal overflow scrolls. |
| `color` | `"#93b4ef"` | Bar colour. Bar lengths encode absolute magnitudes; signs remain in the values. |
| `title`, `subtitle` | `None` | Optional heading and description. |
| `selected` | `{}` | Initial `{field: [values]}` selection. Assign a new dictionary to update it. |

Selections are **OR within**, **AND between** dimensions. Each facet excludes
its own filter, keeping its alternatives available. Thus selecting an AWS
service narrows usage types without an explicit hierarchy declaration.
Incompatible selections remain in the list and removable, marked unavailable.

The search icon replaces a heading with an input; blur restores the heading
with an active indicator. Search covers the entire currently available category
domain and filters choices, not source records. Selected values remain in
ranked order, including through searches, with bold text and a full-height
6px dark red strip to the left. Selection does not move an item to the top.
The × clears the search, while clicking a selected row removes that selection.
Lists have slim vertical scrollbars, native wheel scrolling and keyboard
arrows/Home/End. Horizontal
scrolling and arrow buttons reveal additional dimensions.

`.raw` returns all source records; `.filtered` returns selected records. Both
are detached snapshots. `.set_data(data)` refreshes the source and prunes
missing selections. `.clear()` clears selections independently of search.
Only aggregate category data travels to the browser; virtualization bounds
rendered rows. Source normalization and aggregation remain in memory: for
large sources, preaggregate additive metrics at the needed dimension grain
in SQL before passing them to the grid. Do not sum precomputed means.

## Reference

### Column factories (`col.*`)

These are the only names `col.` exposes — the chain entry points. Factories
other than `auto`, `merge`, `group` and `subcolumns` return a `Column`;
`group`/`subcolumns` return a `ColumnGroup`.

| Factory | Notes |
| --- | --- |
| `col.text(name, *, title=)` | free text |
| `col.number(name, *, fmt=, align=, title=)` | auto-scaling number |
| `col.integer(name, *, fmt=, title=)` | `num0` |
| `col.percent(name, *, whole=False, decimals=, fmt=, title=)` | `pct…`; `whole=True` → `0.0"%"` |
| `col.currency(name, *, code="usd", decimals=, fmt=, title=)` | `usd, eur, gbp, aud, cad, cny, jpy, inr, krw, ngn, sek` |
| `col.boolean(name, *, title=, true_text=, false_text=, true_symbol=, false_symbol=)` | true/false |
| `col.date(name, *, fmt=, relative=, align=, title=)` | `type="date"` |
| `col.time(name, *, fmt=, relative=, align=, title=)` | `hms` |
| `col.datetime(name, *, fmt=, relative=, align=, title=)` | `yyyy-mm-dd HH:MM:SS` |
| `col.flag(name, *, title=)` | alpha-3 country codes |
| `col.icons(name, *, map={...}, title=)` | category → glyph / image |
| `col.bar(source, *, title=, label=, size=, side=, color=, …)` | bar mark with an optional owned label |
| `col.point(source, *, title=, size=, color=, label=)` | point marker |
| `col.points(source, *, size=, color=, outline=, palette=, connect=False)` | array observations or named scalar point series |
| `col.range(low, high, *, cap=, fill=, color=, color_negative=, direction_marker=, label=)` | interval / dumbbell |
| `col.stacked_bar(*sources, *, colors=, labels=, normalize="percent", diverge_at=, neutral="split")` | cumulative stack |
| `col.strip(source, *, colors=, labels=, segmented=)` | ordered categorical strip |
| `col.boxplot(minimum, q1, median, q3, maximum, *, outliers=, whisker="extrema")` | box plot |
| `col.distribution(source, *, x="position", y="density", style="band", height=0.5, density_max=None)` | constant-height uncertainty band; density controls opacity |
| `col.shapes(name, *, shape=, color=, …)` | alias for `symbols` |
| `col.color(name, *, title=, **options)` | colour scale |
| `col.chip(name, *, min_width=, conditional_colors=, scale=, min=, max=, midpoint=, **extra)` | pill |
| `col.delta(name, *, down_is_good=, neutral_range=, chip=)` | change indicator |
| `col.sparkline(name, *, type="line"\|"area"\|"bar"\|"points"\|"change", x=, y=, color=, fit_to_data=, reference=, reference_color=, y_fmt=, width=, height=, markers=, marker_color=, signed=, delta=, steady=, color_scale=, color_domain=, title=)` | trend |
| `col.symbols(name, *, symbol=, shape=, empty=, max=, image=, color=, empty_color=, size=, gap=, align=, title=)` | repeated symbols |
| `col.rating(name, *, max=5, symbol="★", empty="☆", color="#f59e0b")` | star rating |
| `col.repeat(name, **options)` | alias for `symbols` |
| `col.link(name, *, label=, new_tab=, title=)` / `col.url` | hyperlink |
| `col.image(name, *, height=, width=, alt=)` / `col.logo(name, *, height=)` | image |
| `col.markdown(name, *, title=)` / `col.html(name, *, title=)` | rich text |
| `col.auto(name, **overrides)` | keep the inferred definition, then refine |
| `col.merge(name, spec)` | name a `cols_merge_*` result |
| `col.array(name, *, title=)` | a list-valued column (sparkline input) |
| `col.group(label, columns, *, highlight=)` | spanner header (`ColumnGroup`) |
| `col.subcolumns(label, columns, *, group=, highlight=)` | shared leaf header (`ColumnGroup`) |

### `Column` chain methods

| Method | Summary |
| --- | --- |
| `.title(str)` | header text |
| `.fmt(code)` / `.format(code)` | SSF format code |
| `.total_fmt(code)` / `.subtotal_fmt(code)` | aggregate-row format |
| `.align("left"\|"right"\|"center")` | alignment |
| `.align_decimals(bool=True)` | pad decimals |
| `.figure_style("lining"\|"oldstyle"\|"tabular"\|"proportional")` | numerals |
| `.font(family)` / `.font_color(color)` | body font |
| `.bold(bool=True)` / `.italic(bool=True)` | weight / slant |
| `.font_weight(str)` / `.font_style(str)` | escape hatches |
| `.wrap(bool=True)` / `.rotate_title(deg)` | layout |
| `.null_text(str)` / `.blank(pred)` / `.blank_below(v)` / `.blank_above(v)` | suppress values |
| `.neg(color=, bracket=False)` / `.red_negatives(bool=True)` | negatives |
| `.highlight(color)` | tint the column |
| `.cell_style(background=, color=, border=, padding=)` | cell chrome (background may be `"@column"`) |
| `.group(label)` / `.subcolumn(label)` | header structure (dict spelling) |
| `.repeat_values(bool=True)` / `.hide(bool=True)` / `.sort_by(column)` | display |
| `.info(str)` / `.footnote(column)` | tooltip / footnote |
| `.tooltip(value=True, *, delay=None, text_delay=None)` | full values; `False` disables, `"@field"` binds text, other strings are literal; newlines and hover delays in seconds |
| `.markdown()` / `.html()` | render rich text |
| `.link(column=, *, label=, new_tab=)` / `.image(...)` / `.logo(...)` | rich cells |
| `.template(value, **formats)` | fill-in-the-blanks cell |
| `.viz(kind, **options)` | set `viz` directly |
| `.color(...)` / `.chip(...)` / `.delta(...)` / `.sparkline(...)` / `.symbols(...)` | visualisations |
| `.bar(source, …)` / `.point(source, …)` / `.range(low, high, …)` | append a mark |
| `.legend(labels=True, *, outline=False, column_names=None)` | wrapping key; optional box and automatic/explicit column headings |
| `.label(value=True \| "@field", *, source=, text=, position=, format=)` | annotate the last mark |
| `.scale(domain=(lo, hi), include_zero=, unit=, transform="linear"\|"log", axis=, axis_position=, gridlines=)` / `.reference_line(value, label=, color=)` / `.reference_band(low, high, …)` | shared axis / rules |
| `.relative(value=True)` / `.fmt_column(column)` | relative time / format source |
| `.to_config()` | the plain dict |

### Table options

`title`, `subtitle`, `caption`, `null_text`, `stub`, `stub_head`,
`footnote_marks`, `all_caps`, `stretch`, `align_decimals`, `group_gap`,
`rotate_titles`, `figure_style`, `font_size`, `footnote_column`, `footnotes`,
`info`, `info_link`, `info_link_title`, `search`, `page_size`, `sortable`,
`download`, `row_shading`, `row_lines`, `border`, `freeze_columns`, `wrap`,
`wrap_titles`, `format_titles`, `show_total_row`, `total_label`,
`total_position`, `subtotal_position`, `collapsible`, `collapsed`, `groups_open`,
`group_type`, `link`, `width`, `max_height`, `order_columns_by_group`,
`row_numbers`, `column_stats`, `compact`, `empty_message`, `empty_rows`,
`default_sort`, `row_conditional_colors`, `show_link_column`, `select`,
`header_color`, `header_font_color`, `total_row_color`, `total_font_color`,
`background_color`, `theme`, `color_scale`.

### Module functions

Data sources and constructors: `EvidentialTable`, `LiveEvidentialTable`,
`grouped_table`, `grouped_records`, `pivot_table`, `comparison_table`,
`query_table`, `simple_table`. Aggregation: `BUILTIN_AGGREGATIONS`,
`resolve_aggregation`, `apply_aggregations`. Rules: `cells_body`, `tab_style`,
`tab_format`, `text_transform`, `sub_missing`, `sub_zero`, `sub_small_vals`,
`sub_large_vals`, `sub_values`, `cols_merge`, `cols_merge_range`,
`cols_merge_uncert`, `cols_merge_n_pct`, `resolve_rules`. Helpers: `settings`,
`date_range_sql`, `make_column`, `query_values`, `section_row`, `spacer_row`,
`rows`, `Rows`,
`duck`,
`Column`, `ColumnGroup`, `CURRENCY_CODES`, `col`.

### See also

- [`docs/design-and-dx.md`](../design-and-dx.md) — the design principles.
- [`docs/technical-architecture.md`](../technical-architecture.md) — how it
  works.
- [`notebooks/`](../../notebooks) — runnable examples of every feature.
- [`docs/adr/`](../adr/README.md) — the decisions behind the API.
