"""The centered-bar notebook uses labeled marks and explicit shared scales."""

import runpy
from pathlib import Path

import duckdb
import pyarrow as pa
import pyarrow.parquet as pq
import pytest

ROOT = Path(__file__).resolve().parents[2]


def query_league(bundle, end_year=2021):
    with duckdb.connect() as connection:
        return (
            connection.execute(
                (ROOT / "notebooks/sql/34_wdi_league.sql").read_text(),
                {
                    "observations": str(bundle / "wdi_observations/**/*.parquet"),
                    "countries": str(bundle / "country.parquet"),
                    "base_year": 2019,
                    "end_year": end_year,
                },
            )
            .to_arrow_table()
            .to_pylist()
        )


def test_wdi_rank_uses_quantized_sums_and_marks_competition_ties(wdi_bundle):
    # Make three complete rows, with different raw sums rounding to the same point.
    records = []
    for code, gdp in (("DNK", 20.1), ("CHL", 20.4), ("IRL", 10.0)):
        for indicator in ("NY.GDP.MKTP.KD", "NE.CON.PRVT.PC.KD", "NE.GDI.FTOT.KD"):
            records.extend(
                [
                    {"country_code": code, "indicator_code": indicator, "year": 2019, "value": 100.0},
                    {
                        "country_code": code,
                        "indicator_code": indicator,
                        "year": 2021,
                        "value": 100 + gdp if indicator == "NY.GDP.MKTP.KD" else 100.0,
                    },
                ]
            )
        records.extend(
            [
                {"country_code": code, "indicator_code": "CM.MKT.INDX.ZG", "year": year, "value": 0.0}
                for year in (2020, 2021)
            ]
        )
        records.extend(
            [
                {"country_code": code, "indicator_code": "GC.DOD.TOTL.GD.ZS", "year": year, "value": 40.0}
                for year in (2019, 2021)
            ]
        )
    # Replace each fixture partition, preserving missing data for other countries.
    for shard in (wdi_bundle / "wdi_observations").rglob("*.parquet"):
        table = pq.ParquetFile(shard).read()
        year = int(shard.parent.name.split("=")[1])
        retained = [row for row in table.to_pylist() if row["country_code"] not in {"DNK", "CHL", "IRL"}]
        added = [{key: value for key, value in row.items() if key != "year"} for row in records if row["year"] == year]
        pq.write_table(pa.Table.from_pylist(retained + added, schema=table.schema), shard)
    rows = query_league(wdi_bundle)
    by_country = {row["country_code"]: row for row in rows}
    assert by_country["DNK"]["score"] == by_country["CHL"]["score"] == 20
    assert by_country["NZL"]["score"] == 100
    assert by_country["NZL"]["rank_label"] == "1"
    assert by_country["DNK"]["rank_label"] == by_country["CHL"]["rank_label"] == "2="
    assert by_country["IRL"]["rank_label"] == "4"
    assert by_country["DNK"]["country"] == "**Denmark** (2=)"
    assert [row["country_code"] for row in rows[:4]] == ["NZL", "CHL", "DNK", "IRL"]
    assert by_country["CAN"]["score"] is None and by_country["CAN"]["rank_label"] is None
    assert by_country["CAN"]["country"] == "**Canada**"


