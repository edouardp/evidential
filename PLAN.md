# Evidence DataTable feature parity plan

Working checklist derived from Evidence's DataTable docs
(`legacy-docs.evidence.dev/components/data/data-table` and
`docs/components/table.mdx`). `[x]` = done, `[ ]` = todo, `[~]` = partial.

Tech-stack note: our widget is a **display** anywidget; Evidence's
query-builder features (dimensions/pivots/measures, date ranges, comparisons)
are done in SQL. We implement them as Python/DuckDB helpers where feasible.

## Table options

- [x] `data` / rows pass-through
- [x] `title`, `subtitle`
- [x] `info` (+ `info_link`, `info_link_title`)
- [x] `page_size` (max 200)
- [x] `rows="all"` via `page_size="all"`
- [x] `search`
- [x] `sortable`
- [x] `sort` / initial `default_sort`
- [x] `download` (`downloadable`)
- [x] `format_titles`
- [x] `wrap_titles`
- [x] `wrap`
- [x] `row_shading`
- [x] `row_lines`
- [x] `row_numbers`
- [x] `compact`
- [x] `empty_message`
- [x] `link` (clickable row)
- [x] `show_link_column`
- [x] `freeze_columns`
- [x] `width` (px or a CSS length like `80%`)
- [x] `refresh_interval` (notebook-level via `mo.ui.refresh`; documented in README)
- [x] `show_total_row`, `total_label`
- [x] `collapsible`, `collapsed`
- [x] `subtotal_position`, `total_position`
- [x] `row_conditional_colors`

### Theming

- [x] `theme` dict (background, text, border, total/subtotal, link, accent…)
- [x] `header_color`
- [x] `header_font_color`
- [x] `total_row_color`
- [x] `total_font_color`
- [x] `background_color`
- [x] `compact` density

## Column options

- [x] `name` / `id`, `title`
- [x] `align`
- [x] `fmt`
- [x] `fmt_column` (per-row format codes)
- [x] `wrap`, `wrap_title`
- [x] `info` / `description` (header icon)
- [x] `total_agg` / `total_fmt` — `aggregations` built-ins + callables, per-row formats
- [x] `total_fmt` / `subtotal_fmt` per-row formats
- [x] `hide`
- [x] `red_negatives`
- [x] `column_group` / `colGroup`
- [x] `content_type` shorthand (`link`, `image`, `delta`, `colorscale`,
      `sparkline`, `sparkarea`, `sparkbar`, `bar`, `html`)
- [x] `type` inference for arrays/dates

## Content types / visualisations

- [x] `link` (`link_label`, `link_new_tab`)
- [x] `image` (`height`/`width`/`alt` options)
- [x] `logo` (`logo`/`logo_options`, rendered via logo.dev)
- [x] `delta` (`show_value`, `chip`, `down_is_good`, `show_symbol`, neutral range)
- [x] `colorscale` / `color` (`color_scale`, `color_stops`, `scale_column`,
      `min`/`max`/`midpoint`, `conditional_colors`)
- [x] `color_scale` presets (`green`, `blue`, `red`, `orange`, `purple`, `grey`)
- [x] `bar` (`bar_color`, `bar_color_negative`, `hide_labels`, `fit_to_data`)
- [x] `bar` `background_color`
- [x] `sparkline` / `sparkarea` / `sparkbar` (`x`, `y`, `type`, `color`,
      `width`, `height`, `fit_to_data`, `y_fmt`, zero baseline, tooltips)
- [x] `html`
- [x] `bars`/conditional cell backgrounds

## Groups & subtotals

- [x] grouped subtotals via DuckDB `GROUPING SETS` (`grouped_table`)
- [x] collapsible accordion groups
- [x] subtotal/total positions
- [x] `group_type="section"` (merged group cells via rowspan) / `accordion`
- [x] `groups_open` (alias for the inverse of `collapsed`)
- [x] `subtotal_fmt` / `total_fmt`
- [x] `repeat_values` (our renderer already repeats dimension values)
- [x] client-side `group_by` (`grouped_records` for in-memory rows)
- [~] `show_total_column` (done) / `show_subtotal_columns` (pending)
- [x] `measures_first` (pivoted)
- [x] `repeat_values` (renderer repeats dimension values)

## Query builder (Python/DuckDB helpers)

- [x] `grouped_table` (dimensions + measures + subtotals/totals)
- [x] `pivot_table` (pivots → columns, grouped headers, total column, subtotal rows)
- [x] `query_table` (`where`, `order`, `limit`, `qualify`, `date_range`)
- [x] `date_range` presets (`last 12 months`, `month to date`, …)
- [~] `having` (lives inside the base query; not a display-layer clause)
- [x] `comparison` (prior year/quarter/month/week/day → prior + delta + % columns)
- [x] `total_agg` (built-in names + Python callables) / `weight_col` (weighted_mean)
- [x] `total_fmt` / `subtotal_fmt` per-row formats
- [x] `order` initial sort (via `default_sort`)

## Interactivity / polish

- [x] 3-state client sort
- [x] search
- [x] pagination (+ press-and-hold)
- [x] frozen columns
- [x] fullscreen (fit rows, backdrop dismiss, height reset)
- [x] CSV download
- [x] loading overlay + stable height
- [x] live re-query (`LiveEvidenceTable`)
- [ ] comparison tooltips (deferred; delta/% columns are provided)
- [x] column-level description icon
- [x] row-number column

## Docs & demos

- [x] `notebooks/01_taxi_explore.py`
- [x] `notebooks/02_s3_tables.py`
- [x] `notebooks/03_live_drilldown.py`
- [x] `notebooks/04_live_demo.py`
- [x] `notebooks/05_sparklines.py`
- [x] `notebooks/06_evidence_sample_data.py` (needful_things.orders)
- [x] `notebooks/07_table_options.py` (table-level display options)
- [x] `notebooks/08_column_options.py` (column formatting/content types)
- [x] `notebooks/09_pivots.py` (pivoted columns)
- [x] `notebooks/10_query_options.py` (query_table/date_range)
- [x] `notebooks/11_comparisons.py` (prior-period comparisons)
- [x] `notebooks/12_color_scales.py` (colour scales & conditional formatting)
- [x] `notebooks/13_hierarchical_rows.py` (accordion/section groups)
- [x] `notebooks/14_aggregations.py` (built-in + custom aggregations)
- [x] `notebooks/15_client_grouping.py` (in-memory `grouped_records`)
- [x] `notebooks/16_tech_giants.py` (gt-style table: sections, blanks, footnotes)
- [x] `notebooks/README.md` index of all demos
- [x] README feature/API docs

## Presentation parts (gt-inspired)

- [x] Table header (`title`, `subtitle`)
- [x] Caption / source notes (`caption`)
- [x] Section divider rows (`section_row`)
- [x] Data-driven footnotes (`footnote` column option) with row references
- [x] Static footnotes (`footnotes=[...]`)
- [x] Blank rendering (`null_text`) + value cutoffs (`blank_below`/`blank_above`) and a Python `blank` predicate
- [x] Column groups / spanners (`column_groups`)
- [x] Row groups and summary rows (`grouped_table`, `group_type`)
- [ ] Location-based styling API (we use per-column config + conditional colours)
- [ ] Nested spanners
- [ ] Cell text transformations

## Testing

- [x] jsdom unit tests (`frontend/test_table.js`) for renderer behaviour
- [x] pytest unit tests (`tests/test_table.py`, `test_grouped.py`, `test_live.py`)
- [x] Playwright functional tests against `frontend/preview.html` (`make test-browser`)
