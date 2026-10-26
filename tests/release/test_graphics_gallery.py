"""The README graphic gallery executes the styles shown in its excerpts."""

import runpy

from evidential import EvidentialTable
from scripts.api_screenshots import GALLERY_NOTEBOOK


def test_centered_bar_gallery_uses_red_negative_bars_on_a_shared_scale():
    outputs, _ = runpy.run_path(str(GALLERY_NOTEBOOK))["app"].run()
    table = next(
        output
        for output in outputs
        if isinstance(output, EvidentialTable) and output.options["title"] == "Centered bar"
    )
    column = table.columns[1]
    assert column["encodings"][0]["color_negative"] == "red"
    assert column["encodings"][0]["center"] is True
    assert column["scale"]["domain"] == (-0.2, 0.2)
    assert {row["change"] < 0 for row in table.raw} == {False, True}
