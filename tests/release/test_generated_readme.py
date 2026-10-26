"""README excerpts come from runnable notebook cells and cannot silently drift."""

from __future__ import annotations

import ast
import json
import textwrap

import pytest

from scripts import generate_readme as docs

NOTEBOOK = "notebooks/50_graphics_gallery.py"
MARKER = f"<!-- notebook: {NOTEBOOK}#graphic_bar -->"
SOURCE = '''
@app.cell(hide_code=True)
def graphic_bar_doc(mo):
    mo.md(r"""
        #### Example

        Literal **Markdown**, including `code`.
    """)
    return

@app.cell
def graphic_bar(EvidentialTable, col):
    data = [{"region": "Éire", "sales": 12}]
    EvidentialTable(
        data,
        columns=[
            col.text("region"),  # Preserve this comment.
            (
                col.bar('sales', title="Ventes €")
                .scale(domain=(-10, 20))
            ),
        ],
    )
    return
'''


@pytest.fixture
def example(tmp_path):
    notebook = tmp_path / NOTEBOOK
    notebook.parent.mkdir(parents=True)
    notebook.write_text(SOURCE)
    return tmp_path


def test_columns_preserve_source_comments_quotes_and_fluent_chains():
    code = docs.example_code(SOURCE, "graphic_bar")
    assert code == textwrap.dedent("""\
        columns=[
            col.text("region"),  # Preserve this comment.
            (
                col.bar('sales', title="Ventes €")
                .scale(domain=(-10, 20))
            ),
        ]""")
    ast.parse(code)


def test_markdown_is_literal_and_dedented():
    assert docs.markdown(SOURCE, "graphic_bar") == "#### Example\n\nLiteral **Markdown**, including `code`."


@pytest.mark.parametrize("argument", ['f"{secret()}"', 'open("secret").read()', '"one", "two"'])
def test_dynamic_or_ambiguous_markdown_is_rejected_without_execution(argument):
    source = f"@app.cell\ndef demo_doc(mo):\n    mo.md({argument})\n"
    with pytest.raises(ValueError, match="literal|exactly one"):
        docs.markdown(source, "demo")


@pytest.mark.parametrize(
    ("source", "message"),
    [
        ("def demo():\n    pass", "@app.cell"),
        ("@app.cell\ndef demo():\n    pass", "one table call"),
        ("@app.cell\ndef demo():\n    EvidentialTable(data)\n", "provide columns"),
        ("@app.cell\ndef demo():\n    EvidentialTable(data, columns=shared)\n", "inline"),
        ("@app.cell\ndef demo():\n    EvidentialTable(a)\n    EvidentialTable(b)", "one table call"),
    ],
)
def test_invalid_code_fails_instead_of_silently_keeping_an_old_excerpt(source, message):
    with pytest.raises(ValueError, match=message):
        docs.example_code(source, "demo")


def test_aggregate_helpers_extract_the_actual_call():
    source = """@app.cell
def totals(grouped_table, col):
    grouped_table(
        con, "SELECT category, sales FROM orders",
        measures=["sum(sales) AS sales"],
        measure_config={"sales": col.currency("sales")},
    )
    return
"""
    code = docs.example_code(source, "totals")
    assert code.startswith("grouped_table(\n")
    assert 'measure_config={"sales": col.currency("sales")}' in code
    ast.parse(code)


def test_call_mode_extracts_real_layout_options_without_data_preparation():
    source = """@app.cell
def layout_demo(EvidentialTable, rows):
    data = [{"region": "North", "sales": 12}]
    EvidentialTable(
        data,
        columns=shared_columns,
        # This comment belongs with the layout example.
        title="Résumé",
        row_lines=False,
        row_layout=rows.group_by("region")
        .section()
        .summary("Total", values={"sales": "sum"}),
    )
    return
"""
    code = docs.example_code(source, "layout_demo", mode="call")
    assert code == textwrap.dedent("""\
        EvidentialTable(
            data,
            columns=...,
            # This comment belongs with the layout example.
            title="Résumé",
            row_lines=False,
            row_layout=rows.group_by("region")
            .section()
            .summary("Total", values={"sales": "sum"}),
        )""")
    assert "data = [" not in code
    ast.parse(code)


def test_cst_spans_handle_unicode_before_a_call_on_the_same_line():
    source = """@app.cell
def demo():
    note = "é"; EvidentialTable(data, columns=[col.text('name')], title="Café")
"""
    assert docs.example_code(source, "demo") == "columns=[col.text('name')]"
    assert docs.example_code(source, "demo", mode="call") == (
        "EvidentialTable(data, columns=[col.text('name')], title=\"Café\")"
    )


