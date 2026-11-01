# AdventureWorks company report

Open the report with the repository's development environment:

```bash
uv run marimo edit notebooks/59_adventureworks_company_report.py
```

The notebook reads the local Parquet product in
`~/datasets/adventureworks/data/processed/parquet`. Set `ADVENTUREWORKS_DATASET`
to another dataset checkout, processed directory or Parquet directory. The
files are read in place; the notebook creates derived facts only in an
in-memory DuckDB connection. No AdventureWorks business records are committed
to this repository, and missing files produce setup instructions rather than
fabricated replacement data.

## Reading the report

The reporting year and sales channel update the whole report. It starts with
the latest fully covered calendar year: 2024 in the current local product.
Tables and the map persist across filter changes, retaining table search and
collapsed sections.

| Section | Contents |
| --- | --- |
| Executive view | Net sales, estimated gross contribution and margin, orders, units, active customers and average order value. |
| Trading rhythm | Monthly sales bars with prior-year dots, signed sales changes, channel mix and contribution margin. |
| Markets | Country sales map and searchable territory comparisons, grouped into collapsible regions. |
| Product portfolio | Searchable subcategories with category summaries, sales share, margin, units, discounts and monthly sparklines. |
| Customers | First-observed and previously observed customers, plus the largest 15 reseller accounts. |
| Fulfilment | Dispatch lead times, dispatch-by-due-date share and freight-to-sales ratio. |
| Basis of preparation | Live source coverage, cost-fallback share, unknown-cost sales and header/line reconciliation. |

Region and category summaries show additive totals. Closing a section hides its
details and footer, promoting those totals into the heading. Ratios and distinct
customer counts are not summed. Product pagination includes continuation
headings. Search on accounts applies to the displayed top 15, not all accounts.
Product sparklines run oldest to newest with independently scaled vertical axes.
Margin colors share a fixed red–white–green scale, with zero at white.

## The single non-table visual

The country choropleth uses wigglystuff's
[`ObservablePlot`](https://koaning.github.io/wigglystuff/reference/observable-plot/)
widget. Everything else uses Evidential. The map shows country totals, not
customer coordinates, on an equal-area projection. Hover for sales and order
counts. Its square-root blue color scale adapts to the selected period/channel;
gray countries have no recorded sales in that selection.

Plot 0.6.17 is pinned in the widget. Plot and d3 load through the widget's CDN
imports, so the map needs a browser network connection on first use. Table
queries and rendering are independent of that connection. wigglystuff is a
development dependency for this notebook, not an Evidential runtime dependency.

The country geometry is a reduced, committed Natural Earth extract; its pinned
source and public-domain attribution are recorded in the
[map-data README](../notebooks/sample_data/adventureworks/README.md).

## Accounting and comparison conventions

- Net sales are discounted `SalesOrderDetail.LineTotal` on shipped orders
  (`Status = 5`), attributed to order date, in US dollars. Tax and freight are
  excluded. All sales measures use this same line-sales basis. Separate order
  and line facts prevent order amounts from multiplying across sales lines.
- Estimated gross contribution subtracts quantity times effective historical
  standard cost. If no history covers the order date, current product standard
  cost is a disclosed fallback. If any cost remains unknown, contribution and
  margin for its group are unavailable rather than understated. These measures
  exclude overhead, selling expenses, freight and tax; they are not net profit.
- Prior-year windows match the observed calendar dates. The current product ends
  on 29 June 2025, so 2025 compares with 1 January–29 June 2024. No period is
  annualized. If the prior window extends beyond source coverage, comparisons
  are suppressed. A fully covered window with no matching sales is zero;
  growth from a zero base remains unavailable.
- Channels come from `OnlineOrderFlag`: **Online** or **Sales-assisted**.
  Reseller accounts instead come from the customer's store relationship; these
  are separate classifications. First-observed customer dates use all source
  channels, and mean first observed in this extract, not lifetime acquisition.
- Top-account shares use all selected company sales as their denominator,
  including consumer sales. Accounts with prior-period sales but none in the
  selected period remain eligible for the comparison. Percentage and average
  measures divide aggregate numerators by aggregate denominators.
- Dispatch days measure order-to-ship dates. Dispatch-by-due is measured among
  orders with a ship date and does not establish actual delivery performance.
  Freight is the recorded order freight charge. Historical inventory is omitted
  because the current snapshot cannot establish prior year-end stock.

The source is Microsoft's fictional sample company, with dates regenerated by
the local data product. Its coverage and tiny line/header rounding differences
are printed in the report. SQL lives beside the notebook in `sql/59_aw_*.sql`;
synthetic Parquet fixtures test reconciliation, cost history, incomplete periods
and filtering without requiring a developer's local dataset.
