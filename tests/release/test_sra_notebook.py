"""The SRA explorer consumes dbt marts without resolving the parsed data again."""

import runpy
from pathlib import Path

import duckdb
import pyarrow as pa
import pyarrow.parquet as pq
import pytest

NOTEBOOK = Path(__file__).resolve().parents[2] / "notebooks/52_sra_historical_statistics.py"
MONTHS = [
    "september",
    "october",
    "november",
    "december",
    "january",
    "february",
    "march",
    "april",
    "may",
    "june",
    "july",
    "august",
]


@pytest.fixture
def notebook():
    return runpy.run_path(str(NOTEBOOK))


@pytest.fixture
def prepare(notebook):
    _, definitions = notebook["presentation_data"].run(crop_months=MONTHS)
    return definitions["prepare_views"]


def observation(month="september", value=100.0, crop_year="2023-2024", **overrides):
    month_num = (MONTHS.index(month) + 8) % 12 + 1
    return {
        "category": "raw_sugar_production",
        "measure": None,
        "crop_year": crop_year,
        "calendar_year": int(crop_year[:4]) + (month_num < 9),
        "month": month,
        "month_num": month_num,
        "value": value,
        "n_sources": 3,
        "n_values": 1,
        "conflict": False,
        "rel_spread": 0.0,
        **overrides,
    }


def wide_rows(records):
    grouped = {}
    for row in records:
        key = row["category"], row["measure"], row["crop_year"]
        grouped.setdefault(key, dict.fromkeys(MONTHS))[row["month"]] = row["value"]
    return [
        {
            "category": key[0],
            "measure": key[1],
            "crop_year": key[2],
            **months,
            "n_months": sum(value is not None for value in months.values()),
        }
        for key, months in grouped.items()
    ]


def test_dbt_resolved_conflicts_remain_visible_with_their_quality_metadata(prepare):
    records = [observation(conflict=True, n_values=2, rel_spread=0.2)]
    seasons, monthly = prepare(records, wide_rows(records), False)
    assert seasons[0]["metric"] == 100
    assert seasons[0]["conflicts"] == 1
    assert seasons[0]["coverage"] == "1/12"
    detail = monthly["2023-2024"][0]
    assert detail["value"] == 100  # dbt's chosen value is neither dropped nor re-resolved.
    assert detail["n_sources"] == 3
    assert detail["n_values"] == 2
    assert detail["rel_spread"] == 0.2
    assert detail["status"] == "Sources differ"
    assert len(seasons[0]["monthly"]) == 12
    assert seasons[0]["monthly"][1]["value"] is None


@pytest.mark.parametrize(("is_price", "expected"), [(False, 300), (True, 150)])
def test_volumes_sum_observed_months_and_prices_use_the_mean(prepare, is_price, expected):
    records = [observation(), observation("october", 200)]
    seasons, _ = prepare(records, wide_rows(records), is_price)
    assert seasons[0]["metric"] == expected
    assert seasons[0]["coverage"] == "2/12"


def test_crop_year_order_and_comparisons_preserve_missing_values_and_zero(prepare):
    records = [
        observation("september", 100, "2023-2024"),
        observation("october", 0, "2023-2024"),
        observation("september", 125, "2024-2025"),
        observation("october", 50, "2024-2025"),
        observation("january", 200, "2024-2025"),
        observation("september", 999, "2021-2022"),
    ]
    seasons, monthly = prepare(records, wide_rows(records), False)
    assert [row["crop_year"] for row in seasons] == ["2024-2025", "2023-2024", "2021-2022"]
    latest = monthly["2024-2025"]
    assert [row["period"] for row in latest] == [
        "2024-09",
        "2024-10",
        "2024-11",
        "2024-12",
        "2025-01",
        "2025-02",
        "2025-03",
        "2025-04",
        "2025-05",
        "2025-06",
        "2025-07",
        "2025-08",
    ]
    assert latest[0]["change"] == 25
    assert latest[0]["change_pct"] == 0.25
    assert latest[1]["change"] == 50
    assert latest[1]["change_pct"] is None
    assert latest[2]["value"] is None
    assert latest[4]["previous"] is None
    assert monthly["2023-2024"][0]["previous"] is None  # No bridging missing crop years.


