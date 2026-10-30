-- Classify against the complete history BEFORE clipping the visible years.
-- A missing quarter is a real gap, not an implicit zero or an adjacent observation.
WITH countries AS (
    SELECT country_code, any_value(country) AS country FROM gdp_observed GROUP BY country_code
), calendar AS (
    SELECT unnest(generate_series(
        date_trunc('year', min(period_start)),
        date_trunc('year', max(period_start)) + INTERVAL 9 MONTH,
        INTERVAL 3 MONTH
    ))::DATE AS period_start
    FROM gdp_observed
), aligned AS (
    SELECT countries.*, calendar.period_start,
           year(calendar.period_start)::INTEGER AS year,
           quarter(calendar.period_start)::INTEGER AS quarter,
           year(calendar.period_start) * 4 + quarter(calendar.period_start) - 1 AS quarter_index,
           g.growth_percent, g.obs_status, g.obs_status_label
    FROM countries CROSS JOIN calendar
    LEFT JOIN gdp_observed g USING (country_code, period_start)
), neighbours AS (
    SELECT *, lag(growth_percent) OVER history AS previous_growth,
              lead(growth_percent) OVER history AS next_growth
    FROM aligned WINDOW history AS (PARTITION BY country_code ORDER BY period_start)
)
SELECT *, CASE
    WHEN growth_percent IS NULL THEN 'missing'
    WHEN growth_percent < 0 AND (previous_growth < 0 OR next_growth < 0) THEN 'recession'
    ELSE 'other' END AS category
FROM neighbours
