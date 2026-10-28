# Marimo integration

## Keep widget identity stable

Marimo reruns cells that reference changed values. A cell creating a table must
not depend on its filters or selection controls. Create controls, create the
widget, and update the existing widget in separate cells.

For a static report, output `EvidentialTable(...)` directly. Wrap the table in
`mo.ui.anywidget(...)` when another cell needs its state, such as selection.
For a wrapped table, the model is `wrapped.widget`; the wrapper is the displayed
object. `mo.ui.table` is useful for raw grids; it does not render Evidential
marks or row-layout metadata.

The [linked explorer template](../assets/explorer.py) demonstrates this
separation with a parameterized DuckDB query, a stable summary table, and
selection-driven monthly detail. The [report template](../assets/report.py)
is a static report. Both run without access to the author's local datasets.

## Choose the update mechanism

| Data source | Pattern |
| --- | --- |
| Already computed dataframe, Arrow table or records | `existing_table.set_data(data)` |
| SQL query controlled by notebook inputs | `LiveEvidentialTable(..., auto_run=False)` then `set_controls(...)` |
| Another table's selected record | `select="stable_id"`, then read `wrapped.widget.selected` in a separate cell |
| Several model changes together | `with table.hold_sync():` around model updates |
| Plain raw grid beside a report | `mo.ui.table(wrapped.widget.raw, selection=None)` in the updating cell |

`hold_sync()` batches widget messages. It does not freeze computation, hide
dependencies or prevent marimo from rerunning a cell. Keep the widget-creation
cell independent even when batching updates elsewhere.

`LiveEvidentialTable` binds `$name` or `{name}` placeholders to values passed
to `set_controls`. Pass controls or their `.value` as appropriate; values are
bound as SQL parameters. Use DuckDB parameter binding for your own queries too.
Do not interpolate user-controlled values into SQL strings. Outside a reactive
host, `bind_controls=True` supports compatible observable controls; marimo
usually wants the explicit reactive update cell instead.

Keep stable unique row identifiers separate from display names and ranks.
Handle a cleared selection (`None`) and selections removed by upstream
filters. A client-side search can hide a selected row without changing the
upstream dataset; choose that behavior deliberately. A changed filter should
not silently make details refer to a different record with the same label.
Make the selection or drill-down cell depend on the refreshed records or their
available-ID set as well as the widget. Clearing a trait in Python alone may
not invalidate a marimo cell that only listens to browser selection changes.
The explorer template returns `available_products` from the refresh cell for
this dependency, so clearing or restoring a filter cannot resurrect stale detail.

`set_data` preserves column configuration and row layout unless replaced.
Use `set_column`, `set_columns`, or `update_options` for explicit presentation
changes. When updating a visualization option dictionary, merge the current
dictionary before changing one setting so a notebook edit to its type or
other options is not accidentally overwritten by a reactive update.

## Notebook structure and checks

Use standard Python marimo notebooks with PEP 723 dependencies, `marimo.App`,
`@app.cell` functions and `app.run()` under the main guard. Let the installed
marimo formatter maintain cell signatures and returns. Display a cell's output
as its final top-level expression; expressions nested in an `if` block are not
displayed automatically. Keep helper variables local to functions when practical.

For local external datasets, accept a configurable path and show an actionable
missing-data message. Keep machine-specific paths out of reusable templates and
use the requested source rather than substituting fabricated data for a
real-data claim.
Use a documented snapshot or explicit illustrative data when offline behavior
is part of the task. Keep immutable data products and SQL transformation logic
separate from presentation.

Use the project's environment to run:

```bash
uv run marimo check path/to/notebook.py
uv run python path/to/notebook.py
uv run marimo edit path/to/notebook.py
```

Script execution verifies construction, not browser events. When browser tools
are available, also render the notebook and exercise filters, sorting, search,
pagination and row selection. Capture the intended table element `.et-root`,
wait for it to render and fonts to load, and inspect the image. A screenshot
of generated HTML with no connected marimo kernel cannot prove reactive
selection or control updates.
