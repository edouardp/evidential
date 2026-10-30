WITH visible AS (
    SELECT * FROM gdp_quarters WHERE year BETWEEN $start_year AND $end_year
      AND ($aggregates OR country_code NOT IN ('EA', 'EU', 'G20', 'G7', 'OECD', 'OECDE', 'USMCA'))
), changes AS (
    SELECT *, category IS DISTINCT FROM lag(category) OVER (
        PARTITION BY country_code ORDER BY quarter_index
    ) AS changed
    FROM visible
), islands AS (
    SELECT *, sum(changed::INTEGER) OVER (
        PARTITION BY country_code ORDER BY quarter_index
    ) AS island
    FROM changes
), intervals AS (
    SELECT country_code, any_value(country) AS country, island, category,
           min(quarter_index) / 4.0 AS start,
           (max(quarter_index) + 1) / 4.0 AS finish,
           arg_min(year || '-Q' || quarter, quarter_index) AS first_quarter,
           arg_max(year || '-Q' || quarter, quarter_index) AS last_quarter,
           count(*) AS quarters
    FROM islands GROUP BY country_code, island, category
), timelines AS (
SELECT country_code, any_value(country) AS country,
       list(struct_pack(start := start, "end" := finish, category := category,
                        first_quarter := first_quarter, last_quarter := last_quarter,
                        quarters := quarters) ORDER BY start) AS periods,
       sum(CASE WHEN category != 'missing' THEN quarters ELSE 0 END)::BIGINT AS observed_quarters,
       sum(CASE WHEN category = 'recession' THEN quarters ELSE 0 END)::BIGINT AS recession_quarters
FROM intervals GROUP BY country_code
)
SELECT t.*,
       -- Broad geographic display regions, explicitly mapped in this notebook.
       CASE
         WHEN t.country_code IN ('ARG','BRA','CAN','CHL','COL','CRI','MEX','USA') THEN 'Americas'
         WHEN t.country_code IN ('CHN','IDN','IND','ISR','JPN','KOR','SAU','TUR') THEN 'Asia'
         WHEN t.country_code IN ('AUS','NZL') THEN 'Oceania'
         WHEN t.country_code = 'ZAF' THEN 'Africa'
         WHEN t.country_code IN ('EA','EU','G20','G7','OECD','OECDE','USMCA') THEN 'Aggregates'
         WHEN t.country_code IN ('AUT','BEL','CHE','CZE','DEU','DNK','ESP','EST','FIN','FRA',
                                'GBR','GRC','HUN','IRL','ISL','ITA','LTU','LUX','LVA','NLD',
                                'NOR','POL','PRT','RUS','SVK','SVN','SWE') THEN 'Europe'
         ELSE 'Unclassified' END AS region,
       t.recession_quarters / nullif(t.observed_quarters, 0) AS recession_share,
       t.recession_quarters || ' recession quarters / ' || t.observed_quarters ||
           ' observed quarters (' || (($end_year - $start_year + 1) * 4) || ' possible)' AS coverage,
       g.value AS gdp_ppp, d.value AS debt_ratio, f.value AS fiscal_ratio,
       'Annual GDP, current-price PPP US dollars · ' || $end_year || chr(10) ||
           coalesce(format('{:,.2f}', g.value), 'No observation for this year') || chr(10) ||
           coalesce(g.status, '') AS gdp_detail,
       'General government gross debt / GDP · ' || $end_year || chr(10) ||
           coalesce(format('{:.2f}%', d.value * 100), 'No observation for this year') || chr(10) ||
           coalesce(d.status, '') AS debt_detail,
       'General government net lending (+) / borrowing (−), % GDP · ' || $end_year || chr(10) ||
           coalesce(format('{:.2f}%', f.value * 100), 'No observation for this year') || chr(10) ||
           coalesce(f.status, '') AS fiscal_detail
FROM timelines t
LEFT JOIN context_observed g ON g.country_code = t.country_code AND g.year = $end_year AND g.metric = 'gdp_ppp'
LEFT JOIN context_observed d ON d.country_code = t.country_code AND d.year = $end_year AND d.metric = 'debt_ratio'
LEFT JOIN context_observed f ON f.country_code = t.country_code AND f.year = $end_year AND f.metric = 'fiscal_ratio'
ORDER BY region, country
