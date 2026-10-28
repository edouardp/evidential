"""The legend gallery runs offline, with reproducible population shares."""

import json
import runpy
from pathlib import Path

import duckdb
import pytest

ROOT = Path(__file__).resolve().parents[2]
NOTEBOOK = ROOT / "notebooks/54_legends.py"
SQL = ROOT / "notebooks/sql/54_population_ages.sql"
FIELDS = [f"age_{age}_{age + 9}" for age in range(0, 80, 10)] + ["age_80_plus"]


def test_gallery_runs_offline_with_one_two_and_nine_point_legends():
    _, definitions = runpy.run_path(str(NOTEBOOK))["app"].run()
    assert definitions["single"].widget.columns[1]["legend"] is True
    assert sum(bool(col.get("legend")) for col in definitions["double"].widget.columns) == 2
    assert definitions["double"].widget.columns[1]["legend_options"]["outline"] is True
    ages = definitions["age_structure"].widget.columns[-1]
    assert len(ages["encodings"]) == 1
    assert len(ages["encodings"][0]["sources"]) == 9
    assert ages["encodings"][0]["names"]["age_80_plus"] == "80+"
    assert ages["legend"] is True


def test_real_snapshot_has_complete_exhaustive_age_bands():
    records = json.loads((ROOT / "notebooks/data/54_population_age_bands_2024.json").read_text())
    assert len(records) == 12
    assert len({row["country_code"] for row in records}) == 12
    assert {row["year"] for row in records} == {2024}
    assert {row["income_group"] for row in records} == {
        "Low income",
        "Lower middle income",
        "Upper middle income",
        "High income",
    }
    for row in records:
        assert sum(row[field] for field in FIELDS) == pytest.approx(1, abs=1e-8)
        assert "age_min" not in row and "age_max" not in row
        assert row["population"] > 0
    assert records[0]["country"] == "Niger"
    assert records[-1]["country"] == "Japan"


def test_additional_examples_keep_real_results_and_distinct_shape_keys():
    _, definitions = runpy.run_path(str(NOTEBOOK))["app"].run()
    form = definitions["form_table"].widget
    assert len(form.raw) == 4
    for row in form.raw:
        assert len(row["form"]) == 12
        assert row["wins"] == row["form"].count("Win")
        assert row["draws"] == row["form"].count("Draw")
        assert row["losses"] == row["form"].count("Loss")
    assert list(form.columns[-1]["encodings"][0]["colors"]) == ["Win", "Draw", "Loss"]
    targets = definitions["target_table"].widget
    assert [enc["kind"] for enc in targets.columns[-1]["encodings"]] == ["bar", "point"]
    dumbbells = definitions["dumbbell_table"].widget
    assert [enc["kind"] for enc in dumbbells.columns[-1]["encodings"]] == ["range", "points"]
    assert dumbbells.columns[-1]["legend"] == ["Change", "Before", "After"]


def test_population_query_weights_sex_specific_percentages_and_requires_every_band():
    with duckdb.connect() as connection:
        connection.execute("""
            CREATE TABLE country AS SELECT 'NER' AS "Country Code", 'Niger' AS "Short Name",
                'Low income' AS "Income Group";
            CREATE TABLE observations(country_code VARCHAR, indicator_code VARCHAR, year INTEGER, value DOUBLE)
        """)
        rows = [("NER", "SP.POP.TOTL.MA.IN", 2024, 80), ("NER", "SP.POP.TOTL.FE.IN", 2024, 20)]
        bands = [f"{age:02}{age + 4:02}" for age in range(0, 80, 5)] + ["80UP"]
        for sex in ("MA", "FE"):
            shares = [30, 10, *([60 / 15] * 15)] if sex == "MA" else [10, 10, *([80 / 15] * 15)]
            rows.extend(
                ("NER", f"SP.POP.{band}.{sex}.5Y", 2024, share) for band, share in zip(bands, shares, strict=True)
            )
        connection.executemany("INSERT INTO observations VALUES (?, ?, ?, ?)", rows)
        result = connection.sql(SQL.read_text())
        record = dict(zip(result.columns, result.fetchone(), strict=True))
        assert record["age_0_9"] == pytest.approx(0.36)  # Unweighted average would be 0.30.
        assert sum(record[field] for field in FIELDS) == pytest.approx(1)
        connection.execute("DELETE FROM observations WHERE indicator_code = 'SP.POP.80UP.FE.5Y'")
        assert connection.sql(SQL.read_text()).fetchall() == []
