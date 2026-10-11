"""Evidence-style interactive tables for Marimo.

A small anywidget wrapper around a hand-written renderer that mirrors the
formatting, conditional visualisation, grouping and interaction of
`Evidence.dev <https://evidence.dev>`_ tables.

Quick start::

    import duckdb
    from evidence_tables import EvidenceTable

    con = duckdb.connect()
    con.execute("INSTALL httpfs; LOAD httpfs;")
    con.execute(
        "CREATE VIEW trips AS SELECT * FROM "
        "'https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-01.parquet'"
    )

    EvidenceTable(
        con.sql("SELECT * FROM trips LIMIT 500"),
        title="NYC yellow taxi trips",
        search=True,
        page_size=15,
        column_config={
            "trip_distance": {"fmt": "num1"},
            "fare_amount": {"fmt": "usd", "viz": "bar"},
            "tip_amount": {"fmt": "usd", "viz": "color", "color_scale": ["#fee2e2", "#16a34a"]},
        },
    )
"""

from . import duck
from .data import make_column
from .grouped import grouped_table, simple_table
from .table import EvidenceTable

__all__ = [
    "EvidenceTable",
    "grouped_table",
    "simple_table",
    "make_column",
    "duck",
]