@pytest.fixture
def wdi_bundle(tmp_path):
    countries = [
        ("DNK", "Denmark"),
        ("CHL", "Chile"),
        ("IRL", "Ireland"),
        ("USA", "United States"),
        ("AUS", "Australia"),
        ("CAN", "Canada"),
        ("FRA", "France"),
        ("PRT", "Portugal"),
        ("DEU", "Germany"),
        ("ESP", "Spain"),
        ("NZL", "New Zealand"),
    ]
    pq.write_table(
        pa.Table.from_pylist(
            [{"Country Code": code, "Short Name": name, "Region": "Test region"} for code, name in countries]
            + [{"Country Code": "WLD", "Short Name": "World", "Region": None}]
        ),
        tmp_path / "country.parquet",
    )
    records = [
        ("DNK", "NY.GDP.MKTP.KD", 2019, 100),
        ("DNK", "NY.GDP.MKTP.KD", 2020, 90),
        ("DNK", "NY.GDP.MKTP.KD", 2021, 121),
        ("DNK", "NE.CON.PRVT.PC.KD", 2019, 50),
        ("DNK", "NE.CON.PRVT.PC.KD", 2021, 55),
        ("DNK", "CM.MKT.INDX.ZG", 2019, 999),  # Baseline return must be excluded.
        ("DNK", "CM.MKT.INDX.ZG", 2020, 10),
        ("DNK", "CM.MKT.INDX.ZG", 2021, -10),
        ("DNK", "NE.GDI.FTOT.KD", 2019, 0),  # A zero baseline is undefined.
        ("DNK", "NE.GDI.FTOT.KD", 2021, 12),
        ("DNK", "GC.DOD.TOTL.GD.ZS", 2019, 40),
        ("DNK", "GC.DOD.TOTL.GD.ZS", 2021, 55),
        ("CHL", "NY.GDP.MKTP.KD", 2021, 75),  # Missing baseline.
        ("CHL", "NE.CON.PRVT.PC.KD", 2019, 80),  # Missing endpoint.
        ("CHL", "CM.MKT.INDX.ZG", 2019, 10),
        ("CHL", "CM.MKT.INDX.ZG", 2021, 20),  # Missing intermediate return.
        ("CHL", "GC.DOD.TOTL.GD.ZS", 2019, 60),
        ("CHL", "GC.DOD.TOTL.GD.ZS", 2021, None),
        ("IRL", "NY.GDP.MKTP.KD", 2019, 100),
        ("IRL", "NY.GDP.MKTP.KD", 2021, 100),  # A genuine zero change.
        ("USA", "NY.GDP.MKTP.KD", 2019, float("inf")),
        ("USA", "NY.GDP.MKTP.KD", 2021, 100),
        ("NZL", "NY.GDP.MKTP.KD", 2019, 50),
        ("NZL", "NY.GDP.MKTP.KD", 2021, 100),
        ("WLD", "NY.GDP.MKTP.KD", 2019, 500),
        ("WLD", "NY.GDP.MKTP.KD", 2021, 1000),
    ]
    observations = pa.Table.from_pylist(
        [dict(zip(("country_code", "indicator_code", "year", "value"), record, strict=True)) for record in records],
        schema=pa.schema(
            [
                ("country_code", pa.string()),
                ("indicator_code", pa.string()),
                ("year", pa.int64()),
                ("value", pa.float64()),
            ]
        ),
    )
    pq.write_to_dataset(observations, root_path=tmp_path / "wdi_observations", partition_cols=["year"])
    return tmp_path


@pytest.mark.parametrize("end_year, gdp, equity, debt", [(2021, 21, -1, 15), (2020, -10, 10, None)])
def test_wdi_query_preserves_missing_values_and_uses_correct_change_units(wdi_bundle, end_year, gdp, equity, debt):
    rows = query_league(wdi_bundle, end_year)
    assert len(rows) == 11
    scores = [row["score"] for row in rows if row["score"] is not None]
    assert scores == sorted(scores, reverse=True)
    by_country = {row["country_code"]: row for row in rows}
    assert "WLD" not in by_country
    assert all(by_country["CAN"][field] is None for field in ("gdp", "consumption", "prices", "investment", "debt"))
    denmark, chile, ireland, usa = (by_country[code] for code in ("DNK", "CHL", "IRL", "USA"))
    assert denmark["country"].startswith("**Denmark** (")
    assert denmark["gdp"] == pytest.approx(gdp)
    assert denmark["prices"] == pytest.approx(equity)
    assert denmark["debt"] == debt
    assert denmark["investment"] is None
    assert all(chile[field] is None for field in ("gdp", "consumption", "prices", "investment", "debt"))
    assert usa["gdp"] is None
    assert by_country["CAN"]["score"] is None and by_country["CAN"]["rank_label"] is None
    if end_year == 2021:
        assert denmark["consumption"] == pytest.approx(10)
        assert ireland["gdp"] == 0
        assert by_country["NZL"]["gdp"] == pytest.approx(100)
        assert denmark["score"] == 45
        assert denmark["rank_label"] == "2"
    else:
        assert denmark["score"] == 0
        assert denmark["rank_label"] == "1"


