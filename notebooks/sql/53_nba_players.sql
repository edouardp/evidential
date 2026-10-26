-- A traded player is one row across all teams, or just the selected team's stint.
WITH matching AS (
    SELECT * FROM player_games WHERE ($team IS NULL OR team_id = $team)
), totals AS (
    SELECT player_id, arg_max(player, game_date) AS player,
           string_agg(DISTINCT team, ' · ' ORDER BY team) AS teams,
           count(*) AS games, sum(fga) AS fga, sum(fgm) AS fgm,
           sum(two_attempts) AS two_attempts, sum(three_attempts) AS three_attempts,
           sum(three_made) AS three_made,
           sum(fgm)::DOUBLE / sum(fga) AS fg_pct,
           (sum(fgm) + 0.5 * sum(three_made)) / sum(fga) AS efg_pct
    FROM matching GROUP BY player_id HAVING sum(fga) >= $minimum
), recent AS (
    SELECT *, row_number() OVER (
        PARTITION BY player_id ORDER BY game_date DESC, game_id DESC
    ) AS recency FROM matching
), history AS (
    SELECT player_id, list(struct_pack(
        date := strftime(game_date, '%Y-%m-%d') || ' · ' || matchup,
        value := fg_pct
    ) ORDER BY game_date, game_id) AS recent_fg
    FROM recent WHERE recency <= 15 GROUP BY player_id
)
SELECT totals.*, history.recent_fg FROM totals JOIN history USING (player_id)
ORDER BY efg_pct DESC, fga DESC, player
