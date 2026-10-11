# marimo-evidence-tables

Evidence.dev-style interactive data tables for [Marimo](https://marimo.io),
packaged as an [anywidget](https://anywidget.dev) and powered by
[DuckDB](https://duckdb.org).

The goal is to bring the flexibility of Evidence's `DataTable` to Python
notebooks: rich cell formatting, conditional bars/colours/sparklines/deltas,
collapsible grouped subtotals, frozen columns, search, pagination, CSV export
and a fullscreen view — all driven from ordinary Python data.

![EvidenceTable renderer preview](docs/preview.png)

Click the expand button (⛶) to fill the browser viewport. The expanded dialog
recomputes the page size to fit the available height (and re-fits on resize,
restoring your configured `page_size` on exit). It uses an opaque `Canvas`
surface (so it follows light/dark mode) over a dimmed backdrop, and can be
themed with `theme={"surface": "#0b1220"}`.

![EvidenceTable fullscreen](docs/fullscreen.png)

## Features

- **Rich formatting** — Excel-style format codes via `ssf` (`usd2`, `pct1`,
  `num0k`, `mmm-yy`, `#,##0.0`, …) plus auto-scaling `num`/`usd`/`eur`/`pct`
  base formats that pick units (`k`, `M`, `B`) from the data range.
- **Conditional visualisations** — `viz="bar"`, `viz="color"` (heatmap with
  custom colour scales, stops, midpoints and conditional-colour columns),
  `viz="sparkline"` (line/area/bar from an array in a cell, incl.
  `ARRAY_AGG({'date': ..., 'value': ...})`), and `viz="delta"`.
- **Grouped tables** — `grouped_table` runs one DuckDB `GROUPING SETS` query
  and produces collapsible groups, subtotals and a grand total.
- **Hierarchical columns** — `column_groups={"Payment type": ["credit_card",
  "cash"]}` wraps columns under shared headers and clusters them together.
- **Live tables** — `LiveEvidenceTable` re-runs a parameterised query when its
  controls change, preserving sort/search/page state.
- **Interaction** — 3-state column sorting, search, pagination (press and hold
  the prev/next buttons: after 700ms it pages every 700ms, easing to every
  100ms by 3 seconds), row links, clickable rows, sticky/frozen columns,
  resizable fullscreen dialog and CSV download.
- **Presentation** — titles/subtitles, column groups, row shading, row lines,
  text wrapping, red-negative values and per-column alignment.
- **Data sources** — Arrow tables, pandas DataFrames, DuckDB relations, plain
  records, and S3 Tables (Iceberg REST) through DuckDB.

## Install

```bash
uv sync --extra dev          # Python + test dependencies
make frontend-install        # JavaScript build/test dependencies
make frontend-build          # bundle table.js / table.css into the package
```

The repository uses [`uv`](https://docs.astral.sh/uv/). `make` with no
arguments lists every available target.

## Quick start

```python
import duckdb
from evidence_tables import EvidenceTable

con = duckdb.connect()
con.execute("INSTALL httpfs; LOAD httpfs;")
con.execute(
    """
    CREATE VIEW trips AS SELECT * FROM read_parquet(
        'https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-01.parquet'
    )
    """
)

EvidenceTable(
    con.sql("SELECT * FROM trips LIMIT 5000"),
    title="Recent yellow taxi trips",
    search=True,
    page_size=15,
    row_shading=True,
    freeze_columns=2,
    column_config={
        "trip_distance": {"fmt": "num1", "viz": "bar"},
        "fare_amount": {"fmt": "usd2"},
        "tip_rate": {
            "fmt": "pct1",
            "viz": "color",
            "color_scale": ["#fee2e2", "#fef9c3", "#bbf7d0", "#15803d"],
            "color_options": {"midpoint": 0.15, "min": 0, "max": 0.4},
        },
    },
)
```

In Marimo, display the widget directly or wrap it with
`mo.ui.anywidget(EvidenceTable(...))` when you want to read state back.

## Grouped tables with subtotals

`grouped_table` builds the SQL for you. Pass a base query, the dimensions to
group by, and aggregate expressions:

```python
from evidence_tables import grouped_table

grouped_table(
    con,
    "SELECT * FROM trips",
    dimensions=["payment", "is_weekend"],
    measures=[
        "count(*) AS trips",
        "round(sum(total_amount), 0) AS revenue",
        "round(avg(tip_rate) * 100, 1) AS avg_tip_pct",
    ],
    total_label="All trips",
    subtotal_position="top",
    title="Trips by payment type",
    collapsible=True,
    dimension_config={"is_weekend": {"title": "Weekend"}},
    measure_config={
        "revenue": {"fmt": "usd0", "viz": "bar"},
        "avg_tip_pct": {"title": "Avg tip %", "fmt": "num1"},
    },
)
```

Measures may be strings (`"sum(x) AS total"`), `(alias, expression)` tuples, or
`{alias: expression}` mappings. The resulting table is a normal `EvidenceTable`
with `render_type` (`cell_data` / `row_subtotal` / `row_total`) and grouping
metadata on each row.

### Aggregations for subtotals/totals

By default subtotals re-run the measure's SQL aggregate. `aggregations`
recomputes them from the detail values (Evidence's `totalAgg`) using built-in
names or any Python callable:

```python
import statistics
from evidence_tables import grouped_table, BUILTIN_AGGREGATIONS

grouped_table(con, sql, ["category", "item"], ["sum(sales) AS sales"],
              aggregations={"sales": "mean"})        # sum, mean, median, min,
                                                     # max, count, count_distinct,
                                                     # weighted_mean

grouped_table(..., aggregations={"sales": statistics.median})
grouped_table(..., aggregations={"sales": lambda values: max(values) - min(values)})
grouped_table(..., aggregations={"sales": "weighted_mean"},
              weight_columns={"sales": "weight"})
```

`total_measures={"sales": "avg(sales)"}` is also available for a direct SQL
override of the grand total. See `notebooks/14_aggregations.py`.

## Live, parameterised tables

`LiveEvidenceTable` keeps a parameterised query and re-runs it when its
controls change, without recreating the widget — so sort, search and page state
survive. In Marimo, keep the widget persistent and let a reactive cell drive it:

```python
# controls
min_fare = mo.ui.slider(0, 80, value=10, label="Minimum fare")
min_fare

# persistent widget (created once; no control references)
live = LiveEvidenceTable(
    con,
    "SELECT * FROM trips WHERE fare_amount >= {min_fare}",
    auto_run=False,
)
live

# reactive cell: re-runs whenever the slider changes
_ = live.set_controls(min_fare=min_fare)
```

Values from `params` / `set_controls` are bound as SQL parameters, never spliced
into the SQL text. Updates run in place: fast queries swap the rows in without
flashing, while slow ones keep the current table on screen and fade it into a
dimmed “Processing…” state over 0.6s, then reveal the new data immediately. The
table keeps a stable height throughout.

Outside a reactive host, `bind_controls=True` makes the widget re-run itself on
control changes. `query_values(con, sql)` returns one column as a list, handy
for populating dropdowns/multiselects from dimension queries. See
`notebooks/03_live_drilldown.py` and `notebooks/04_live_demo.py`.

> **Important:** the cell that creates the widget must **not** reference the
> controls. Referencing a control registers a Marimo dependency, so wrapping
> the widget and its controls in the same `mo.vstack([controls, live])` makes
> that cell re-run on every change and recreate the widget — the table then
> disappears and reappears. Display controls in their own cell instead.

## Amazon S3 Tables

`evidence_tables.duck` can attach an S3 Tables Iceberg catalog to DuckDB using
your ambient AWS credentials:

```python
from evidence_tables import duck

con = duck.connect_s3_tables(table_bucket_arn="arn:aws:s3tables:...:bucket/...")
con.sql("SELECT * FROM s3tables.taxi.yellow_trips LIMIT 100")
```

See `notebooks/02_s3_tables.py` for a full example (it gracefully stops if
`S3TABLES_TABLE_BUCKET_ARN` is not set).

## API

### `EvidenceTable(data=..., *, columns=None, column_config=None, column_groups=None, **options)`

- `data`: records, Arrow table, pandas DataFrame, or DuckDB relation.
- `columns`: optional list of column definitions (dicts or names).
- `column_config`: `{column_name: {overrides}}` merged onto inferred columns.
- `column_groups`: `{group_title: [column, ...]}` renders the listed columns
  under a shared header and clusters them together (ungrouped columns keep
  their place). Equivalent to setting `column_group` on each column; disable
  clustering with `order_columns_by_group=False`.
- `options`: table-level display options (below).
- Methods: `set_data(...)`, `update_options(...)`, `set_column(name, ...)`.
- Constructors: `from_records`, `from_arrow`, `from_pandas`, `from_duckdb`.

### Column definition

| Key | Description |
| --- | --- |
| `name`, `title` | Row key and display title. |
| `type` | `string`, `number`, `date`, `boolean`, `array`, `object`. |
| `fmt` | Format code or preset (`usd2`, `pct1`, `num1m`, `mmm-yy`, …). |
| `fmt_column` | Column of format codes used per row. |
| `total_fmt`, `subtotal_fmt` | Format codes for total/subtotal rows. |
| `align` | `left`, `right`, `center` (defaults by type). |
| `wrap`, `hide`, `red_negatives` | Layout / value tweaks. |
| `viz` | `bar`, `color`, `sparkline`, `delta`, or `None`. |
| `bar_options` | `bar_color`, `bar_color_negative`, `hide_labels`, `fit_to_data`. |
| `color_options` | `color_scale`, `color_stops`, `conditional_colors`, `scale_column`, `scale_mode`, `min`, `max`, `midpoint`. |
| `delta_options` | `down_is_good`, `show_symbol`, `symbol_position`, `neutral_range`. |
| `sparkline_options` | `type` (`line`/`area`/`bar`), `x`/`y` (field names for struct arrays), `color`, `fit_to_data`, `width`, `height`, `y_fmt`. |
| `link`, `link_label`, `link_new_tab` | Per-cell links. |
| `html`, `image`, `image_options`, `logo` | Custom cell content (HTML, image URL, or logo.dev domain). |
| `column_group`, `info`, `repeat_values`, `viz_include_subtotals` | Additional metadata. |

### Table options

`title`, `subtitle`, `info`, `info_link`, `info_link_title`, `search`,
`page_size`, `sortable`, `download`, `row_shading`, `row_lines`,
`freeze_columns`, `wrap`, `wrap_titles`, `format_titles`, `show_total_row`,
`total_label`, `total_position`, `subtotal_position`, `collapsible`,
`collapsed`, `link`, `width`, `max_height`, `order_columns_by_group`, `theme`,
`color_scale`.

## Architecture

The widget has two halves:

- **Python** (`src/evidence_tables/`) normalises data into JSON-serialisable
  `rows`, `columns` and `options` traitlets. `data.py` handles type inference
  and Arrow/Decimal/date conversion; `grouped.py` builds the `GROUPING SETS`
  SQL and the row metadata; `duck.py` manages DuckDB connections, S3
  credentials and the S3 Tables catalog.
- **JavaScript** (`frontend/src/`, bundled to `src/evidence_tables/static/`)
  is a dependency-light vanilla renderer. `format.js` ports Evidence's
  `formatValue` (on `ssf`), `color.js` ports its chroma-based colour scales,
  and `table.js` owns rendering, sorting, search, grouping, frozen columns,
  fullscreen and CSV export.

The bundle is committed so the Python package works with no JS toolchain.
Rebuild it with `make frontend-build` after editing `frontend/src/`.

## Development

```bash
make test             # Python + JavaScript tests
make lint             # ruff
make check-notebooks  # marimo check
make validate         # lint + notebooks + tests + build
make run-marimo       # open the notebooks
make screenshot       # render frontend/preview.html to /tmp/evidence_preview.png
```

## Relationship to Evidence

This project is a focused reimplementation for the Python/Marimo ecosystem.
The formatting presets, colour-scale maths and overall table presentation are
ported from Evidence's `formatValue`, `table-viz`, `table-styles` and
`color-scale-utils` modules. Evidence is MIT licensed; the same license applies
here.

## Roadmap

- Pivoted columns (measures across a pivot dimension).
- Column comparisons (period-over-period) and comparison tooltips.
- Excel export.
- Virtualised rendering for very large result sets.

## License

MIT.
