# Demo notebooks

Run them with `make run-marimo` (or `uv run marimo edit notebooks`).
Notebooks fall back to small offline samples in script mode so they run fast
and without network access.

| Notebook | Features |
| --- | --- |
| [`01_taxi_explore.py`](01_taxi_explore.py) | EvidenceTable on the NYC TLC parquet via DuckDB httpfs; formatting, bars, colour, grouped totals, hierarchical columns. |
| [`02_s3_tables.py`](02_s3_tables.py) | Querying Amazon S3 Tables (Iceberg REST) through DuckDB. |
| [`03_live_drilldown.py`](03_live_drilldown.py) | `LiveEvidenceTable` with a slider + dropdown re-querying in place. |
| [`04_live_demo.py`](04_live_demo.py) | Full live demo: slider/dropdowns driving a persistent table. |
| [`05_sparklines.py`](05_sparklines.py) | Line/area/bar sparklines from `ARRAY_AGG({'date','value'})`. |
| [`06_evidence_sample_data.py`](06_evidence_sample_data.py) | Evidence's own `needful_things.orders` sample: sparklines, grouped subtotals, raw orders. |
| [`07_table_options.py`](07_table_options.py) | Table-level options: row numbers, compact, default sort, row colours, theming, links, empty state. |
| [`08_column_options.py`](08_column_options.py) | Column formatting, `fmt_column`, links, HTML, `contentType` shorthands, bar/colour/delta/sparkline. |
| [`09_pivots.py`](09_pivots.py) | `pivot_table`: pivoted columns, `measures_first`, subtotal rows. |
| [`10_query_options.py`](10_query_options.py) | `query_table` with `where`/`order`/`limit`/`date_range`, live date-range selector, `page_size="all"`. |
| [`11_comparisons.py`](11_comparisons.py) | `comparison_table`: prior year / prior quarter with delta and % columns. |
| [`12_color_scales.py`](12_color_scales.py) | Every `viz="color"` option side by side: presets, bounds, midpoint, stops, scale column, conditional colours. |
| [`13_hierarchical_rows.py`](13_hierarchical_rows.py) | Accordion and section (merged-cell) hierarchical groups, collapsed-by-default. |
| [`14_aggregations.py`](14_aggregations.py) | Built-in and Python-callable aggregations for subtotals/totals. |
| [`15_client_grouping.py`](15_client_grouping.py) | `grouped_records`: grouping in-memory rows without a database. |
| [`16_tech_giants.py`](16_tech_giants.py) | gt-style table: section dividers, blanks, conditional colours, data-driven footnotes. |
| [`17_gt_features.py`](17_gt_features.py) | Nested spanners, stub, markdown titles, location rules. |
| [`18_great_tables.py`](18_great_tables.py) | Column merging, substitutions, special formatters. |
| [`19_typography.py`](19_typography.py) | Readable table typography: decimal alignment, no stretching, minimal furniture. |

`sample_data/needful_things/orders.parquet` is Evidence's demo dataset, copied
from the published docs site.
