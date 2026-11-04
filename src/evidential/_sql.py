"""SQL identifier boundaries and token-aware binding for authored queries."""

from __future__ import annotations

import re
from collections.abc import Iterator, Mapping
from typing import Any

_PARAMETER = re.compile(r"\$\{(\w+)\}|\$(\w+)|\{(\w+)\}")
_PROTECTED = re.compile(r"--|/\*|['\"]|\$(?:[A-Za-z_]\w*|)\$")
_COMMENT_EDGE = re.compile(r"/\*|\*/")


def quote_identifier(name: str) -> str:
    """Quote one field name, rather than treating its contents as SQL syntax."""
    return '"' + name.replace('"', '""') + '"'


def _quote_end(source: str, start: int) -> int:
    quote = source[start]
    escaped = (
        quote == "'"
        and start > 0
        and source[start - 1] in "eE"
        and (start < 2 or not (source[start - 2].isalnum() or source[start - 2] == "_"))
    )
    index = start + 1
    while index < len(source):
        if escaped and source[index] == "\\":
            index += 2
        elif source[index] != quote:
            index += 1
        elif source[index : index + 2] == quote * 2:
            index += 2
        else:
            return index + 1
    return len(source)


def _comment_end(source: str, start: int) -> int:
    depth = 1
    for edge in _COMMENT_EDGE.finditer(source, start + 2):
        depth += 1 if edge.group() == "/*" else -1
        if depth == 0:
            return edge.end()
    return len(source)


def _protected_spans(source: str) -> Iterator[tuple[int, int]]:
    index = 0
    while match := _PROTECTED.search(source, index):
        delimiter, start = match.group(), match.start()
        if delimiter == "--":
            newline = source.find("\n", match.end())
            end = len(source) if newline < 0 else newline
        elif delimiter == "/*":
            end = _comment_end(source, start)
        elif delimiter in ("'", '"'):
            end = _quote_end(source, start)
        else:
            close = source.find(delimiter, match.end())
            end = len(source) if close < 0 else close + len(delimiter)
        yield start, end
        index = end


def bind_parameters(source: str, parameters: Mapping[str, Any]) -> tuple[str, list[Any]]:
    """Replace placeholders only outside quoted values, identifiers and comments."""
    values: list[Any] = []

    def replace(match: re.Match[str]) -> str:
        name = next(group for group in match.groups() if group is not None)
        if name not in parameters:
            raise KeyError(f"Unknown SQL parameter {name!r}; known parameters: {sorted(parameters)}")
        values.append(parameters[name])
        return "?"

    parts = []
    previous = 0
    for start, end in _protected_spans(source):
        parts.extend((_PARAMETER.sub(replace, source[previous:start]), source[start:end]))
        previous = end
    parts.append(_PARAMETER.sub(replace, source[previous:]))
    return "".join(parts), values
