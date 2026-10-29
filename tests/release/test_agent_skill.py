"""The distributable skill is portable and its examples execute against the API."""

import re
import runpy
import shutil
from pathlib import Path
from types import SimpleNamespace
from urllib.parse import urlparse

import pytest
import yaml

from evidential import EvidentialTable

ROOT = Path(__file__).resolve().parents[2]
SKILL = ROOT / "skills/evidential"


@pytest.fixture
def installed_skill(tmp_path):
    destination = tmp_path / "installed" / "evidential"
    shutil.copytree(SKILL, destination, ignore=shutil.ignore_patterns("__pycache__"))
    return destination


def test_portable_skill_metadata_and_local_resources(installed_skill):
    entrypoint = (installed_skill / "SKILL.md").read_text()
    frontmatter = yaml.safe_load(entrypoint.split("---\n", 2)[1])
    assert frontmatter["name"] == installed_skill.name
    assert re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", frontmatter["name"])
    assert 0 < len(frontmatter["description"]) <= 1024
    assert frontmatter["license"] == "MIT"
    assert (installed_skill / "LICENSE.txt").read_text() == (ROOT / "LICENSE").read_text()
    for document in installed_skill.rglob("*.md"):
        for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", document.read_text()):
            parsed = urlparse(target)
            if parsed.scheme or not parsed.path:
                continue
            resource = (document.parent / parsed.path).resolve()
            assert resource.is_relative_to(installed_skill), f"{document.name}: resource escapes the skill: {target}"
            assert resource.is_file(), f"{document.name}: missing bundled resource: {target}"
    interface = yaml.safe_load((installed_skill / "agents/openai.yaml").read_text())
    assert "$evidential" in interface["interface"]["default_prompt"]


@pytest.mark.parametrize("relative", ["SKILL.md", "references/tables.md", "references/graphics.md"])
def test_instruction_examples_construct_real_tables(installed_skill, relative):
    document = installed_skill / relative
    examples = re.findall(r"```python\n(.*?)\n```", document.read_text(), re.DOTALL)
    assert examples
    namespace = {}
    for example in examples:
        exec(compile(example, str(document), "exec"), namespace)
    tables = [value for value in namespace.values() if isinstance(value, EvidentialTable)]
    assert tables
    assert all(table.raw for table in tables)


def test_report_template_runs_after_copying_outside_the_repository(installed_skill):
    _, definitions = runpy.run_path(str(installed_skill / "assets/report.py"))["app"].run()
    table = definitions["report_table"]
    assert len(table.raw) == 3
    assert sum(row["sales"] for row in table.raw) == 5400
    assert len(table.row_layout["groups"]) == 2
    assert table.row_layout["grand_summary"]["cells"]["sales"]["value"] == 5400
    assert table.raw[0]["note"] == "Launch month."


def test_dimension_slicer_reference_filters_persistent_results_after_copying(installed_skill):
    document = installed_skill / "references/dimensions.md"
    examples = re.findall(r"```python\n(.*?)\n```", document.read_text(), re.DOTALL)
    namespace = {}
    for example in examples:
        exec(compile(example, str(document), "exec"), namespace)
    slicer = namespace["slicer"].widget
    results = namespace["results"].widget
    assert results.raw == namespace["facts"]
    slicer.selected = {"region": ["North"], "product": ["Lamp", "Chair"]}
    exec(compile(examples[-1], str(document), "exec"), namespace)
    assert namespace["results"].widget is results
    assert sum(row["sales"] for row in results.raw) == 3000
    assert slicer.where()[1] == ["North", "Lamp", "Chair"]
    slicer.clear()
    exec(compile(examples[-1], str(document), "exec"), namespace)
    assert results.raw == namespace["facts"]


def test_explorer_template_updates_in_place_and_binds_selection(installed_skill):
    notebook = runpy.run_path(str(installed_skill / "assets/explorer.py"))
    _, definitions = notebook["app"].run()
    live = definitions["live"]
    detail = definitions["detail_table"]
    connection = definitions["connection"]
    original = live.widget
    try:
        assert [row["product_id"] for row in live.widget.raw] == ["desk", "chair", "lamp"]
        assert detail.widget.raw == []
        notebook["refresh_detail"].run(connection=connection, detail_table=detail, selected_id="lamp")
        assert [row["month"] for row in detail.widget.raw] == ["2026-01-01", "2026-02-01"]
        assert sum(row["sales"] for row in detail.widget.raw) == 3000
        notebook["refresh_detail"].run(connection=connection, detail_table=detail, selected_id="' OR 1=1 --")
        assert detail.widget.raw == []
        live.widget.selected = "desk"
        notebook["refresh_summary"].run(live=live, minimum_units=SimpleNamespace(value=25))
        assert live.widget is original
        assert [row["product_id"] for row in live.widget.raw] == ["lamp"]
        assert live.widget.selected is None
        _, selection = notebook["selection"].run(available_products={"lamp"}, live=live)
        assert selection["selected_id"] is None
        notebook["refresh_detail"].run(connection=connection, detail_table=detail, selected_id=None)
        assert detail.widget.raw == []
    finally:
        connection.close()


def test_markdown_gates_include_the_distributable_skill():
    config = yaml.safe_load((ROOT / ".pre-commit-config.yaml").read_text())
    hook = next(hook for repo in config["repos"] for hook in repo["hooks"] if hook["id"] == "rumdl")
    assert hook["entry"].endswith(" docs notebooks skills")
    for path in (ROOT / "scripts/lint.sh", ROOT / "Makefile"):
        commands = [line.strip() for line in path.read_text().splitlines() if "uvx rumdl " in line]
        assert commands
        assert all(command.endswith(" docs notebooks skills") for command in commands)
