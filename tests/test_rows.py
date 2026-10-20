"""Display-only row layout, data binding and legacy input adaptation (ADR-064)."""

from __future__ import annotations

import json

import pytest

from evidential import EvidentialTable, col, grouped_records, rows, section_row, spacer_row
from evidential.rows import RowView

DETAIL = [
    {"region": "North", "country": "Mexico", "arr": 135.4},
    {"region": "North", "country": "Canada", "arr": 210.0},
    {"region": "LATAM", "country": "Brazil", "arr": 100.4},
]


def test_layout_never_injects_synthetic_data_or_metadata() -> None:
    layout = rows.group_by("region").section().summary().grand_summary()
    table = EvidentialTable(DETAIL, row_layout=layout)
    assert table.rows == DETAIL
    assert all("render_type" not in row and "__parent_key" not in row for row in table.rows)
    assert [group["section"]["label"] for group in table.row_layout["groups"]] == ["North", "LATAM"]
    assert table.row_layout["groups"][0]["members"] == [0, 1]
    assert table.row_layout["grand_summary"]["cells"]["arr"]["value"] == pytest.approx(445.8)
    json.dumps(table.row_layout, allow_nan=False)


def test_bound_build_contains_only_detail_data_and_preserves_layout() -> None:
    view = rows.of(DETAIL).group_by("region").section().summary("Average", values={"arr": "mean"}).total().build()
    assert isinstance(view, RowView)
    assert list(view) == DETAIL
    table = EvidentialTable(rows=view)
    assert table.rows == DETAIL
    assert table.row_layout["groups"][0]["summary"]["cells"]["arr"]["value"] == 172.7


def test_callables_only_receive_detail_records_and_annotation_callbacks_are_separate() -> None:
    visits = []

    def mark(row):
        visits.append(row["country"])
        return row["arr"] * 2

    layout = rows.group_by("region").section(values={"country": lambda members: f"{len(members)} products"})
    table = EvidentialTable(DETAIL, row_layout=layout.summary().grand_summary(), columns=[col.bar(mark)])
    assert visits == ["Mexico", "Canada", "Brazil"]
    assert table.row_layout["groups"][0]["section"]["cells"]["country"]["value"] == "2 products"
    assert len(table.rows) == 3
    table.set_data(DETAIL[:1])
    assert visits == ["Mexico", "Canada", "Brazil", "Mexico"]
    assert table.row_layout["groups"][0]["section"]["cells"]["country"]["value"] == "1 products"


def test_portable_counts_and_totals_are_display_expressions() -> None:
    layout = rows.group_by("region").section(values={"country": rows.count(suffix=" products"), "arr": "sum"})
    table = EvidentialTable(DETAIL, row_layout=layout)
    cells = table.row_layout["groups"][0]["section"]["cells"]
    assert cells["country"] == {
        "value": 2,
        "operation": "count",
        "source": None,
        "prefix": "",
        "suffix": " products",
        "format": "num0",
    }
    assert cells["arr"]["operation"] == "sum"
    assert cells["arr"]["value"] == 345.4


def test_nested_groups_preserve_first_appearance_and_summarize_details_once() -> None:
    data = [
        {"region": "B", "type": "X", "value": 1},
        {"region": "A", "type": "Y", "value": 3},
        {"region": "B", "type": "Y", "value": 7},
    ]
    table = EvidentialTable(data, row_layout=rows.group_by("region", "type").section().summary().grand_summary())
    groups = table.row_layout["groups"]
    assert [group["section"]["label"] for group in groups] == ["B", "A"]
    assert groups[0]["members"] == [0, 2]
    assert [group["section"]["label"] for group in groups[0]["children"]] == ["X", "Y"]
    assert groups[0]["summary"]["cells"]["value"]["value"] == 8
    assert table.row_layout["grand_summary"]["cells"]["value"]["value"] == 11


def test_annotations_have_independent_style_rule_alignment_and_values() -> None:
    table = EvidentialTable(
        DETAIL,
        row_layout=rows.group_by("region").section(
            values={"country": "27 products"}, style={"font_weight": "normal"}, rule="below", label_column="region"
        ),
    )
    annotation = table.row_layout["groups"][0]["section"]
    assert annotation["cells"]["country"]["value"] == "27 products"
    assert annotation["style"] == {"font_weight": "normal"}
    assert annotation["rule"] == "below" and annotation["label_column"] == "region"


