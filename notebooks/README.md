# Demo notebooks

Run them with `make run-marimo` (or `uv run marimo edit notebooks`).
Notebooks fall back to small offline samples in script mode so they run fast
and without network access.

| Notebook | Features |
| --- | --- |
| [`01_taxi_explore.py`](01_taxi_explore.py) | EvidentialTable on the NYC TLC parquet via DuckDB httpfs; formatting, bars, colour, grouped totals, hierarchical columns. |
| [`02_s3_tables.py`](02_s3_tables.py) | Querying Amazon S3 Tables (Iceberg REST) through DuckDB. |
| [`03_live_drilldown.py`](03_live_drilldown.py) | `LiveEvidentialTable` with a slider + dropdown re-querying in place. |
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
| [`16_tech_giants.py`](16_tech_giants.py) | gt-style table: section dividers, blanks, conditional colours, data-driven footnotes; slider demonstrates singles, interleaved doubles and numeric fallback. |
| [`17_gt_features.py`](17_gt_features.py) | Nested spanners, stub, markdown titles, location rules. |
| [`18_great_tables.py`](18_great_tables.py) | Column merging, substitutions, special formatters. |
| [`19_typography.py`](19_typography.py) | Readable table typography: decimal alignment, no stretching, minimal furniture. |
| [`20_whitespace_grouping.py`](20_whitespace_grouping.py) | Grouping with white space and group-size stripes. |
| [`21_studio_dashboard.py`](21_studio_dashboard.py) | An `EvidentialTable` in a marimo Studio view: live dashboard, KPI strip, filter. |
| [`22_duckdb_metadata.py`](22_duckdb_metadata.py) | Column metadata: DuckDB comments, Parquet/Arrow field metadata and `column_config` descriptions, plus type-driven formats. |
| [`23_wdi.py`](23_wdi.py) | World Development Indicators Parquet: live filterable ranking, all-years sparklines with 5y-vs-10y % change, trend, pivot, grouped subtotals, prior-year comparison, dimensions and footnotes. |
| [`24_dotted_groups.py`](24_dotted_groups.py) | Column groups from dotted column names: a World Bank WDI pivot aliases indicators as `"GDP Measure.GDP (nominal)"`, grouped automatically. |
| [`25_column_stats.py`](25_column_stats.py) | Optional per-column statistics under the header (`min`/`max`/`avg`/`null`, `distinct`/`null`), toggled with a checkbox; mixed sub-columns with cycling statistics and centered dot controls. |
| [`26_multiline_headers.py`](26_multiline_headers.py) | Multi-line column headers: a `\n` forces a break and headers bottom-align. |
| [`27_chips.py`](27_chips.py) | `viz="chip"`: values in a rounded, centred chip, coloured by a scale or conditional colours. |
| [`28_column_highlights.py`](28_column_highlights.py) | Highlight an entire column or column group with a background colour. |
| [`29_row_selection.py`](29_row_selection.py) | Click a country row to drive a second table: the year-by-year drill-down re-queries on `table.widget.selected`. |
| [`30_subcolumns.py`](30_subcolumns.py) | Shared-header sub-columns: economic value/period pairs and a three-part right-aligned value, left-aligned text, centered chip, plus a close recreation of the supplied Economist economic data table. |
| [`31_imdb_media.py`](31_imdb_media.py) | IMDb-Media CSV: top-rated ranking, dotted-name column groups, column stats, a decade pivot and a row-selection cast drill-down. |
| [`32_column_builder.py`](32_column_builder.py) | The `col.*` column builder and the `settings(...)` bundle: a configured report plus a default table to experiment with. |
| [`33_relative_time.py`](33_relative_time.py) | Temporal kinds (`col.date` / `col.time` / `col.datetime`) and `relative=` for localised "3 days ago" rendering. |
| [`34_centered_bars.py`](34_centered_bars.py) | Centred (diverging) `bar(center=True)`: a zero line, the bar left/right by sign, and the value on the opposite side — The Economist's league-table bar. Also back-to-back bars (`bar(direction="left")`) with a benchmark rule (`reference=`) and per-row colours (`color="@column"`), as a mirrored league table and a tolerance-vs-intolerance chart. |
| [`35_negatives.py`](35_negatives.py) | Negative styling with `.neg()`: red negatives, a custom colour, and accounting-style brackets (`-1,234` → `(1,234)`), alone and with a centred bar. |
| [`36_repeated_symbols.py`](36_repeated_symbols.py) | `col.symbols` / `col.repeat` / `col.rating`: a number drawn as repeated glyphs, emoji or images — The Economist's squares, a medal table, star ratings. |
| [`39_synthetic_rows.py`](39_synthetic_rows.py) | Display-only headings, portable counts and averages, optional group/grand summaries, and continuation headings across detail-based pages. |
| [`44_spec_conformance.py`](44_spec_conformance.py) | Scale reference layouts, fixed bounds and missing marks, point outlines, shared diverging stacks, irregular sparklines and paginated section summaries. |
| [`45_display_row_layout.py`](45_display_row_layout.py) | Display-only group headings with counts/totals, optional group and grand summaries, nested groups, centered headings, and detail-based pagination with continuation headings. |

`sample_data/needful_things/orders.parquet` is Evidence's demo dataset, copied
from the published docs site.
