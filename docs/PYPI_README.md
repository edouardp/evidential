<!-- Generated from README.md by make readme; do not edit. -->

# evidential

[![PyPI](https://img.shields.io/pypi/v/evidential.svg)](https://pypi.org/project/evidential/)
[![Python versions](https://img.shields.io/pypi/pyversions/evidential.svg)](https://pypi.org/project/evidential/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/edouardp/evidential/blob/main/LICENSE)

Evidence.dev-style interactive tables for [Marimo](https://marimo.io), packaged
as an [anywidget](https://anywidget.dev) and powered by
[DuckDB](https://duckdb.org) when you need it.

`evidential` is a **display** widget. SQL or pandas shapes the data, Python says
how to present it, and the browser renders it: sort, search, paginate, freeze
columns, group with subtotals, download CSV and open a fullscreen view.

<!-- notebook: notebooks/49_api_screenshots.py#preview image-only -->

Sections, sub-columns, footnotes, bars, colour scales and sparklines in one table.

![preview](https://raw.githubusercontent.com/edouardp/evidential/main/docs/preview.png)

[Notebook source: `preview`](https://github.com/edouardp/evidential/blob/main/notebooks/49_api_screenshots.py)

<!-- /notebook -->

> **Status:** alpha. The API may change.

## Install

```bash
uv add "evidential[marimo,duckdb]"
```

To explore the demo notebooks from a checkout:

```bash
git clone https://github.com/edouardp/evidential
cd evidential
uv sync
uv run marimo edit notebooks
```

The renderer bundle is committed, so users need no JavaScript toolchain.
Extras are `evidential[duckdb]`, `evidential[marimo]` and `evidential[studio]`
(see [`pyproject.toml`](https://github.com/edouardp/evidential/blob/main/pyproject.toml)).

## 1. Your first table

```python
from evidential import EvidentialTable

tips = [
    {"city": "Boston", "trips": 1284, "revenue": 48120.50, "tip_rate": 0.183},
    {"city": "New York", "trips": 3502, "revenue": 142880.25, "tip_rate": 0.171},
    {"city": "Chicago", "trips": 2118, "revenue": 76540.00, "tip_rate": 0.164},
    {"city": "San Francisco", "trips": 1907, "revenue": 98320.75, "tip_rate": 0.196},
    {"city": "Seattle", "trips": 1463, "revenue": 61140.10, "tip_rate": 0.188},
]

EvidentialTable(tips, title="Tipping by city")
```

Types are inferred from the data. Integers default to whole numbers (`num0`),
floats choose an auto-scaling format, dates render as dates, and lists become
sparkline input.

In Marimo, output the table directly. Wrap it with `mo.ui.anywidget(...)` only
when another cell needs to read widget state:

```python
import marimo as mo

table = mo.ui.anywidget(EvidentialTable(tips, title="Tipping by city"))
table
```

## 2. Point it at your data

`EvidentialTable` accepts a list of dicts, a pandas `DataFrame`, a PyArrow
table, or a DuckDB relation:

```python
EvidentialTable(frame)
EvidentialTable(arrow_table)
EvidentialTable(con.table("orders"))
EvidentialTable(con.sql("SELECT * FROM orders LIMIT 500"))
```

DuckDB is optional, but it makes the examples below concise:

```python
from evidential import duck

con = duck.connect()  # DuckDB with httpfs loaded
```

A DuckDB **table or view** relation carries `COMMENT ON COLUMN` text into the
header tooltip. A raw `con.sql(...)` result does not know its source; pass the
comments explicitly:

```python
from evidential import EvidentialTable, duck

comments = {name: {"info": text} for name, text in duck.column_comments(con, "orders").items()}
EvidentialTable(con.sql("SELECT * FROM orders LIMIT 500"), column_config=comments)
```

Arrow field metadata (`comment`, `description` or `info`) works the same way,
including through Parquet and Feather. You can also set a description directly:

```python
col.currency("revenue").info("Net revenue in USD")
```

For Amazon S3 Tables, use [`duck.connect_s3_tables`](https://github.com/edouardp/evidential/blob/main/docs/technical-architecture.md)
or see [`notebooks/02_s3_tables.py`](https://github.com/edouardp/evidential/blob/main/notebooks/02_s3_tables.py).

<!-- notebook: notebooks/49_api_screenshots.py#quickstart -->

## 3. Describe columns

Column descriptions are built one column at a time with `col.*`. Every factory
returns an immutable `Column`; every chain method returns a new one.

```python
columns=[
    col.text("city", title="City"),
    col.integer("trips", title="Trips"),
    col.currency("revenue", title="Revenue"),
    col.percent("tip_rate", decimals=1, title="Tip rate"),
]
```

![3. Describe columns](https://raw.githubusercontent.com/edouardp/evidential/main/docs/api/images/quickstart.png)

[Notebook source: `quickstart`](https://github.com/edouardp/evidential/blob/main/notebooks/49_api_screenshots.py)

<!-- /notebook -->

<!-- notebook: notebooks/49_api_screenshots.py#kinds -->

### Kinds

The factory chooses the kind; the chain refines it.

| Kind | Factories |
| --- | --- |
| Text | `col.text`, `col.chip`, `col.icons`, `col.flag`, `col.boolean` |
| Numbers | `col.number`, `col.integer`, `col.currency`, `col.percent` |
| Time | `col.date`, `col.time`, `col.datetime` |
| Marks | `col.bar`, `col.point`, `col.points`, `col.range`, `col.stacked_bar`, `col.strip`, `col.boxplot`, `col.distribution` |
| Values as marks | `col.color`, `col.delta`, `col.sparkline`, `col.symbols`, `col.rating`, `col.repeat` |
| Cells | `col.link` / `col.url`, `col.image`, `col.logo`, `col.markdown`, `col.html` |
| Composition | `col.group`, `col.subcolumns`, `col.merge`, `col.array`, `col.auto` |

`col.number` auto-scales. `col.currency` takes `code=` (`usd`, `eur`, `gbp`, …)
and `decimals=`. `col.percent` treats values as proportions unless
`whole=True`. Dates and times accept `relative=`.

```python
columns=[
    col.text("item", title="Item"),
    col.integer("count", title="Count"),
    col.currency("price", title="Price"),
    col.percent("share", decimals=0, title="Share"),
    col.date("day", title="Day"),
    col.flag("origin", title="Origin"),
    col.boolean("active", title="Active"),
]
```

![Kinds](https://raw.githubusercontent.com/edouardp/evidential/main/docs/api/images/kinds.png)

[Notebook source: `kinds`](https://github.com/edouardp/evidential/blob/main/notebooks/49_api_screenshots.py)

<!-- /notebook -->

### Refine a column

```python
col.currency("revenue", decimals=0).neg(bracket=True).bold()
col.percent("growth", decimals=1).delta(down_is_good=False).italic()
col.number("score").color(scale="Blues", min=0, max=100)
```

| Need | Chain methods |
| --- | --- |
| Formatting | `.fmt(code)` / `.format(code)`, `.total_fmt()`, `.subtotal_fmt()`, `.align()`, `.align_decimals()`, `.figure_style()` |
| Text | `.title()`, `.info()`, `.footnote()`, `.bold()`, `.italic()`, `.font()`, `.font_color()`, `.wrap()`, `.rotate_title()` |
| Values | `.neg()`, `.red_negatives()`, `.null_text()`, `.blank()`, `.blank_below()`, `.blank_above()`, `.highlight()`, `.cell_style()` |
| Placement | `.group()`, `.subcolumn()`, `.hide()`, `.repeat_values()`, `.sort_by()`, `.relative()`, `.fmt_column()` |
| Rich cells | `.markdown()`, `.html()`, `.link()`, `.image()`, `.logo()`, `.template()` |
| Visualisations | `.color()`, `.chip()`, `.delta()`, `.sparkline()`, `.symbols()`, `.bar()`, `.point()`, `.range()`, `.scale()`, `.label()`, `.domain()` |

`.fmt()` is the escape hatch for an exact [SSF](https://github.com/SheetJS/ssf)
code. Common presets:

```python
col.number("share").fmt("pct1")
col.number("distance").fmt("num1k")
col.currency("revenue").fmt("usd0")
col.date("month").fmt("mmm-yy")
col.number("bytes").fmt("bytes")
col.number("elapsed").fmt("duration")
col.number("rank").fmt("roman")
col.number("value").fmt("sci")       # 1.23 × 10⁵
```

`col.auto("revenue")` keeps the inferred type, format and metadata, then applies
your refinements. A `Column` is a `Mapping`, so `to_config()` returns the plain
dict and the dict form remains valid anywhere a column is accepted:

```python
columns=[col.text("city"), col.auto("revenue").font_color("#334155")]
column_config={"revenue": col.currency("revenue", decimals=0)}
```

## 4. Set the table's presentation

Use `settings(...)` for a reusable bundle. Explicit keyword arguments win over
the bundle.

```python
REPORT = settings(
    title="Monthly revenue",
    subtitle="By city and channel",
    caption="Source: orders.parquet",
    page_size=15,
    search=True,
    download=True,
    row_shading=True,
    row_lines=True,
    freeze_columns=1,
    width="900px",
    max_height="70vh",
)

EvidentialTable(tips, columns=[...], settings=REPORT, title="This month")
```

| Goal | Options |
| --- | --- |
| Frame and type | `title`, `subtitle`, `caption`, `info`, `info_link`, `width`, `max_height`, `border`, `compact`, `font_size`, `theme`, `header_color`, `header_font_color`, `background_color` |
| Columns | `freeze_columns`, `wrap`, `wrap_titles`, `format_titles`, `stretch`, `order_columns_by_group`, `column_stats`, `align_decimals`, `figure_style`, `rotate_titles` |
| Interaction | `search`, `sortable`, `page_size`, `download`, `row_numbers`, `default_sort`, `select` |
| Rows | `row_shading`, `row_lines`, `group_gap`, `stub`, `stub_head`, `null_text` |
| Groups and totals | `show_total_row`, `total_label`, `total_position`, `subtotal_position`, `collapsible`, `collapsed`, `groups_open`, `group_type` |

The [API reference](https://github.com/edouardp/evidential/blob/main/docs/api/API.md#table-options) lists every option and value.

<!-- notebook: notebooks/49_api_screenshots.py#visualizations -->

## 5. Add visualisations

A visualisation presents the underlying value; sorting, search, statistics and
CSV export still use the raw value.

```python
columns=[
    col.text("region", title="Region"),
    col.bar("revenue", title="Revenue"),
    col.bar("growth", center=True, title="Growth"),
    col.color("share", title="Share"),
    col.chip("region", title="Chip"),
    col.sparkline("trend", type="area", title="Trend"),
    col.percent("growth", decimals=0, title="Δ").delta(),
]
```

![5. Add visualisations](https://raw.githubusercontent.com/edouardp/evidential/main/docs/api/images/visualizations.png)

[Notebook source: `visualizations`](https://github.com/edouardp/evidential/blob/main/notebooks/49_api_screenshots.py)

<!-- /notebook -->

### Graphic gallery

Every graphic type, with the Python that builds it. The images come from
[`notebooks/50_graphics_gallery.py`](https://github.com/edouardp/evidential/blob/main/notebooks/50_graphics_gallery.py), captured
together with these descriptions and code excerpts by `make readme`.

<!-- notebook: notebooks/50_graphics_gallery.py#graphic_bar -->

#### Bar

Labels prefer the outside end, moving inside when space is tight.

```python
columns=[
    col.text("region"),
    col.bar("sales", format="usd0", label=label.auto_position("outside end"), title="Sales"),
]
```

![Bar](https://raw.githubusercontent.com/edouardp/evidential/main/docs/img/graphics/bar.png)

[Notebook source: `graphic_bar`](https://github.com/edouardp/evidential/blob/main/notebooks/50_graphics_gallery.py)

<!-- /notebook -->

<!-- notebook: notebooks/50_graphics_gallery.py#graphic_bar_centered -->

#### Centered bar

Positive and negative values extend from zero on a shared scale.

```python
columns=[
    col.text("team"),
    col.bar("change", center=True, format="pct1", label=True, title="Change").scale(
        domain=(-0.2, 0.2), axis=True, axis_position="bottom"
    ),
]
```

![Centered bar](https://raw.githubusercontent.com/edouardp/evidential/main/docs/img/graphics/bar-centered.png)

[Notebook source: `graphic_bar_centered`](https://github.com/edouardp/evidential/blob/main/notebooks/50_graphics_gallery.py)

<!-- /notebook -->

<!-- notebook: notebooks/50_graphics_gallery.py#graphic_bar_overlay -->

#### Overlaid bars with a target

Layer the current value over the previous value, then mark the target.

```python
columns=[
    col.text("party"),
    col.bar("previous", format="num0", color="#d1d5db", size=0.85)
    .bar("current", format="num0", color="@colour", size=0.45, label=label.position("inside end"), title="Current vs previous")
    .point("target", color="#0f766e", size=7)
    .scale(domain=(0, 45)),
]
```

![Overlaid bars with a target](https://raw.githubusercontent.com/edouardp/evidential/main/docs/img/graphics/bar-overlay.png)

[Notebook source: `graphic_bar_overlay`](https://github.com/edouardp/evidential/blob/main/notebooks/50_graphics_gallery.py)

<!-- /notebook -->

<!-- notebook: notebooks/50_graphics_gallery.py#graphic_bar_back_to_back -->

#### Back-to-back bars

Mirror two measures around a shared text column.

```python
columns=[
    col.bar(
        "spend",
        format="usd1",
        direction="left",
        color="@color",
        label=label.auto_position("outside end"),
        pad=3,
        title="Sales per capita",
    ).align("left"),
    col.text("country", title=""),
    col.bar(
        "rate",
        format="num2",
        color="@color",
        label=label.auto_position("outside end"),
        pad=3,
        title="Foreign-to-Canadian rate",
    ).align("right"),
    col.auto("color").hide(),
]
```

![Back-to-back bars](https://raw.githubusercontent.com/edouardp/evidential/main/docs/img/graphics/bar-back-to-back.png)

[Notebook source: `graphic_bar_back_to_back`](https://github.com/edouardp/evidential/blob/main/notebooks/50_graphics_gallery.py)

<!-- /notebook -->

<!-- notebook: notebooks/50_graphics_gallery.py#graphic_color -->

#### Color scale

Encode the score as a background colour while keeping its numeric value.

```python
columns=[
    col.text("region"),
    col.number("score", fmt="num0").color(scale="Blues", min=0, max=100).title("Score"),
]
```

![Color scale](https://raw.githubusercontent.com/edouardp/evidential/main/docs/img/graphics/color.png)

[Notebook source: `graphic_color`](https://github.com/edouardp/evidential/blob/main/notebooks/50_graphics_gallery.py)

<!-- /notebook -->

<!-- notebook: notebooks/50_graphics_gallery.py#graphic_chip -->

#### Chip

Use chips for categories or a numeric colour scale.

```python
columns=[
    col.text("service"),
    col.chip("status", min_width=84, title="Status"),
    col.number("latency", fmt="num0").chip(scale="red", min=0, max=500).title("Latency (ms)"),
]
```

![Chip](https://raw.githubusercontent.com/edouardp/evidential/main/docs/img/graphics/chip.png)

[Notebook source: `graphic_chip`](https://github.com/edouardp/evidential/blob/main/notebooks/50_graphics_gallery.py)

<!-- /notebook -->

<!-- notebook: notebooks/50_graphics_gallery.py#graphic_delta -->

#### Delta

Treat changes within the neutral range as steady, with optional chip backgrounds.

```python
columns=[
    col.text("metric"),
    col.percent("change", decimals=1, title="Change").delta(down_is_good=False, neutral_range="-0.02:0.02"),
    col.percent("change", decimals=1, title="As a chip").delta(
        down_is_good=False, neutral_range="-0.02:0.02", chip=True
    ),
]
```

![Delta](https://raw.githubusercontent.com/edouardp/evidential/main/docs/img/graphics/delta.png)

[Notebook source: `graphic_delta`](https://github.com/edouardp/evidential/blob/main/notebooks/50_graphics_gallery.py)

<!-- /notebook -->

<!-- notebook: notebooks/50_graphics_gallery.py#graphic_sparklines -->

#### Sparklines

Show a series as a line, area, bars, points or increase/steady/decrease marks.

```python
columns=[
    col.text("series"),
    col.sparkline("line", type="line", width=110, height=30, title="Line"),
    col.sparkline("area", type="area", fit_to_data=True, width=110, height=30, title="Area"),
    col.sparkline("bar", type="bar", width=110, height=30, title="Bar"),
    col.sparkline("points", type="points", width=110, height=30, markers=True, title="Points"),
    col.sparkline("change", type="change", width=110, height=30, title="Change"),
]
```

![Sparklines](https://raw.githubusercontent.com/edouardp/evidential/main/docs/img/graphics/sparklines.png)

[Notebook source: `graphic_sparklines`](https://github.com/edouardp/evidential/blob/main/notebooks/50_graphics_gallery.py)

<!-- /notebook -->

<!-- notebook: notebooks/50_graphics_gallery.py#graphic_symbols -->

#### Symbols and rating

Repeat glyphs or shapes for counts, or show a five-point rating.

```python
columns=[
    col.text("country"),
    col.symbols("gold", symbol="■", color="#d97706", title="Glyph"),
    col.symbols("gold", shape="square", color="#d97706", title="Squares"),
    col.rating("score", title="Rating"),
]
```

![Symbols and rating](https://raw.githubusercontent.com/edouardp/evidential/main/docs/img/graphics/symbols.png)

[Notebook source: `graphic_symbols`](https://github.com/edouardp/evidential/blob/main/notebooks/50_graphics_gallery.py)

<!-- /notebook -->

<!-- notebook: notebooks/50_graphics_gallery.py#graphic_boolean_icons -->

#### Boolean, icons and flags

Render booleans, mapped icons and country flags.

```python
columns=[
    col.text("feature"),
    col.boolean("active", true_symbol="✓", false_symbol="✗", title="Active"),
    col.icons("signal", map={"up": "▲", "flat": "●", "down": "▼"}, title="Signal"),
    col.flag("country", title="Country"),
]
```

![Boolean, icons and flags](https://raw.githubusercontent.com/edouardp/evidential/main/docs/img/graphics/boolean-icons.png)

[Notebook source: `graphic_boolean_icons`](https://github.com/edouardp/evidential/blob/main/notebooks/50_graphics_gallery.py)

<!-- /notebook -->

<!-- notebook: notebooks/50_graphics_gallery.py#graphic_dumbbell -->

#### Dumbbell: range plus points

Connect two values, colour decreases red and add a direction chevron.

```python
columns=[
    col.text("country"),
    col.range("before", "after", color="#222222", color_negative="#cc1111", size=2, direction_marker=True)
       .point("before", color="#6699ee", outline="#2f5fa8", size=12)
       .point("after", color="#ff6666", outline="#cc1111", size=12)
       .title("Before → after")
       .align("center")
       .scale(domain=(0, 100), axis=True, axis_position="bottom"),
]
```

![Dumbbell: range plus points](https://raw.githubusercontent.com/edouardp/evidential/main/docs/img/graphics/dumbbell.png)

[Notebook source: `graphic_dumbbell`](https://github.com/edouardp/evidential/blob/main/notebooks/50_graphics_gallery.py)

<!-- /notebook -->

<!-- notebook: notebooks/50_graphics_gallery.py#graphic_points -->

#### Points from an array

Plot every sample on one horizontal scale, with transparent marks for overlap.

```python
columns=[
    col.text("metric"),
    col.points("samples", color="#2563eb30", size=9, outline=False, title="Samples").scale(
        domain=(0, 60), axis=True, axis_position="bottom"
    ),
]
```

![Points from an array](https://raw.githubusercontent.com/edouardp/evidential/main/docs/img/graphics/points.png)

[Notebook source: `graphic_points`](https://github.com/edouardp/evidential/blob/main/notebooks/50_graphics_gallery.py)

<!-- /notebook -->

<!-- notebook: notebooks/50_graphics_gallery.py#graphic_boxplot -->

#### Box plot

Show quartiles, a median, whiskers and outliers.

```python
columns=[
    col.text("group"),
    col.boxplot("lo", "q1", "med", "q3", "hi", outliers="outs", whisker="iqr", title="Spread").scale(
        domain=(0, 32), axis=True, axis_position="bottom"
    ),
]
```

![Box plot](https://raw.githubusercontent.com/edouardp/evidential/main/docs/img/graphics/boxplot.png)

[Notebook source: `graphic_boxplot`](https://github.com/edouardp/evidential/blob/main/notebooks/50_graphics_gallery.py)

<!-- /notebook -->

<!-- notebook: notebooks/50_graphics_gallery.py#graphic_distribution -->

#### Distribution band

Draw a density band with a median point.

```python
columns=[
    col.text("name"),
    col.distribution("curve", x="x", y="pdf", color="@ink")
    .point("median", color="#111111", outline=False)
    .title("Density")
    .align("center")
    .scale(domain=(0, 100), axis=True, axis_position="bottom"),
]
```

![Distribution band](https://raw.githubusercontent.com/edouardp/evidential/main/docs/img/graphics/distribution.png)

[Notebook source: `graphic_distribution`](https://github.com/edouardp/evidential/blob/main/notebooks/50_graphics_gallery.py)

<!-- /notebook -->

<!-- notebook: notebooks/50_graphics_gallery.py#graphic_stacked_bar -->

#### Stacked bar

Stack components and label them within the bar.

```python
columns=[
    col.text("region"),
    col.stacked_bar(
        "new",
        "renewal",
        "expansion",
        colors=["#2563eb", "#60a5fa", "#bfdbfe"],
        labels=True,
        format="num0",
        size=0.6,
        title="New · Renewal · Expansion",
    ),
]
```

![Stacked bar](https://raw.githubusercontent.com/edouardp/evidential/main/docs/img/graphics/stacked-bar.png)

[Notebook source: `graphic_stacked_bar`](https://github.com/edouardp/evidential/blob/main/notebooks/50_graphics_gallery.py)

<!-- /notebook -->

<!-- notebook: notebooks/50_graphics_gallery.py#graphic_stack_likert -->

#### Diverging Likert stack

Split neutral responses around zero and label the normalised shares.

```python
columns=[
    col.text("question"),
    col.stacked_bar(
        "sd",
        "d",
        "n",
        "a",
        "sa",
        colors=["#b91c1c", "#fca5a5", "#e5e7eb", "#86efac", "#16a34a"],
        labels="percent",
        label_align="begin",
        diverge_at="n",
        neutral="split",
        normalize="percent",
        size=1,
        title="Response",
    ),
]
```

![Diverging Likert stack](https://raw.githubusercontent.com/edouardp/evidential/main/docs/img/graphics/stack-likert.png)

[Notebook source: `graphic_stack_likert`](https://github.com/edouardp/evidential/blob/main/notebooks/50_graphics_gallery.py)

<!-- /notebook -->

<!-- notebook: notebooks/50_graphics_gallery.py#graphic_strip -->

#### Strip

Display an ordered sequence of categorical outcomes.

```python
columns=[
    col.text("team"),
    col.strip("form", colors={"W": "#16a34a", "D": "#9ca3af", "L": "#dc2626"}, labels=True).title("Form"),
]
```

![Strip](https://raw.githubusercontent.com/edouardp/evidential/main/docs/img/graphics/strip.png)

[Notebook source: `graphic_strip`](https://github.com/edouardp/evidential/blob/main/notebooks/50_graphics_gallery.py)

<!-- /notebook -->

<!-- notebook: notebooks/50_graphics_gallery.py#graphic_reference -->

#### Axis, reference line and band

Add an external axis, gridlines, a target line and a reference band.

```python
columns=[
    col.text("team"),
    col.bar("score", format="num0", label=label.auto_position("outside end"), title="Score")
    .scale(domain=(0, 100), axis=True, axis_position="bottom", gridlines=True)
    .reference_band(60, 80, color="#fef3c7")
    .reference_line(70, color="#dc2626"),
]
```

![Axis, reference line and band](https://raw.githubusercontent.com/edouardp/evidential/main/docs/img/graphics/reference.png)

[Notebook source: `graphic_reference`](https://github.com/edouardp/evidential/blob/main/notebooks/50_graphics_gallery.py)

<!-- /notebook -->

### Labels and shared domains

```python
from evidential import col, domain, label

annotation = label.fmt("usd0").bold().auto_position("inside end")

payments = domain.numeric("payments").include_zero().palette("Blues")

columns=[
    col.bar("card", label=annotation).domain(payments),
    col.number("cash").color().domain("payments"),
]
```

A label can show the mark's value, another field (`label="@candidate"`), or fixed
text. A named domain pools values across columns so bars, heatmaps and
sparklines share one scale and palette. See
[`notebooks/47_shared_domains.py`](https://github.com/edouardp/evidential/blob/main/notebooks/47_shared_domains.py).

<!-- notebook: notebooks/49_api_screenshots.py#subcolumns -->

## 6. Build header structures

`col.subcolumns(label, [...])` gives its members one shared leaf header.
`col.group(label, [...])` adds a spanner over a run of columns. Both nest.
A column named `"GDP Measure.GDP nominal"` groups under **GDP Measure**
automatically; `column_groups={...}` is the equivalent mapping form.

```python
columns=[
    col.text("country", title="Country"),
    col.group(
        "Gross domestic product",
        [
            col.subcolumns(
                "Latest",
                [
                    col.number("gdp", fmt="num1", align="right").neg(),
                    col.auto("quarter").align("left").font_color("#94a3b8"),
                ],
            ),
            col.number("forecast", fmt="num1", align="right", title="Annual forecast"),
        ],
    ),
    col.group(
        "Consumer prices",
        [
            col.subcolumns(
                "Latest",
                [
                    col.number("cpi", fmt="num1", align="right").neg(),
                    col.auto("month").align("left").font_color("#94a3b8"),
                ],
            )
        ],
    ),
]
```

![6. Build header structures](https://raw.githubusercontent.com/edouardp/evidential/main/docs/api/images/subcolumns.png)

[Notebook source: `subcolumns`](https://github.com/edouardp/evidential/blob/main/notebooks/49_api_screenshots.py)

<!-- /notebook -->

The `stub` setting marks row-label columns, and `stub_head` labels the stub:

```python
settings(stub="country", stub_head="Country")
```

## 7. Derive values and add display rules

Merged columns build one cell from several source columns:

```python
from evidential import col, cols_merge_n_pct, cols_merge_range, cols_merge_uncert

columns=[
    col.text("site"),
    col.merge("range", cols_merge_range("low", "high", fmt="num0", title="Range")),
    col.merge("measurement", cols_merge_uncert("value", "uncert", fmt="num1")),
    col.merge("share", cols_merge_n_pct("n", "pct", title="Share")),
]
```

Display rules transform values at render time. Rules run in order; the last
match wins.

```python
from evidential import cells_body, tab_format, tab_style, text_transform

EvidentialTable(
    tips,
    columns=[col.text("city"), col.currency("revenue"), col.percent("tip_rate")],
    rules=[
        text_transform(cells_body("city"), str.upper),
        tab_style(cells_body("revenue"), color="#b45309"),
        tab_format(cells_body("revenue"), "usd0"),
    ],
)
```

Substitutions are also rules: `sub_missing`, `sub_zero`, `sub_small_vals`,
`sub_large_vals` and `sub_values`. Location selectors accept column names and
either 0-based row indices or a Python predicate.

## Presentation parts

A table also has a frame, notes and optional dividers:

- `section_row("Label")` / `spacer_row()` create display-only rows in `rows`.
- `col.text("product").footnote("note")` marks cells; `footnotes=[...]` adds
  static notes, and `footnote_marks="numbers"|"letters"|"symbols"` chooses the
  mark scheme.
- `caption=...` adds source notes; `stub` / `stub_head` define row labels.
- `column_stats=True` adds min/max/avg/null under each header.
- `null_text`, `.blank_below`, `.blank_above` and `.blank(...)` control missing
  values.

## 8. Group, pivot and compare

The aggregate helpers accept the same `col.*` builders, run their aggregation
in DuckDB, and return a normal `EvidentialTable`.

<!-- notebook: notebooks/49_api_screenshots.py#grouped_totals -->

### Grouped totals

Group the sample orders by category, with sales and order counts. The helper
adds subtotals and a grand total. `sample_orders()` opens the bundled fixture
in DuckDB; its definition lives in the notebook.

```python
grouped_table(
    sample_orders(),
    "SELECT category AS category, sales FROM needful_things.orders",
    dimensions=["category"],
    measures=["round(sum(sales), 0) AS sales", "count(*) AS orders"],
    dimension_config={"category": col.text("category")},
    measure_config={
        "sales": col.currency("sales", decimals=0),
        "orders": col.integer("orders"),
    },
    settings=settings(title="Grouped totals", page_size=10, width="560px"),
)
```

![Grouped totals](https://raw.githubusercontent.com/edouardp/evidential/main/docs/api/images/grouped-table.png)

[Notebook source: `grouped_totals`](https://github.com/edouardp/evidential/blob/main/notebooks/49_api_screenshots.py)

<!-- /notebook -->

### Aggregations for subtotals/totals

`aggregations={"sales": "mean"}` recomputes subtotals from detail values with a
built-in name or a Python callable. Use `weight_columns={"sales": "weight"}`
for weighted means.

<!-- notebook: notebooks/49_api_screenshots.py#pivoted_columns -->

### Pivot, compare and query

Turn each year into a column group, with one row per category. This example
uses the same `sample_orders()` fixture connection as the grouped table.

```python
pivot_table(
    sample_orders(),
    "SELECT category, year(order_datetime) AS year, sales FROM needful_things.orders",
    dimensions=["category"],
    pivots=["year"],
    measures=["round(sum(sales), 0) AS sales"],
    dimension_config={"category": col.text("category")},
    measure_config={"sales": col.currency("sales", decimals=0)},
    settings=settings(title="Pivoted columns", page_size=10, width="640px"),
)
```

![Pivot, compare and query](https://raw.githubusercontent.com/edouardp/evidential/main/docs/api/images/pivot-table.png)

[Notebook source: `pivoted_columns`](https://github.com/edouardp/evidential/blob/main/notebooks/49_api_screenshots.py)

<!-- /notebook -->

```python
from evidential import comparison_table, query_table

# Adds <measure>_prior, <measure>_delta and <measure>_pct columns.
comparison_table(
    con,
    "SELECT region, order_date, sales FROM orders",
    dimensions=["region"],
    measures=["sum(sales) AS sales"],
    date_column="order_date",
    compare_vs="prior year",
)

# Ad-hoc SQL with Evidence-style where / order / limit / date_range.
query_table(
    con,
    "SELECT * FROM orders",
    where="sales > 0",
    order="sales DESC",
    limit=100,
    date_range="last 30 days",
    date_column="order_date",
)
```

For rows already in Python, `grouped_records(rows, group_by=..., measures=...)`
does the same grouping without a database.

### Display-only headings and summaries

`rows` adds headings and summaries without making them source records.

```python
from evidential import EvidentialTable, col, rows

layout = (
    rows.group_by("region")
    .section(values={"category": rows.count(suffix=" products"), "sales": "sum"})
    .summary("Region total", values={"sales": "sum"})
    .grand_summary("All regions", values={"sales": "sum"})
)

EvidentialTable(
    products,
    row_layout=layout,
    columns=[col.text("product"), col.text("category"), col.bar("sales", format="usd2")],
    page_size=3,
    section_indent=1,
)
```

Search recalculates named aggregations; a callable keeps its source scope until
the next `set_data`. `table.rows` contains details only, while
`table.display_rows` is an inspection snapshot that includes synthetic rows.
`rows.of(products).group_by("region").summary(...).build()` returns a view that
can be passed directly to `EvidentialTable`.

## 9. Live tables and row selection

`LiveEvidentialTable` re-runs a parameterised query without recreating the
widget, so sort, search and page state survive.

```python
from evidential import LiveEvidentialTable, col

# 1. controls
min_fare = mo.ui.slider(0, 80, value=10, label="Minimum fare")
min_fare

# 2. persistent widget: no control references in this cell
live = LiveEvidentialTable(
    con,
    "SELECT * FROM trips WHERE fare_amount >= {min_fare}",
    auto_run=False,
    columns=[col.number("fare_amount", fmt="usd2"), col.number("trip_distance", fmt="num1")],
)
live

# 3. reactive cell: re-runs whenever the slider changes
_ = live.set_controls(min_fare=min_fare)
```

Values are bound as SQL parameters, never spliced into the SQL text. Outside a
reactive host, `bind_controls=True` makes the widget re-run itself.
`query_values(con, sql)` returns one column as a list for populating selectors.

> The cell that creates the widget must not reference a control. Referencing one
> registers a Marimo dependency and recreates the widget on every change.

Set `select="country_code"` to make rows clickable. The clicked value crosses to
Python through the widget's `selected` trait:

```python
countries = mo.ui.anywidget(
    EvidentialTable(
        rows,
        columns=[col.text("country"), col.integer("population")],
        select="country_code",
        empty_message="Click a country",
    )
)
countries
```

```python
# another cell
selected = countries.widget.selected
detail.widget.set_data(con.sql(detail_sql, params={"code": selected or ""}))
```

`set_data` keeps the widget and its layout in place; `update_options` and
`set_column` change presentation without rebuilding it.

<!-- notebook: notebooks/21_studio_dashboard.py#revenue_table -->

## 10. Marimo Studio views

A [marimo Studio](https://marimo.io/blog/introducing-marimo-studio) view
projects named cells from a notebook, so one table can back a dashboard, report
or slide deck. This is the table from the Studio demo; its view projects the
same `revenue_table` cell alongside KPIs and a region filter.

```html
<marimo-cell name="revenue_table"></marimo-cell>
<strong mo-value="kpis.revenue"></strong>
```

```console
make studio-serve
make studio-validate
```

The interactive table uses Studio's **Server** runtime. See
[the Studio guide](https://github.com/edouardp/evidential/blob/main/docs/marimo-studio.md) for the full dashboard view.
The table's column configuration is:

```python
columns=[
    col.text("region", title="Region"),
    col.text("city", title="City"),
    col.integer("trips", title="Trips"),
    col.bar("revenue", title="Revenue", format='usd0', label=True),
    col.percent("tip_rate", decimals=1, title="Tip rate").color(
        scale=["#fee2e2", "#fef9c3", "#bbf7d0", "#15803d"], min=0, max=0.35
    ),
]
```

![10. Marimo Studio views](https://raw.githubusercontent.com/edouardp/evidential/main/docs/img/studio-table.png)

[Notebook source: `revenue_table`](https://github.com/edouardp/evidential/blob/main/notebooks/21_studio_dashboard.py)

<!-- /notebook -->

## 11. Amazon S3 Tables

```python
from evidential import duck

con = duck.connect_s3_tables(table_bucket_arn="arn:aws:s3tables:...:bucket/...")
con.sql("SELECT * FROM s3tables.taxi.yellow_trips LIMIT 100")
```

This attaches an Iceberg REST catalog using ambient AWS credentials. See
[`notebooks/02_s3_tables.py`](https://github.com/edouardp/evidential/blob/main/notebooks/02_s3_tables.py).

## Compatibility

The fluent API is the preferred surface, but the older spellings still work:

- `column_config={"revenue": {"fmt": "usd0"}}` is merged onto inferred columns.
- Raw `viz="bar"` dictionaries are accepted.
- `column_groups={...}` remains the mapping form of `col.group(...)`.
- `fmt=` and `format=` are equivalent; the same applies to the other alias pairs
  listed in the [API reference](https://github.com/edouardp/evidential/blob/main/docs/api/API.md#consistent-option-names-and-updates).

The scalar `col.number(...).bar()` shortcut was removed. Use the mark factory:

```python
col.bar("sales", format="usd0", label=True)
```

## Reference

- [API reference](https://github.com/edouardp/evidential/blob/main/docs/api/API.md) — the full factory, chain, mark, settings and
  module reference, with screenshots.
- [Design & DX](https://github.com/edouardp/evidential/blob/main/docs/design-and-dx.md) — why the table works the way it does.
- [Technical architecture](https://github.com/edouardp/evidential/blob/main/docs/technical-architecture.md) — wire format, render
  pipeline and diagrams.
- [marimo Studio views](https://github.com/edouardp/evidential/blob/main/docs/marimo-studio.md) — projections and troubleshooting.
- [ADRs](https://github.com/edouardp/evidential/blob/main/docs/adr/README.md) — the decisions behind the API.
- [`notebooks/`](https://github.com/edouardp/evidential/blob/main/notebooks/README.md) — runnable examples of every feature.

The public surface is re-exported from `evidential`:

| Import | Purpose |
| --- | --- |
| `EvidentialTable`, `LiveEvidentialTable` | tables and live queries |
| `col`, `label`, `domain`, `rows` | column, annotation, scale and row-layout builders |
| `settings`, `TableOptions`, `ColumnOptions` | typed table and column configuration |
| `grouped_table`, `grouped_records`, `pivot_table`, `comparison_table`, `query_table` | aggregate and query helpers |
| `cells_body`, `tab_style`, `tab_format`, `text_transform`, `sub_*`, `cols_merge_*` | display rules and merged values |
| `duck`, `query_values`, `date_range_sql` | DuckDB and query utilities |

## Development

```bash
make install            # Python and JavaScript dependencies
make install-hooks      # pre-commit hooks
make lint               # ruff · bandit · pip-audit · pyrefly · shellcheck · checkmake · rumdl
make format             # auto-fix formatting and lint issues
make test               # Python tests (with coverage) and JavaScript tests
make test-browser       # Playwright functional tests
make check-notebooks    # marimo check on every notebook
make check-artifact     # build a wheel/sdist and verify their contents
make validate           # lint + notebook checks + tests + bundle check + build
make readme             # generate README examples and capture notebook tables
make readme-check       # detect stale text/images without launching a browser
make frontend-build     # rebuild static/table.js and static/table.css
```

The gates are mirrored in [`.pre-commit-config.yaml`](https://github.com/edouardp/evidential/blob/main/.pre-commit-config.yaml)
(on commit) and [`scripts/lint.sh`](https://github.com/edouardp/evidential/blob/main/scripts/lint.sh) (local validation).
`tests/release/` checks the repository workflow itself, including that the wheel
contains the committed renderer assets.

Descriptions, column snippets and images in the illustrated table examples
come from the same named notebook cells. Edit those notebooks rather than the
generated README regions. See [the authoring guide](https://github.com/edouardp/evidential/blob/main/docs/notebook-documentation.md).

For a release, run `make release` to choose patch, minor or major, or use
`make release-minor` (and the corresponding patch/major targets).
`make release VERSION=0.2.0rc1` selects an exact version. The release checks
README/image freshness before changing the version, opens `CHANGELOG.md` in
`$EDITOR`, validates locally, publishes through the keyring, and creates the
GitHub release. See [the release process](https://github.com/edouardp/evidential/blob/main/docs/RELEASE_PROCESS.md).

## Relationship to Evidence

This is a focused reimplementation for the Python/Marimo ecosystem. Formatting
presets, colour-scale maths and table presentation are ported from Evidence's
`formatValue`, `table-viz`, `table-styles` and `color-scale-utils` modules.
Evidence is MIT licensed; the same license applies here.

## License

MIT.
