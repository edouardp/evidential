-- Discover only league/window combinations with recorded, scored fixtures.
WITH played AS (
    SELECT competition, CAST(date AS DATE) AS match_date
    FROM games
    WHERE level = 'national' AND competition IS NOT NULL AND date IS NOT NULL
      AND gh IS NOT NULL AND ga IS NOT NULL
      AND home_ident IS NOT NULL AND away_ident IS NOT NULL
), windows AS (
    SELECT competition, start_month, match_date,
           YEAR(match_date) - CASE WHEN MONTH(match_date) < start_month THEN 1 ELSE 0 END AS season_start
    FROM played
    CROSS JOIN (VALUES (1), (7)) AS periods(start_month)
)
SELECT competition, start_month, season_start,
       COUNT(*) AS match_count, MIN(match_date) AS first_match, MAX(match_date) AS last_match
FROM windows
GROUP BY competition, start_month, season_start
ORDER BY competition, start_month, season_start DESC;
