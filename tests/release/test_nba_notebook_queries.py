"""NBA notebook queries preserve denominators, traded-player scope and order."""

import re
import runpy
import shutil
import tarfile
import tempfile
from pathlib import Path

import duckdb
import pytest

NOTEBOOK = Path(__file__).resolve().parents[2] / "notebooks/53_nba_shooting.py"
SQL = NOTEBOOK.parent / "sql"


@pytest.fixture
def notebook():
    return runpy.run_path(str(NOTEBOOK))


@pytest.fixture
def loaded(notebook, nba_dataset):
    _, helpers = notebook["archive_loader"].run(
        Path=Path, duckdb=duckdb, shutil=shutil, tarfile=tarfile, tempfile=tempfile
    )
    connection = helpers["load_shots"](nba_dataset / "datasets/shotdetail_2024.tar.xz")
    try:
        yield connection, helpers["query_rows"]
    finally:
        connection.close()


def test_discovery_separates_playoffs_and_excludes_wnba_and_other_sources(notebook, nba_dataset):
    for name in ("wnba_shotdetail_2025.tar.xz", "nbastats_2025.tar.xz", "shotdetail_latest.tar.xz"):
        (nba_dataset / "datasets" / name).touch()
    _, definitions = notebook["archive_discovery"].run(re=re)
    assert set(definitions["discover_archives"](nba_dataset)) == {
        (2024, "Regular season"),
        (2025, "Regular season"),
        (2025, "Playoffs"),
    }


def test_weighted_percentages_combine_traded_players_without_averaging_games(loaded):
    connection, query = loaded
    players = query(connection, (SQL / "53_nba_players.sql").read_text(), {"team": None, "minimum": 1})
    alpha = next(row for row in players if row["player_id"] == 1)
    assert alpha["teams"] == "North · South"
    assert alpha["fga"] == 140
    assert alpha["fgm"] == 60
    assert alpha["games"] == 3
    assert alpha["fg_pct"] == pytest.approx(3 / 7)
    assert alpha["efg_pct"] == pytest.approx(4 / 7)
    assert alpha["three_attempts"] == alpha["three_made"] == 40
    assert [point["value"] for point in alpha["recent_fg"]] == [0.5, 0.25, 1.0]
    assert [point["date"][:10] for point in alpha["recent_fg"]] == ["2024-10-01", "2024-10-02", "2024-10-03"]


def test_team_filter_uses_only_the_players_selected_stint_and_threshold_is_inclusive(loaded):
    connection, query = loaded
    sql = (SQL / "53_nba_players.sql").read_text()
    players = query(connection, sql, {"team": 10, "minimum": 120})
    assert len(players) == 1
    assert players[0]["teams"] == "North"
    assert players[0]["fga"] == 120
    assert players[0]["fg_pct"] == pytest.approx(1 / 3)
    assert players[0]["efg_pct"] == pytest.approx(2.5 / 6)
    assert query(connection, sql, {"team": 10, "minimum": 121}) == []


def test_zones_use_full_league_benchmark_and_games_are_newest_first(loaded):
    connection, query = loaded
    parameters = {"player": 1, "team": 20}
    zones = query(connection, (SQL / "53_nba_zones.sql").read_text(), parameters)
    assert len(zones) == 1
    assert zones[0]["fga"] == 20
    assert zones[0]["share"] == 1
    assert zones[0]["fg_pct"] == 1
    assert zones[0]["league_fg"] == pytest.approx(2 / 3)  # Includes North's attempts too.
    games = query(connection, (SQL / "53_nba_games.sql").read_text(), {"player": 1, "team": None})
    assert [row["game_date"].isoformat() for row in games] == ["2024-10-03", "2024-10-02", "2024-10-01"]
    assert games[0]["efg_pct"] == 1.5
    assert games[0]["field_goal_points"] == 60  # Field goals only, not a box-score point total.


def test_recent_history_is_last_fifteen_in_chronological_order(loaded):
    connection, query = loaded
    connection.execute("""
        INSERT INTO shots SELECT 'extra-' || i, '0', 9, 'History', 10, 'North',
            DATE '2024-11-01' + i::INTEGER, 'STH @ NTH', 'Restricted Area', 1, 0
        FROM range(20) t(i)
    """)
    players = query(connection, (SQL / "53_nba_players.sql").read_text(), {"team": None, "minimum": 1})
    history = next(row["recent_fg"] for row in players if row["player_id"] == 9)
    assert len(history) == 15
    assert history[0]["date"].startswith("2024-11-06")
    assert history[-1]["date"].startswith("2024-11-20")


def test_notebook_runs_from_archives_and_preserves_raw_shooting_values(notebook, nba_dataset, monkeypatch):
    monkeypatch.setenv("NBA_DATASET", str(nba_dataset))
    _, definitions = notebook["app"].run()
    try:
        assert definitions["season_picker"].value == 2025
        assert definitions["season_summary"]["attempts"] == 200
        assert len(definitions["players"]) == 2
        assert definitions["players"][0]["efg_pct"] == 1.5
        assert definitions["player_table"].widget.raw[0]["efg_pct"] == 1.5
        assert definitions["zone_table"].widget.raw == []
        assert definitions["game_table"].widget.raw == []
        assert definitions["player_table"].widget.columns[-1]["domain"]["bounds"] == (0, 1)
        assert not list((nba_dataset / "datasets").glob("*.csv"))
    finally:
        definitions["connection"].close()
