# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo",
#     "duckdb",
#     "evidential",
# ]
# ///
"""Search football teams, inspect their result sparklines, and select match detail."""

import marimo

__generated_with = "0.25.1"
app = marimo.App(width="full")


@app.cell
def imports():
    import json
    import os
    from collections import defaultdict
    from pathlib import Path

    import duckdb
    import marimo as mo

    from evidential import EvidentialTable, col, label

    return EvidentialTable, Path, col, defaultdict, duckdb, json, label, mo, os


@app.cell
def introduction(mo):
    mo.md("""
    # Football results explorer

    Choose a calendar year and domestic league, search for a team, and click
    its row. The top table summarizes **all recorded matches** for those teams
    in the year, including international competitions. The bottom table lists
    the selected team's individual results. Click the selected row again to clear.

    Each sparkline rectangle is one match, oldest first: **up = win**, **center =
    draw**, **down = loss**. Magnitude never changes the rectangle's height.
    Enable the gradient to color by goal margin; draws stay at its gray midpoint.
    """)
    return


@app.cell
def dataset(Path, duckdb, json, mo, os):
    football_path = Path(
        os.environ.get("FOOTBALL_PARQUET", "~/datasets/football-data/data/results/games.parquet")
    ).expanduser()
    snapshot = json.loads((mo.notebook_location() / "data" / "46_football_england_2024.json").read_text())
    if football_path.is_file():
        with duckdb.connect() as metadata_connection:
            available_years = [
                row[0]
                for row in metadata_connection.execute(
                    "SELECT DISTINCT year(date) FROM read_parquet(?) WHERE date IS NOT NULL ORDER BY 1 DESC",
                    [str(football_path)],
                ).fetchall()
            ]
            available_competitions = [
                row[0]
                for row in metadata_connection.execute(
                    "SELECT DISTINCT competition FROM read_parquet(?) WHERE level = 'national' AND competition IS NOT NULL ORDER BY 1",
                    [str(football_path)],
                ).fetchall()
            ]
        default_year = max(available_years) - 1
        if default_year not in available_years:
            default_year = available_years[0]
        source_label = "Local football-data dataset"
    else:
        available_years = [snapshot["year"]]
        available_competitions = [snapshot["competition"]]
        default_year = snapshot["year"]
        source_label = "Committed real-data snapshot: England, 2024"
    football_sql = (mo.notebook_location() / "sql" / "46_football_outcomes.sql").read_text()
    return (
        available_competitions,
        available_years,
        default_year,
        football_path,
        football_sql,
        snapshot,
        source_label,
    )


@app.cell
def controls(available_competitions, available_years, default_year, mo):
    year_picker = mo.ui.dropdown(
        options={str(year): year for year in available_years}, value=str(default_year), label="Year"
    )
    competition_picker = mo.ui.dropdown(
        options=available_competitions,
        value="england" if "england" in available_competitions else available_competitions[0],
        label="Domestic league",
    )
    color_by_margin = mo.ui.switch(value=False, label="Color by goal margin")
    mo.hstack([year_picker, competition_picker, color_by_margin], justify="start", gap=2)
    return color_by_margin, competition_picker, year_picker


@app.cell
def summarize(defaultdict):
    def summarize_matches(matches):
        grouped = defaultdict(list)
        for match in matches:
            grouped[match["team_id"]].append(match)
        summaries = []
        for team_id, games in grouped.items():
            games = sorted(
                games, key=lambda game: (game["match_date"], game["competition"], game["opponent"], game["venue"])
            )
            summaries.append(
                {
                    "team_id": team_id,
                    "team": games[-1]["team"],
                    "country": games[-1]["country"],
                    "played": len(games),
                    "wins": sum(game["result"] == "Win" for game in games),
                    "draws": sum(game["result"] == "Draw" for game in games),
                    "losses": sum(game["result"] == "Loss" for game in games),
                    "outcomes": [
                        {
                            "date": f"{game['match_date']} · {game['opponent']} ({game['venue']}) · {game['competition']}",
                            "value": game["goal_margin"],
                        }
                        for game in games
                    ],
                }
            )
        return sorted(summaries, key=lambda team: team["team"])

    return (summarize_matches,)


@app.cell
def matching_data(
    competition_picker,
    duckdb,
    football_path,
    football_sql,
    snapshot,
    summarize_matches,
    year_picker,
):
    if football_path.is_file():
        with duckdb.connect() as connection:
            matches = (
                connection.execute(
                    football_sql,
                    {
                        "games": str(football_path),
                        "year": year_picker.value,
                        "competition": competition_picker.value,
                    },
                )
                .to_arrow_table()
                .to_pylist()
            )
    else:
        matches = snapshot["matches"]
    team_summaries = summarize_matches(matches)
    return matches, team_summaries


