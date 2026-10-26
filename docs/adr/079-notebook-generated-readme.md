---
status: accepted
date: 2026-10-26
deciders: edouard
---

# ADR-079: Notebook-Generated README Examples

## Context and Problem Statement

The README manually duplicates descriptions and column configurations from
the screenshot notebooks. Some snippets already differ from the rendered
images. Descriptions, displayed code and screenshots need a common source
without making the whole README generated or executing notebook code merely
to extract documentation.

## Decision Drivers

- Keep illustrated examples runnable and readable in marimo.
- Preserve editable README prose and its editorial ordering.
- Copy real column code, including fluent chains and comments.
- Capture the corresponding widget with Playwright.
- Detect stale documentation using a cheap local validation gate.
- Reuse the existing named-cell screenshot registry and browser workflow.

## Considered Options

1. Maintain separate snippets and periodically compare them by hand.
2. Export whole notebooks as Markdown and replace the entire README.
3. Generate delimited README regions from paired named notebook cells.

## Decision Outcome

Chosen option: **3**. Each documented table has a named cell and a paired
`<cell>_doc` cell containing literal Markdown. README comment markers select
the notebook and table cell. The generator extracts `columns=[...]` using
Python AST source locations, preserving the original source rather than
unparsing it. Aggregate helpers contribute their complete call when columns
are configured through measure/dimension mappings. Dynamic Markdown and
ambiguous table calls fail explicitly.

Playwright captures the actual named-cell widget through the existing
screenshot registry. A single `make readme` command refreshes text, images and
a committed provenance manifest. Images are staged until all captures
succeed. `make readme-check` verifies text and hashes without a browser and
is included in local release validation. No hosted build service is added.

Repository README images use relative paths. The generator also writes
`docs/PYPI_README.md`, resolving local image and documentation links to GitHub
URLs for package metadata. `pyproject.toml` points to this generated copy;
there is still only one source README.

### Consequences

Descriptions, code and table images have one notebook source. Manual README
sections remain editable. Changes to implementation, fixtures, rendering or
the locked environment conservatively require refreshing all snapshots.
The manifest detects drift but does not replace visual review. Standard AST
source locations cover the deliberately small extraction contract without
adding LibCST as a dependency. The Studio section uses its demo notebook's
actual table; full Studio view documentation remains in its separate guide.

## More Information

- [Authoring and generation workflow](../notebook-documentation.md).
- `scripts/generate_readme.py`, `scripts/api_screenshots.py`.
- `notebooks/49_api_screenshots.py`, `notebooks/50_graphics_gallery.py`.
- `notebooks/21_studio_dashboard.py`.
- [ADR-078: Local Release Validation](078-local-release-validation.md).
