# Changelog

All notable changes to this project are documented in this file. The format is
based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this
project follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## 0.1.0 (2026-10-13)

First release.

### Added

- **`EvidentialTable`** — an [anywidget](https://anywidget.dev) that renders
  Evidence.dev-style interactive data tables in [Marimo](https://marimo.io),
  driven from Arrow tables, pandas DataFrames, DuckDB relations or plain lists.
- **Presentation** — titles/subtitles/info, hierarchical columns
  (`column_groups`, and the dotted `"Group.Column"` name convention), column
  statistics, row shading and lines, frozen columns, wrapping, rotated headings,
  column merging (`cols_merge*`), substitutions (`sub_*`) and footnote marks.
- **Formats** — Excel-style codes via `ssf`, auto-scaling `num`/`usd`/`pct`, and
  the special formatters `bytes`, `duration`, `roman` and `flag` (ISO 3166-1
  alpha-2 and alpha-3 country codes).
- **Conditional visualisations** — `viz="bar"`, `viz="color"`, `viz="chip"`,
  `viz="sparkline"` (line/area/bar), `viz="delta"`, plus column/group highlights
  and per-row conditional colours.
- **Grouping** — `grouped_table` (one DuckDB `GROUPING SETS` query with
  collapsible groups, subtotals and a grand total), `pivot_table`,
  `comparison_table`, `query_table` and client-side `grouped_records`.
- **Live tables** — `LiveEvidentialTable` re-runs a parameterised query when its
  controls change.
- **Interaction** — sorting, search, pagination, row links, row selection that
  drives the notebook, CSV download and a fullscreen dialog.
- **Documentation** — 29 runnable notebooks plus design, architecture and ADR
  documents.