def test_centered_bar_demo_prefers_the_configured_local_wdi_bundle(monkeypatch, wdi_bundle):
    monkeypatch.setenv("WDI_PARQUET", str(wdi_bundle))
    _, definitions = runpy.run_path(str(ROOT / "notebooks/34_centered_bars.py"))["app"].run()
    assert definitions["wdi_source"] == f"Queried local WDI bundle: `{wdi_bundle}`"
    table = definitions["league_table"].widget
    by_country = {row["country_code"]: row for row in table.rows}
    assert by_country["DNK"]["gdp"] == pytest.approx(21)
    assert by_country["DNK"]["debt"] == 15
    assert by_country["CHL"]["debt"] is None
    assert by_country["NZL"]["gdp"] == pytest.approx(100)
    assert len(table.rows) == 11
    assert table.columns[-1]["scale"]["domain"][1] > 0


def test_zero_wdi_changes_keep_a_nonzero_scale(monkeypatch, wdi_bundle):
    for shard in (wdi_bundle / "wdi_observations").rglob("*.parquet"):
        table = pq.ParquetFile(shard).read()
        records = table.to_pylist()
        for record in records:
            if record["indicator_code"] == "NY.GDP.MKTP.KD":
                record["value"] = 100
        pq.write_table(pa.Table.from_pylist(records, schema=table.schema), shard)
    monkeypatch.setenv("WDI_PARQUET", str(wdi_bundle))
    _, definitions = runpy.run_path(str(ROOT / "notebooks/34_centered_bars.py"))["app"].run()
    table = definitions["league_table"].widget
    assert all(row["gdp"] in (0, None) for row in table.rows)
    low, high = table.columns[1]["scale"]["domain"]
    assert low < 0 < high


def test_centered_bar_demo_uses_marks_for_every_bar(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("WDI_PARQUET", str(tmp_path / "unavailable"))
    notebook = Path(__file__).resolve().parents[2] / "notebooks" / "34_centered_bars.py"
    _, definitions = runpy.run_path(str(notebook))["app"].run()
    for name in ("league_table", "variants", "back_to_back", "diverging"):
        table = definitions[name].widget
        bars = [column for column in table.columns if column["type"] == "number"]
        assert bars
        for column in bars:
            assert column.get("viz") != "bar"
            assert column["encodings"][0]["kind"] == "bar"
            if name == "variants" and column["title"] == "Bar only":
                assert not column["encodings"][0].get("label")
            else:
                assert column["encodings"][0]["label"]
                if name in ("league_table", "variants"):
                    assert column["encodings"][0]["label"]["position"] == "outside_start"

    for name in ("league_table", "variants"):
        table = definitions[name].widget
        for column in table.columns[1:]:
            low, high = column["scale"]["domain"]
            assert low == -high
            assert column["references"][0]["value"] == 0
            source = column["encodings"][0]["source"]
            assert all(abs(row[source]) <= high for row in table.rows if row[source] is not None)
            assert high == max(abs(row[source]) for row in table.rows if row[source] is not None)

    league = definitions["league_table"].widget
    assert "saved WDI query result" in definitions["wdi_source"]
    assert len(league.rows) == 217
    by_country = {row["country_code"]: row for row in league.rows}
    assert "NZL" in by_country and "WLD" not in by_country
    assert by_country["DNK"]["country"] == "**Denmark** (4)"
    assert by_country["DNK"]["score"] == 89
    assert sum(row["rank_label"] is not None for row in league.rows) == 208
    assert by_country["DNK"]["debt"] is None
    assert by_country["DNK"]["consumption"] is not None
    assert "percentage points" in league.options["subtitle"]
    assert all("income" not in row for row in league.rows)

    for name, index, field, expected_format, reference in (
        ("back_to_back", 0, "spend", "usd1", -4.3),
        ("diverging", 1, "tolerance", "pct0", 0),
    ):
        table = definitions[name].widget
        column = table.columns[index]
        encoding = column["encodings"][0]
        assert encoding["label"]["source"] == field
        assert encoding["label"]["format"] == expected_format
        assert column["scale"]["domain"][0] < column["scale"]["domain"][1] == 0
        assert column["references"][0]["value"] == reference
        for row in table.rows:
            assert row[field] > 0
            assert row[encoding["source"]] == -row[field]
