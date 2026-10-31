---
status: accepted
date: 2026-11-01
deciders: edouard
---

# ADR-089: Collapsible Display Sections

## Context and Problem Statement

Display-only `rows.group_by(...).section()` headings could not collapse their
groups, although historical grouped-table helpers supported folding. Adding
folding must preserve the separation between detail data and annotations,
without hiding all navigation when every group is closed. The user requires
group summaries to disappear with details, with an optional way to show their
values in a closed heading. Centered headings cannot hold per-column totals.

## Decision Drivers

- Keep grouping, filtering, aggregation, domains and export independent of folding.
- Hide a closed group's own summary and all nested content.
- Preserve nested collapse states when reopening an ancestor.
- Keep closed headings reachable through pagination and keyboard controls.
- Support frozen columns, continuation headings and measured expanded pages.
- Make summary promotion explicit and preserve existing heading values.

## Considered Options

1. Reuse legacy synthetic records and table-level collapse defaults.
2. Remove closed details after paginating, leaving empty or redundant pages.
3. Fold the display tree before pagination, retaining closed groups as display slots.

## Decision Outcome

Chosen option: **3**, while retaining detail-only source records and analysis.

Both `.section(collapsible=True)` and `.section().collapsible()` enable folding.
Groups start open, independently of legacy table-level collapse options. The
fluent modifier can also create a default section heading. Both forms accept
`collapsed_summary=True`; `.collapsible(False)` disables interaction without
discarding heading configuration.

Browser state uses stable group-path keys, separate from legacy grouped-table
state. Native heading buttons expose `aria-expanded`, support Enter and Space,
and restore focus after rendering. Reopening an ancestor retains child states;
search and data refresh retain states for matching group paths. Folding never
updates source records or invalidates cached statistical/domain calculations.

An open group contributes its detail records to pagination. A closed group
contributes one display slot holding its heading, with no details, nested
headings, or top/bottom summary rows. Ordinary annotations consume no slots.
When folding is active, the pager distinguishes display items from matching
detail records. All-closed tables remain navigable rather than becoming empty
tables. Row numbers retain the matching detail ordinals, excluding annotations.
Inline toggling moves to the page containing the toggled heading, including
when invoked from a continuation. Expanded mode resets its measured page
boundaries when folding changes the projection, as for other group changes.
The fitter counts display slots while measuring all rendered annotation height.

Heading values and summaries still read all matching group members. Grand
summaries include matching details in closed groups and appear once on the
last display page. CSV exports matching detail records in group order, including
closed groups; raw data and the inspection snapshot remain unchanged.

With `collapsed_summary=True`, a closed heading with no explicit value cells
uses its group's summary cells. It retains its own label, style, rule and label
column. Summary formatting and portable reducers retain their normal behavior;
literal/callable summaries retain source scope. Explicit heading cells take
precedence as a set; missing fields are not filled from the summary. Reopening
restores the normal heading and separate summary row. Without a summary the
option has no effect. Centered headings can collapse, but combining
`align="center"` and `collapsed_summary=True` raises a Python validation error.

### Consequences

- Good, because folding remains entirely a display concern and cannot change totals.
- Good, because empty-looking pages and inaccessible all-closed groups are avoided.
- Good, because summary visibility and promotion have explicit, testable rules.
- Bad, because pagination has mixed display units while groups are closed; the
  footer must distinguish them from underlying record counts.
- Bad, because changing folding resets measured expanded-page history.

## More Information

- Extends [ADR-064](064-display-only-row-layout.md) and the measured page model
  in [ADR-088](088-measured-expanded-pages.md).
- Demos: `notebooks/39_synthetic_rows.py`.
- Coverage: `tests/test_rows.py`, `frontend/test_row_layout.js`,
  `frontend/test_display_rows.js`, `frontend/test_table.js`,
  `frontend/test_lifecycle.js`, `tests/browser/test_collapsible_sections.py`.
