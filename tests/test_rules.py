from __future__ import annotations

from evidence_tables import (
    EvidenceTable,
    cells_body,
    tab_format,
    tab_style,
    text_transform,
)


def test_style_rule_resolves_rows() -> None:
    table = EvidenceTable(
        [{"city": "NYC", "trips": 12000}, {"city": "LA", "trips": 8000}],
        rules=[
            tab_style(
                cells_body(columns=["trips"], rows=lambda row: row["trips"] > 10000),
                color="#b91c1c",
                font_weight="600",
            )
        ],
    )
    rules = table.options["rules"]
    assert rules[0]["rows"] == [0]
    assert rules[0]["style"] == {"color": "#b91c1c", "font-weight": "600"}


def test_format_rule_by_index() -> None:
    table = EvidenceTable(
        [{"a": 1}, {"a": 2}],
        rules=[tab_format(cells_body(columns="a", rows=[1]), "usd0")],
    )
    assert table.options["rules"][0]["fmt"] == "usd0"
    assert table.options["rules"][0]["rows"] == [1]


def test_text_transform_applied() -> None:
    table = EvidenceTable(
        [{"name": "alpha"}, {"name": "beta"}],
        rules=[text_transform(cells_body(columns="name"), str.upper)],
    )
    assert [row["name"] for row in table.rows] == ["ALPHA", "BETA"]


def test_rows_get_stable_id_when_rules_present() -> None:
    table = EvidenceTable([{"a": 1}, {"a": 2}], rules=[tab_format(cells_body("a"), "id")])
    assert [row["__row_id"] for row in table.rows] == [0, 1]
