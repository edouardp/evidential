# Notebook data snapshots

`34_wdi_league_2019_2021.json` is the result of
[`34_wdi_league.sql`](../sql/34_wdi_league.sql), queried from the local
`WDI_CSV_2026_10_01/parquet` World Development Indicators bundle on 21 October
2026. It is a real-data fallback for notebook 34 when the local bundle is
unavailable, and keeps the example reproducible in CI. A local bundle takes
precedence; set `WDI_PARQUET` to its `parquet/` directory to query it directly.

Source: [World Bank, World Development Indicators](https://datacatalog.worldbank.org/search/dataset/0037712/world-development-indicators).
Use is subject to the World Bank's
[dataset terms](https://www.worldbank.org/en/about/legal/terms-of-use-for-datasets).

The selected indicators are real GDP (`NY.GDP.MKTP.KD`), real household and
NPISH consumption per person (`NE.CON.PRVT.PC.KD`), S&P equity price changes in
US dollars (`CM.MKT.INDX.ZG`), real fixed investment (`NE.GDI.FTOT.KD`), and
central-government debt as a share of GDP (`GC.DOD.TOTL.GD.ZS`). Consumption
does not measure household income, and central-government debt is narrower
than general-government debt.

For 2019–2021, level series use `100 * (value_2021 / value_2019 - 1)`. Equity
price returns compound the annual changes for 2020 and 2021. Debt uses the
2021 minus 2019 difference in percentage points of GDP. Missing observations
remain JSON `null`; no values are imputed. Country order is illustrative and
does not imply a ranking.
