"""Contiguous strip intervals share an edge even at fractional container widths."""

import pytest
from test_spec_conformance import mount

from evidential import col

pytestmark = pytest.mark.browser


def test_contiguous_positioned_strips_have_no_rounding_seams_but_real_gaps_remain(page, live_server):
    intervals = [
        {"start": index / 4, "end": (index + 1) / 4, "category": "a" if index % 2 else "b"} for index in range(240)
    ]
    mount(
        page,
        live_server,
        [
            (
                "Quarterly strips",
                [{"periods": intervals}, {"periods": intervals[:120] + intervals[121:]}],
                [col.strip("periods", colors={"a": "red", "b": "blue"}, segmented=False).scale(domain=(0, 60))],
                {"width": "100%"},
            )
        ],
    )
    strips = page.locator(".et-mark-strip-positioned")
    for width in [257.3, 599.7, 783.123]:
        page.locator("section").evaluate("(el, width) => el.style.width = `${width}px`", width)
        gaps = strips.first.locator(".et-strip-run").evaluate_all("""els => els.slice(1).map((el, i) =>
            el.getBoundingClientRect().left - els[i].getBoundingClientRect().right)""")
        # Inset layout can overlap by one 1/64px layout unit, but never separates.
        assert max(gaps) < 0.001, (min(gaps), max(gaps))
        assert min(gaps) >= -1 / 64
        real_gap = (
            strips.nth(1)
            .locator(".et-strip-run")
            .evaluate_all("""els =>
            els[120].getBoundingClientRect().left - els[119].getBoundingClientRect().right""")
        )
        assert real_gap == pytest.approx(strips.nth(1).bounding_box()["width"] / 240, abs=1 / 32)
