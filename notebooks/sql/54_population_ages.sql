-- World Bank WDI 2024, sourced from UN World Population Prospects.
-- Inputs: observations and country views, as in notebooks 23 and 34.
-- Age percentages have SEX-SPECIFIC denominators. Weight by male/female
-- population before combining; never average the two percentages.
WITH selected(code) AS (
    VALUES ('NER'), ('UGA'), ('KEN'), ('IND'), ('IDN'), ('BRA'),
           ('MEX'), ('CHN'), ('USA'), ('GBR'), ('DEU'), ('JPN')
), bands(code, age) AS (
    VALUES ('0004', 0), ('0509', 0), ('1014', 10), ('1519', 10),
           ('2024', 20), ('2529', 20), ('3034', 30), ('3539', 30),
           ('4044', 40), ('4549', 40), ('5054', 50), ('5559', 50),
           ('6064', 60), ('6569', 60), ('7074', 70), ('7579', 70), ('80UP', 80)
), population AS (
    SELECT country_code,
           MAX(value) FILTER (WHERE indicator_code = 'SP.POP.TOTL.MA.IN') AS male,
           MAX(value) FILTER (WHERE indicator_code = 'SP.POP.TOTL.FE.IN') AS female
    FROM observations
    JOIN selected ON selected.code = country_code
    WHERE year = 2024
      AND indicator_code IN ('SP.POP.TOTL.MA.IN', 'SP.POP.TOTL.FE.IN')
    GROUP BY country_code
    HAVING male > 0 AND female > 0
), shares AS (
    SELECT o.country_code, b.age,
           SUM(o.value / 100 * CASE SUBSTR(o.indicator_code, 13, 2)
               WHEN 'MA' THEN p.male ELSE p.female END) / (p.male + p.female) AS share
    FROM observations o
    JOIN population p USING (country_code)
    JOIN bands b ON b.code = SUBSTR(o.indicator_code, 8, 4)
    WHERE o.year = 2024
      AND o.indicator_code LIKE 'SP.POP.%.5Y'
      AND SUBSTR(o.indicator_code, 13, 2) IN ('MA', 'FE')
      AND o.value IS NOT NULL
    GROUP BY o.country_code, b.age, p.male, p.female
    HAVING COUNT(*) = CASE WHEN b.age = 80 THEN 2 ELSE 4 END
), wide AS (
    SELECT country_code,
           MAX(share) FILTER (WHERE age = 0) AS age_0_9,
           MAX(share) FILTER (WHERE age = 10) AS age_10_19,
           MAX(share) FILTER (WHERE age = 20) AS age_20_29,
           MAX(share) FILTER (WHERE age = 30) AS age_30_39,
           MAX(share) FILTER (WHERE age = 40) AS age_40_49,
           MAX(share) FILTER (WHERE age = 50) AS age_50_59,
           MAX(share) FILTER (WHERE age = 60) AS age_60_69,
           MAX(share) FILTER (WHERE age = 70) AS age_70_79,
           MAX(share) FILTER (WHERE age = 80) AS age_80_plus,
           MIN(share) AS age_min, MAX(share) AS age_max
    FROM shares
    GROUP BY country_code
    HAVING COUNT(*) = 9
)
SELECT w.country_code, c."Short Name" AS country,
       c."Income Group" AS income_group, 2024 AS year,
       p.male + p.female AS population,
       w.* EXCLUDE (country_code)
FROM wide w
JOIN country c ON c."Country Code" = w.country_code
JOIN population p USING (country_code)
ORDER BY age_0_9 DESC, country;
