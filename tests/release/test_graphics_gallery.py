"""The README graphic gallery executes the styles shown in its excerpts."""

import json
import runpy

from evidential import EvidentialTable
from scripts.api_screenshots import GALLERY_NOTEBOOK


def test_centered_bar_gallery_uses_red_negative_bars_on_a_shared_scale():
    outputs, _ = runpy.run_path(str(GALLERY_NOTEBOOK))["app"].run()
    table = next(
        output
        for output in outputs
        if isinstance(output, EvidentialTable) and output.options["title"] == "Centered bar"
    )
    column = table.columns[1]
    assert column["encodings"][0]["color_negative"] == "red"
    assert column["encodings"][0]["center"] is True
    assert column["scale"]["domain"] == (-0.2, 0.2)
    assert {row["change"] < 0 for row in table.raw} == {False, True}


def test_back_to_back_gallery_compares_six_european_traders_on_one_domain():
    outputs, _ = runpy.run_path(str(GALLERY_NOTEBOOK))["app"].run()
    table = next(
        output
        for output in outputs
        if isinstance(output, EvidentialTable) and output.options["title"] == "Imports and exports · 2024"
    )
    snapshot = json.loads((GALLERY_NOTEBOOK.parent / "data/50_europe_trade_2024.json").read_text())
    assert table.raw == snapshot
    assert [row["country_code"] for row in snapshot] == ["DEU", "GBR", "FRA", "NLD", "IRL", "ITA"]
    assert [row["total_trade"] for row in snapshot] == sorted((row["total_trade"] for row in snapshot), reverse=True)
    assert all(row["imports"] > 0 and row["exports"] > 0 for row in snapshot)
    imports, country, exports = table.columns
    assert imports["domain"] == exports["domain"]
    assert imports["domain"]["name"] == "trade"
    assert imports["domain"]["include_zero"] is True
    assert imports["encodings"][0]["direction"] == "left"
    assert imports["align"] == "left"
    assert country["align"] == "center"
    assert imports["fmt"] == exports["fmt"] == "compact4"
    assert country["title"] == ""


def test_football_form_uses_only_league_matches_and_the_latest_twelve_results():
    outputs, _ = runpy.run_path(str(GALLERY_NOTEBOOK))["app"].run()
    table = next(
        output
        for output in outputs
        if isinstance(output, EvidentialTable) and output.options["title"] == "Premier League form · 2024"
    )
    snapshot = json.loads((GALLERY_NOTEBOOK.parent / "data/46_football_england_2024.json").read_text())
    league = [game for game in snapshot["matches"] if game["level"] == "national" and game["competition"] == "england"]
    assert len(table.raw) == 6
    assert [row["points"] for row in table.raw] == sorted((row["points"] for row in table.raw), reverse=True)
    for row in table.raw:
        games = sorted((game for game in league if game["team"] == row["team"]), key=lambda game: game["match_date"])
        assert row["wins"] == sum(game["result"] == "Win" for game in games)
        assert row["draws"] == sum(game["result"] == "Draw" for game in games)
        assert row["losses"] == sum(game["result"] == "Loss" for game in games)
        assert row["points"] == 3 * row["wins"] + row["draws"]
        assert len(row["form"]) == 12
        assert [item["value"] for item in row["form"]] == [game["goal_margin"] for game in games[-12:]]
    assert table.columns[-1]["sparkline_options"]["type"] == "change"
    assert not table.columns[-1]["sparkline_options"].get("delta")


def test_symbol_gallery_distinguishes_circles_from_centered_squares():
    outputs, _ = runpy.run_path(str(GALLERY_NOTEBOOK))["app"].run()
    table = next(
        output
        for output in outputs
        if isinstance(output, EvidentialTable) and output.options["title"] == "Symbols and rating"
    )
    circles, squares = table.columns[1:3]
    assert circles["symbol_options"]["symbol"] == "●"
    assert circles["title"] == "Circles"
    assert squares["symbol_options"]["shape"] == "square"
    assert squares["align"] == "center"
