---
status: accepted
date: 2026-10-20
deciders: edouard
---

# ADR-063: Cell Style Independent of Marks

## Context and Problem Statement

The design system's *Single Datum Cell, Multiple visual presentations* says a
value can appear several ways at once: as formatted text, with a conditional
text colour, with a background gradient, and (with the marks model) as a bar
with its own fill. The v1.1 specification (§3.2, §8) names the missing piece
explicitly: `.cell_style(...)` should style the **cell** without changing the
mark, and "a cell background rule must not accidentally recolour a bar fill".

Before this, a column could have a `highlight` band or a `viz="color"`
background, but neither composes with a bar in the same cell.

## Decision Drivers

- A cell has chrome (background, text colour, border, padding) distinct from
  the marks drawn on it.
- The design system wants conditional, data-driven backgrounds alongside marks.
- Precedence must be explicit: rules > cell_style > column/row defaults.
- It must work on the mark columns (ADR-058) as well as the classic columns.

## Decision Outcome

Chosen option: a `cell_style` column option and a `.cell_style(...)` chain
method, available on every column.

```python
col.bar("return_pct", fmt="num1", color="#2563eb", label=True) \
   .cell_style(background="@band", color="#111", border="1px solid #e2e8f0")
```

- `background` is a colour or `"@column"` (the reference convention, ADR-051):
  a per-row colour taken from that column, normalised to `background_column`.
- `color`, `border` and `padding` are CSS values applied to the cell.
- The renderer applies `cell_style` to the `<td>` **before** matching
  `rules`; a `tab_style` rule for the same property still wins, so the
  documented precedence (theme < row/column defaults < `cell_style` < rules)
  holds.
- A mark's own `color=`/`fill` is untouched: the bar fill and the cell
  background are separate properties.

### Consequences

- Good, because one value can now be text, bar, label, and conditional
  background simultaneously.
- Good, because the background can be computed upstream (SQL/Python) into a
  column and referenced with `@`.
- Note: `cell_style` is a constant or a referenced column; arbitrary per-row
  callables are resolved to hidden columns upstream (ADR-006), as elsewhere.
- Note: `highlight=` remains the full-width column band and wins over row
  shading; `cell_style` is more specific and is applied after it.

## More Information

- `src/evidential/_column.py` (`cell_style`),
  `src/evidential/configuration.py` (`CellStyle`),
  `src/evidential/_column_options.py`, `src/evidential/data.py`.
- `frontend/src/cells.js`, `tests/test_column_builder.py`,
  `frontend/test_table.js`, `notebooks/43_cell_presentations.py`.
- Implements specification §3.2/§8; complements
  [ADR-058](058-encoding-based-columns.md) and
  [ADR-051](051-at-column-reference.md).
