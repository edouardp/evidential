"""Small local data bundles shared by notebook execution and browser tests."""

import csv
import io
import tarfile

import pytest


@pytest.fixture
def nba_dataset(tmp_path):
    """Two seasons with a traded player, weighted rates and an all-three-point game."""
    directory = tmp_path / "nba_data" / "datasets"
    directory.mkdir(parents=True)

    def shot(player_id, team_id, game_id, day, made, three=False):
        return {
            "GAME_ID": str(game_id),
            "GAME_EVENT_ID": "0",
            "PLAYER_ID": str(player_id),
            "PLAYER_NAME": "Alpha" if player_id == 1 else "Beta",
            "TEAM_ID": str(team_id),
            "TEAM_NAME": "North" if team_id == 10 else "South",
            "GAME_DATE": day,
            "HTM": "NTH",
            "VTM": "STH",
            "SHOT_ZONE_BASIC": "Above the Break 3" if three else "Restricted Area",
            "SHOT_ATTEMPTED_FLAG": "1",
            "SHOT_MADE_FLAG": str(made),
            "SHOT_TYPE": "3PT Field Goal" if three else "2PT Field Goal",
        }

    old = [
        shot(1, 10, 1, "20241001", 1, True),
        shot(1, 10, 1, "20241001", 0),
        shot(1, 10, 2, "20241002", 1),
        *[shot(1, 10, 2, "20241002", 0) for _ in range(3)],
        shot(1, 20, 3, "20241003", 1, True),
        shot(2, 20, 3, "20241003", 0, True),
        shot(2, 20, 3, "20241003", 1),
    ]
    old = [dict(row) for row in old for _ in range(20)]
    new = [shot(1, 10, 10, "20251001", 1, True) for _ in range(100)]
    new += [shot(2, 20, 10, "20251001", 1) for _ in range(100)]
    playoff = [shot(1, 10, 20, "20260401", 0, True) for _ in range(100)]

    for name, records in {
        "shotdetail_2024": old,
        "shotdetail_2025": new,
        "shotdetail_po_2025": playoff,
    }.items():
        stream = io.StringIO()
        writer = csv.DictWriter(stream, fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows({**row, "GAME_EVENT_ID": str(index)} for index, row in enumerate(records, start=1))
        payload = stream.getvalue().encode()
        with tarfile.open(directory / f"{name}.tar.xz", "w:xz") as archive:
            member = tarfile.TarInfo(f"{name}.csv")
            member.size = len(payload)
            archive.addfile(member, io.BytesIO(payload))
    return directory.parent
