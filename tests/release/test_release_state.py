import json

import pytest

from scripts.release_state import (
    check_pending,
    check_publish,
    read_receipt,
    release_notes,
    verify_receipt,
    write_receipt,
)


def test_receipt_binds_successful_upload_to_one_version_and_commit(tmp_path):
    path = tmp_path / "receipt.json"
    check_pending(path)
    with pytest.raises(ValueError, match="No successful"):
        verify_receipt(path, "1.0.0", "abc")
    write_receipt(path, "1.0.0rc1", "abc")
    assert verify_receipt(path, "1.0.0rc1", "abc") == "prerelease"
    with pytest.raises(ValueError, match="release-resume"):
        check_pending(path)
    for version, commit in [("1.0.0", "abc"), ("1.0.0rc1", "def")]:
        with pytest.raises(ValueError, match="does not match"):
            verify_receipt(path, version, commit)
    write_receipt(path, "1.0.0", "abc", completed=True)
    assert verify_receipt(path, "1.0.0", "abc") == "stable"
    check_pending(path)
    check_publish(path, "1.0.1")
    with pytest.raises(ValueError, match="already published"):
        check_publish(path, "1.0.0")
    assert not path.with_suffix(".tmp").exists()


@pytest.mark.parametrize("value", [[], {}, {"version": "1.0.0", "commit": "a", "completed": "false"}])
def test_invalid_receipts_fail_closed(tmp_path, value):
    path = tmp_path / "receipt.json"
    path.write_text(json.dumps(value))
    with pytest.raises(ValueError, match="Invalid"):
        read_receipt(path)


def test_release_notes_exclude_other_versions_and_unreleased_changes():
    text = "# Changelog\n\n## Unreleased\n\nUpcoming.\n\n## 1.0.1 (2026-11-04)\n\n### Fixed\n\n- Bug.\n\n## 1.0.0 (2026-10-01)\n\nOld.\n"
    assert release_notes(text, "1.0.1") == "### Fixed\n\n- Bug.\n"
    assert release_notes(text, "1.0.0") == "Old.\n"
    with pytest.raises(ValueError, match="No release notes"):
        release_notes(text, "2.0.0")
