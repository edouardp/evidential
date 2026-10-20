"""Separate legacy display records at the input boundary (ADR-064)."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from .rows import Rows, RowView


def unwrap_view(data: Any, records: Any, layout: Rows | None) -> tuple[Any, Any, Rows | None]:
    if layout is not None and not isinstance(layout, Rows):
        raise TypeError("row_layout must be a rows.Rows declaration or None")
    value = records if records is not None else data
    if isinstance(value, Rows):
        value = value.build()
    if isinstance(value, RowView):
        if layout is not None:
            raise ValueError("a bound RowView already supplies row_layout")
        return None, value.data, value.layout
    return data, records, layout


def split_legacy(records: Sequence[Mapping[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Adapt historical flattened input to detail records plus display tokens."""
    detail: list[dict[str, Any]] = []
    tokens: list[dict[str, Any]] = []
    for record in records:
        row = dict(record)
        if row.get("render_type") in (None, "cell_data"):
            tokens.append({"index": len(detail)})
            detail.append(row)
        else:
            tokens.append({"row": row, "members": []})
    if len(detail) == len(records):
        return detail, {}
    for position, token in enumerate(tokens):
        if "row" not in token:
            continue
        row = token["row"]
        key = row.get("__group_key")
        if row.get("render_type") == "row_total":
            token["members"] = list(range(len(detail)))
        elif key:
            token["members"] = [
                index
                for index, member in enumerate(detail)
                if key in member.get("__ancestors", []) or member.get("__parent_key") == key
            ]
        else:
            # Standalone dividers introduce the following contiguous detail block.
            members = []
            for following in tokens[position + 1 :]:
                if "row" in following:
                    break
                members.append(following["index"])
            token["members"] = members
            if not members and position and "index" in tokens[position - 1]:
                token["members"] = [tokens[position - 1]["index"]]
    return detail, {"version": 1, "legacy": tokens}


def display_records(detail: Sequence[Mapping[str, Any]], layout: Mapping[str, Any]) -> list[dict[str, Any]]:
    """An unfiltered display snapshot for inspection; never used as source data."""
    if "legacy" in layout:
        return [dict(token["row"] if "row" in token else detail[token["index"]]) for token in layout["legacy"]]
    result: list[dict[str, Any]] = []

    def append_annotation(annotation: Mapping[str, Any], kind: str) -> None:
        values = {name: cell["value"] for name, cell in annotation["cells"].items()}
        values.update(render_type=kind, __label=annotation["label"])
        result.append(values)

    def append_groups(groups: Sequence[Mapping[str, Any]]) -> None:
        for group in groups:
            if "section" in group:
                append_annotation(group["section"], "row_section")
            if group.get("summary", {}).get("position") == "top":
                append_annotation(group["summary"], "row_subtotal")
            if group["children"]:
                append_groups(group["children"])
            else:
                result.extend(dict(detail[index]) for index in group["members"])
            if group.get("summary", {}).get("position") == "bottom":
                append_annotation(group["summary"], "row_subtotal")

    if layout.get("groups"):
        append_groups(layout["groups"])
    else:
        result.extend(dict(row) for row in detail)
    if "grand_summary" in layout:
        append_annotation(layout["grand_summary"], "row_total")
    return result
