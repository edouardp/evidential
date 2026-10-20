"""Distribution's precomputed-data and uncertainty-band contract (ADR-065)."""

from __future__ import annotations

import json

import duckdb
import pytest

from evidential import EvidentialTable, col


def test_band_spec_keeps_position_density_height_and_intensity_independent() -> None:
    column = col.distribution("curve", x="seats", y="pdf", height=0.4, density_max=0.2, color="@ink").point("median")
    table = EvidentialTable(
        [{"curve": [{"seats": 10, "pdf": 0.1}, {"seats": 20, "pdf": 0.3}], "median": 15, "ink": "#123456"}],
        columns=[column],
    )
    band, point = table.columns[0]["encodings"]
    assert band == {
        "kind": "distribution",
        "source": "curve",
        "color_column": "ink",
        "distribution": {"x": "seats", "y": "pdf", "height": 0.4, "density_max": 0.2},
    }
    assert point["kind"] == "point" and point["source"] == "median"
    defaults = col.distribution("curve")["encodings"][0]["distribution"]
    assert defaults == {"x": "position", "y": "density", "height": 0.5, "density_max": None}


@pytest.mark.parametrize(
    "options, message",
    [
        ({"height": 0}, "height"),
        ({"height": -1}, "height"),
        ({"height": 1.01}, "height"),
        ({"height": float("inf")}, "height"),
        ({"height": True}, "height"),
        ({"density_max": 0}, "density_max"),
        ({"density_max": -1}, "density_max"),
        ({"density_max": float("nan")}, "density_max"),
        ({"density_max": True}, "density_max"),
        ({"x": ""}, "field names"),
        ({"y": ""}, "field names"),
        ({"style": "violin"}, "style"),
    ],
)
def test_band_configuration_rejects_ambiguous_or_invalid_values(options, message) -> None:
    with pytest.raises(ValueError, match=message):
        col.distribution("curve", **options)


@pytest.mark.parametrize(
    "curve, message",
    [
        ([1, 2, 3], "precomputed"),
        ({"position": 1, "density": 2}, "list"),
        ([{"position": 1, "density": -1}], "nonnegative"),
        ([{"position": 2, "density": 1}, {"position": 1, "density": 1}], "increasing"),
        ([{"position": 1, "density": 1}, {"position": 1, "density": 2}], "increasing"),
        ([{"position": 1, "wrong": 2}], "density"),
        ([{"position": True, "density": 2}], "numeric"),
        ([{"position": 1, "density": "2"}], "numeric"),
    ],
)
def test_curve_validation_rejects_samples_bad_bindings_and_invalid_density(curve, message) -> None:
    with pytest.raises(ValueError, match=message):
        EvidentialTable([{"curve": curve}], columns=[col.distribution("curve")])


def test_nulls_and_insufficient_support_remain_missing_in_the_wire_data() -> None:
    curves = [
        None,
        [],
        [{"position": 1, "density": 2}],
        [
            {"position": 1, "density": 0},
            None,
            {"position": 2, "density": None},
            {"position": 3, "density": 1},
            {"position": None, "density": 1},
        ],
    ]
    table = EvidentialTable([{"curve": curve} for curve in curves], columns=[col.distribution("curve")])
    assert [row["curve"] for row in table.rows] == curves
    json.dumps(table.rows, allow_nan=False)


def test_log_scale_validates_positions_instead_of_converting_the_array_to_a_number() -> None:
    column = col.distribution("curve").point("median").scale(domain=(1, 100), transform="log")
    EvidentialTable(
        [{"curve": [{"position": 1, "density": 0}, {"position": 100, "density": 1}], "median": 10}], columns=[column]
    )
    with pytest.raises(ValueError, match="log scale"):
        EvidentialTable([{"curve": [{"position": 0, "density": 1}]}], columns=[column])


def test_density_bindings_recompute_on_refresh_and_invalid_refresh_is_atomic() -> None:
    column = col.distribution(lambda row: row["prepared"], color="@ink")
    good = [{"prepared": [{"position": 1, "density": 0}, {"position": 4, "density": 2}], "ink": "navy"}]
    table = EvidentialTable(good, columns=[column])
    source = table.columns[0]["encodings"][0]["source"]
    assert table.rows[0][source] == good[0]["prepared"]
    with pytest.raises(ValueError, match="nonnegative"):
        table.set_data([{"prepared": [{"position": 1, "density": -1}], "ink": "red"}])
    assert table.rows[0][source] == good[0]["prepared"]
    replacement = [{"prepared": [{"position": 5, "density": 1}, {"position": 8, "density": 0}], "ink": "red"}]
    table.set_data(replacement)
    assert table.rows[0][source] == replacement[0]["prepared"]


def test_duckdb_struct_list_passes_through_without_density_estimation() -> None:
    with duckdb.connect() as connection:
        relation = connection.sql("""
            SELECT list({'position': x, 'density': pdf} ORDER BY x) AS curve
            FROM (VALUES (1.0, 0.0), (2.5, 0.8), (8.0, 0.0)) AS t(x, pdf)
        """)
        table = EvidentialTable(relation, columns=[col.distribution("curve")])
    assert table.rows[0]["curve"] == [
        {"position": 1.0, "density": 0.0},
        {"position": 2.5, "density": 0.8},
        {"position": 8.0, "density": 0.0},
    ]
