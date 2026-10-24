"""Evidence-style interactive tables for Marimo.

A small anywidget wrapper around a hand-written renderer that mirrors the
formatting, conditional visualisation, grouping and interaction of
`Evidence.dev <https://evidence.dev>`_ tables.

Quick start::

    import duckdb
    from evidential import EvidentialTable

    con = duckdb.connect()
    con.execute("INSTALL httpfs; LOAD httpfs;")
    con.execute(
        "CREATE VIEW trips AS SELECT * FROM "
        "'https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-01.parquet'"
    )

    EvidentialTable(
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

from . import col, duck, label, rows
from ._column import CURRENCY_CODES, Column, ColumnGroup
from ._label import Label
from .aggregations import BUILTIN_AGGREGATIONS, apply_aggregations, resolve_aggregation
from .client import grouped_records
from .comparison import comparison_table
from .configuration import ColumnOptions, TableOptions, settings
from .data import make_column
from .grouped import grouped_table, simple_table
from .live import LiveEvidentialTable, query_values
from .pivot import pivot_table
from .query import date_range_sql, query_table
from .rows import Rows
from .rules import (
    cells_body,
    cols_merge,
    cols_merge_n_pct,
    cols_merge_range,
    cols_merge_uncert,
    resolve_rules,
    sub_large_vals,
    sub_missing,
    sub_small_vals,
    sub_values,
    sub_zero,
    tab_format,
    tab_style,
    text_transform,
)
from .table import EvidentialTable, section_row, spacer_row

__all__ = [
    "TableOptions",
    "ColumnOptions",
    "col",
    "label",
    "Label",
    "Column",
    "ColumnGroup",
    "rows",
    "Rows",
    "CURRENCY_CODES",
    "settings",
    "EvidentialTable",
    "section_row",
    "spacer_row",
    "LiveEvidentialTable",
    "grouped_table",
    "grouped_records",
    "pivot_table",
    "comparison_table",
    "query_table",
    "date_range_sql",
    "BUILTIN_AGGREGATIONS",
    "resolve_aggregation",
    "apply_aggregations",
    "cells_body",
    "tab_style",
    "tab_format",
    "text_transform",
    "sub_missing",
    "sub_zero",
    "sub_small_vals",
    "sub_large_vals",
    "sub_values",
    "cols_merge",
    "cols_merge_range",
    "cols_merge_uncert",
    "cols_merge_n_pct",
    "resolve_rules",
    "simple_table",
    "query_values",
    "make_column",
    "duck",
]
