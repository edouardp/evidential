# /// script
# requires-python = ">=3.12"
# dependencies = ["marimo", "duckdb>=1.3", "evidential"]
# ///
"""Choose a football league and year; SQL highlights each team's biggest results."""

import marimo

__generated_with = "0.25.1"
app = marimo.App(width="full")


@app.cell
def imports():
    import os
    from pathlib import Path

    import duckdb
    import marimo as mo

    from evidential import EvidentialTable, col

    return EvidentialTable, Path, col, duckdb, mo, os


@app.cell(hide_code=True)
def introduction(mo):
    mo.md("""
    # A season's biggest results

    Choose a **league**, a **July–June season or calendar year**, and a **year**.
    The default is England, 2024/25: 20 teams with 38 league matches each.
    Each bar is one match's goal margin, oldest first: wins rise above zero,
    losses fall below it, and draws sit on the baseline. Every row uses the same
    vertical scale. **Blue** highlights that team's biggest win; **red** highlights
    its heaviest loss; the remaining matches are muted gray. Tied extremes are
    all highlighted. Hover a bar for the date, opponent, venue, score and highlight.

    The query calculates the extremes and puts a `color` on each observation.
    There is no special maximum/minimum setting in the sparkline renderer:

    ```python
    col.sparkline(
        "season", type="bar", x="match", y="margin", width=440,
    ).domain("goal_margin")
    ```

    `match` is a categorical date/opponent label, so every match has an equal
    slot, even when the fixture calendar is uneven. The named domain shares the
    goal-margin scale across rows. Table search retains each team's highlights;
    changing the league or date window recomputes them in SQL.
    """)
    return


@app.cell
def query_helpers():
    def register_games(connection, path, parquet):
        relation = connection.read_parquet(str(path)) if parquet else connection.read_json(str(path))
        relation.create_view("games")

    def season_rows(connection, sql, season_start=2024, competition="england", start_month=7):
        return (
            connection.execute(
                sql, {"season_start": season_start, "competition": competition, "start_month": start_month}
            )
            .to_arrow_table()
            .to_pylist()
        )

    return register_games, season_rows


@app.cell
def dataset(Path, duckdb, mo, os, register_games):
    football_path = Path(
        os.environ.get(
            "FOOTBALL_PARQUET",
            "~/datasets/football-data/data/results/games.parquet",
        )
    ).expanduser()
    query_path = mo.notebook_location() / "sql" / "60_football_season_highlights.sql"
    season_sql = query_path.read_text()
    periods_sql = (mo.notebook_location() / "sql" / "60_football_available_periods.sql").read_text()
    use_parquet = football_path.is_file()
    games_path = football_path if use_parquet else mo.notebook_location() / "data" / "60_football_england_2024_25.json"
    source_label = "Local football-data Parquet" if use_parquet else "Committed 2024/25 match snapshot"
    with duckdb.connect() as metadata_connection:
        register_games(metadata_connection, games_path, use_parquet)
        available_periods = metadata_connection.execute(periods_sql).to_arrow_table().to_pylist()
    if not available_periods:
        raise ValueError("The data source contains no played national-league matches")
    leagues = sorted({period["competition"] for period in available_periods})
    return (
        available_periods,
        games_path,
        leagues,
        season_sql,
        source_label,
        use_parquet,
    )


@app.cell
def league_controls(leagues, mo):
    league_options = {league.replace("_", " ").title(): league for league in leagues}
    default_league = "england" if "england" in leagues else leagues[0]
    league_picker = mo.ui.dropdown(
        options=league_options,
        value=default_league.replace("_", " ").title(),
        label="League",
        searchable=len(leagues) > 30,
    )
    window_picker = mo.ui.dropdown(
        options={"July–June season": 7, "Calendar year": 1},
        value="July–June season",
        label="Date window",
    )
    return league_picker, window_picker


@app.cell
def year_control(available_periods, league_picker, mo, window_picker):
    years = sorted(
        {
            period["season_start"]
            for period in available_periods
            if period["competition"] == league_picker.value and period["start_month"] == window_picker.value
        },
        reverse=True,
    )
    year_options = {f"{year}/{(year + 1) % 100:02}" if window_picker.value == 7 else str(year): year for year in years}
    default_year = 2024 if 2024 in years else years[0]
    default_label = f"{default_year}/{(default_year + 1) % 100:02}" if window_picker.value == 7 else str(default_year)
    year_picker = mo.ui.dropdown(options=year_options, value=default_label, label="Year")
    return (year_picker,)


@app.cell
def controls(league_picker, mo, window_picker, year_picker):
    mo.hstack([league_picker, window_picker, year_picker], justify="start", gap=2)
    return


