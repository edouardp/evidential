"""Named domains pool independent columns while keeping configuration immutable."""

import math

import pytest

from evidential import Domain, EvidentialTable, col, domain


def test_domain_builder_is_immutable_and_all_column_kinds_accept_it():
    base = domain.numeric("payments")
    shared = base.include_zero().bounds(0, 100).palette("Blues").midpoint(50)
    assert dict(base) == {"name": "payments"}
    expected = {"name": "payments", "include_zero": True, "bounds": (0, 100), "palette": "blues", "midpoint": 50}
    assert dict(shared) == expected
    for column in (col.bar("a"), col.point("a"), col.number("a").color(), col.chip("a"), col.array("a").sparkline()):
        assert column.domain(shared)["domain"] == expected
        assert "domain" not in column
    colors = ["red", "gray", "blue"]
    spec = base.palette(colors)
    colors[0] = "black"
    exported = spec["palette"]
    exported[0] = "yellow"
    assert spec["palette"] == ["red", "gray", "blue"]


def test_named_and_mapping_domains_merge_without_mutating_inputs():
    shared = domain.numeric("payments").palette("Blues").include_zero()
    columns = [col.bar("a").domain("payments"), col.number("b").color().domain(shared)]
    table = EvidentialTable([{"a": 1, "b": 100}], columns=columns)
    assert table.columns[0]["domain"] == table.columns[1]["domain"] == dict(shared)
    assert dict(columns[0])["domain"] == {"name": "payments"}
    table.set_data([{"a": 10, "b": 500}])
    assert table.columns[1]["domain"] == dict(shared)
    raw = {"name": "a", "type": "number", "domain": {"name": "x", "bounds": [0, 10]}}
    assert EvidentialTable([{"a": 2}], columns=[raw]).columns[0]["domain"]["bounds"] == (0, 10)
    assert raw["domain"]["bounds"] == [0, 10]


def test_default_zero_and_neutral_policy_follow_member_encodings():
    table = EvidentialTable([{"a": 2, "b": 10}], columns=[col.bar("a").domain("x"), col.point("b").domain("x")])
    assert all(column["domain"]["include_zero"] for column in table.columns)
    explicit = domain.numeric("x").include_zero(False)
    assert not EvidentialTable([{"a": 2}], columns=[col.bar("a").domain(explicit)]).columns[0]["domain"]["include_zero"]
    shared = domain.numeric("change").palette(["red", "gray", "blue"])
    table = EvidentialTable(
        [{"a": [-1, 0, 2], "b": 1}],
        columns=[
            col.sparkline("a", type="change", steady=(-0.5, 0.5)).domain(shared),
            col.number("b").color().domain("change"),
        ],
    )
    assert all(column["domain"]["neutral_range"] == (-0.5, 0.5) for column in table.columns)


@pytest.mark.parametrize(
    "operation",
    [
        lambda: domain.numeric(""),
        lambda: Domain("x", {"unknown": 1}),
        lambda: domain.numeric("x").bounds(2, 1),
        lambda: domain.numeric("x").bounds(1, 1),
        lambda: domain.numeric("x").bounds(0, math.inf),
        lambda: domain.numeric("x").midpoint(math.nan),
        lambda: domain.numeric("x").palette("not-a-palette"),
        lambda: domain.numeric("x").palette(["red"]),
        lambda: domain.numeric("x").palette(["red", ""]),
        lambda: domain.numeric("x").include_zero("yes"),
    ],
)
def test_domain_builder_rejects_invalid_specs(operation):
    with pytest.raises((ValueError, TypeError)):
        operation()


@pytest.mark.parametrize(
    "columns",
    [
        [
            col.bar("a").domain(domain.numeric("x").bounds(0, 10)),
            col.bar("b").domain(domain.numeric("x").bounds(0, 20)),
        ],
        [col.bar("a").scale(domain=(0, 10)).domain("x")],
        [col.number("a").color(min=0).domain("x")],
        [col.point("a").scale(transform="log").domain("x")],
        [col.bar("a", center=True).domain(domain.numeric("x").bounds(-10, 20))],
        [col.number("a").color(scale="Reds").domain(domain.numeric("x").palette("Blues"))],
        [col.sparkline("a", type="change", color="red").domain(domain.numeric("x").palette("Blues"))],
        [col.sparkline("a", type="change").domain(domain.numeric("x").bounds(1, 10))],
        [col.sparkline("a", type="change").domain(domain.numeric("x").midpoint(2))],
        [col.sparkline("a", type="change").domain("x"), col.sparkline("b", type="change", steady=(-1, 1)).domain("x")],
    ],
)
def test_domain_conflicts_are_rejected_before_rendering(columns):
    with pytest.raises(ValueError):
        EvidentialTable([{"a": 1, "b": 2}], columns=columns)


def test_domain_updates_are_transactional_and_plain_columns_can_anchor_a_domain():
    table = EvidentialTable([{"a": 1, "b": 20}], columns=[col.bar("a").domain("x"), col.number("b").domain("x")])
    before = list(table.columns)
    with pytest.raises(ValueError):
        table.set_column("b", domain=domain.numeric("x").palette("blue"), color_options={"min": 5})
    assert table.columns == before


def test_shared_domain_demo_runs_with_independent_header_groups():
    import runpy
    from pathlib import Path

    notebook = Path(__file__).resolve().parents[1] / "notebooks/47_shared_domains.py"
    _, definitions = runpy.run_path(str(notebook))["app"].run()
    counts = definitions["counts"].widget
    assert len(counts.columns) == 5
    assert {column["domain"]["name"] for column in counts.columns[1:]} == {"payments"}
    assert {column["domain"]["palette"] for column in counts.columns[1:]} == {"blues"}
    changes = definitions["change_table"].widget
    assert all(column["domain"]["bounds"] == (-10, 10) for column in changes.columns[1:])
    assert all(column["domain"]["neutral_range"] == (-0.5, 0.5) for column in changes.columns[1:])


def test_shared_palette_rejects_conditional_colors_and_independent_interpolation():
    shared = domain.numeric("x").palette("Blues")
    for colors in ({"conditional_colors": "ink"}, {"scale_mode": "rgb"}):
        with pytest.raises(ValueError, match="[Ss]hared palette"):
            EvidentialTable(
                [{"x": 1, "ink": "red"}],
                columns=[
                    {"name": "x", "viz": "color", "domain": shared, "color_options": colors},
                ],
            )
