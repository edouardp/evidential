"""Exercise skill discovery using a built wheel outside the source checkout."""

import subprocess
import sys
import zipfile
from pathlib import Path

import pytest
import yaml

from evidential import skills
from scripts import check_artifact as gate

ROOT = Path(__file__).resolve().parents[2]


def test_artifact_gate_covers_the_complete_skill_tree():
    folder = skills.path()
    resources = {
        file.relative_to(folder).as_posix()
        for file in folder.rglob("*")
        if file.is_file() and "__pycache__" not in file.parts
    }
    assert resources == set(gate.SKILL_FILES)


@pytest.fixture(scope="module")
def distributions(tmp_path_factory):
    destination = tmp_path_factory.mktemp("skill-distributions")
    subprocess.run(["uv", "build", "--out-dir", str(destination)], cwd=ROOT, check=True, capture_output=True, text=True)
    return destination


def test_wheel_and_sdist_ship_every_skill_resource(distributions):
    for pattern, reader in (("*.whl", gate.wheel_members), ("*.tar.gz", gate.sdist_members)):
        (archive,) = distributions.glob(pattern)
        members = reader(archive)
        assert gate.inspect(members) == []
        for name in gate.SKILL_FILES:
            assert members[f"{gate.SKILL_ROOT}/{name}"] == (ROOT / "src" / gate.SKILL_ROOT / name).read_bytes()
    members = dict.fromkeys(gate.REQUIRED, b"x" * 20000)
    for name in gate.SKILL_FILES:
        target = f"{gate.SKILL_ROOT}/{name}"
        del members[target]
        assert f"missing {target}" in gate.inspect(members)
        members[target] = b""
        assert f"empty {target}" in gate.inspect(members)
        members[target] = b"x"


def test_wheel_skill_discovery_works_without_a_checkout(distributions, tmp_path):
    (wheel,) = distributions.glob("*.whl")
    installed = tmp_path / "installed package"
    with zipfile.ZipFile(wheel) as archive:
        archive.extractall(installed)
    # -I ignores PYTHONPATH and the current directory. Prepend only the wheel's
    # contents, keeping the test interpreter's installed runtime dependencies.
    script = """
import runpy
import sys
from importlib.metadata import entry_points
from pathlib import Path

installed = Path(sys.argv[1])
sys.path.insert(0, str(installed))
(entry_point,) = (
    entry for entry in entry_points(group='agent.skills', name='evidential')
    if entry.dist.name == 'evidential'
)
assert entry_point.dist.locate_file('') == installed
assert entry_point.value == 'evidential.skills:path'
get_skill_directory = entry_point.load()
assert callable(get_skill_directory)
folder = get_skill_directory()
assert isinstance(folder, Path) and folder.is_relative_to(installed)
import evidential
assert Path(evidential.__file__).is_relative_to(installed)
assert folder == evidential.skills.path()
sys.argv = ['evidential.skills', 'path']
runpy.run_module('evidential.skills', run_name='__main__')
"""
    result = subprocess.run(
        [sys.executable, "-I", "-c", script, str(installed)], cwd=tmp_path, check=True, capture_output=True, text=True
    )
    folder = Path(result.stdout.strip())
    assert folder.is_relative_to(installed)
    assert result.stderr == ""
    metadata = yaml.safe_load((folder / "SKILL.md").read_text().split("---\n", 2)[1])
    assert metadata["name"] == folder.name
    assert all((folder / name).is_file() for name in gate.SKILL_FILES)
    assert not (tmp_path / ".agents").exists()


def test_discovery_skill_has_no_duplicated_templates_or_references():
    folder = ROOT / "skills/evidential"
    metadata = yaml.safe_load((folder / "SKILL.md").read_text().split("---\n", 2)[1])
    assert metadata["name"] == "evidential"
    assert not (folder / "references").exists()
    assert not (folder / "assets").exists()
