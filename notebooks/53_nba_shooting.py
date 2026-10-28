# /// script
# requires-python = ">=3.12"
# dependencies = ["marimo", "duckdb>=1.3", "evidential"]
# ///
"""A local NBA shooting explorer with player, shot-zone and game tables.

Run ``uv run marimo edit notebooks/53_nba_shooting.py``.
Set ``NBA_DATASET`` to override ``~/datasets/nba_data``.
"""

import marimo

__generated_with = "0.25.1"
app = marimo.App(width="full")


@app.cell
def imports():
    import os
    import re
    import shutil
    import tarfile
    import tempfile
    from pathlib import Path

    import duckdb
    import marimo as mo

    from evidential import EvidentialTable, col, domain, label

    return (
        EvidentialTable,
        Path,
        col,
        domain,
        duckdb,
        label,
        mo,
        os,
        re,
        shutil,
        tarfile,
        tempfile,
    )


@app.cell(hide_code=True)
def introduction(mo):
    mo.md("""
    # NBA · the shape of a shot

    Compare **shooting efficiency and shot selection**, then click a player to
    see where their shots came from and their game-by-game shooting log.
    Choose a season, regular season or playoffs, a team, and a minimum attempt
    count. The initial order is effective field-goal percentage, highest first.

    **FG% = makes / attempts. eFG% = (makes + ½ × three-point makes) / attempts.**
    The percentages use total makes and attempts, rather than averages of game
    percentages. Blue/teal stacks show **two-point / three-point attempt share**.
    The last-15-game FG% sparklines all use a fixed 0–100% scale, oldest first.

    These are **recorded field-goal attempts**. Free throws, games without a
    recorded attempt, and other box-score statistics are outside this view.
    A traded player's totals combine their teams unless a team filter is set.
    """)
    return


@app.cell
def archive_discovery(re):
    def discover_archives(root):
        archives = {}
        for path in (root / "datasets").glob("shotdetail_*.tar.xz"):
            match = re.fullmatch(r"shotdetail_(po_)?(\d{4})\.tar\.xz", path.name)
            if match:
                archives[
                    int(match[2]), "Playoffs" if match[1] else "Regular season"
                ] = path
        return archives

    return (discover_archives,)


@app.cell
def local_data(Path, discover_archives, mo, os):
    dataset_path = Path(
        os.environ.get("NBA_DATASET", "~/datasets/nba_data")
    ).expanduser()
    archives = discover_archives(dataset_path)
    mo.stop(
        not archives,
        mo.md(
            "No NBA shot-detail archives found. Set `NBA_DATASET` to the local "
            "`nba_data` repository, with `datasets/shotdetail_YYYY.tar.xz` files."
        ),
    )
    season_years = sorted({year for year, phase in archives}, reverse=True)
    sql_directory = mo.notebook_location() / "sql"
    player_sql = (sql_directory / "53_nba_players.sql").read_text()
    zone_sql = (sql_directory / "53_nba_zones.sql").read_text()
    game_sql = (sql_directory / "53_nba_games.sql").read_text()
    return archives, dataset_path, game_sql, player_sql, season_years, zone_sql


@app.cell
def season_control(mo, season_years):
    season_picker = mo.ui.dropdown(
        options={f"{year}–{str(year + 1)[-2:]}": year for year in season_years},
        value=f"{season_years[0]}–{str(season_years[0] + 1)[-2:]}",
        label="Season",
    )
    minimum_picker = mo.ui.number(
        start=1, stop=5000, step=25, value=100, label="Minimum FGA"
    )
    mo.hstack([season_picker, minimum_picker], justify="start", gap=2)
    return minimum_picker, season_picker


@app.cell
def phase_control(archives, mo, season_picker):
    phases = [
        phase
        for phase in ["Regular season", "Playoffs"]
        if (season_picker.value, phase) in archives
    ]
    phase_picker = mo.ui.dropdown(options=phases, value=phases[0], label="Season phase")
    phase_picker
    return (phase_picker,)


