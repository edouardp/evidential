"""The tooltip gallery runs offline and keeps observation metadata intact."""

import runpy
from pathlib import Path

NOTEBOOK = Path(__file__).resolve().parents[2] / "notebooks/55_tooltips.py"


def test_tooltip_gallery_examples_and_sources():
    _, definitions = runpy.run_path(str(NOTEBOOK))["app"].run()
    precision = definitions["precision_table"].widget
    assert precision.raw[0]["revenue"] == 1_253_224_564.12
    overlap = definitions["overlap_table"].widget
    assert overlap.raw[0]["younger"] == overlap.raw[0]["middle"]
    assert overlap.raw[1]["younger"] != overlap.raw[1]["middle"]
    assert definitions["stack_table"].widget.columns[-1]["fmt"] == "usd0"
    assert definitions["neutral_table"].widget.columns[-1]["encodings"][0]["diverge_at"] == "neutral"
    matches = definitions["match_table"].widget.raw[0]["form"]
    assert len(matches) == 12
    assert all(game["opponent"] and game["date"] and game["score"] for game in matches)
    assert len(definitions["range_table"].widget.raw) == 2
    custom = definitions["custom_table"].widget.columns
    assert custom[0]["tooltip"] == "@hover_text"
    assert "\n" in custom[1]["tooltip"]
    assert custom[2]["tooltip"] is False
    spark = definitions["spark_table"].widget
    assert spark.options["tooltips"] == {"delay": 0.8, "text_delay": 1.5}
    assert spark.columns[-1]["tooltip_options"]["delay"] == 0
    assert spark.columns[1]["sparkline_options"]["signed"] is True
