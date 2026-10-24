-- Select league participants, then retain all their recorded matches in the year.
WITH year_matches AS (
    SELECT home, away, home_ident, away_ident, home_country, away_country,
           date, gh, ga, competition, level
    FROM read_parquet($games)
    WHERE date >= make_date($year, 1, 1)
      AND date < make_date($year + 1, 1, 1)
      AND gh IS NOT NULL AND ga IS NOT NULL
      AND home_ident IS NOT NULL AND away_ident IS NOT NULL
), league_teams AS (
    SELECT home_ident AS team_id FROM year_matches
    WHERE competition = $competition AND level = 'national'
    UNION
    SELECT away_ident AS team_id FROM year_matches
    WHERE competition = $competition AND level = 'national'
), team_matches AS (
    SELECT home_ident AS team_id, home AS team, home_country AS country,
           date, away AS opponent, 'Home' AS venue, competition, level,
           gh AS goals_for, ga AS goals_against
    FROM year_matches
    UNION ALL
    SELECT away_ident AS team_id, away AS team, away_country AS country,
           date, home AS opponent, 'Away' AS venue, competition, level,
           ga AS goals_for, gh AS goals_against
    FROM year_matches
)
SELECT t.*, CAST(t.date AS VARCHAR) AS match_date,
       t.goals_for - t.goals_against AS goal_margin,
       CAST(t.goals_for AS VARCHAR) || '–' || CAST(t.goals_against AS VARCHAR) AS score,
       CASE WHEN t.goals_for > t.goals_against THEN 'Win'
            WHEN t.goals_for = t.goals_against THEN 'Draw' ELSE 'Loss' END AS result,
       CASE WHEN t.goals_for > t.goals_against THEN '#2166ac'
            WHEN t.goals_for = t.goals_against THEN '#b8bcc2' ELSE '#b2182b' END AS result_color
FROM team_matches AS t
JOIN league_teams AS l USING (team_id)
ORDER BY t.team_id, t.date, t.competition, t.opponent, t.venue;
