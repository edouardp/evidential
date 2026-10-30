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


@pytest.fixture
def oecd_dataset(tmp_path):
    """Quarterly GDP with gaps, a boundary-spanning run and incompatible series."""
    import datetime as dt

    import pyarrow as pa
    import pyarrow.parquet as pq

    directory = tmp_path / "oecd" / "data" / "processed"
    directory.mkdir(parents=True)

    def observation(code, year, quarter, growth, **extra):
        return {
            "dataflow": "gdp_growth",
            "dataflow_name": "Real GDP growth",
            "ref_area": code,
            "ref_area_label": {"USA": "United States", "NZL": "New Zealand", "OECD": "OECD"}[code],
            "freq": "Q",
            "freq_label": "Quarterly",
            "adjustment": "Y",
            "adjustment_label": "Calendar and seasonally adjusted",
            "transaction": "B1GQ",
            "transaction_label": "Gross domestic product",
            "sector": "S1",
            "counterpart_sector": "S1",
            "activity": "_Z",
            "expenditure": "_Z",
            "instr_asset": "_Z",
            "unit_measure": "PC",
            "unit_measure_label": "Percentage change",
            "price_base": "L",
            "transformation": "G1",
            "transformation_label": "Growth rate, period on period",
            "table_identifier": "T0102",
            "conf_status": "F",
            "unit_mult": "0",
            "multiplier": 1.0,
            "period_start": dt.date(year, (quarter - 1) * 3 + 1, 1),
            "year": year,
            "quarter": quarter,
            "time_period": f"{year}-Q{quarter}",
            "obs_value": growth,
            "obs_status": "A",
            "obs_status_label": "Normal value",
            **extra,
        }

    records = [
        observation("USA", year, quarter, value)
        for year, quarter, value in [
            (1959, 4, -2.0),
            (1960, 1, -1.0),
            (1960, 2, 1.0),
            (1960, 3, -0.5),
            (1960, 4, 0.0),
            (1961, 1, -1.0),
            (1961, 2, -2.0),
            (1961, 3, -3.0),
            (1961, 4, -1.0),
            (1962, 1, -2.0),
            (1962, 2, 0.5),
        ]
    ]
    records += [
        observation("NZL", year, quarter, value)
        for year, quarter, value in [
            (1960, 2, -0.5),
            (1960, 4, -0.4),
            (1961, 1, -0.2),
            (1961, 2, 0.0),
            (1961, 3, 0.5),
        ]
    ]
    records.append(observation("NZL", 1961, 4, None, obs_status="P", obs_status_label="Provisional value"))
    records += [observation("OECD", 1960, quarter, -1.0) for quarter in (1, 2)]
    records += [
        observation("USA", 1960, 1, 99.0, transformation="GY"),
        observation("USA", 1960, 1, -99.0, transaction="P6"),
        observation("USA", 1960, 1, -99.0, adjustment="N"),
        observation("USA", 1960, 1, -99.0, price_base="V"),
    ]
    pq.write_table(pa.Table.from_pylist(records), directory / "gdp_growth.parquet")
    finance = [
        {
            "ref_area": "NZL",
            "ref_area_label": "New Zealand",
            "time_period": "1961",
            "period_start": dt.date(1961, 1, 1),
            "year": 1961,
            "quarter": None,
            "freq": "A",
            "freq_label": "Annual",
            "unit_measure": "USD",
            "unit_measure_label": "US dollars",
            "obs_value": 12.5,
            "multiplier": 1_000_000.0,
            "measure_label": "Public debt",
            "sector_label": "General government",
            "sector": "S13",
            "category": "PF",
            "edition": "YU",
            "measure": "GGD",
            "obs_status": "A",
            "obs_status_label": "Normal value",
        }
    ]
    finance += [
        {
            **finance[0],
            "unit_measure": "PT_B1GQ",
            "unit_measure_label": "Percentage of GDP",
            "obs_value": value,
            "multiplier": 1.0,
            "measure": measure,
        }
        for measure, value in [("GGD", 35.0), ("GNLB", -4.0)]
    ]
    pq.write_table(pa.Table.from_pylist(finance), directory / "gov_finance.parquet")
    annual_gdp = [
        {
            **observation(code, year, 1, value),
            "freq": "A",
            "freq_label": "Annual",
            "time_period": str(year),
            "unit_measure": "USD_PPP",
            "unit_measure_label": "US dollars, PPP converted",
            "price_base": "V",
            "transformation": "LA",
            "unit_mult": "6",
            "multiplier": 1_000_000.0,
        }
        for code, year, value in [("USA", 1961, 100.0), ("USA", 1962, 200.0), ("NZL", 1961, 15.0)]
    ]
    annual_gdp += [
        {**annual_gdp[0], "freq": "Q", "obs_value": 999.0},
        {**annual_gdp[0], "price_base": "LR", "obs_value": 999.0},
    ]
    pq.write_table(pa.Table.from_pylist(annual_gdp), directory / "gdp_quarterly_usd.parquet")
    return directory.parent.parent
