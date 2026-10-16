# Sparkline SVGs

Standalone versions of the sparkline styles the table renders — just the graph,
with no table chrome. There are **five series** (rows) × **three styles**
(columns), named `<style>-<series>.svg`:

| Series | line | area | bar |
| --- | --- | --- | --- |
| 1 | [`line-1.svg`](line-1.svg) | [`area-1.svg`](area-1.svg) | [`bar-1.svg`](bar-1.svg) |
| 2 | [`line-2.svg`](line-2.svg) | [`area-2.svg`](area-2.svg) | [`bar-2.svg`](bar-2.svg) |
| 3 | [`line-3.svg`](line-3.svg) | [`area-3.svg`](area-3.svg) | [`bar-3.svg`](bar-3.svg) |
| 4 | [`line-4.svg`](line-4.svg) | [`area-4.svg`](area-4.svg) | [`bar-4.svg`](bar-4.svg) |
| 5 | [`line-5.svg`](line-5.svg) | [`area-5.svg`](area-5.svg) | [`bar-5.svg`](bar-5.svg) |

They come from the committed renderer via
[`scripts/sparkline_svgs.py`](../../../scripts/sparkline_svgs.py):

```bash
uv run python scripts/sparkline_svgs.py
```

Open [`index.html`](index.html) to preview them, grouped by style. The hidden
interaction layer (the per-point hover targets and their tooltips) is stripped
so each file is only the visible graphic, and the CSS variables are resolved to
the colours the notebooks use (line `#2563eb`, area `#53768a`, bar `#97ba99`).

Every file is **120×32** (`width`/`height`), but its `viewBox` is *expanded* to
contain the whole graph — the renderer's nominal area plus a **1.5px margin**
past the anti-aliased stroke, e.g. `viewBox="-1.5 -1.5 123 35"`. A consumer that
lays out by the file size, or clips to the `viewBox`, therefore never cuts the
graph; and the `viewBox` lets it scale.
