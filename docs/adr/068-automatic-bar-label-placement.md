---
status: accepted
date: 2026-10-24
deciders: edouard
---

# ADR-068: Automatic Bar Label Placement

## Context and Problem Statement

Outside labels disappear when long bars leave insufficient room beside their
tips. Inside labels can disappear on short bars. The user requested an automatic
fallback while retaining explicit start/end placement and the preferred side of
the bar edge.

## Decision Drivers

- Preserve the caller's preferred position and start/end choice.
- Show a complete label when either candidate has enough space.
- Omit labels when neither candidate fits, retaining accessible source values.
- Respond to resizing and preserve shared scale geometry.
- Keep defaults and explicitly fixed label positions stable.

## Considered Options

1. Add an ambiguous `position="auto"` without a preferred side or edge.
2. Reserve space for every label by shrinking the shared plot track.
3. Add `auto=True` to the label specification, retaining its preferred position.

## Decision Outcome

Chosen option: **3**.

```python
from evidential import col, label

col.bar("sales", label=label.fmt("usd0").auto_position("outside end"))
col.bar("sales", format="usd0").label(True, position="outside_end", auto=True)
col.bar("sales", format="usd0").label(True, position="inside_start", auto=True)
col.bar("sales", label={"value": True, "position": "inside_end", "auto": True})
```

Automatic placement is opt-in and applies to bar labels. The preferred position
is one of `outside_start`, `inside_start`, `outside_end` or `inside_end`:

- Try the requested position first.
- If it does not fit, swap `inside`/`outside` and retain `start`/`end`.
- If neither fits, omit the label. Never truncate the value or change edges.
- Retry the original preference on every fit, including after a resize.

The existing default position applies when omitted: `outside_end`, or
`outside_start` for centered bars. The behavior is the same for positive,
negative, mirrored and explicit-side bars. Inside start/end alignment follows
the bar's numeric origin/tip; an explicit label alignment overrides it.

The Python builder, mappings and mutation paths validate the same specification.
Automatic placement rejects center/above/below positions, other mark kinds and
`overflow="show"`, which contradicts the requirement to omit a label when
neither candidate fits. Explicit color and minimum-width settings are retained.

The renderer shares its positioning and fit checks with fixed labels. A weak
map retains the immutable preference and geometry separately from the chosen
DOM position. Moving outside restores inherited text color; moving inside
applies existing contrast selection. Omitted automatic labels use `hidden` so
their off-cell boxes cannot create scrollable overflow. They are restored for
measurement on the next fit. Original values remain in mark accessibility text.

### Consequences

Scale domains, axes and bar widths are unaffected. Automatic fitting measures up
to two label candidates per layout pass. No new default placement policy or
reserved label gutter is introduced. Existing fixed labels continue to use
their configured overflow policy.

## More Information

- Extends [ADR-058](058-encoding-based-columns.md) and
  [ADR-066](066-consistent-public-api-preparation.md).
- `frontend/src/mark-labels.js`, `frontend/test_mark_labels.js`.
- `tests/test_marks.py`, `tests/browser/test_spec_conformance.py`.