@app.cell
def archive_loader(Path, duckdb, shutil, tarfile, tempfile):
    def load_shots(archive_path):
        """Read only the expected CSV member; leave the dataset untouched."""
        with tempfile.TemporaryDirectory(prefix="evidential-nba-") as temporary:
            csv_path = Path(temporary) / "shots.csv"
            with tarfile.open(archive_path, "r:xz") as archive:
                member = archive.getmember(
                    archive_path.name.removesuffix(".tar.xz") + ".csv"
                )
                if not member.isfile():
                    raise ValueError(
                        "The shot-detail CSV must be a regular archive member"
                    )
                with (
                    archive.extractfile(member) as source,
                    csv_path.open("wb") as target,
                ):
                    shutil.copyfileobj(source, target)
            connection = duckdb.connect()
            connection.read_csv(str(csv_path), header=True, all_varchar=True).filter("""
                SHOT_ATTEMPTED_FLAG = '1' AND SHOT_MADE_FLAG IN ('0', '1')
                AND SHOT_TYPE IN ('2PT Field Goal', '3PT Field Goal')
            """).project("""
                GAME_ID AS game_id, GAME_EVENT_ID AS event_id,
                PLAYER_ID::BIGINT AS player_id, PLAYER_NAME AS player,
                TEAM_ID::BIGINT AS team_id, TEAM_NAME AS team,
                strptime(GAME_DATE, '%Y%m%d')::DATE AS game_date,
                VTM || ' @ ' || HTM AS matchup,
                coalesce(SHOT_ZONE_BASIC, 'Unclassified') AS zone,
                SHOT_MADE_FLAG::INTEGER AS made,
                (SHOT_TYPE = '3PT Field Goal')::INTEGER AS is_three
            """).create("shots")
        connection.execute("""
            CREATE VIEW player_games AS
            SELECT player_id, game_id, team_id, game_date,
                   any_value(player) AS player, any_value(team) AS team,
                   any_value(matchup) AS matchup,
                   count(*) AS fga, sum(made) AS fgm,
                   count(*) FILTER (WHERE is_three = 0) AS two_attempts,
                   sum(is_three) AS three_attempts, sum(made * is_three) AS three_made,
                   sum(made)::DOUBLE / count(*) AS fg_pct,
                   (sum(made) + 0.5 * sum(made * is_three)) / count(*) AS efg_pct
            FROM shots GROUP BY player_id, game_id, team_id, game_date
        """)
        return connection

    def query_rows(connection, sql, parameters=None):
        result = connection.execute(sql, parameters or {})
        names = [column[0] for column in result.description]
        return [dict(zip(names, row, strict=True)) for row in result.fetchall()]

    return load_shots, query_rows


@app.cell
def season_data(
    archives,
    load_shots,
    mo,
    phase_picker,
    query_rows,
    season_picker,
):
    archive_path = archives[season_picker.value, phase_picker.value]
    connection = load_shots(archive_path)
    season_summary = query_rows(
        connection,
        """
        SELECT count(*) AS attempts, count(DISTINCT game_id) AS games,
               count(DISTINCT player_id) AS players, count(DISTINCT team_id) AS teams,
               min(game_date) AS first_date, max(game_date) AS last_date,
               sum(made)::DOUBLE / nullif(count(*), 0) AS league_fg,
               count(*) - count(DISTINCT (game_id, event_id)) AS duplicate_events
        FROM shots
    """,
    )[0]
    mo.stop(
        not season_summary["attempts"],
        mo.md("No valid field-goal attempts in this archive."),
    )
    mo.stop(
        bool(season_summary["duplicate_events"]),
        mo.md(
            "This archive has repeated game/event identifiers. Resolve duplicate shot events "
            "in the dataset before using the shooting summaries."
        ),
    )
    return archive_path, connection, season_summary


@app.cell(hide_code=True)
def coverage(mo, season_summary):
    mo.md(f"""
    **{season_summary["games"]:,} recorded games** · {season_summary["attempts"]:,} attempts ·
    {season_summary["players"]:,} shooters · {season_summary["teams"]} teams ·
    {season_summary["first_date"]} → {season_summary["last_date"]}.
    League FG%: **{season_summary["league_fg"]:.1%}**.
    Coverage reflects the archive, not a claim that every scheduled game is present.
    """)
    return


@app.cell
def team_control(connection, mo, query_rows):
    teams = query_rows(
        connection, "SELECT DISTINCT team, team_id FROM shots ORDER BY team"
    )
    team_picker = mo.ui.dropdown(
        options={"All teams": None, **{row["team"]: row["team_id"] for row in teams}},
        value="All teams",
        label="Team",
    )
    team_picker
    return (team_picker,)


@app.cell
def matching_players(
    connection,
    minimum_picker,
    player_sql,
    query_rows,
    team_picker,
):
    players = query_rows(
        connection,
        player_sql,
        {"team": team_picker.value, "minimum": minimum_picker.value},
    )
    return (players,)


