"""The synthetic-row builder (ADR-060)."""

from __future__ import annotations

import pytest

from evidential import EvidentialTable, col, rows
from evidential.rows import Rows

DETAIL = [
    {"region": "North", "country": "Mexico", "arr": 135.4},
    {"region": "North", "country": "Canada", "arr": 210.0},
    {"region": "LATAM", "country": "Brazil", "arr": 100.4},
]


def test_section_summary_and_total_rows() -> None:
    built = (
        rows.of(DETAIL)
        .group_by("region")
        .section()
        .summary(label="Average", values={"arr": lambda group: sum(r["arr"] for r in group) / len(group)})
        .total(label="All regions")
        .build()
    )
    types = [row.get("render_type", "cell_data") for row in built]
    assert types == [
        "row_section",
        "cell_data",
        "row_subtotal",
        "row_section",
        "cell_data",
        "cell_data",
        "row_subtotal",
        "row_total",
    ]
    # Sections name their group; summaries carry the custom label and value.
    sections = [row for row in built if row.get("render_type") == "row_section"]
    assert [row["__label"] for row in sections] == ["LATAM", "North"]
    latam_summary = built[2]
    assert latam_summary["region"] == "Average" and latam_summary["arr"] == 100.4
    north_summary = next(row for row in built if row.get("render_type") == "row_subtotal" and row["arr"] == 172.7)
    assert north_summary["region"] == "Average"
    # The default total sums the numeric columns.
    total = built[-1]
    assert total["region"] == "All regions" and total["arr"] == pytest.approx(445.8)


def test_summary_accepts_aggregation_names_and_positions() -> None:
    built = rows.of(DETAIL).group_by("region").summary(label="Total", values={"arr": "sum"}, position="top").build()
    # Each top summary precedes its detail rows.
    assert built[0]["render_type"] == "row_subtotal" and built[0]["arr"] == 100.4
    assert built[1].get("render_type") is None


def test_callable_labels_and_section_values() -> None:
    built = (
        rows.of(DETAIL)
        .group_by("region")
        .section(lambda group: f"{group[0]['region']} ({len(group)})", values={"arr": "sum"})
        .build()
    )
    north = next(row for row in built if row.get("__label", "").startswith("North"))
    assert north["__label"] == "North (2)"
    assert north["__label"] != "" and north["arr"] == 345.4


def test_total_without_grouping() -> None:
    built = rows.of(DETAIL).total(label="Everything").build()
    assert len(built) == 4
    assert built[-1]["render_type"] == "row_total"
    assert built[-1]["arr"] == pytest.approx(445.8)


def test_rows_is_iterable_and_immutable() -> None:
    base = rows.of(DETAIL).group_by("region")
    with_summary = base.summary(label="Avg", values={"arr": "mean"})
    assert isinstance(base, Rows)
    assert len(list(base)) == 3  # no summary rows on the base builder
    assert len(list(with_summary)) == 5
    assert len(list(base)) == 3  # unchanged


def test_rows_flows_into_a_table() -> None:
    built = rows.of(DETAIL).group_by("region").summary(label="Average", values={"arr": "mean"}).total().build()
    table = EvidentialTable(rows=built, columns=[col.text("region"), col.currency("arr", decimals=1)])
    assert [row["render_type"] for row in table.rows if row.get("render_type")] == [
        "row_subtotal",
        "row_subtotal",
        "row_total",
    ]


def test_rows_validation() -> None:
    with pytest.raises(ValueError, match="group_by"):
        rows.of(DETAIL).group_by()
    with pytest.raises(ValueError, match="summary position"):
        rows.of(DETAIL).group_by("region").summary(position="middle")
    with pytest.raises(ValueError, match="section align"):
        rows.of(DETAIL).group_by("region").section(align="justify")


def test_builder_rows_carry_stable_group_identity_without_changing_details() -> None:
    builder = rows.of(DETAIL).group_by("region").section().summary().total()
    built = builder.build()
    assert built == builder.build()
    section = built[0]
    member = built[1]
    summary = built[2]
    assert section["__group_key"] == member["__parent_key"] == summary["__group_key"]
    assert member["__ancestors"] == [section["__group_key"]]
    assert "__parent_key" not in DETAIL[0]
    assert all(row["__row_builder"] for row in built)


def test_centered_sections_cannot_discard_summary_values() -> None:
    with pytest.raises(ValueError, match="centered.*values"):
        rows.of(DETAIL).group_by("region").section(align="center", values={"arr": "sum"})


def test_ungrouped_total_keeps_its_label_and_excludes_metadata_from_sums() -> None:
    built = rows.of([{"country": "A", "arr": 10, "__row_id": 5}]).total("Everything").build()
    assert built[-1]["__label"] == "Everything"
    assert "__row_id" not in built[-1]
