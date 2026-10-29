# AWS CUR explorer

[Notebook 57](../notebooks/57_aws_cur_explorer.py) explores the processed local
`aws-cur-example` data product. It replaces the synthetic cloud example from
notebook 56; that notebook keeps its portable Needful Things sales example.

## Run

```bash
uv run marimo edit notebooks/57_aws_cur_explorer.py
```

The default input is
`~/datasets/aws-cur-example/data/processed/cur_line_items.parquet`.
Override the checkout location when needed:

```bash
AWS_CUR_DATASET=/path/to/aws-cur-example uv run marimo edit notebooks/57_aws_cur_explorer.py
```

Build the data product first if that processed file is missing. The notebook
reads it locally without copying data into this repository. Its PEP 723 header
declares marimo, DuckDB, PyArrow and Evidential. The explorer expects USD costs;
it does not sum different currencies together.

## Filters and results

Nine useful dimensions are shown: **service, usage type, region, account,
charge type, environment, workload, cost centre and billing month**. Multiple
selections within a dimension combine with OR; dimensions combine with AND.
Empty selection means all values. Selecting AmazonRDS constrains usage types
and other facets to its matching records while keeping service alternatives.
Search narrows choices; select a category to filter the results.

The slicer preaggregates additive cost at the full nine-dimension grain,
preserving all filter combinations. A parameterized predicate from `.where()`
then filters the original line items for each result:

- **Summary cards:** amortized and unblended cost, line-item count and service
  count across every matching record.
- **Cost drivers:** service, usage type, region, charge type and billing unit,
  with quantities, cost bars, unblended comparison, share of selected cost and
  daily sparklines. Missing days in the selected range are zero-filled.
- **Individual charges:** highest amortized cost first, with dates, account,
  resource, usage, quantity, unit and description. The row limit is adjustable
  from 250 to 2,500; it affects only this table. Its search and CSV cover the
  loaded rows, not the entire source.

Widgets are created once; reactive cells update their data. Search, pagination
and other table state survive filter and limit changes. Account IDs use a
twelve-digit format rather than automatic compact-number formatting.

## Cost definitions

The SQL matches the data product's `build.py` definition: `DiscountedUsage`
uses `reservation_effective_cost`; other charge types use
`line_item_unblended_cost`. Existing fee rows remain included. The displayed
unblended column sums the original unblended cost for comparison. This follows
the product's measure definition rather than deriving a new invoice measure.

Usage quantities aggregate only within their billing unit and driver grain;
hours are not added to storage or request counts. Missing tags and regions
remain selectable null categories. Detail limits never change card totals,
cost-driver sums, share denominators or daily trends.

The normalization, driver, summary and detail queries live in
[`notebooks/sql/57_cur_source.sql`](../notebooks/sql/57_cur_source.sql),
[`57_cur_drivers.sql`](../notebooks/sql/57_cur_drivers.sql),
[`57_cur_summary.sql`](../notebooks/sql/57_cur_summary.sql) and
[`57_cur_details.sql`](../notebooks/sql/57_cur_details.sql).
See the [DimensionGrid API](api/API.md#dimension-slicers) for reusable controls.