@app.cell
def matching_data(
    available_periods,
    duckdb,
    games_path,
    league_picker,
    register_games,
    season_rows,
    season_sql,
    use_parquet,
    window_picker,
    year_picker,
):
    with duckdb.connect() as query_connection:
        register_games(query_connection, games_path, use_parquet)
        teams = season_rows(query_connection, season_sql, year_picker.value, league_picker.value, window_picker.value)
    coverage = next(
        period
        for period in available_periods
        if period["competition"] == league_picker.value
        and period["start_month"] == window_picker.value
        and period["season_start"] == year_picker.value
    )
    period_label = (
        f"{year_picker.value}/{(year_picker.value + 1) % 100:02}"
        if window_picker.value == 7
        else str(year_picker.value)
    )
    return coverage, period_label, teams


@app.cell
def season_table(EvidentialTable, col, mo):
    season_highlights = mo.ui.anywidget(
        EvidentialTable(
            [],
            title="A season's biggest results",
            subtitle="Biggest wins in blue · heaviest losses in red · all tied extremes highlighted",
            border=False,
            row_lines=False,
            row_shading=True,
            search=True,
            page_size=0,
            freeze_columns=1,
            columns=[
                col.text("team").bold(),
                col.integer("played"),
                col.integer("wins"),
                col.integer("draws"),
                col.integer("losses"),
                col.integer("match_points"),
                col.integer("goal_difference", title="GD"),
                col.integer("biggest_win"),
                col.integer("heaviest_loss"),
                col.sparkline(
                    "season",
                    type="bar",
                    x="match",
                    y="margin",
                    width=440,
                    y_fmt="num0",
                    title="Goal margin · oldest → newest",
                ).domain("goal_margin"),
            ],
        )
    )
    season_highlights
    return (season_highlights,)


@app.cell
def update_table(
    coverage,
    league_picker,
    period_label,
    season_highlights,
    source_label,
    teams,
):
    appearances = [team["played"] for team in teams]
    played_label = (
        str(min(appearances)) if min(appearances) == max(appearances) else f"{min(appearances)}–{max(appearances)}"
    )
    with season_highlights.widget.hold_sync():
        season_highlights.widget.set_data(teams)
        season_highlights.widget.update_options(
            title=f"{league_picker.value.replace('_', ' ').title()} · {period_label}",
            subtitle=f"{len(teams)} teams · {coverage['match_count']} matches · {played_label} per team · "
            "biggest wins in blue · heaviest losses in red",
            caption=f"{source_label}. Recorded matches: {coverage['first_match']} to {coverage['last_match']}. "
            "Coverage may be partial; all tied extremes are highlighted. "
            "Match points = 3 × wins + draws; administrative adjustments are not included. "
            "Source: football-data / worldclubratings.com, ODC Attribution 1.0.",
        )
    return


@app.cell(hide_code=True)
def sql_explanation(mo, season_sql):
    explanation = mo.md("""
    ## The colors come from SQL

    Window functions find `MAX(margin)` and `MIN(margin)` **within each team**,
    after filtering to this league season. A `CASE` expression assigns the colors
    before `LIST(STRUCT_PACK(...))` collects the chronological observations.
    Positive/negative guards prevent draws being called wins, or a winless team's
    least-bad result being called its biggest win. The raw array also carries
    the score and highlight description for the tooltip.
    """)
    mo.vstack(
        [
            explanation,
            mo.accordion({"Show the query used by this table": mo.md(f"```sql\n{season_sql}\n```")}),
        ]
    )
    return


@app.cell(hide_code=True)
def notes(mo):
    mo.md("""
    The selectors list leagues and date windows with recorded results in the
    source. **July–June** selects 1 July of the starting year through 30 June
    of the next; **calendar year** selects January through December. These are
    explicit date windows, not provider season identifiers: postponed fixtures
    can cross a boundary. Choose the convention appropriate to the league.
    Recorded dates and match counts are shown, including partial years. Cups,
    international fixtures and unplayed matches are excluded.
    Each match contributes one perspective for each team. Sorting uses match
    points, then goal difference, then team name; this is not an official table
    with disciplinary adjustments or a complete league tie-break procedure.

    Set `FOOTBALL_PARQUET` to use another copy of the local results product.
    Without it, the same SQL runs against the committed raw 380-match snapshot;
    highlights are still computed at notebook execution, not baked into the data.
    Data: **football-data / worldclubratings.com**,
    [Open Data Commons Attribution License 1.0](https://opendatacommons.org/licenses/by/1-0/).
    """)
    return


if __name__ == "__main__":
    app.run()
