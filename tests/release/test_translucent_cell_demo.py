"""The transparency demo runs offline and retains alpha in its serialized colors."""

import runpy
from pathlib import Path


def test_color_scale_notebook_compares_opaque_soft_and_transparent_neutrals():
    notebook = Path(__file__).resolve().parents[2] / "notebooks/12_color_scales.py"
    _, definitions = runpy.run_path(str(notebook))["app"].run()
    try:
        table = definitions["transparency_table"]
        assert len(table.rows) == 6
        assert sum(row["soft"] == 0 for row in table.rows) == 2
        assert table.options["row_shading"] is True
        assert table.columns[2]["color_options"]["color_scale"] == ["red", "#ffffffcc", "blue"]
        assert table.columns[3]["color_options"]["color_scale"] == ["red", "#ffffff00", "blue"]
        assert table.columns[4]["cell_style"]["background"] == "#ffffffcc"
    finally:
        definitions["connection"].close()
