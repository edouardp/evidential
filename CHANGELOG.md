# Changelog

All notable changes to this project are documented in this file. The format is
based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this
project follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased

### Added

- Fluent `.legend()` for mark columns: compact, wrapping colour keys beside
  the table title, with source-derived or custom names, optional omitted
  entries, an optional outline, and matching bar, point, range and strip swatches.
- Notebook 54 demonstrates one and two stacked-bar legends plus nine coloured
  age-band points using genuine 2024 WDI population estimates for twelve
  countries. A documented snapshot and aggregation query keep it usable offline.
- Named multi-field `col.points(...)` accepts field lists or display-name maps,
  automatic categorical colours, sampled palettes and optional connecting
  spans. Its legend shares the names and colours; no derived data fields are needed.

## 0.1.2 (2026-10-26)

### Added

- **Table layout gallery** — 19 runnable examples in notebook 51, with
  notebook-generated README descriptions, code and Playwright screenshots.
  Covers titles, captions, footnotes, frames, rules, row shading, group-heading
  styles, indented details, summaries, grand totals and nested column groups.
- **Real-data graphics examples** — WDI imports and exports for six European
  economies on one shared scale, plus Premier League wins, draws, losses and
  recent-form change sparklines. Committed snapshots keep both examples
  runnable without local datasets.

### Changed

- **README excerpts** — LibCST extracts complete table calls for layout
  examples. Inline SQL makes the selected fields visible; shared column and
  settings references become `...`, while inline definitions stay explicit.
- **Example clarity** — remove redundant automatic column titles, use filled
  circles alongside square symbols, and improve trade-table alignment.

### Fixed

- Nested `col.group(...)` builders preserve child header paths and highlights
  instead of replacing them with the parent group's settings.
- `.repeat_values(False)` now suppresses adjacent duplicate display values,
  restarting on each page and after headings or summaries. Raw data, sorting,
  filtering and exports retain the original values.
- `section_indent` also indents detail labels beneath top summaries when no
  separate section heading is present.
- Reference bands fill the cell height behind gridlines and marks. Explicit
  colors and alpha are preserved instead of receiving an additional fade;
  the default theme band remains subtle.

## 0.1.1 (2026-10-26)

### Added

- **Notebook-generated README examples** — descriptions, column definitions
  and Playwright screenshots now come from the same named marimo cells.
- **Documentation freshness checks** — `make readme` regenerates examples and
  images; `make readme-check` detects stale content using source and image
  hashes. Checks run in pre-commit, lint and release validation.

### Changed

- **README image paths** — repository images use local paths. A generated
  PyPI README resolves image and documentation links to absolute URLs.
- **Local release workflow** — aligned with Galaga's `make release` chooser,
  patch/minor/major targets and exact `VERSION=` requests, including alpha,
  beta and release candidates. Releases edit the changelog, validate locally,
  retrieve credentials through the keyring, publish, tag and create a GitHub
  release.

### Fixed

- Run the keyring CLI through the locked project interpreter, avoiding broken
  global wrappers after Homebrew Python upgrades. Check CLI startup before
  release edits or builds without retrieving credentials.
- Align the `uv_build` requirement with `uv 0.13.4` to remove the build-backend
  version warning, and remove empty notebook cells reported by `marimo check`.
- Stop releases with stale README examples or screenshots before changing
  the version or opening the changelog editor.
- Remove old distributions before building, preventing stale artifacts from
  being checked or uploaded alongside the current version.

## 0.1.0 (2026-10-26)

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
  per-value `compact` units, readable scientific notation with superscript
  exponents, plus `bytes`, `duration`, `roman` and `flag` (ISO 3166-1 alpha-2
  and alpha-3 country codes).
- **Conditional visualisations** — `viz="bar"`, `viz="color"`, `viz="chip"`,
  `viz="sparkline"` (line/area/bar), `viz="delta"`, plus column/group highlights
  and per-row conditional colours.
- **Grouping** — `grouped_table` (one DuckDB `GROUPING SETS` query with
  collapsible groups, subtotals and a grand total), `pivot_table`,
  `comparison_table`, `query_table` and client-side `grouped_records`.
- **Live tables** — `LiveEvidentialTable` re-runs a parameterised query when its
  controls change.
- **Fluent API** — typed column kinds, reusable label builders, shared numeric
  domains, hierarchical header groups and independently aligned sub-columns.
- **Declarative graphics** — labeled, centered, overlaid, back-to-back and
  stacked bars; points, ranges, dumbbells with signed colors and direction
  chevrons; strips, boxplots and distribution uncertainty bands. Shared axes
  support logarithmic scales, minor ticks, references and gridlines.
- **Sparklines** — line, area, bar, points and change styles, optional adjacent
  differences, gradients and signed area fills around a configurable reference.
- **Display rows** — synthetic group headings, summaries and grand totals stay
  separate from source records, with continuation headings across pages.
- **Source inspection** — `.raw` returns detached, unformatted source records
  on regular and live tables, including the query and aggregation helpers.
- **Readable details** — adaptive superscript footnote symbols, sub-column
  statistics controls, contrast-aware labels, automatic inside/outside bar
  labels, chart-aware column widths and nulls-last sorting in both directions.
- **Interaction** — sorting, search, pagination, row links, row selection that
  drives the notebook, CSV download and a fullscreen dialog.
- **Documentation** — 50 demo notebooks, a graphics gallery, repeatable
  Playwright screenshots, API documentation and architecture decisions.
