# /// script
# requires-python = ">=3.12"
# dependencies = ["marimo", "duckdb>=1.3", "evidential"]
# ///
"""Twenty football teams: SQL highlights each team's biggest win and heaviest loss."""

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

    **Premier League, 2024/25 · 20 teams · 38 league matches each.**
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
    goal-margin scale across rows. Filtering retains each team's season highlights.
    """)
    return


@app.cell
def query_helpers():
    def season_rows(connection, sql, season_start=2024, competition="england"):
        return (
            connection.execute(sql, {"season_start": season_start, "competition": competition})
            .to_arrow_table()
            .to_pylist()
        )

    return (season_rows,)


@app.cell
def dataset(Path, duckdb, mo, os, season_rows):
    football_path = Path(
        os.environ.get(
            "FOOTBALL_PARQUET",
            "~/datasets/football-data/data/results/games.parquet",
        )
    ).expanduser()
    query_path = mo.notebook_location() / "sql" / "60_football_season_highlights.sql"
    season_sql = query_path.read_text()
    with duckdb.connect() as connection:
        if football_path.is_file():
            connection.read_parquet(str(football_path)).create_view("games")
            source_label = "Local football-data Parquet"
        else:
            snapshot_path = mo.notebook_location() / "data" / "60_football_england_2024_25.json"
            connection.read_json(str(snapshot_path)).create_view("games")
            source_label = "Committed 2024/25 match snapshot"
        teams = season_rows(connection, season_sql)
    return season_sql, source_label, teams


@app.cell
def season_table(EvidentialTable, col, mo, source_label, teams):
    season_highlights = mo.ui.anywidget(
        EvidentialTable(
            teams,
            title="Premier League · 2024/25",
            subtitle="Biggest wins in blue · heaviest losses in red · all tied extremes highlighted",
            caption=f"{source_label}. Source: football-data / worldclubratings.com, ODC Attribution 1.0. "
            "Match points = 3 × wins + draws; administrative adjustments are not included.",
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
    This is the domestic **2024/25 season**, selected from 1 July 2024 through
    30 June 2025. Cups, international fixtures and unplayed matches are excluded.
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