def test_call_excerpt_elides_only_shared_setup_and_preserves_inline_definitions_and_comments():
    source = """@app.cell
def demo():
    EvidentialTable(
        layout_data,
        columns=layout_columns,  # These are shared.
        settings=(layout_frame),
        title="Products by region",
        row_layout=rows.group_by("region").section(),
    )
"""
    code = docs.example_code(source, "demo", mode="call")
    assert "columns=...,  # These are shared." in code
    assert "settings=(...)" in code
    assert 'title="Products by region"' in code
    assert 'row_layout=rows.group_by("region").section()' in code
    inline = source.replace("columns=layout_columns", 'columns=[col.text("product")]').replace(
        "settings=(layout_frame)", "settings=settings(border=False)"
    )
    code = docs.example_code(inline, "demo", mode="call")
    assert 'columns=[col.text("product")]' in code
    assert "settings=settings(border=False)" in code
    assert "settings=None" in docs.example_code(
        source.replace("settings=(layout_frame)", "settings=None"), "demo", mode="call"
    )


def test_call_marker_selects_the_table_call_and_invalid_modes_are_rejected(example):
    marker = MARKER.replace(" -->", " call -->")
    result = docs.generate(marker + "\n" + docs.END, example)
    assert docs.example_code(SOURCE, "graphic_bar", mode="call") in result
    assert "data = [{" not in result
    assert docs.generate(result, example) == result
    with pytest.raises(ValueError, match="Unknown code extraction mode"):
        docs.example_code(SOURCE, "graphic_bar", mode="unrecognised")


def test_only_generated_contents_change_and_generation_is_idempotent(example):
    before, after = "# Manual prose\n\n", "\n\nKeep these trailing spaces.  \n"
    original = before + MARKER + "\nold code and old image\n" + docs.END + after
    result = docs.generate(original, example)
    assert result.startswith(before + MARKER)
    assert result.endswith(docs.END + after)
    assert docs.markdown(SOURCE, "graphic_bar") in result
    assert docs.example_code(SOURCE, "graphic_bar") in result
    assert "](docs/img/graphics/bar.png)" in result
    assert "old code" not in result
    assert docs.generate(result, example) == result


def test_image_only_uses_markdown_but_omits_code(example):
    marker = MARKER.replace(" -->", " image-only -->")
    result = docs.generate(marker + "\n" + docs.END, example)
    assert "#### Example" in result
    assert "![Example]" in result
    assert "```" not in result


@pytest.mark.parametrize(
    "text",
    [
        "No generated regions",
        MARKER,
        docs.END + "\n" + MARKER + "\n" + docs.END,
        MARKER + "\n" + MARKER + "\n" + docs.END + "\n" + docs.END,
        MARKER + "\n" + docs.END + "\n" + MARKER + "\n" + docs.END,
        MARKER.replace("#graphic_bar", "#unknown") + "\n" + docs.END,
        MARKER + "\n" + docs.END + "\n<!-- notebook: malformed -->",
    ],
)
def test_invalid_regions_fail_explicitly(example, text):
    with pytest.raises(ValueError):
        docs.generate(text, example)


def test_check_catches_stale_text_input_and_image_independently(example, monkeypatch):
    generated = docs.generate(MARKER + "\n" + docs.END, example)
    (example / "README.md").write_text(generated)
    image = example / "docs/img/graphics/bar.png"
    image.parent.mkdir(parents=True)
    image.write_bytes(b"original image")
    targets = [(docs.ROOT / NOTEBOOK, [(docs.ROOT / image.relative_to(example), "graphic_bar")])]
    monkeypatch.setattr(docs, "_notebook_targets", lambda: targets)
    monkeypatch.setattr(docs, "inputs", lambda root=docs.ROOT: {NOTEBOOK: docs._digest(root / NOTEBOOK)})
    manifest = example / docs.MANIFEST.relative_to(docs.ROOT)
    manifest.write_text(json.dumps(docs.snapshot_manifest(example)))
    pypi = example / docs.PYPI_README.relative_to(docs.ROOT)
    pypi.write_text(docs.pypi_readme(generated))
    assert docs.check(example) == []

    stale = generated.replace("Literal **Markdown**", "Stale prose")
    (example / "README.md").write_text(stale)
    pypi.write_text(docs.pypi_readme(stale))
    assert docs.check(example) == ["README notebook regions differ from their source cells"]
    (example / "README.md").write_text(generated)
    assert docs.check(example) == ["PyPI README differs from the repository README"]
    pypi.write_text(docs.pypi_readme(generated))
    (example / NOTEBOOK).write_text(SOURCE + "\n# A data/helper or cell change also invalidates the image.\n")
    assert docs.check(example) == [f"Stale screenshot inputs: {NOTEBOOK}"]
    (example / NOTEBOOK).write_text(SOURCE)
    image.write_bytes(b"changed image")
    assert docs.check(example) == ["Stale screenshot images: docs/img/graphics/bar.png"]


