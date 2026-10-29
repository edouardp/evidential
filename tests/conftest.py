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


@pytest.fixture
def aws_cur_dataset(tmp_path):
    """A small CUR product for deterministic query and live-widget tests."""
    import datetime as dt

    import pyarrow as pa
    import pyarrow.parquet as pq

    directory = tmp_path / "aws-cur-example" / "data" / "processed"
    directory.mkdir(parents=True)
    records = []
    for index, (service, usage, region, kind, quantity, unit, cost, effective, day, environment) in enumerate(
        [
            ("AmazonRDS", "RDS:Instance", "eu-west-1", "DiscountedUsage", 2, "Hrs", 0, 12, 1, "prod"),
            ("AmazonRDS", "RDS:Instance", "eu-west-1", "Usage", 1, "Hrs", 8, 0, 3, "prod"),
            ("AmazonEC2", "EC2:Compute", "us-east-1", "Usage", 10, "Hrs", 20, 0, 1, "dev"),
            ("AmazonEC2", "EC2:Storage", "us-east-1", "Usage", 5, "GB-Mo", 3, 0, 3, "dev"),
            ("AmazonRDS", "RDS:Instance", "eu-west-1", "RIFee", 0, "Hrs", 5, 0, 3, ""),
            ("AmazonEC2", "EC2:Compute", "us-east-1", "Credit", 0, "Hrs", -2, 0, 3, "dev"),
        ]
    ):
        records.append(
            {
                "billing_month": "2018-10",
                "usage_date": dt.date(2018, 10, day),
                "identity_line_item_id": f"line-{index}",
                "product_servicecode": service,
                "line_item_product_code": service,
                "line_item_usage_type": usage,
                "product_region": region,
                "line_item_usage_account_id": "test-account",
                "line_item_line_item_type": kind,
                "resource_tags_user_environment": environment,
                "resource_tags_user_workload": "orders",
                "resource_tags_user_cost_center": "platform",
                "line_item_resource_id": f"resource-{index}",
                "line_item_line_item_description": f"Test {usage}",
                "pricing_unit": unit,
                "line_item_usage_amount": float(quantity),
                "line_item_currency_code": "USD",
                "line_item_unblended_cost": float(cost),
                "pricing_public_on_demand_cost": float(max(cost, 0)),
                "reservation_effective_cost": float(effective),
            }
        )
    pq.write_table(pa.Table.from_pylist(records), directory / "cur_line_items.parquet")
    return directory.parent.parent
