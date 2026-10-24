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
remain JSON `null`; no values are imputed. All 217 WDI countries and territories
are included, including those with no observations.
Aggregate regions and income groups are excluded using the country dimension's
`Region` field.

`score` is the sum of the available metric values, including debt with its
displayed sign, rounded to the nearest whole point. Higher scores rank first.
`rank_label` uses competition ranks, with an `=` suffix for ties (for example,
`1`, `2=`, `2=`, `4`). Rows without any reported metrics have a null score and
rank and sort last. Country names break score ties alphabetically. The country
display text includes its rank in parentheses. The score is an unweighted sum
of the displayed changes.

## Football results

`46_football_england_2024.json` is the output of
[`46_football_outcomes.sql`](../sql/46_football_outcomes.sql), queried from
`~/datasets/football-data/data/results/games.parquet` on 24 October 2026.
It contains 812 team perspectives for the 23 clubs participating in England's
recorded top domestic division during calendar year 2024, including those
clubs' international matches in the dataset. Both sides of a match appear when
both clubs are in that set. This is match data, not a season league table.

Notebook 46 reads the local parquet first (`FOOTBALL_PARQUET` overrides its
location); the snapshot keeps its default example usable without that file.
Source: **football-data / worldclubratings.com**, distributed under the
[Open Data Commons Attribution License 1.0](https://opendatacommons.org/licenses/by/1-0/).
The source covers top domestic divisions and selected international
competitions; domestic cup fixtures are not comprehensively included.
