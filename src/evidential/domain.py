"""Named numeric domains shared by columns, independently of their headers."""

from ._domain import Domain as _Domain

__all__ = ["numeric"]


def numeric(name: str) -> _Domain:
    """Start an immutable shared domain: ``domain.numeric("sales").include_zero()``."""
    return _Domain(name)
