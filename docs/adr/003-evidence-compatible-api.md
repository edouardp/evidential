---
status: accepted
date: 2026-10-12
deciders: edouard
---

# ADR-003: Evidence-Compatible API Surface

## Context and Problem Statement

The widget needs names for table options, column options and content types.
We can invent Pythonic names, mirror Evidence's props, or follow gt/Great
Tables. The choice determines how quickly an existing Evidence user becomes
productive and how stable the API feels.

## Decision Drivers

- Familiarity for Evidence users.
- An API that has already been argued over and battle-tested.
- Room to add gt/Great Tables and typography ideas that Evidence lacks.

## Considered Options

1. Mirror Evidence's prop names, with snake_case Python spellings.
2. Invent fully Pythonic names.
3. Mirror gt/Great Tables names.

## Decision Outcome

Chosen option: "Mirror Evidence", because it buys portability and familiarity
at no design cost. Where Evidence uses camelCase, we accept both spellings
(`contentType` and `content_type`, `colorScale` and `color_scale`); where a
feature comes from gt/Great Tables, we use that project's names
(`cells_body`, `tab_style`, `sub_*`, `cols_merge*`).

### Consequences

- Good, because an Evidence user can translate a table almost mechanically.
- Good, because documented Evidence values (`viz`, `page_size`, `group_type`,
  `color_scale`) mean the same thing here.
- Bad, because the API carries some awkward Evidence names.
- Bad, because there are two vocabularies (Evidence and gt) to document.

## More Information

- [Design & DX §2.3, §3](../design-and-dx.md#23-evidence-shaped-names)
