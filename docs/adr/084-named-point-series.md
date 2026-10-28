---
status: accepted
date: 2026-10-28
deciders: edouard
---

# ADR-084: Named Point Series

## Context and Problem Statement

Showing nine population age bands previously required nine point declarations,
a colour list, separate legend labels, minimum/maximum data fields and a range
that needed excluding from the legend. These are presentation decisions that
should be declared once, without changing the data.

## Decision Drivers

- Remove repeated point declarations and independent colour/name lists.
- Support automatic categorical colours and sampled named colour ranges.
- Keep rendering and legend identities consistent through missing data.
- Compute the connecting span entirely in the renderer.
- Preserve the existing array-backed `col.points("samples")` API.

## Considered Options

1. Keep manually composing a range and individual points.
2. Add a separate chart constructor for each multi-point use case.
3. Let the existing points mark bind a list or mapping of scalar fields.

## Decision Outcome

Chosen option: **3**. `col.points(fields, palette=None, connect=False, ...)`
accepts either a field-name sequence or a field-to-display-name mapping. It
produces one points encoding with `sources` and optional `names`, retaining a
first `source` for the presentation slot's existing column identity. A string
or callable source keeps the prior array-observation encoding and defaults.

Wide series use the categorical Tableau `tab10` sequence by default, cycling
after ten fields. A named colour range such as `viridis` is sampled evenly
across its stops in declaration order; a colour list provides custom stops.
An explicit point `color` takes precedence. Colours are assigned before missing
values are omitted, so filtering or incomplete rows cannot shift the remaining
series' colours. Named-series defaults are nine-pixel points without rings;
`size` and `outline` retain explicit overrides. Array defaults remain unchanged.

`connect=True` draws a thin span between the minimum and maximum projected
valid points, behind the dots. Equal values, singletons and empty series have
no span. This is a range of shares, not chronological interpolation or an
uncertainty interval. No extrema columns are created, and raw data retains
only its original fields. The connector has no separate legend entry.

The same series expansion and palette resolver serve marks and legends.
Mapping names become the automatic legend labels; ordinary legend overrides
can still rename or omit entries. Shared tooltips expose series names and full
values, including overlapping points (see [ADR-085](085-data-tooltips.md)).
Domain inference includes every bound field; log validation
checks each non-null field even when the first is missing. Rebinding a measure
updates its entry in both source and name metadata.

### Consequences

The population example needs one points declaration, its semantic scale and
`.legend()`. Unit tests cover bindings, palettes, missing values, domain/log
behavior, compatibility and untouched raw data. Browser tests exercise the
shipped bundle and the actual marimo notebook, including all 108 population
points, twelve connectors and nine correctly coloured legend entries.
The frontend bundle must be rebuilt with encoding changes before a notebook
uses them; Python-only execution cannot detect an outdated browser renderer.

One mapping now carries series identity and labels. Automatic colours do not
imply an ordering for categorical data; choose a sequential palette deliberately
for ordered bands. Formats and shared scale bounds remain explicit because
numeric values alone cannot establish their units or comparison policy.

## More Information

- [Legend and population notebook](../../notebooks/54_legends.py).
- [ADR-058: Encoding-Based Columns](058-encoding-based-columns.md).
- [ADR-083: Mark Legends](083-mark-legends.md).
