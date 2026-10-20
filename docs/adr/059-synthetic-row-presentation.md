---
status: accepted
date: 2026-10-20
deciders: edouard
---

# ADR-059: Synthetic Section and Summary Row Presentation

## Context and Problem Statement

The *Tabular Design System* describes grouped tables in terms of **synthetic
rows**: a section row introduces a group, a summary row reports its aggregate,
and the two may be combined into one row (`North America | 345.4M`). It also
wants row separation to be a choice of rule (`black`, `grey`, `white`, none),
and section labels to be left- or center-aligned. The grouped helpers already
emit `render_type` metadata (ADR-009), but there was no way to combine a
section and its summary, no centered section label, and `row_lines` was only a
boolean.

## Decision Drivers

- A combined section+summary row saves a row and makes a small table read as a
  hierarchy.
- A centered section label is a presentation choice, independent of the values.
- Row rules are a design token (black / grey / white / none), not just on/off.
- The row kinds stay semantic (`render_type`), so sorting, paging and export
  keep treating data rows and synthetic rows differently.

## Decision Outcome

Chosen option: extend the existing row model rather than add a parallel one.

- `grouped_table(..., combined=True)` and `grouped_records(..., combined=True)`
  mark every subtotal row with `__combined`; the renderer gives it the section
  rule (`border-top`/`border-bottom`) while keeping the group label in the stub
  and the aggregated values in their measure cells.
- `section_row(label, align="center")` sets `__align`, rendered as
  `et-section-center`. A centered section carries its meaning in the label, so
  it is used without summary cells.
- `spacer_row(height=)` emits a blank gap (`render_type="row_spacer"`) with no
  rule, for separating blocks without a label.
- Section rows take part in the alternating `row_shading` pattern, consuming a
  slot like any other row (the design system asks for this explicitly).
- `row_lines` accepts a colour name as well as `True`/`False`; a string drives
  the `--et-row-border` token, so `"black"`, `"grey"` and `"white"` are one
  option.
- A section that spans a page break is re-introduced at the top of the later
  page as `"<label> (cont.)"` (`et-row-continuation`). Plain section rows no
  longer suppress pagination. Builder sections, summaries and totals paginate
  in their declared order; hierarchical accordion subtotals still stay on one
  page. A continuation is not inserted before a grand total.
- `section_indent` insets detail stub cells beneath left-aligned builder
  sections by that many rem, independently of font weight or shading. Explicit
  `stub` columns are inset, or the first column when no stub is configured.
  Centered sections do not inset their detail rows.
- The first and last body rows retain horizontal boundary rules even when
  `row_lines=False`; the rules apply to each displayed page.

### Consequences

- Good, because the three grouped-table presentations in the design system
  (separate header, separate summary, combined) are one flag apart.
- Good, because row rules are themeable without new CSS.
- Note: `__combined` is presentation metadata; the row keeps its `row_subtotal`
  kind and its collapsible behaviour.
- Note: a continued section is derived at render time from the page's preceding
  rows, so it does not appear in the exported CSV.
- Note: this does not add a general row builder. Per-column summary values with
  arbitrary callables remain served by `grouped_records`' `aggregations`; a
  dedicated row-structure API is still open (specification §9).

## More Information

- `src/evidential/grouped.py` (`decorate_grouped_rows`),
  `src/evidential/client.py` (`grouped_records`), `src/evidential/table.py`
  (`section_row`), `src/evidential/configuration.py` (`TableOptions.row_lines`).
- `frontend/src/table.js` (`_renderRow`, `_applyTheme`), `frontend/src/table.css`.
- `tests/test_client.py`, `tests/test_table.py`, `frontend/test_table.js`.
- Extends [ADR-009](009-grouping-sets-for-grouped-totals.md) and
  [ADR-019](019-accordion-indentation.md); complements
  [ADR-058](058-encoding-based-columns.md).