@app.cell(expand_output=True)
def tables(EvidentialTable, col, domain, label, mo):
    percentage = domain.numeric("fg-percent").bounds(0, 1)
    player_table = mo.ui.anywidget(
        EvidentialTable(
            [],
            title="Shooting leaders",
            select="player_id",
            search=True,
            page_size=12,
            border=False,
            row_lines=True,
            row_shading=False,
            empty_message="No player meets this attempt threshold; lower Minimum FGA.",
            columns=[
                col.text("player").bold(),
                col.text("teams").wrap(),
                col.integer("games").title("Games w/FGA"),
                col.integer("fga").title("FGA"),
                col.bar(
                    "fg_pct",
                    title="FG%",
                    format="pct1",
                    color="#2563eb",
                    label=label.fmt("pct1").auto_position("outside end"),
                ).domain(percentage),
                col.percent("efg_pct", decimals=1, title="eFG%"),
                col.stacked_bar(
                    "two_attempts",
                    "three_attempts",
                    normalize="percent",
                    labels="percent",
                    colors=["#2563eb", "#0f766e"],
                    label_align="center",
                    title="2PT · 3PT attempts",
                ),
                col.sparkline(
                    "recent_fg",
                    type="line",
                    width=150,
                    height=26,
                    markers="ends",
                    y_fmt="pct1",
                    title="Last 15 · FG%",
                ).domain(percentage),
            ],
        )
    )
    zone_table = mo.ui.anywidget(
        EvidentialTable(
            [],
            title="Shot zones",
            search=False,
            page_size=0,
            empty_rows=1,
            border=False,
            empty_message="Select a player above to explore their shot zones",
            columns=[
                col.text("zone"),
                col.bar(
                    "fga",
                    title="FGA",
                    format="num0",
                    color="#93c5fd",
                    label=label.auto_position("outside end"),
                ),
                col.percent("share", decimals=1),
                col.percent("fg_pct", decimals=1, title="FG%"),
                col.percent("league_fg", decimals=1, title="League FG%"),
                col.range(
                    "league_fg",
                    "fg_pct",
                    color="#0f766e",
                    color_negative="#dc2626",
                    direction_marker=True,
                    format="pct0",
                )
                .point("league_fg", color="#94a3b8", size=8)
                .point("fg_pct", color="#0f766e", size=9, outline=False)
                .title("FG% · league → player")
                .scale(domain=(0, 1), axis=True),
            ],
        )
    )
    game_table = mo.ui.anywidget(
        EvidentialTable(
            [],
            title="Shooting game log",
            search=True,
            page_size=12,
            border=False,
            empty_message="Select a player above to see their shooting game log",
            columns=[
                col.date("game_date", title="Date"),
                col.text("matchup"),
                col.text("team"),
                col.integer("fgm").title("FGM"),
                col.integer("fga").title("FGA"),
                col.percent("fg_pct", decimals=1, title="FG%"),
                col.integer("three_made").title("3PM"),
                col.integer("three_attempts").title("3PA"),
                col.bar(
                    "efg_pct",
                    title="eFG%",
                    format="pct1",
                    color="#0f766e",
                    label=label.fmt("pct1").auto_position("outside end"),
                ).scale(domain=(0, 1.5)),
                col.integer("field_goal_points").title("FG points"),
            ],
        )
    )
    mo.vstack([player_table, zone_table, game_table], gap=2)
    return game_table, player_table, zone_table


@app.cell
def update_players(
    minimum_picker,
    phase_picker,
    player_table,
    players,
    season_picker,
    season_summary,
    team_picker,
):
    with player_table.widget.hold_sync():
        player_table.widget.set_data(players)
        player_table.widget.update_options(
            title=f"Shooting leaders · {season_picker.value}–{str(season_picker.value + 1)[-2:]} · {phase_picker.value}",
            subtitle=f"{len(players):,} players · minimum {minimum_picker.value:g} FGA · {team_picker.selected_key or 'All teams'} · Click a row for detail.",
            caption=f"Games counts games with at least one recorded FGA. FG% and sparkline scales are 0–100%. League FG%: {season_summary['league_fg']:.1%}. eFG% may exceed 100%.",
        )
        if player_table.widget.selected not in {row["player_id"] for row in players}:
            player_table.widget.selected = None
    return


@app.cell
def selection(player_table):
    selected_player = player_table.widget.selected
    return (selected_player,)


@app.cell
def detail_data(
    connection,
    game_sql,
    players,
    query_rows,
    selected_player,
    team_picker,
    zone_sql,
):
    selected_name = next(
        (row["player"] for row in players if row["player_id"] == selected_player), None
    )
    parameters = {"player": selected_player, "team": team_picker.value}
    zones = query_rows(connection, zone_sql, parameters) if selected_name else []
    games = query_rows(connection, game_sql, parameters) if selected_name else []
    return games, selected_name, zones


@app.cell
def update_detail(game_table, games, selected_name, zone_table, zones):
    with zone_table.widget.hold_sync():
        zone_table.widget.set_data(zones)
        zone_table.widget.update_options(
            title=f"{selected_name} · Shot zones" if selected_name else "Shot zones",
            caption="Zone benchmarks use the full selected season/phase, including the player's attempts. Gray = league; teal = player; red connectors mark lower FG%. Share is the player's attempt share.",
        )
    with game_table.widget.hold_sync():
        game_table.widget.set_data(games)
        game_table.widget.update_options(
            title=f"{selected_name} · Shooting game log"
            if selected_name
            else "Shooting game log",
            caption="Newest game first. FG points = 2 × FGM + 3PM; free throws are excluded. eFG% can reach 150%.",
        )
    return


@app.cell(hide_code=True)
def attribution(archive_path, dataset_path, mo):
    mo.md(f"""
    Source: **NBA Stats shot details**, collected by **Vladislav Shufinskiy**
    (`shufinskiy/nba_data`). Local archive: `{dataset_path.name}/datasets/{archive_path.name}`.
    Season labels use the archive's starting year. WNBA files are kept separate
    and are not included in this NBA explorer.

    The notebook reads the expected CSV member into a temporary directory,
    materializes the selected season in DuckDB, and removes the temporary CSV.
    Filters reuse that in-memory table. It does not download, unpack into, or
    modify the dataset repository. Set `NBA_DATASET` to use another local clone.
    """)
    return


if __name__ == "__main__":
    app.run()
