-- The benchmark always uses the whole selected season/phase, independent of team.
WITH player AS (
    SELECT zone, count(*) AS fga, sum(made) AS fgm,
           sum(made)::DOUBLE / count(*) AS fg_pct
    FROM shots WHERE player_id = $player AND ($team IS NULL OR team_id = $team)
    GROUP BY zone
), league AS (
    SELECT zone, sum(made)::DOUBLE / count(*) AS league_fg FROM shots GROUP BY zone
)
SELECT player.*, fga::DOUBLE / sum(fga) OVER () AS share, league.league_fg,
       100 * (fg_pct - league_fg) AS difference_pp
FROM player JOIN league USING (zone) ORDER BY fga DESC, zone
