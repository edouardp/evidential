-- Endpoint changes, not averages of annual growth rates. Keep every WDI
-- country/territory even when an indicator or endpoint is missing.
WITH observations AS (
    SELECT country_code, indicator_code, year, value
    FROM read_parquet($observations, hive_partitioning = true)
    WHERE year BETWEEN $base_year AND $end_year
      AND indicator_code IN (
          'NY.GDP.MKTP.KD', 'NE.CON.PRVT.PC.KD', 'CM.MKT.INDX.ZG',
          'NE.GDI.FTOT.KD', 'GC.DOD.TOTL.GD.ZS'
      )
      AND isfinite(value)
), changes AS (
    SELECT country_code, indicator_code,
           CASE
               WHEN indicator_code = 'CM.MKT.INDX.ZG' THEN
                   -- Each year after the baseline must have a reported return.
                   CASE WHEN count(*) FILTER (WHERE year > $base_year) = $end_year - $base_year
                        THEN 100 * (product(1 + value / 100)
                             FILTER (WHERE year > $base_year) - 1)
                   END
               WHEN indicator_code = 'GC.DOD.TOTL.GD.ZS' THEN
                   max(value) FILTER (WHERE year = $end_year)
                     - max(value) FILTER (WHERE year = $base_year)
               ELSE 100 * (
                   max(value) FILTER (WHERE year = $end_year)
                     / nullif(max(value) FILTER (WHERE year = $base_year), 0) - 1
               )
           END AS change
    FROM observations
    GROUP BY country_code, indicator_code
), countries AS (
    SELECT c."Country Code" AS country_code,
           '**' || c."Short Name" || '**' AS country,
           max(change) FILTER (WHERE indicator_code = 'NY.GDP.MKTP.KD') AS gdp,
           max(change) FILTER (WHERE indicator_code = 'NE.CON.PRVT.PC.KD') AS consumption,
           max(change) FILTER (WHERE indicator_code = 'CM.MKT.INDX.ZG') AS prices,
           max(change) FILTER (WHERE indicator_code = 'NE.GDI.FTOT.KD') AS investment,
           max(change) FILTER (WHERE indicator_code = 'GC.DOD.TOTL.GD.ZS') AS debt
    FROM read_parquet($countries) c
    LEFT JOIN changes ON changes.country_code = c."Country Code"
    -- WDI aggregate regions/income groups have no Region in the country dimension.
    WHERE c.Region IS NOT NULL
    GROUP BY c."Country Code", c."Short Name"
), scored AS (
    -- list_sum ignores missing metrics; an entirely missing row stays NULL.
    SELECT *, CAST(round(list_sum([gdp, consumption, prices, investment, debt]), 0) AS BIGINT) AS score
    FROM countries
), ranked AS (
    SELECT country_code,
           CAST(rank() OVER (ORDER BY score DESC) AS VARCHAR) ||
           CASE WHEN count(*) OVER (PARTITION BY score) > 1 THEN '=' ELSE '' END AS rank_label
    FROM scored
    WHERE score IS NOT NULL
)
SELECT s.country_code,
       s.country || CASE WHEN r.rank_label IS NOT NULL THEN ' (' || r.rank_label || ')' ELSE '' END AS country,
       s.gdp, s.consumption, s.prices, s.investment, s.debt, s.score, r.rank_label
FROM scored s
LEFT JOIN ranked r USING (country_code)
ORDER BY s.score DESC NULLS LAST, s.country, s.country_code
