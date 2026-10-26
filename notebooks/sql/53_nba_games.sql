SELECT game_date, matchup, team, fga, fgm, three_attempts, three_made,
       fg_pct, efg_pct, 2 * fgm + three_made AS field_goal_points
FROM player_games
WHERE player_id = $player AND ($team IS NULL OR team_id = $team)
ORDER BY game_date DESC, game_id DESC
