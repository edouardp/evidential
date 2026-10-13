# Performance Measurements

Local measurements on 2026-10-13 guided the changes in
[ADR-039](adr/039-derived-data-cache-and-group-index.md). Node was `v24.15.0`;
Python was `3.12.13`. These are illustrative local medians, not CI timing
thresholds. Scheduling, garbage collection, and hardware affect elapsed times.

## Table navigation

The frontend scenario uses eight numeric columns, a color visualization,
column statistics, decimal alignment, and 20 visible rows. The median covers
five page changes. jsdom measures data processing and DOM construction;
browser layout and paint are excluded.

| Dataset rows | Before (ms) | After (ms) |
| ------------ | ----------- | ---------- |
| 10,000       | 26.1        | 7.5        |
| 50,000       | 108.9       | 8.4        |
| 100,000      | 222.5       | 4.1        |

The initial render still computes full-dataset summaries. Page changes reuse
them; source, configuration, search, sort, and visibility changes invalidate
the relevant projection. A regression test counts value reads during page
navigation so this property does not depend on machine speed. A separate test
checks decimal alignment with 200,000 records without an argument-limit error.

## Python summary overrides

Each group contains ten detail rows; two measures use sum and mean overrides.
The median covers three aggregation passes. SQL execution and widget/data
construction are excluded.

| Groups | Detail rows | Before (ms) | After (ms) |
| ------ | ----------- | ----------- | ---------- |
| 100    | 1,000       | 4.8         | 0.3        |
| 500    | 5,000       | 109.0       | 3.1        |
| 2,000  | 20,000      | 1,594.8     | 16.0       |

The ancestor index replaces repeated detail scans. Tests verify that descendant
lookup reads ancestor metadata once per detail row and preserves summary
values, including weighted and pivot overrides.

## Reproduce

From the repository root, with development dependencies installed:

```sh
node frontend/benchmark.js
uv run --locked python scripts/benchmark_aggregations.py
```

Pass dataset sizes to the frontend command, or `--groups 100 500 2000` to the
Python command, to explore other sizes. `make benchmark` runs both defaults.

The widget still materializes the full input dataset. Grouped tables render
all visible rows, so large expanded groups can remain expensive. These changes
optimize repeated processing, rather than introducing virtualization.
