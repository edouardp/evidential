---
status: accepted
date: 2026-10-21
deciders: edouard
---

# ADR-064: Display-Only Row Layout

## Context and Problem Statement

The synthetic-row builder inserted headings and summaries into the dataset.
Detail mark callables therefore received records without their required fields.
Sorting, filtering, statistics, scale inference, pagination and export each had
to rediscover which records were data. Formatting a heading's text as a numeric
measure could also produce invalid output. The user requires synthetic rows to
be entirely a display concern, with optional heading values, group summaries,
one grand summary, and continuation headings across pages.

## Decision Drivers

- Detail records must remain the sole input to data bindings and analysis.
- Headings may contain numeric aggregates or formatted text such as "27 products".
- Group summaries and a grand summary must be independently optional.
- Pagination must count details and preserve the context of nested groups.
- Search must update portable summaries in static exports as well as live widgets.
- Historical grouped helpers and manually declared dividers must remain usable.

## Considered Options

1. Add more synthetic-record guards to every data consumer.
2. Keep detail records and a separate layout declaration, projecting annotations
   only when rendering a page.
3. Require Python round trips to rebuild an entire rendered table after each
   browser interaction.

## Decision Outcome

Chosen option: **2**, a separate display projection over detail records.

```python
EvidentialTable(
    detail,
    row_layout=rows.group_by("region")
        .section(values={"product": rows.count(suffix=" products"), "sales": "sum"})
        .summary("Subtotal", values={"sales": "sum"})
        .grand_summary(values={"sales": "sum"}),
)
```

- `Rows` is an immutable layout declaration. `row_layout=` binds it to detail
  data. The bound convenience `rows.of(data)...build()` returns a `RowView`, a
  sequence of detail records with a separate layout, rather than injected rows.
- The synced `rows` trait contains detail records only. A separate `row_layout`
  trait contains group membership by source index, nested groups and annotation
  specifications. `display_rows` provides an unfiltered inspection snapshot;
  it is never an input to bindings or browser analysis.
- Group order follows first appearance. Search filters details; sorting orders
  details within groups. The display projection then paginates details and emits
  headings, optional summaries, and a single final grand summary. Summaries
  aggregate details directly, including at nested levels.
- An intersecting group emits its heading on every page; a repeated heading is
  labelled `(cont.)` and omits aggregate cells. Bottom summaries appear on the
  page with the group's final matching detail, top summaries on its first page,
  and the grand summary on the final nonempty page. No annotations consume a
  detail-page slot. Empty filtered results have no annotations.
- Named reducers and `rows.aggregate(...)`/`rows.count(...)` serialize portable
  expressions and recalculate over all matching details, across pages. Literal
  values and arbitrary Python annotation callbacks retain source scope until
  `set_data`; Python callbacks cannot execute during browser-only search.
- Annotation cells have a dedicated renderer, independent `style` and `rule`,
  and plain formatted values. They bypass detail marks, cell rules, links,
  selection and footnotes. An explicit first-column value does not replace the
  heading label. Centered headings span the table and reject value cells.
- Annotation rows participate in alternating shading. `rule` controls their
  horizontal rules independently; page boundary rules remain. `section_indent`
  insets details under left-aligned headings or top summaries. Centered headings
  leave detail labels flush left. CSV exports matching details in
  display order across every page, excluding annotations.
- A dedicated group-label column can use `.repeat_values(False)` to blank
  adjacent equal values in the rendered detail order. The default and explicit
  `True` repeat values. Runs restart on every page and after annotations, so a
  continued group retains its label. Summaries are never suppressed. This only
  affects cell content; raw data, search, sorting and export retain full values.
- `set_data` preserves the layout declaration unless replaced or cleared with
  `row_layout=None`; it rebinds membership and summaries atomically with data.
- Legacy flattened inputs from `grouped_records`, SQL helpers, `section_row`
  and `spacer_row` are split into details and display tokens at the input
  boundary, before callable evaluation and inference. Their precomputed values
  and existing accordion/merged-cell presentation remain source-scoped. Use the
  new layout for detail-based pagination and filter-sensitive summaries.

### Consequences

- Good, because annotation handling no longer leaks into detail mark evaluation,
  summary calculations, domains, statistics or row numbering.
- Good, because the same display projection works without a Python connection.
- Good, because nested headings, group summaries and a grand summary share one
  layout model and cannot double-count summary values.
- Compatibility change: iterating a built `RowView` and reading `table.rows`
  returns details only. Code inspecting synthetic records should use
  `table.display_rows`. Legacy helpers retain their precomputed summary behavior.
- Note: arbitrary Python annotation callbacks use source scope. Authors needing
  search-sensitive summaries should use portable reducers or filter upstream.
- Note: groups and annotations add membership metadata proportional to the
  number of details times nesting depth; they do not copy detail field values.

## More Information

- Supersedes the injected-data model of
  [ADR-060](060-synthetic-row-builder.md); updates the presentation in
  [ADR-059](059-synthetic-row-presentation.md).
- `src/evidential/rows.py`, `src/evidential/_row_layout.py`,
  `frontend/src/row-layout.js`, `frontend/src/display-rows.js`.
- `tests/test_rows.py`, `frontend/test_row_layout.js`,
  `tests/browser/test_spec_conformance.py`, `notebooks/45_display_row_layout.py`.
