-- One bar per league match. Compute extremes before collecting each team's array.
WITH season_matches AS (
    SELECT home, away, home_ident, away_ident, CAST(date AS DATE) AS match_date, gh, ga
    FROM games
    WHERE competition = $competition AND level = 'national'
      AND CAST(date AS DATE) >= make_date($season_start, $start_month, 1)
      AND CAST(date AS DATE) < make_date($season_start + 1, $start_month, 1)
      AND gh IS NOT NULL AND ga IS NOT NULL
      AND home_ident IS NOT NULL AND away_ident IS NOT NULL
), perspectives AS (
    SELECT home_ident AS team_id, home AS team, match_date,
           away AS opponent, 'Home' AS venue, gh AS goals_for, ga AS goals_against
    FROM season_matches
    UNION ALL
    SELECT away_ident AS team_id, away AS team, match_date,
           home AS opponent, 'Away' AS venue, ga AS goals_for, gh AS goals_against
    FROM season_matches
), margins AS (
    SELECT *, goals_for - goals_against AS margin
    FROM perspectives
), extremes AS (
    SELECT *, MAX(margin) OVER (PARTITION BY team_id) AS best,
              MIN(margin) OVER (PARTITION BY team_id) AS worst
    FROM margins
), colored AS (
    SELECT *,
        CASE WHEN margin = best AND best > 0 THEN '#2166ac'
             WHEN margin = worst AND worst < 0 THEN '#b2182b'
             ELSE '#a7b4c2' END AS color,
        CASE WHEN margin = best AND best > 0 THEN 'Biggest win'
             WHEN margin = worst AND worst < 0 THEN 'Heaviest loss'
             ELSE NULL END AS highlight
    FROM extremes
)
SELECT team_id, team, COUNT(*) AS played,
       COUNT(*) FILTER (WHERE margin > 0) AS wins,
       COUNT(*) FILTER (WHERE margin = 0) AS draws,
       COUNT(*) FILTER (WHERE margin < 0) AS losses,
       SUM(CASE WHEN margin > 0 THEN 3 WHEN margin = 0 THEN 1 ELSE 0 END) AS match_points,
       SUM(margin) AS goal_difference,
       MAX(margin) FILTER (WHERE margin > 0) AS biggest_win,
       MIN(margin) FILTER (WHERE margin < 0) AS heaviest_loss,
       LIST(STRUCT_PACK(
           match := CAST(match_date AS VARCHAR) || ' · ' || opponent || ' (' || venue || ')',
           margin := margin,
           color := color,
           score := CAST(goals_for AS VARCHAR) || '–' || CAST(goals_against AS VARCHAR),
           highlight := highlight
       ) ORDER BY match_date, opponent, venue) AS season
FROM colored
GROUP BY team_id, team
ORDER BY match_points DESC, goal_difference DESC, team;
