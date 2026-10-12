"""Optional-dependency detection so Arrow/pandas remain soft requirements."""

from __future__ import annotations

from typing import Any

from .data import jsonify


def is_arrow_table(data: Any) -> bool:
    module = type(data).__module__
    return module.startswith("pyarrow") and hasattr(data, "to_pylist")


def is_pandas_dataframe(data: Any) -> bool:
    module = type(data).__module__
    return module.startswith("pandas") and hasattr(data, "to_dict")


def arrow_table_to_rows(table: Any) -> list[dict[str, Any]]:
    return [jsonify(row) for row in table.to_pylist()]
