"""SQL-generated observation colors preserve season scope, ties and missing outcomes."""

import runpy
from pathlib import Path

import duckdb
import pytest

ROOT = Path(__file__).resolve().parents[2]
NOTEBOOK = ROOT / "notebooks/60_football_season_highlights.py"
SQL = (ROOT / "notebooks/sql/60_football_season_highlights.sql").read_text()
PERIODS_SQL = (ROOT / "notebooks/sql/60_football_available_periods.sql").read_text()
SNAPSHOT = ROOT / "notebooks/data/60_football_england_2024_25.json"


@pytest.fixture
def season():
    with duckdb.connect() as connection:
        connection.execute("""CREATE TABLE games (
            home VARCHAR, away VARCHAR, home_ident VARCHAR, away_ident VARCHAR,
            date DATE, gh INTEGER, ga INTEGER, competition VARCHAR, level VARCHAR
        )""")
        matches = [
            ("Alpha", "Beta", "2024-09-02", 0, 3, "england", "national"),
            ("Alpha", "Beta", "2024-07-01", 4, 0, "england", "national"),
            ("Alpha", "Gamma", "2024-08-01", 5, 1, "england", "national"),
            ("Gamma", "Alpha", "2024-09-01", 3, 0, "england", "national"),
            ("Alpha", "Gamma", "2024-10-01", 1, 0, "england", "national"),
            ("Alpha", "Delta", "2024-10-02", 0, 0, "england", "national"),
            ("Alpha", "Beta", "2025-06-30", 1, 0, "england", "national"),
            ("Winless", "Unbeaten", "2024-11-01", 0, 2, "england", "national"),
            ("Alpha", "Beta", "2024-06-30", 99, 0, "england", "national"),
            ("Alpha", "Beta", "2025-07-01", 99, 0, "england", "national"),
            ("Alpha", "Beta", "2024-12-01", 99, 0, "cup", "national"),
            ("Alpha", "Beta", "2024-12-02", 99, 0, "england", "international"),
            ("Alpha", "Beta", "2024-12-03", None, 0, "england", "national"),
            ("Alpha", "Beta", "2024-11-01", 8, 0, "france", "national"),
        ]
        connection.executemany(
            "INSERT INTO games VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            [
                (home, away, f"{home} (England)", f"{away} (England)", date, gh, ga, competition, level)
                for home, away, date, gh, ga, competition, level in matches
            ],
        )
        yield connection


def query(connection, year=2024, league="england", start_month=7):
    return (
        connection.execute(SQL, {"season_start": year, "competition": league, "start_month": start_month})
        .to_arrow_table()
        .to_pylist()
    )


def test_sql_colors_all_tied_extremes_and_orders_the_original_matches(season):
    teams = query(season)
    alpha = next(row for row in teams if row["team"] == "Alpha")
    assert (alpha["played"], alpha["wins"], alpha["draws"], alpha["losses"]) == (7, 4, 1, 2)
    assert alpha["match_points"] == 13
    assert alpha["goal_difference"] == 4
    assert alpha["biggest_win"] == 4 and alpha["heaviest_loss"] == -3
    points = alpha["season"]
    assert [point["margin"] for point in points] == [4, 4, -3, -3, 1, 0, 1]
    assert [point["color"] for point in points] == [
        "#2166ac",
        "#2166ac",
        "#b2182b",
        "#b2182b",
        "#a7b4c2",
        "#a7b4c2",
        "#a7b4c2",
    ]
    assert points[0]["score"] == "4–0" and "Beta (Home)" in points[0]["match"]
    assert points[2]["score"] == "0–3" and "Gamma (Away)" in points[2]["match"]
    assert points[0]["highlight"] == "Biggest win"
    assert points[2]["highlight"] == "Heaviest loss"
    assert points[5]["highlight"] is None
    assert sum(row["played"] for row in teams) == 16
    assert sum(row["goal_difference"] for row in teams) == 0
    assert all(point["margin"] != 99 for row in teams for point in row["season"])
    assert {row["team"] for row in query(season, 2025)} == {"Alpha", "Beta"}


