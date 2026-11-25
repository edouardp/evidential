"""Prepared notebook rows keep SQL totals distinct from detail data."""

import runpy
from pathlib import Path

import duckdb
import pytest

NOTEBOOKS = Path(__file__).resolve().parents[2] / "notebooks"


def test_wdi_subtotals_use_original_observations_and_stay_out_of_detail_rows():
    with duckdb.connect() as connection:
        connection.execute("""
            CREATE TABLE country AS SELECT * FROM (VALUES
                ('a', 'North', 'High'), ('b', 'North', 'High'),
                ('c', 'North', NULL), ('d', 'South', 'Low')
            ) AS t("Country Code", Region, "Income Group");
            CREATE TABLE observations AS SELECT * FROM (VALUES
                ('a', 'SP.DYN.LE00.IN', 2023, 70), ('b', 'SP.DYN.LE00.IN', 2023, 90),
                ('c', 'SP.DYN.LE00.IN', 2023, 50), ('d', 'SP.DYN.LE00.IN', 2023, 60)
            ) AS t(country_code, indicator_code, year, value);
        """)
        cell = runpy.run_path(str(NOTEBOOKS / "23_wdi.py"))["regional_subtotals"]
        _, definitions = cell.run(connection=connection)

    table = definitions["grouped"].widget
    assert [(row["region"], row["income_group"]) for row in table.raw] == [
        ("North", "High"),
        ("North", None),
        ("South", "Low"),
    ]
    north = table.row_layout["groups"][0]
    assert north["section"]["label"] == "North"
    assert north["section"]["collapsible"] is True
    assert north["summary"]["position"] == "top"
    assert north["summary"]["cells"]["avg_life_expectancy"]["value"] == pytest.approx(70)
    assert north["summary"]["cells"]["countries"]["value"] == 3
    assert table.row_layout["grand_summary"]["cells"]["avg_life_expectancy"]["value"] == pytest.approx(67.5)


def test_imdb_other_includes_unknown_and_missing_media_types_in_each_total():
    with duckdb.connect() as connection:
        connection.execute("""
            CREATE TABLE media AS SELECT * FROM (VALUES
                ('1992', 'Documentary', 7), ('1995', 'Feature Film', 8),
                ('1998', 'Short Film', 6), ('1999', 'TV Series', 7),
                ('2001', NULL, 5), ('2002', 'Short Film', NULL)
            ) AS t(details_release_date, media_type, imdb_rating);
        """)
        cell = runpy.run_path(str(NOTEBOOKS / "31_imdb_media.py"))["titles_by_decade"]
        _, definitions = cell.run(connection=connection)

    records = definitions["by_decade"].widget.raw
    assert [(row["period"], row["other"], row["films"]) for row in records] == [
        ("1990", 1, 4),
        ("2000", 1, 1),
        ("All decades", 2, 5),
    ]
    for row in records:
        assert row["films"] == sum(row[name] for name in ("documentary", "feature_film", "short_film", "other"))
