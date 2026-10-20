-- Endpoint changes, not averages of annual growth rates. Keep every selected
-- country even when an indicator or endpoint is missing.
WITH selected(country_code, position) AS (
    VALUES ('DNK', 1), ('CHL', 2), ('IRL', 3), ('USA', 4), ('AUS', 5),
           ('CAN', 6), ('FRA', 7), ('PRT', 8), ('DEU', 9), ('ESP', 10)
), observations AS (
    SELECT country_code, indicator_code, year, value
    FROM read_parquet($observations, hive_partitioning = true)
    WHERE year BETWEEN $base_year AND $end_year
      AND country_code IN (SELECT country_code FROM selected)
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
)
SELECT s.country_code,
       '**' || c."Short Name" || '**' AS country,
       max(change) FILTER (WHERE indicator_code = 'NY.GDP.MKTP.KD') AS gdp,
       max(change) FILTER (WHERE indicator_code = 'NE.CON.PRVT.PC.KD') AS consumption,
       max(change) FILTER (WHERE indicator_code = 'CM.MKT.INDX.ZG') AS prices,
       max(change) FILTER (WHERE indicator_code = 'NE.GDI.FTOT.KD') AS investment,
       max(change) FILTER (WHERE indicator_code = 'GC.DOD.TOTL.GD.ZS') AS debt
FROM selected s
JOIN read_parquet($countries) c ON c."Country Code" = s.country_code
LEFT JOIN changes USING (country_code)
GROUP BY s.country_code, c."Short Name", s.position
ORDER BY s.position