def test_pypi_copy_resolves_images_and_links_but_preserves_urls_anchors_and_code():
    text = (
        "![Local image](docs/img/example.png)\n"
        "[Notebook](notebooks/example.py)\n"
        "[Section](#section) [External](https://example.org)\n"
        "[![License](https://example.org/badge.svg)](LICENSE)\n"
        "```markdown\n![Literal example](docs/example.png)\n```\n"
    )
    result = docs.pypi_readme(text)
    assert f"![Local image]({docs.ASSET_ROOT}docs/img/example.png)" in result
    assert f"[Notebook]({docs.REPO_ROOT}notebooks/example.py)" in result
    assert "[Section](#section) [External](https://example.org)" in result
    assert f"[![License](https://example.org/badge.svg)]({docs.REPO_ROOT}LICENSE)" in result
    assert "```markdown\n![Literal example](docs/example.png)\n```" in result


@pytest.mark.parametrize("filename", ["pyproject.toml", "uv.lock"])
def test_release_version_bump_does_not_invalidate_images_but_dependency_changes_do(tmp_path, filename):
    project = tmp_path / filename
    if filename == "pyproject.toml":
        content = '[project]\nname="evidential"\nversion="0.1.0"\ndependencies=["anywidget>=0.9"]\n'
    else:
        content = (
            '[[package]]\nname="evidential"\nversion="0.1.0"\nsource={editable="."}\n'
            '[[package]]\nname="anywidget"\nversion="0.9"\n'
        )
    project.write_text(content)
    original = docs._input_digest(project)
    project.write_text(content.replace("0.1.0", "0.1.1"))
    assert docs._input_digest(project) == original
    project.write_text(content.replace("0.9", "0.10"))
    assert docs._input_digest(project) != original


def test_failed_capture_leaves_existing_readme_images_and_manifest_untouched(tmp_path, monkeypatch):
    readme, manifest, image = (tmp_path / name for name in ("README.md", "manifest.json", "image.png"))
    for path in (readme, manifest, image):
        path.write_text("original")
    monkeypatch.setattr(docs, "README", readme)
    monkeypatch.setattr(docs, "MANIFEST", manifest)
    monkeypatch.setattr(docs, "generate", lambda text: "new README")
    monkeypatch.setattr(docs, "inputs", lambda: {})

    def fail(*, output_root):
        partial = output_root / "image.png"
        partial.write_text("new image")
        yield partial
        raise RuntimeError("notebook failed")

    monkeypatch.setattr(docs, "render", fail)
    with pytest.raises(RuntimeError, match="notebook failed"):
        docs.build()
    assert all(path.read_text() == "original" for path in (readme, manifest, image))


@pytest.mark.parametrize("failure", ["partial", "source change"])
def test_incomplete_capture_and_sources_changed_during_capture_are_rejected(tmp_path, monkeypatch, failure):
    readme = tmp_path / "README.md"
    readme.write_text("original")
    monkeypatch.setattr(docs, "README", readme)
    monkeypatch.setattr(docs, "generate", lambda text: "new README")
    state = {"source": "before"}
    monkeypatch.setattr(docs, "inputs", lambda: dict(state))
    monkeypatch.setattr(
        docs, "_notebook_targets", lambda: [(docs.ROOT / NOTEBOOK, [(docs.ROOT / "image.png", "demo")])]
    )

    def capture(*, output_root):
        if failure == "source change":
            path = output_root / "image.png"
            path.write_bytes(b"new")
            yield path
            state["source"] = "after"

    monkeypatch.setattr(docs, "render", capture)
    with pytest.raises(ValueError, match="every registered screenshot|sources changed"):
        docs.build()
    assert readme.read_text() == "original"


def test_committed_readme_and_screenshots_are_current():
    assert docs.check() == [], "Run make readme and commit the generated files"
