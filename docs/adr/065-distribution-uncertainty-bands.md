---
status: accepted
date: 2026-10-21
deciders: edouard
---

# ADR-065: Distribution as an Uncertainty Band

## Context and Problem Statement

The original `col.distribution` was an area-chart renderer disguised as a
distribution band. Its SVG used a vertical density axis, could overflow a row,
coerced missing observations to zero, clamped off-screen samples onto the edge,
and lacked a validated data contract. The user explicitly requested a restart.
That implementation and its element-existence tests are discarded.

The design reference `image-20261018173437650.png` shows a horizontal,
constant-height band: pale tails and dark high-density regions on a quantitative
x-axis, with a marker for a central estimate. Specification §6.9 distinguishes
this from a violin plot and distinguishes precomputed densities from samples.

## Decision Drivers

- Match the reference's uncertainty band rather than a miniature area chart.
- Preserve the meaning of supplied coordinates, densities, gaps and support.
- Give density intensity and band height explicit, independent meanings.
- Share horizontal coordinates with axes, points and interval markers.
- Keep estimation and statistical calculations in SQL/Python.
- Test numerical geometry and painted output, including the small table shown
  in the user's screenshot.

## Considered Options

1. Modify the existing filled-curve SVG.
2. Estimate a density from raw observations in the browser.
3. Define a new distribution specification, validation boundary and standalone
   uncertainty-band component, retaining only the shared mark integration.

## Decision Outcome

Chosen option: **3**. Replace the distribution implementation end to end.

```python
col.distribution(
    "curve", x="position", y="density", color="#4169a0",
    height=0.5, density_max=None,
).point("median", color="#111111", outline=False)
```

- Input is a list of records with numeric `x` and nonnegative numeric `y` fields.
  Positions must be strictly increasing. Explicit null samples or null fields
  break support; no interpolation crosses a gap. Empty or insufficient support
  paints nothing. Raw samples, missing field bindings and invalid values fail
  at the Python boundary. Log axes require positive positions.
- `x`, `y` and `style="band"` remain the public field-binding spellings from
  the specification. They are deliberately retained because they describe the
  desired data, not to preserve the former renderer's behavior.
- A dedicated nested `distribution` specification carries the two bindings,
  `height` and `density_max` in the mark encoding. This replaces the former
  distribution-specific top-level wire fields. Source/color callable resolution
  and the common quantitative axis remain shared mark infrastructure.
- Density controls opacity of a single ink color. The band has constant height
  and no density outline, vertical density axis, or filled curve. Adjacent
  samples interpolate linearly along their projected x coordinates. The band
  stops at its supplied support; it does not extrapolate tails.
- `height` is a fraction of the row's mark track, in `(0, 1]`, default `0.5`.
  It is independent of density and stays centered inside the cell.
- With `density_max=None`, each row's peak maps to full opacity. This compares
  uncertainty width and shape, not absolute density heights between rows.
  Supply the same positive `density_max` to several distributions to compare
  intensities on a fixed scale. Opacity saturates at that value; all-zero
  densities paint nothing. Clipping/search do not renormalize the visible tail.
- The frontend separates parsing, scale projection/clipping, and DOM painting
  in `density-band.js`. Only valid coordinate/density observations contribute
  to the automatic x-domain. Interval clipping interpolates boundary density;
  it does not relocate off-screen samples.
- Each continuous support run is one colored rectangle with a CSS alpha mask.
  This has no SVG reference IDs, no nested coordinate-system sizing, and no
  vertical geometry derived from density. It supports CSS/theme/per-row colors
  and preserves the background through transparent tails and gaps.
- Layer order remains declaration order. The band can be followed by an
  independent point or a zero-width capped range for a central tick, both on
  the column's quantitative scale. Accessible text retains source values.

### Consequences

- Good, because the visual matches the reference and remains confined to a row.
- Good, because the input, opacity normalization, support and height contracts
  can be verified separately from DOM construction.
- Good, because fixed density scales permit meaningful intensity comparison
  without silently renormalizing visible slices.
- Compatibility change: direct consumers of the private encoding wire shape
  must use the nested `distribution` specification. Public `x`/`y`/`style`
  constructor calls continue to describe precomputed curves.
- Note: the renderer never estimates a KDE, computes quantiles, sorts source
  samples or converts observations into densities. Supply these upstream.

## More Information

- Replaces the distribution portion of
  [ADR-058](058-encoding-based-columns.md).
- `src/evidential/_distribution.py`, `frontend/src/density-band.js`.
- `tests/test_distribution.py`, `frontend/test_density_band.js`,
  `tests/browser/test_spec_conformance.py`, `notebooks/37_encoding_marks.py`.
