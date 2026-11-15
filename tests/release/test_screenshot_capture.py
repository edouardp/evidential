"""Screenshot layout overrides preserve notebook cells, paths and saved views."""

import pytest

from scripts.api_screenshots import _capture_source


@pytest.mark.parametrize("layout", ['"slides.json"', "None", None])
def test_capture_changes_only_app_layout_metadata_and_cleans_up(tmp_path, layout):
    argument = f", layout_file={layout}" if layout else ""
    source = (
        f"import marimo\napp = marimo.App(width='full'{argument})\n"
        "# Keep cell code and unrelated keyword arguments untouched.\n"
        "def example():\n    return other(layout_file='keep.json')\n"
    )
    notebook = tmp_path / "example.py"
    notebook.write_text(source)
    with _capture_source(notebook) as captured:
        assert captured.parent == notebook.parent
        expected = source.replace('layout_file="slides.json"', "layout_file=None")
        assert captured.read_text() == expected
        assert (captured == notebook) is (layout != '"slides.json"')
        assert notebook.read_text() == source
    if captured != notebook:
        assert not captured.exists()
    assert notebook.read_text() == source


def test_capture_removes_temporary_notebook_when_rendering_fails(tmp_path):
    notebook = tmp_path / "example.py"
    notebook.write_text('import marimo\napp = marimo.App(layout_file="slides.json")\n')
    with pytest.raises(RuntimeError, match="capture failed"), _capture_source(notebook) as captured:
        assert captured.exists()
        raise RuntimeError("capture failed")
    assert not captured.exists()
    assert list(tmp_path.iterdir()) == [notebook]
