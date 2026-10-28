"""Named point series need neither derived data fields nor repeated marks."""

import pytest

from evidential import EvidentialTable, col
from evidential.marks import rebind_measure


def test_named_points_copy_bindings_and_derive_legend_names_without_mutating_data():
    fields = {"young": "0–9", "old": "80+"}
    series = col.points(fields, palette="VIRIDIS", connect=True, format="pct0").legend()
    fields["young"] = "Changed"
    encoding = series["encodings"][0]
    assert encoding["sources"] == ["young", "old"]
    assert encoding["names"] == {"young": "0–9", "old": "80+"}
    assert encoding["palette"] == "viridis"
    assert encoding["size"] == 9 and encoding["outline"] is False
    assert encoding["connect"] is True
    data = [{"young": 0.2, "old": 0.1}]
    table = EvidentialTable(data, columns=[series])
    assert table.raw == data
    assert set(table.rows[0]) <= {"young", "old", "__row_id"}
    assert table.columns[0]["encodings"][0]["names"] == encoding["names"]


def test_point_series_defaults_overrides_composition_and_legacy_arrays():
    default = col.points(["a", "b"])["encodings"][0]
    assert default["palette"] == "tab10"
    assert default["connect"] is False
    colors = ["navy", "red"]
    series = col.points(["a", "b"], palette=colors, size=12, outline="black")
    colors[0] = "Changed"
    assert series["encodings"][0]["palette"] == ["navy", "red"]
    assert series["encodings"][0]["size"] == 12
    assert series["encodings"][0]["outline"] == "black"
    appended = col.bar("target").points({"a": "A", "b": "B"}, palette="plasma", connect=True)
    assert [enc["kind"] for enc in appended["encodings"]] == ["bar", "points"]
    legacy = col.points("samples")
    assert legacy["type"] == "array"
    assert dict(legacy)["encodings"] == [{"kind": "points", "source": "samples"}]
    assert col.points({"@a": "A"})["encodings"][0]["names"] == {"a": "A"}


@pytest.mark.parametrize("fields", [[], {}, ["a", "a"], ["a", ""], ["a", 3], {"a": 3}])
def test_point_series_rejects_invalid_sources(fields):
    with pytest.raises((TypeError, ValueError)):
        col.points(fields)


@pytest.mark.parametrize("palette", ["unknown", "", [], [3], [""]])
def test_point_series_rejects_invalid_palettes(palette):
    with pytest.raises((TypeError, ValueError), match="palette"):
        col.points(["a", "b"], palette=palette)


def test_point_series_validation_covers_raw_configs_all_log_fields_and_rebinding():
    series = col.points({"a": "A", "b": "B"}, connect=True).scale(transform="log")
    with pytest.raises(ValueError, match="positive.*'b'"):
        EvidentialTable([{"a": None, "b": -1}], columns=[series])
    with pytest.raises(ValueError, match="source fields"):
        EvidentialTable(
            [{"a": 1}],
            columns=[
                {
                    "name": "a",
                    "encodings": [{"kind": "points", "source": "a", "sources": ["a"], "names": {"typo": "A"}}],
                }
            ],
        )
    rebound = rebind_measure(series, "a", "2024.a")
    assert rebound["encodings"][0]["sources"] == ["2024.a", "b"]
    assert rebound["encodings"][0]["names"] == {"2024.a": "A", "b": "B"}
    with pytest.raises(ValueError, match="field list or mapping"):
        col.points("samples", palette="viridis")
    with pytest.raises(TypeError, match="connect"):
        col.points(["a", "b"], connect="yes")
