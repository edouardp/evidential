"""The installed package exposes its version-matched skill without installation side effects."""

import subprocess
import sys
from importlib.metadata import distribution
from pathlib import Path

import pytest

import evidential
from evidential import skills
from evidential.skills.__main__ import main


def test_path_returns_the_bundled_skill_and_its_resources():
    folder = skills.path()
    assert isinstance(folder, Path) and folder.is_absolute()
    assert folder.is_relative_to(Path(evidential.__file__).parent)
    assert (folder / "SKILL.md").is_file()
    assert (folder / "references/graphics.md").is_file()
    assert (folder / "assets/explorer.py").is_file()


def test_entry_point_resolves_to_the_bundled_skill():
    (entry_point,) = distribution("evidential").entry_points.select(group="agent.skills", name="evidential")
    get_skill_directory = entry_point.load()
    assert callable(get_skill_directory)
    assert get_skill_directory() == skills.path()


def test_package_module_prints_summary_and_skill_directory():
    result = subprocess.run([sys.executable, "-m", "evidential"], check=True, capture_output=True, text=True)
    summary, directory = result.stdout.splitlines()
    assert "Evidential" in summary and "Marimo" in summary
    assert directory == str(skills.path())
    assert result.stderr == ""


def test_path_command_prints_only_the_directory(capsys):
    assert main(["path"]) == 0
    captured = capsys.readouterr()
    assert captured.out == f"{skills.path()}\n"
    assert captured.err == ""


@pytest.mark.parametrize("argv, code", [([], 2), (["install"], 2), (["path", "--unknown"], 2), (["--help"], 0)])
def test_cli_help_and_invalid_commands_do_not_print_a_skill_path(argv, code, capsys):
    with pytest.raises(SystemExit) as error:
        main(argv)
    assert error.value.code == code
    captured = capsys.readouterr()
    assert str(skills.path()) not in captured.out
    assert "python -m evidential.skills" in (captured.out if code == 0 else captured.err)
