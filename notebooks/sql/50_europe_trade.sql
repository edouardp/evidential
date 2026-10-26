-- Goods and services, current US dollars. The six largest traders in the
-- WDI Europe & Central Asia region in 2024 are all European economies.
WITH trade AS (
    SELECT
        c."Country Code" AS country_code,
        c."Short Name" AS country,
        max(o.value) FILTER (WHERE o.indicator_code = 'NE.IMP.GNFS.CD') AS imports,
        max(o.value) FILTER (WHERE o.indicator_code = 'NE.EXP.GNFS.CD') AS exports
    FROM observations o
    JOIN country c ON o.country_code = c."Country Code"
    WHERE o.year = 2024
      AND c.Region = 'Europe & Central Asia'
      AND o.indicator_code IN ('NE.IMP.GNFS.CD', 'NE.EXP.GNFS.CD')
    GROUP BY c."Country Code", c."Short Name"
)
SELECT *, imports + exports AS total_trade
FROM trade
WHERE imports IS NOT NULL AND exports IS NOT NULL
ORDER BY total_trade DESC, country
LIMIT 6
