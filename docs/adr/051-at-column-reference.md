---
status: accepted
date: 2026-10-13
deciders: edouard
---

# ADR-051: The `@column` Reference Convention

## Context and Problem Statement

Several column options name **another column**: `conditional_colors`,
`scale_column`, `sort_by`, `fmt_column`, `footnote`, `link`, `image`, `logo`.
Each is a distinct keyword, and `scale=` is overloaded — it takes a colour scale
*or* (via `conditional_colors`) a column of per-row colours. So the caller has to
remember which spelling a value takes:

```python
col.chip("status", conditional_colors="status_color")
```

## Decision Drivers

- One way to say "this option refers to that column".
- Fewer keyword names to remember; the value carries the intent.
- No collision with the existing format codes.

## Decision Outcome

Chosen option: a leading `@` marks a column reference.

A string `"@name"` denotes the column `name`:

- **Wherever an option names a column** — `sort_by`, `fmt_column`,
  `scale_column`, `conditional_colors`, `footnote`, `link`, `image`, `logo` —
  `"@name"` is accepted and the `@` is stripped.
- **`scale="@name"`** on `.color()` / `.chip()` is shorthand for
  `conditional_colors="name"` — colour each cell from that column's values:

  ```python
  col.chip("status", align="center", scale="@status_color")
  col.number("gdp", fmt="num1").color(scale="@gdp_color")
  ```

The fluent methods strip the prefix (`_field`), and `_normalize_column_options`
does the same for the dict form, so `column_config={"x": {"color_options":
{"conditional_colors": "@c"}}}` works too.

`fmt` is deliberately **exempt**: `"@"` is a real Excel/`ssf` format code (the
text placeholder), so `fmt="@"` stays a format.

### Consequences

- Good, because the chain reads as "use this column", and one convention covers
  every column reference.
- Good, because `scale=` no longer needs a separate `conditional_colors=` to
  colour from a column.
- Good, because both spellings work — `conditional_colors=` and `@name` are
  equivalent; the dict form is normalized the same way.
- Note: the prefix is only meaningful to the options listed above; a literal
  value that happens to start with `@` in another option (such as `fmt`) is left
  alone.

## More Information

- `src/evidential/_column.py` (`_field`, `color`, `chip`),
  `src/evidential/_column_options.py`.
- `tests/test_column_builder.py`, `notebooks/27_chips.py`,
  `notebooks/30_subcolumns.py`.
- Relates to [ADR-042](042-column-builder-and-settings.md),
  [ADR-043](043-column-kinds.md) and [ADR-050](050-negative-styling.md).
