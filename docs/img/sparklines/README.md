# Sparkline SVGs

Standalone versions of the three sparkline styles the table renders — just the
graph, with no table chrome.

| File | Style |
| --- | --- |
| [`line.svg`](line.svg) | a line |
| [`area.svg`](area.svg) | a filled area |
| [`bar.svg`](bar.svg) | bars |

They come from the committed renderer via
[`scripts/sparkline_svgs.py`](../../../scripts/sparkline_svgs.py):

```bash
uv run python scripts/sparkline_svgs.py
```

Open [`index.html`](index.html) to preview them. The hidden interaction layer
(the per-point hover targets and their tooltips) is stripped so each file is
only the visible graphic, and the CSS variables are resolved to the colours the
notebooks use. Each file carries `width`/`height`/`viewBox`, so it scales.
