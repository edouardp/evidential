"""Sample browser-painted pixels without adding an image-library dependency."""

from base64 import b64encode

import pytest


def painted_colors(page, cells, *, center=False):
    points = []
    for cell in cells:
        bounds = cell.bounding_box()
        points.append(
            {
                "x": int(bounds["x"] + (bounds["width"] / 2 if center else 4)),
                "y": int(bounds["y"] + (bounds["height"] / 2 if center else 3)),
            }
        )
    png = b64encode(page.screenshot()).decode()
    return page.evaluate(
        """async ({png, points}) => {
            const image = new Image();
            image.src = 'data:image/png;base64,' + png;
            await image.decode();
            const canvas = document.createElement('canvas');
            canvas.width = image.width; canvas.height = image.height;
            const context = canvas.getContext('2d');
            context.drawImage(image, 0, 0);
            return points.map(({x, y}) => [...context.getImageData(x, y, 1, 1).data].slice(0, 3));
        }""",
        {"png": png, "points": points},
    )


def assert_colors(actual, expected):
    # GPU compositing can round alpha blends one level differently over opaque
    # (frozen) and transparent (ordinary) table backdrops.
    for color, reference in zip(actual, expected, strict=True):
        assert color == pytest.approx(reference, abs=1)
