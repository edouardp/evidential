# OECD economic cycles explorer

Run the local OECD data product through the recession timeline and linked source
browser in [`58_oecd_economic_cycles.py`](../notebooks/58_oecd_economic_cycles.py):

```bash
uv run marimo edit notebooks/58_oecd_economic_cycles.py
```

The notebook reads `~/datasets/oecd/data/processed/*.parquet` directly through
DuckDB. Set `OECD_DATASET` to use another checkout. Build the data product there
first; the notebook does not download data or substitute fabricated observations.
No local dataset is included in this repository.

## Timeline and drilldown

The opening view follows the reference chart's 1960–2019 window. A year-range
slider exposes the full local history. Countries are alphabetical within broad
geographic regions, with regional aggregates excluded unless enabled. Search filters the displayed country list.
Click a row to update the quarterly evidence and source observations below it.
The widgets persist when filters change.

The first column is an explicit geographic display mapping in the notebook SQL,
not an OECD classification. Türkiye is placed in Asia and Russia in Europe;
unknown future country codes display **Unclassified**. Aggregate entities have
their own category.

| Context column | Meaning |
| --- | --- |
| GDP | Annual, current-price GDP in PPP-converted US dollars, displayed with four significant digits. The tooltip shows the full value. |
| Debt/GDP | General government gross debt as a percentage of GDP. |
| Fiscal/GDP | General government net lending (+) or borrowing (−) as a percentage of GDP. |
| Recession share | Recession quarters divided by observed growth quarters in the chosen window, on a fixed light-to-dark red 0–100% scale. The tooltip gives observed and possible quarters. |

Annual context uses the **last selected year**, printed in the headers. Missing
figures are not carried forward from another year. Annual GDP is taken directly
from the annual series, never summed from quarterly annualized levels. Filters
choose one comparable series per metric; duplicate keys fail explicitly.

The product also has government revenue, expenditure, investment, primary balance
and interest measures, plus GDP expenditure components and external-sector data.
Those are available in the source browser. Population is absent, so GDP per person
would require another source rather than being inferred from these figures.

The chart uses `col.strip` with explicit quarter intervals, a shared year domain,
a top axis and a three-category legend. Adjacent quarters of the same category
are combined into a single interval. Hover a band for its first/last quarter and
duration. Grey covers missing observations, including years before a country's
series starts and unobserved quarters at the edges of the available history.

## Recession convention

Only quarterly, calendar and seasonally adjusted, quarter-on-quarter real GDP
growth is used: GDP transaction `B1GQ`, whole-economy sector `S1`, chain-linked
volume price base `L`, percentage-change unit `PC`, transformation `G1`, and
table `T0102`. Annual growth, nominal levels, components and unadjusted series
are excluded. The SQL lives beside the notebook in `notebooks/sql/58_oecd_*.sql`.
Duplicate country/quarter observations fail explicitly rather than being averaged.

Red marks every quarter in a run of at least two consecutive negative growth
observations, including the first contraction. An isolated negative quarter stays
blue. Zero or missing growth ends a run. A complete quarterly calendar prevents
observations separated by a missing quarter from becoming false neighbours.
Classification uses the full history before the selected years are clipped.
Values are not rounded before testing their sign.

This is a retrospective **technical-recession convention**, not official OECD
recession dating. The [ONS explanation of the economic cycle](https://www.ons.gov.uk/economy/grossdomesticproductgdp/methodologies/communicatingtheukeconomiccycle)
discusses the two-quarter convention and its limitations. Revisions, different
vintages and the chosen convention can produce different bands from the older
reference image. Provisional, estimated and break-in-series statuses remain
visible in the quarterly evidence; the notebook does not adjust published values.

## Source observations and units

Choose among the available GDP, government finance, public debt, balance of
payments, international investment position and trade-in-services extracts.
The source browser shows individual observations for the selected country and
years, up to the latest 500 matches, with the total matching count in its caption.
Search applies to those loaded rows. Hover **Series** to see additional dimensions.
Frequency, units, adjustment and observation status remain separate columns.

Values include the product's multiplier. For example, a value published as 12.5
million US dollars displays as 12.5M, while percentage-change values remain in
their published percentage units. The quarterly growth detail instead divides
by 100 once for the table's percentage formatter. Unlike series are never summed.
Current-price, annualized PPP GDP levels are not used to infer real recessions;
other source datasets can contain projections, so their dates and statuses matter.

The inventory lists local files, row counts and date coverage. The combined
`bop_family.parquet` is omitted because it duplicates the separate BOP/IIP/TIS
extracts. The dataflow catalogue is listed in the inventory, not treated as an
observation series.
