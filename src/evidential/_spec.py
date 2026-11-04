"""Copy configuration containers while preserving callable source identities."""

from collections.abc import Mapping
from typing import Any


def copy_spec(value: Any) -> Any:
    if callable(value):
        return value
    if isinstance(value, Mapping):
        return {key: copy_spec(item) for key, item in value.items()}
    if isinstance(value, list):
        return [copy_spec(item) for item in value]
    if isinstance(value, tuple):
        return tuple(copy_spec(item) for item in value)
    return value
