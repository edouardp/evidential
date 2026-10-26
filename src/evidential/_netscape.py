"""A small detour through 1996."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from html import escape
from typing import Any

_STYLE = """<style>
table.netscape {
  border-collapse: separate;
  border-spacing: 1px;
  border: 10px solid;
  border-color: #b0b0b0 #505050 #505050 #b0b0b0;
  background: white;
  color: black;
  font-family: Arial, sans-serif;
}
table.netscape td {
  border: 1px inset #aaa;
  background: white;
  padding: 0 2px;
  font-size: 14px;
  line-height: 14px;
  white-space: nowrap;
}
table.netscape th {
  border: 1px inset #aaa;
  background: #99ccff;
  padding: 0 5px;
  font-size: 17px;
  line-height: 19px;
  font-weight: bold;
  text-align: center;
}
</style>"""


@dataclass(frozen=True)
class _NetscapeHTML:
    _content: str

    def __str__(self) -> str:
        return self._content

    def _repr_html_(self) -> str:
        return self._content


def render(rows: Sequence[Mapping[str, Any]]) -> _NetscapeHTML:
    columns = list(dict.fromkeys(key for row in rows for key in row))
    parts = [_STYLE, '<table class="netscape">']
    if columns:
        parts.append("<thead><tr>")
        parts.extend(f'<th scope="col">{escape(str(column))}</th>' for column in columns)
        parts.append("</tr></thead>")
    parts.append("<tbody>")
    for row in rows:
        parts.append("<tr>")
        parts.extend(f"<td>{escape(str(row.get(column, '')))}</td>" for column in columns)
        parts.append("</tr>")
    parts.append("</tbody></table>")
    return _NetscapeHTML("".join(parts))
