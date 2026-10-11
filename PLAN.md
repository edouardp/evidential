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
- [ ] `rows="all"` (show every row, no pagination)
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
- [ ] `show_link_column` (currently always shows a chevron column)
- [x] `freeze_columns`
- [x] `width` (px or a CSS length like `80%`)
- [ ] `refresh_interval` (notebook-level; document)
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
- [ ] `total_agg`, `total_fmt`, `weight_col` (query/group helper)
- [x] `hide`
- [x] `red_negatives`
- [x] `column_group` / `colGroup`
- [x] `content_type` shorthand (`link`, `image`, `delta`, `colorscale`,
      `sparkline`, `sparkarea`, `sparkbar`, `bar`, `html`)
- [x] `type` inference for arrays/dates

## Content types / visualisations

- [x] `link` (`link_label`, `link_new_tab`)
- [x] `image` (`height`/`width`/`alt` options)
- [ ] `logo` (Evidence uses logo.dev; skip/deferred)
- [x] `delta` (`show_value`, `chip`, `down_is_good`, `show_symbol`, neutral range)
- [x] `colorscale` / `color` (`color_scale`, `color_stops`, `scale_column`,
      `min`/`max`/`midpoint`, `conditional_colors`)
- [ ] `color_scale` presets (`green`, `blue`, `red`, …)
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
- [ ] client-side `group_by` column (Evidence legacy `groupBy`)
- [ ] `group_type="section"` (merged group cells vs accordion)
- [ ] `groups_open`
- [ ] `subtotal_fmt`
- [ ] `show_total_column` / `show_subtotal_columns` (pivoted)
- [ ] `measures_first` (pivoted)
- [ ] `repeat_values` (rowspan vs repeat)

## Query builder (Python/DuckDB helpers)

- [x] `grouped_table` (dimensions + measures + subtotals/totals)
- [x] `pivot_table` (pivots → columns, grouped headers, total column, subtotal rows)
- [ ] `query_table` / `date_range` (`where`, `having`, `order`, `limit`,
      `qualify`)
- [ ] `date_range` presets (`last 12 months`, `month to date`, …)
- [ ] `comparison` (prior year / prior period → delta + % columns)
- [ ] `total_agg` / `total_fmt` / weighted mean
- [ ] `order` initial sort

## Interactivity / polish

- [x] 3-state client sort
- [x] search
- [x] pagination (+ press-and-hold)
- [x] frozen columns
- [x] fullscreen (fit rows, backdrop dismiss, height reset)
- [x] CSV download
- [x] loading overlay + stable height
- [x] live re-query (`LiveEvidenceTable`)
- [ ] comparison tooltips
- [ ] column-level description icon
- [ ] row-number column

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
- [ ] a per-feature gallery notebook as things land
- [x] README feature/API docs

## Testing

- [x] jsdom unit tests (`frontend/test_table.js`) for renderer behaviour
- [x] pytest unit tests (`tests/test_table.py`, `test_grouped.py`, `test_live.py`)
- [x] Playwright functional tests against `frontend/preview.html` (`make test-browser`)