@app.cell
def team_list(EvidentialTable, col, mo):
    teams = mo.ui.anywidget(
        EvidentialTable(
            [],
            title="Teams",
            subtitle="Search for a team, then click its row to view its matches below.",
            select="team_id",
            search=True,
            page_size=12,
            border=False,
            row_lines=True,
            row_shading=False,
            freeze_columns=1,
            columns=[
                col.text("team").bold(),
                col.integer("played", title="Played"),
                col.integer("wins", title="Wins"),
                col.integer("draws", title="Draws"),
                col.integer("losses", title="Losses"),
                col.sparkline("outcomes", title="Outcomes · oldest → newest", type="change", width=184, y_fmt="num0"),
            ],
        )
    )
    mo.vstack([teams])
    return (teams,)


@app.cell
def update_teams(
    color_by_margin,
    competition_picker,
    source_label,
    team_summaries,
    teams,
    year_picker,
):
    with teams.widget.hold_sync():
        teams.widget.set_data(team_summaries)
        _outcome_options = next(
            column["sparkline_options"] for column in teams.widget.columns if column["name"] == "outcomes"
        )
        if _outcome_options.get("type", "line") == "change":
            teams.widget.set_column(
                "outcomes",
                sparkline_options={
                    **_outcome_options,
                    "color_scale": ["#b2182b", "#b8bcc2", "#2166ac"] if color_by_margin.value else None,
                    "color_domain": (-6, 6) if color_by_margin.value else None,
                },
            )
        teams.widget.update_options(
            title=f"{competition_picker.value.title()} teams · {year_picker.value}",
            subtitle=f"{source_label} · League participants; summaries include all recorded competitions. Click a row below.",
        )
        if teams.widget.selected not in {team["team_id"] for team in team_summaries}:
            teams.widget.selected = None
    return


@app.cell
def selection(teams):
    selected_team = teams.widget.selected
    return (selected_team,)


@app.cell
def match_list(EvidentialTable, col, label, mo):
    match_details = mo.ui.anywidget(
        EvidentialTable(
            [],
            title="Match details",
            empty_message="Select a team in the table above",
            search=True,
            page_size=15,
            border=False,
            row_lines=True,
            row_shading=False,
            columns=[
                col.date("match_date", title="Date"),
                col.text("opponent", title="Opponent"),
                col.text("competition", title="Competition"),
                col.text("venue", title="Venue"),
                col.text("score", title="Score · team first").align("center"),
                col.chip("result", title="Result", scale="@result_color"),
                col.bar(
                    "goal_margin",
                    title="Goal margin",
                    center=True,
                    color="#2166ac",
                    color_negative="#b2182b",
                    label=label.fmt("num0").auto_position("outside start"),
                ),
            ],
        )
    )
    mo.vstack([match_details])
    return (match_details,)


@app.cell
def update_details(
    match_details,
    matches,
    selected_team,
    team_summaries,
    year_picker,
):
    selected_summary = next((team for team in team_summaries if team["team_id"] == selected_team), None)
    selected_matches = [game for game in matches if selected_summary and game["team_id"] == selected_team]
    with match_details.widget.hold_sync():
        match_details.widget.set_data(
            sorted(selected_matches, key=lambda game: (game["match_date"], game["competition"], game["opponent"]))
        )
        match_details.widget.update_options(
            title=f"{selected_summary['team']} · {year_picker.value}" if selected_summary else "Match details",
            subtitle=f"{len(selected_matches)} recorded matches · scores show the selected team's goals first"
            if selected_summary
            else "",
        )
    return


@app.cell
def notes(mo):
    mo.md("""
    `col.sparkline("outcomes", type="change")` uses the goal margin directly.
    `steady=(low, high)` changes the inclusive central range; the default `(0, 0)`
    classifies draws. Rectangles shift up/down by half their height, leaving
    missing observations as gaps.

    A `color_scale` can be a named palette such as `"RdBu"` or a list of colors.
    Its midpoint anchors the **entire steady interval**. Each side interpolates
    independently to `color_domain`'s endpoints. This demo fixes them at −6 and +6
    goals, clamping more extreme scores. Without explicit endpoints, all matching
    teams share inferred bounds before pagination.

    The default year is the year before the latest observation. Set
    `FOOTBALL_PARQUET` to use another copy of the results parquet. If the local
    bundle is absent, the committed England 2024 snapshot keeps the demo usable.
    The source covers domestic top divisions and selected international
    competitions; it does not include every domestic cup.

    Source: **football-data / worldclubratings.com**, distributed under the
    Open Data Commons Attribution License 1.0.
    """)
    return


if __name__ == "__main__":
    app.run()
