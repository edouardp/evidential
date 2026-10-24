"""Change sparklines encode state by position and magnitude by optional color."""

import math

import pytest

from evidential import EvidentialTable, SparklineType, col


def test_change_sparkline_factory_fluent_and_mapping_share_one_wire_shape():
    options = {
        "type": "change",
        "steady": (-0.2, 0.3),
        "color_scale": ["red", "gray", "blue"],
        "color_domain": (-4, 9),
        "width": 96,
        "height": 20,
        "y_fmt": "num1",
    }
    for column in (
        col.sparkline("changes", **options),
        col.array("changes").sparkline(**options),
        {"name": "changes", "type": "array", "viz": "sparkline", "sparkline_options": options},
    ):
        table = EvidentialTable([{"changes": [-2, 0, 2, None]}], columns=[column])
        assert table.columns[0]["sparkline_options"] == options
        assert table.rows[0]["changes"] == [-2, 0, 2, None]


def test_change_sparkline_can_be_refined_immutably_and_accepts_json_pairs():
    base = col.sparkline("changes", type="change")
    refined = base.sparkline(steady=(-1, 1), color_scale="RdBu", color_domain=(-10, 10))
    assert dict(base)["sparkline_options"] == {"type": "change"}
    assert refined["sparkline_options"]["steady"] == (-1, 1)
    assert (
        EvidentialTable(
            [{"changes": [1]}],
            columns=[
                {
                    "name": "changes",
                    "viz": "sparkline",
                    "sparkline_options": {
                        "type": "change",
                        "steady": [-1, 1],
                        "color_scale": "RdBu",
                        "color_domain": [-10, 10],
                    },
                }
            ],
        ).columns[0]["sparkline_options"]
        == refined["sparkline_options"]
    )


@pytest.mark.parametrize(
    "options",
    [
        {"steady": (1, -1)},
        {"steady": (math.nan, 1)},
        {"steady": (0, math.inf)},
        {"steady": (0,)},
        {"steady": "zero"},
        {"color_scale": "not-a-palette"},
        {"color_scale": ["red"]},
        {"color_scale": ["red", ""]},
        {"color_domain": (-2, 2)},
        {"color_scale": "RdBu", "color_domain": (1, 2)},
        {"color_scale": "RdBu", "color_domain": (0, 0)},
        {"color_scale": "RdBu", "color_domain": (math.nan, 1)},
        {"color_scale": "RdBu", "color": "red"},
        {"width": 0},
        {"height": -1},
        {"width": math.inf},
        {"markers": True},
        {"signed": True},
        {"fit_to_data": True},
        {"marker_color": "red"},
    ],
)
def test_invalid_change_options_fail_for_builder_and_mapping(options):
    with pytest.raises((ValueError, TypeError)):
        col.sparkline("changes", type="change", **options)
    with pytest.raises((ValueError, TypeError)):
        EvidentialTable(
            [{"changes": [1]}],
            columns=[
                {
                    "name": "changes",
                    "viz": "sparkline",
                    "sparkline_options": {"type": "change", **options},
                }
            ],
        )


@pytest.mark.parametrize("options", [{"steady": (0, 1)}, {"color_scale": "RdBu"}, {"color_domain": (-1, 1)}])
def test_change_only_options_are_not_silently_ignored_by_other_styles(options):
    with pytest.raises(ValueError, match="type='change'"):
        col.sparkline("changes", **options)


def test_structured_change_series_retains_bindings_and_explicit_single_color():
    series = [{"period": "Mon", "delta": -2}, {"period": "Tue", "delta": 0}, {"period": "Wed", "delta": 5}]
    table = EvidentialTable(
        [{"series": series}],
        columns=[
            col.sparkline("series", type="change", x="period", y="delta", color="tab:blue"),
        ],
    )
    assert table.rows[0]["series"] == series
    assert table.columns[0]["sparkline_options"]["x"] == "period"
    assert table.columns[0]["sparkline_options"]["color"] == "tab:blue"


