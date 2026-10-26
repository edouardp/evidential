# Notebook-generated README examples

The illustrated table examples in the README come from runnable marimo
notebooks. Edit the notebook, then run:

```console
make readme
make readme-check
```

`make readme` builds the renderer, starts the screenshot notebooks with
`marimo run`, and uses Playwright to capture the actual widget output. It
updates the generated README regions, PNGs and `docs/readme-snapshots.json`.
It also generates `docs/PYPI_README.md`, the package metadata's README, from
the repository README. Repository image paths stay relative; the PyPI copy
resolves images to GitHub raw URLs and documentation links to GitHub pages.
This copy is an output, never a separately maintained source.
`make api-screenshots` is an alias. Commit these outputs with the notebook edit.
The browser requirement is the same as `make test-browser`: installed Chrome,
Edge or Playwright Chromium (`uv run playwright install chromium`).

`make readme-check` does not start a browser. It compares generated Markdown
with the README and verifies SHA-256 hashes of the screenshot inputs and image
files. It runs in pre-commit, `make lint`, `make validate` and the repository tests. Changes to a
notebook, Python implementation, committed renderer, fixture, generator or
locked environment invalidate the screenshots. This is deliberately
conservative: refresh the complete set rather than guessing whether an edit
affects a particular image. The check establishes provenance; inspect the
new images for visual quality as well.

A version-only release bump is excluded from the environment fingerprint;
dependency and configuration changes still invalidate it.

## Adding an example

1. Add a named table cell to `notebooks/49_api_screenshots.py` (API examples),
   `notebooks/50_graphics_gallery.py` (graphic examples),
   `notebooks/51_table_layouts.py` (layout examples) or another notebook
   registered in the capture script, such as `notebooks/21_studio_dashboard.py`.
   Keep a single table call in that cell. Use an inline `columns=[...]` list
   for column excerpts; complete-call excerpts can reference shared columns.
2. Immediately above it, add a Markdown cell named `<table_cell>_doc`, with
   one literal `mo.md(r"""...""")` call. Include the README heading and
   description there. Both display in the notebook and copy into the README.
   Interpolated strings are rejected so documentation extraction never needs
   to execute arbitrary code.
3. Register its image path and cell name in `scripts/api_screenshots.py`.
4. Add a generated region wherever it belongs in the README:

```html
<!-- notebook: notebooks/50_graphics_gallery.py#graphic_bar -->

<!-- /notebook -->
```

5. Run `make readme`, inspect the resulting PNG and run `make readme-check`.

Only the region contents are replaced. Everything outside the markers remains
manually editable, including installation, integration instructions and API
reference prose. The Studio section also extracts and captures the real table
from notebook 21; the full dashboard view is shown in the [Studio guide](marimo-studio.md).

## Extraction rules

The generator selects code with LibCST and copies the original source span
for `columns=[...]`. It preserves
comments, quoting, parentheses and fluent chains, removing only the cell's
outer indentation. There is no second, shortened copy of the column code.
The snippet is a configuration excerpt; follow its notebook source link for
imports, data preparation, settings and a complete runnable example.

Aggregate helpers such as `grouped_table` and `pivot_table` configure columns
through dimension/measure mappings. Their complete call is extracted instead.
An `image-only` suffix on the opening marker suppresses the code excerpt, as
used by the introductory hero. A `call` suffix selects the complete table call,
including its table settings and inline `row_layout`, for layout examples.
Shared `columns` and `settings` variable references become `...`; inline
definitions, other options and comments are preserved by a LibCST transform:

```html
<!-- notebook: notebooks/51_table_layouts.py#layout_titles call -->

<!-- /notebook -->
```

The call is copied from the same named cell that Playwright captures. Data
preparation and shared column/settings definitions stay in the runnable
notebook; there is no independently maintained example call. The ellipses are
documentation placeholders, not values passed to the running table. For layout
examples, keep an inline SQL query as the data argument so its selected fields
are visible in the excerpt. Notebook 51 creates a local DuckDB `orders` table
in a setup cell and queries it in each table call, including hidden fields
needed for grouping or footnotes. Markdown strings
are still read statically as literals without executing notebook code.
Missing cells, ambiguous table calls, dynamic
Markdown and malformed markers fail the build instead of silently keeping
old content.

All screenshots are staged before existing files are replaced. A failed
capture or source edit during rendering leaves the previous README, images
and provenance unchanged. `pyproject.toml` uses the generated PyPI copy so
images work in published package metadata as well as in the repository.
