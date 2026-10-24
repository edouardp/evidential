"""The reusable label builder shares typography with scalar columns."""

from collections.abc import Mapping

import pytest

from evidential import EvidentialTable, Label, col, label
from evidential._text_style import TextStyle


def test_requested_label_chain_round_trips_without_mutating_reusable_specs():
    base = label.fmt("num0").bold()
    automatic = base.auto_position("inside end").colour("black")
    expected = {
        "value": True,
        "format": "num0",
        "font_weight": "600",
        "position": "inside_end",
        "auto": True,
        "color": "black",
    }
    assert isinstance(automatic, Mapping)
    assert dict(automatic) == expected
    assert dict(base) == {"value": True, "format": "num0", "font_weight": "600"}
    for column in (col.bar("x", label=automatic), col.bar("x").label(automatic)):
        table = EvidentialTable([{"x": 100}], columns=[column])
        assert table.columns[0]["encodings"][0]["label"] == expected
    assert dict(Label()) == {"value": True}
    assert col.bar("x", label=Label())["encodings"][0]["label"] == {"value": True}


def test_label_and_column_share_typography_implementation():
    assert col.text("x").fmt.__func__ is label.fmt.__func__ is TextStyle.fmt
    assert col.text("x").bold.__func__ is label.bold.__func__ is TextStyle.bold
    styled = label.format("num2").font("monospace").font_color("red").italic().figure_style("proportional")
    assert dict(styled) == {
        "value": True,
        "format": "num2",
        "font": "monospace",
        "color": "red",
        "font_style": "italic",
        "figure_style": "proportional",
    }
    assert dict(label.color("navy")) == dict(label.colour("navy")) == dict(label.font_color("navy"))
    assert "font_weight" not in label.bold().bold(False)
    assert "font_style" not in label.italic().italic(False)
    assert label.font_weight("900")["font_weight"] == "900"
    assert label.font_style("oblique")["font_style"] == "oblique"
    assert col.text("x").color()["viz"] == "color"  # The column heatmap API stays distinct.


@pytest.mark.parametrize("position", ["inside start", "inside end", "outside start", "outside end"])
def test_preferred_positions_accept_spaces_underscores_and_hyphens(position):
    preferred = label.auto_position(position)
    assert preferred["position"] == position.replace(" ", "_")
    assert dict(preferred) == dict(label.auto_position(position.replace(" ", "_")))
    assert dict(preferred) == dict(label.auto_position(position.replace(" ", "-")))
    fixed = preferred.position("center")
    assert fixed["position"] == "center"
    assert fixed["auto"] is False
    updated = col.bar("x", label=preferred).label(fixed)
    assert updated["encodings"][0]["label"]["auto"] is False
    assert preferred["auto"] is True


def test_label_bindings_replace_one_another_and_callable_sources_are_prepared():
    spec = label.text("Hello").source("@caption").prefix("[").suffix("]")
    assert dict(spec) == {"source": "caption", "prefix": "[", "suffix": "]"}
    assert dict(spec.value()) == {"value": True, "prefix": "[", "suffix": "]"}
    assert dict(spec.text("literal")) == {"text": "literal", "prefix": "[", "suffix": "]"}
    table = EvidentialTable([{"x": 4}], columns=[col.point("x", label=label.source(lambda row: row["x"] * 2).bold())])
    encoding = table.columns[0]["encodings"][0]
    assert table.rows[0][encoding["label"]["source"]] == 8


def test_label_options_work_on_fixed_points_and_stack_segments():
    spec = label.position("inside start").align("left").share().fmt("pct0").min_width(12).overflow("show")
    assert spec["align"] == "begin"
    assert label.align("right")["align"] == "end"
    assert col.point("x", label=label.position("above").italic())["encodings"][0]["label"]["font_style"] == "italic"
    assert col.stacked_bar("x", "y", labels=spec)["encodings"][0]["label"]["share"] is True
    column = col.bar("x").label(True, font="monospace", font_weight="700", font_style="italic", figure_style="tabular")
    assert column["encodings"][0]["label"]["font_weight"] == "700"


@pytest.mark.parametrize(
    "operation",
    [
        lambda: label.auto_position("center"),
        lambda: label.position("middle"),
        lambda: label.align("middle"),
        lambda: label.min_width(-1),
        lambda: label.overflow("ellipsis"),
        lambda: label.auto_position("inside end").overflow("show"),
        lambda: Label({"text": "x", "source": "x"}),
    ],
)
def test_label_builder_validates_before_use(operation):
    with pytest.raises((ValueError, TypeError)):
        operation()


def test_label_mapping_is_copied_and_style_fields_are_validated_on_all_paths():
    original = {"font_weight": "700", "value": True}
    spec = Label(original)
    original["font_weight"] = "100"
    assert spec["font_weight"] == "700"
    for column in (
        col.bar("x", label=spec),
        col.bar("x", label={"value": True, "font_weight": "700"}),
        col.bar("x", label=True, label_options={"font_weight": "700"}),
    ):
        assert column["encodings"][0]["label"] == dict(spec)
    with pytest.raises(TypeError, match="font_weight"):
        Label({"font_weight": 700})


def test_stack_labels_reject_positions_the_stack_renderer_cannot_draw():
    with pytest.raises(ValueError, match="stacked_bar label position"):
        col.stacked_bar("x", "y", labels=label.position("above"))
    with pytest.raises(ValueError, match="auto.*bar"):
        col.stacked_bar("x", "y", labels=label.auto_position("inside end"))