def test_empty_views_and_a_zero_month_are_not_confused(prepare):
    assert prepare([], [], False) == ([], {})
    records = [observation(value=0)]
    seasons, monthly = prepare(records, wide_rows(records), True)
    assert seasons[0]["metric"] == 0
    assert seasons[0]["coverage"] == "1/12"
    assert monthly["2023-2024"][0]["status"] == "Sources agree"
    assert monthly["2023-2024"][1]["status"] == "Not reported"


def test_notebook_reads_only_dbt_products_and_keeps_measures_and_printed_labels_separate(
    notebook, tmp_path, monkeypatch
):
    records = [
        observation(),
        observation("october", 200),
        observation("september", 150, "2024-2025", conflict=True, n_values=2, rel_spread=0.1),
        observation(value=700, category="millsite_prices", measure="composite"),
        observation(value=999, category="millsite_prices", measure="domestic"),
    ]
    printed = [
        {
            "category": "raw_sugar_production",
            "measure": None,
            "crop_year": "2024-2025",
            "kind": "total",
            "row_label": "Total Production",
            "value": 9000.0,
            "n_votes": 3,
        },
        {
            "category": "raw_sugar_production",
            "measure": None,
            "crop_year": "2024-2025",
            "kind": "total",
            "row_label": "Total Area (Hectares)",
            "value": 8000.0,
            "n_votes": 2,
        },
    ]
    processed = tmp_path / "data/processed"
    processed.mkdir(parents=True)
    for name, rows in {"sra_monthly": records, "sra_monthly_wide": wide_rows(records), "sra_totals": printed}.items():
        pq.write_table(pa.Table.from_pylist(rows), processed / f"{name}.parquet")
    # No PDFs, parsed-layer data, manifest, dbt installation or DuckDB file is needed.
    monkeypatch.setenv("SRA_DATASET", str(tmp_path))
    _, definitions = notebook["app"].run()
    try:
        assert definitions["dataset_path"] == tmp_path
        assert len(definitions["coverage_rows"]) == 2
        assert definitions["measure_picker"].value is None
        season_widget = definitions["season_table"].widget
        assert [row["metric"] for row in season_widget.raw] == [150, 300]
        assert season_widget.columns[2]["title"] == "Observed-month total"
        assert definitions["monthly_table"].widget.raw[0]["change"] == 50
        assert len(definitions["monthly_table"].widget.raw) == 12
        assert {row["row_label"] for row in definitions["printed_table"].widget.raw} == {
            "Total Production",
            "Total Area (Hectares)",
        }
        # Published totals are displayed independently, never substituted or added.
        assert sum(row["value"] for row in definitions["printed_table"].widget.raw) == 17000
        assert season_widget.raw[0]["metric"] == 150
        _, filtered = notebook["filtered_data"].run(
            category_picker=type("Picker", (), {"value": "millsite_prices"})(),
            measure_picker=type("Picker", (), {"value": "composite"})(),
            connection=definitions["connection"],
            prepare_views=definitions["prepare_views"],
            query_rows=definitions["query_rows"],
            series_units=definitions["series_units"],
        )
        assert filtered["seasons"][0]["metric"] == 700
        assert filtered["printed_rows"] == []
    finally:
        definitions["connection"].close()


def test_queries_bind_measure_values_instead_of_interpolating_sql(notebook):
    with duckdb.connect() as connection:
        rows = notebook["query_rows"](connection, "SELECT $measure AS measure", {"measure": "price's name"})
    assert rows == [{"measure": "price's name"}]