def test_draw_only_winless_and_unbeaten_teams_do_not_get_false_highlights(season):
    teams = {row["team"]: row for row in query(season)}
    assert teams["Delta"]["biggest_win"] is None and teams["Delta"]["heaviest_loss"] is None
    assert teams["Delta"]["season"][0]["color"] == "#a7b4c2"
    assert teams["Winless"]["biggest_win"] is None
    assert teams["Winless"]["season"][0]["highlight"] == "Heaviest loss"
    assert teams["Unbeaten"]["heaviest_loss"] is None
    assert teams["Unbeaten"]["season"][0]["highlight"] == "Biggest win"


def test_discovery_and_queries_respect_league_year_and_window_convention(season):
    periods = season.execute(PERIODS_SQL).to_arrow_table().to_pylist()
    england = [period for period in periods if period["competition"] == "england"]
    assert {(period["start_month"], period["season_start"]) for period in england} == {
        (7, 2023),
        (7, 2024),
        (7, 2025),
        (1, 2024),
        (1, 2025),
    }
    july = next(period for period in england if period["start_month"] == 7 and period["season_start"] == 2024)
    assert july["match_count"] == 8
    assert str(july["first_match"]) == "2024-07-01" and str(july["last_match"]) == "2025-06-30"
    french = query(season, league="france")
    assert {row["team"] for row in french} == {"Alpha", "Beta"}
    assert next(row for row in french if row["team"] == "Alpha")["biggest_win"] == 8
    calendar = next(row for row in query(season, start_month=1) if row["team"] == "Alpha")
    assert calendar["biggest_win"] == 99
    assert calendar["season"][0]["match"].startswith("2024-06-30")
    assert all(point["match"].startswith("2024-") for point in calendar["season"])
    assert calendar["season"][0]["color"] == "#2166ac"
    assert calendar["season"][1]["color"] == "#a7b4c2"  # The July 4–0 is no longer the maximum.


def test_real_snapshot_has_twenty_complete_teams_and_keeps_raw_fixtures():
    with duckdb.connect() as connection:
        connection.read_json(str(SNAPSHOT)).create_view("games")
        assert connection.sql("SELECT count(*) FROM games").fetchone()[0] == 380
        assert "color" not in connection.sql("SELECT * FROM games LIMIT 0").columns
        teams = query(connection)
    assert len(teams) == 20 and all(row["played"] == 38 and len(row["season"]) == 38 for row in teams)
    assert sum(row["goal_difference"] for row in teams) == 0
    for team in teams:
        points = team["season"]
        margins = [point["margin"] for point in points]
        assert [point["match"][:10] for point in points] == sorted(point["match"][:10] for point in points)
        for point in points:
            expected = (
                "#2166ac"
                if point["margin"] == max(margins) and point["margin"] > 0
                else ("#b2182b" if point["margin"] == min(margins) and point["margin"] < 0 else "#a7b4c2")
            )
            assert point["color"] == expected


def test_notebook_runs_offline_with_query_generated_colors(monkeypatch, tmp_path):
    monkeypatch.setenv("FOOTBALL_PARQUET", str(tmp_path / "missing.parquet"))
    _, definitions = runpy.run_path(str(NOTEBOOK))["app"].run()
    table = definitions["season_highlights"].widget
    assert len(table.rows) == 20
    assert definitions["source_label"] == "Committed 2024/25 match snapshot"
    sparkline = table.columns[-1]
    assert sparkline["sparkline_options"]["type"] == "bar"
    assert sparkline["sparkline_options"]["x"] == "match"
    assert sparkline["domain"]["name"] == "goal_margin"
    for name in ("biggest_win", "heaviest_loss"):
        column = next(column for column in table.columns if column["name"] == name)
        assert column["viz"] == "color"
        assert column["color_options"] == {"color_scale": ["#b2182b", "#ffffffcc", "#2166ac"], "midpoint": 0}
        assert column["domain"] == sparkline["domain"]
    assert sum(len(row["season"]) for row in table.rows) == 760
    assert definitions["league_picker"].value == "england"
    assert definitions["window_picker"].value == 7
    assert definitions["year_picker"].value == 2024
    assert table.options["title"] == "England · 2024/25"
