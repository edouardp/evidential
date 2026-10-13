# Architectural Decision Records

This directory contains Architectural Decision Records (ADRs) for
`evidential`.

## What are ADRs?

ADRs document significant architectural decisions. Each records the context, the
options considered, the decision, and its consequences, so future contributors
understand *why* the table works the way it does and do not relitigate settled
questions without the original constraints.

The narrative explanation of the current design lives in
[design-and-dx.md](../design-and-dx.md) and
[technical-architecture.md](../technical-architecture.md). The ADRs are the
dated, immutable record of the decisions behind them.

## ADR Index

| ADR | Title | Status |
| --- | --- | --- |
| [001](001-use-architectural-decision-records.md) | Use Architectural Decision Records | Accepted |
| [002](002-display-only-widget.md) | Display-Only Widget, Not a Query Builder | Accepted |
| [003](003-evidence-compatible-api.md) | Evidence-Compatible API Surface | Accepted |
| [004](004-json-wire-format.md) | JSON Wire Format for Rows, Columns and Options | Accepted |
| [005](005-layer-responsibilities.md) | Responsible Layers — SQL Shapes, Python Binds, the Browser Paints | Accepted |
| [006](006-hidden-helper-columns.md) | Hidden Helper Columns for Presentation Logic | Accepted |
| [007](007-ssf-format-codes.md) | SSF (Excel Format Codes) for Value Formatting | Accepted |
| [008](008-chroma-js-colours.md) | chroma-js for Colour Scales | Accepted |
| [009](009-grouping-sets-for-grouped-totals.md) | `GROUPING SETS` for Grouped Totals | Accepted |
| [010](010-gt-style-location-rules.md) | gt-Style Location-Based Rules | Accepted |
| [011](011-live-tables-reactive-cell.md) | Live Tables Use a Persistent Widget and a Reactive Cell | Accepted |
| [012](012-non-flickering-loading.md) | Non-Flickering Live Updates | Accepted |
| [013](013-ala-typography-defaults.md) | A List Apart Typography as Defaults | Accepted |
| [014](014-committed-frontend-bundle.md) | Committed Frontend Bundle, No JS Toolchain for Users | Accepted |
| [015](015-composed-quality-gates.md) | Composed Quality Gates Mirrored in Pre-commit and a Script | Accepted |
| [016](016-layered-testing.md) | Layered Testing Strategy | Accepted |
| [017](017-release-workflow-tests.md) | Repository Release-Workflow Tests and Artifact Check | Accepted |
| [018](018-dependency-update-lag.md) | One-Week Lag on Dependency Updates | Accepted |
| [019](019-accordion-indentation.md) | Indent Dimension Cells in Accordion Groups | Accepted |
| [020](020-bar-visualisation-geometry.md) | Bar Visualisation Geometry | Accepted |
| [021](021-marimo-studio-projections.md) | Support marimo Studio Views by Projection | Accepted |
| [022](022-type-driven-column-defaults.md) | Derive Default Column Format and Alignment from the Data Type | Accepted |
| [023](023-duckdb-column-comments.md) | Surface DuckDB Column Comments as Header Descriptions | Accepted |
| [024](024-arrow-field-metadata.md) | Read Arrow Field Metadata as Column Descriptions | Accepted |
| [025](025-immediate-column-tooltip.md) | An Immediate Custom Tooltip for Column Descriptions | Accepted |
| [026](026-delta-indicator-and-neutral-band.md) | Delta Indicator After the Value, Dash for Neutral | Accepted |
| [027](027-sort-by-another-column.md) | Sort a Column by Another Column's Values | Accepted |
| [028](028-dotted-column-name-groups.md) | Column Groups from Dotted Column Names | Accepted |
| [029](029-native-header-tooltip.md) | Native Header Tooltip on the Whole Cell | Accepted |
| [030](030-chip-visualisation.md) | Chip Visualisation | Accepted |
| [031](031-column-highlights.md) | Column and Column-Group Highlights | Accepted |
| [032](032-row-selection.md) | Row Selection Drives the Notebook | Accepted |
| [033](033-stable-empty-table.md) | A Stable Empty Table (Placeholder Rows and an Overlay) | Accepted |
| [034](034-uv-build-backend.md) | `uv_build` as the Build Backend | Accepted |
| [035](035-correct-pivot-aggregations.md) | Aggregate Pivot Totals from Original Records | Accepted |
| [036](036-persistent-column-configuration.md) | Preserve Explicit Column Configuration Across Refreshes | Accepted |
| [037](037-renderer-module-boundaries.md) | Separate Renderer Processing, Cells, and Lifecycles | Accepted |
| [038](038-typed-configuration-validation.md) | Typed Configuration with Early Runtime Validation | Accepted |
| [039](039-derived-data-cache-and-group-index.md) | Cache Derived Table Data and Index Group Descendants | Accepted |
| [040](040-shared-header-subcolumns.md) | Shared-Header Sub-columns | Accepted |
| [041](041-adaptive-symbol-footnotes.md) | Adaptive Symbol Footnotes | Accepted |
| [042](042-column-builder-and-settings.md) | The `col` Column Builder and the `settings` Bundle | Accepted |
| [043](043-column-kinds.md) | Column Kinds as the Entry Point | Accepted |
| [044](044-column-group-builders.md) | Column Group Builders | Accepted |
| [045](045-col-namespace-surface.md) | The `col` Namespace Exposes Only Chain Entry Points | Accepted |
| [046](046-temporal-kinds-and-relative-time.md) | Temporal Kinds and Relative Time | Accepted |
| [047](047-inference-preserving-column-specs.md) | Inference-Preserving Column Specs | Accepted |
| [048](048-fluent-derived-columns.md) | Fluent Construction of Derived Columns | Accepted |
| [049](049-align-decimals-explicit-precision.md) | `align_decimals` Respects an Explicit Precision | Accepted |

## Creating New ADRs

1. Copy the template from [ADR-001](001-use-architectural-decision-records.md).
2. Number sequentially (e.g., `021-your-decision.md`).
3. Fill in every section.
4. Add a row to the [ADR Index](#adr-index) above.

`tests/release/test_adrs.py` checks that the numbering, frontmatter and index
stay consistent.

## Format

All ADRs follow the [MADR](https://adr.github.io/madr/) (Markdown Any Decision
Records) format:

```markdown
---
status: {proposed | accepted | deprecated | superseded by ADR-XXX}
date: YYYY-MM-DD
deciders: {list of people involved}
---

# ADR-XXX: {Title}

## Context and Problem Statement
## Decision Drivers
## Considered Options
## Decision Outcome
### Consequences
## More Information
```