def test_summary_and_grand_summary_are_optional_and_not_implicit() -> None:
    table = EvidentialTable(DETAIL, row_layout=rows.group_by("region").section())
    assert all("summary" not in group for group in table.row_layout["groups"])
    assert "grand_summary" not in table.row_layout
    assert table.row_layout["groups"][0]["section"]["cells"] == {}


def test_ungrouped_grand_summary_excludes_metadata() -> None:
    table = EvidentialTable([{"value": 10, "__row_id": 99}], row_layout=rows.Rows().grand_summary("Everything"))
    assert table.row_layout["grand_summary"]["label"] == "Everything"
    assert list(table.row_layout["grand_summary"]["cells"]) == ["value"]


def test_layout_is_immutable_and_ids_stable() -> None:
    base = rows.group_by("region")
    values = {"arr": "sum"}
    annotated = base.section(values=values)
    values["arr"] = "mean"
    first = EvidentialTable(DETAIL, row_layout=annotated).row_layout
    assert first == EvidentialTable(DETAIL, row_layout=annotated).row_layout
    assert first["groups"][0]["section"]["cells"]["arr"]["operation"] == "sum"
    assert "section" not in EvidentialTable(DETAIL, row_layout=base).row_layout["groups"][0]


def test_refresh_rebinds_and_can_explicitly_clear_layout() -> None:
    table = EvidentialTable(DETAIL, row_layout=rows.group_by("region").section().grand_summary())
    table.set_data(DETAIL[:1])
    assert table.row_layout["groups"][0]["members"] == [0]
    assert table.row_layout["grand_summary"]["cells"]["arr"]["value"] == 135.4
    table.set_data(DETAIL, row_layout=None)
    assert table.row_layout == {}


def test_failed_layout_refresh_preserves_widget_state() -> None:
    table = EvidentialTable(DETAIL, row_layout=rows.group_by("region").section())
    before = table.row_layout
    with pytest.raises(ValueError, match="group_by"):
        table.set_data(DETAIL[:1], row_layout=rows.Rows().section())
    assert table.rows == DETAIL and table.row_layout == before


def test_legacy_synthetic_inputs_are_adapted_before_binding_and_inference() -> None:
    data = [section_row("Heading"), {"value": 2}, spacer_row(), {"value": 4}]
    table = EvidentialTable(data, columns=[col.bar(lambda row: row["value"] * 2)])
    assert [row["value"] for row in table.rows] == [2, 4]
    assert table.row_layout["legacy"][0]["row"]["__label"] == "Heading"
    assert len(table.display_rows) == 4
    assert table.display_rows[0]["render_type"] == "row_section"


def test_grouped_records_keep_precomputed_summaries_out_of_source_data() -> None:
    table = grouped_records(DETAIL, group_by=["region", "country"], measures=["arr"])
    assert len(table.rows) == len(DETAIL)
    assert all(row["render_type"] == "cell_data" for row in table.rows)
    assert any(row.get("render_type") == "row_total" for row in table.display_rows)


def test_layout_validation() -> None:
    with pytest.raises(ValueError, match="group_by"):
        rows.group_by()
    with pytest.raises(ValueError, match="summary position"):
        rows.group_by("region").summary(position="middle")
    with pytest.raises(ValueError, match="centered.*values"):
        rows.group_by("region").section(align="center", values={"arr": "sum"})
    with pytest.raises(ValueError, match="row rule"):
        rows.group_by("region").section(rule="dotted")
    with pytest.raises(ValueError, match="Unknown summary"):
        rows.aggregate("not-an-aggregate")
    with pytest.raises(ValueError, match="build needs data"):
        rows.group_by("region").build()
    with pytest.raises(ValueError, match="group_by"):
        EvidentialTable(DETAIL, row_layout=rows.Rows().section())
    with pytest.raises(ValueError, match="already supplies"):
        EvidentialTable(rows.of(DETAIL).build(), row_layout=rows.group_by("region"))
    with pytest.raises(TypeError, match="row_layout must be"):
        EvidentialTable(DETAIL, row_layout={})
    with pytest.raises(ValueError, match="Unknown summary"):
        rows.Aggregate("invalid")


def test_aggregate_defaults_to_destination_field_and_empty_counts_are_zero() -> None:
    table = EvidentialTable(
        [{"group": "A", "value": None}],
        row_layout=rows.group_by("group").summary(
            values={"value": rows.aggregate("mean"), "present": rows.aggregate("count", "value")}
        ),
    )
    cells = table.row_layout["groups"][0]["summary"]["cells"]
    assert cells["value"]["source"] == "value"
    assert cells["value"]["value"] is None
    assert cells["present"]["value"] == 0