def test_change_demo_runs_offline_and_selection_populates_match_details(monkeypatch, tmp_path):
    import runpy
    from pathlib import Path

    monkeypatch.setenv("FOOTBALL_PARQUET", str(tmp_path / "missing.parquet"))
    notebook = Path(__file__).resolve().parents[1] / "notebooks" / "46_change_sparklines.py"
    app = runpy.run_path(str(notebook))["app"]
    _, definitions = app.run()
    results = definitions["teams"].widget
    assert len(results.rows) == 23
    assert definitions["year_picker"].value == 2024
    assert definitions["match_details"].widget.rows == []
    for row in results.rows:
        values = [point["value"] for point in row["outcomes"]]
        assert row["wins"] == sum(value > 0 for value in values)
        assert row["losses"] == sum(value < 0 for value in values)
        assert row["draws"] == values.count(0)
        assert row["played"] == len(values)
    selected = "Arsenal FC (England)"
    summary = next(row for row in results.rows if row["team_id"] == selected)
    _, selected_definitions = app.run(defs={"selected_team": selected})
    details = selected_definitions["match_details"].widget
    assert len(details.rows) == summary["played"]
    assert {game["team_id"] for game in details.rows} == {selected}
    assert all(game["match_date"].startswith("2024-") for game in details.rows)
    assert any(game["competition"] != "england" for game in details.rows)
    assert not any(column.get("viz") == "sparkline" for column in details.columns)
    assert [game["match_date"] for game in details.rows] == sorted(game["match_date"] for game in details.rows)


@pytest.mark.parametrize("style", ["line", "area", "bar", "points", "change"])
@pytest.mark.parametrize("gradient", [False, True])
def test_football_updates_preserve_declared_sparkline_style(monkeypatch, tmp_path, style: SparklineType, gradient):
    import runpy
    from pathlib import Path
    from types import SimpleNamespace

    import marimo as mo

    monkeypatch.setenv("FOOTBALL_PARQUET", str(tmp_path / "missing.parquet"))
    notebook = Path(__file__).resolve().parents[1] / "notebooks" / "46_change_sparklines.py"
    app = runpy.run_path(str(notebook))["app"]
    table = EvidentialTable(
        [],
        columns=[
            col.sparkline(
                "outcomes",
                type=style,
                width=137,
                height=28,
                y_fmt="num2",
                color_scale="RdBu" if style == "change" else None,
                color_domain=(-3, 3) if style == "change" else None,
            )
        ],
    )
    teams = mo.ui.anywidget(table)
    app.run(
        defs={
            "teams": teams,
            "color_by_margin": SimpleNamespace(value=gradient),
            "year_picker": SimpleNamespace(value=2024),
            "competition_picker": SimpleNamespace(value="england"),
        }
    )
    options = table.columns[0]["sparkline_options"]
    assert len(table.rows) == 23
    assert options["type"] == style
    assert options["width"] == 137
    assert options["height"] == 28
    assert options["y_fmt"] == "num2"
    if style == "change" and gradient:
        assert options["color_scale"] == ["#b2182b", "#b8bcc2", "#2166ac"]
        assert options["color_domain"] == (-6, 6)
    else:
        assert "color_scale" not in options
        assert "color_domain" not in options


def test_football_sql_filters_year_and_league_but_keeps_international_matches(tmp_path):
    from pathlib import Path

    import duckdb

    source = tmp_path / "games.parquet"
    with duckdb.connect() as connection:
        connection.execute("""
            CREATE TABLE games AS SELECT * FROM (VALUES
                ('Alpha', 'Beta', 'Alpha (A)', 'Beta (A)', 'a', 'a', DATE '2024-01-01', 2, 0, 'a', 'national'),
                ('Foreign', 'Alpha', 'Foreign (B)', 'Alpha (A)', 'b', 'a', DATE '2024-02-01', 1, 2, 'Cup', 'international'),
                ('Alpha', 'Beta', 'Alpha (A)', 'Beta (A)', 'a', 'a', DATE '2023-12-31', 1, 0, 'a', 'national'),
                ('Alpha', 'Beta', 'Alpha (A)', 'Beta (A)', 'a', 'a', DATE '2025-01-01', 1, 0, 'a', 'national'),
                ('Foreign', 'Other', 'Foreign (B)', 'Other (B)', 'b', 'b', DATE '2024-01-01', 1, 1, 'b', 'national'),
                ('Alpha', 'Beta', 'Alpha (A)', 'Beta (A)', 'a', 'a', DATE '2024-03-01', NULL, NULL, 'a', 'national')
            ) AS t(home,away,home_ident,away_ident,home_country,away_country,date,gh,ga,competition,level)
        """)
        connection.execute("COPY games TO ? (FORMAT PARQUET)", [str(source)])
        query = (Path(__file__).resolve().parents[1] / "notebooks/sql/46_football_outcomes.sql").read_text()
        rows = (
            connection.execute(query, {"games": str(source), "year": 2024, "competition": "a"})
            .to_arrow_table()
            .to_pylist()
        )
    assert len(rows) == 3  # Two perspectives for the league match, one for Alpha's cup game.
    assert {row["team_id"] for row in rows} == {"Alpha (A)", "Beta (A)"}
    cup = next(row for row in rows if row["competition"] == "Cup")
    assert cup["venue"] == "Away" and cup["goal_margin"] == 1 and cup["score"] == "2–1"
    assert cup["result"] == "Win"
