# Cell graphics

## Marks and fluent labels

Declare the graphic with `col.bar`, `point`, `range`, `stacked_bar`, `strip`,
`boxplot` or `distribution`. Chain additional marks on a mark column when they
share its track. Scalar text/number columns do not have a `.bar()` decorator.

```python
from evidential import EvidentialTable, col, domain, label

observations = [
    {"item": "A", "actual": 75, "target": 60, "change": 12,
     "renewal": 30, "new": 45, "history": [5, 4, 8, 9, 8]},
    {"item": "B", "actual": 40, "target": 65, "change": -8,
     "renewal": 25, "new": 15, "history": [3, 4, 4, 2, 5]},
]
counts = domain.numeric("counts").bounds(0, 100)
graphics_table = EvidentialTable(
    observations,
    columns=[
        col.text("item"),
        col.bar("actual", format="num0", color="#2563eb",
                label=label.fmt("num0").bold().auto_position("outside end"))
            .domain(counts).scale(axis=True, axis_position="bottom", gridlines=True),
        col.bar("change", format="num0", center=True, color="#0f766e",
                color_negative="#dc2626", label=label.auto_position("outside end"))
            .scale(domain=(-20, 20)),
        col.stacked_bar("renewal", "new", title="Renewal · New",
                        colors=["#2563eb", "#0f766e"], normalize="percent",
                        labels="percent", label_align="center"),
        col.sparkline("history", type="change", delta=True, y_fmt="num0", width=150),
    ],
    border=False,
    page_size=0,
)
```

Fluent labels mirror text styling: `label.fmt`, `.bold()`, `.italic()`,
`.font(...)`, `.color(...)` / `.colour(...)`. Start/end are numeric endpoints,
so negative bars retain the intended anchoring. Positions include `inside
start`, `inside end`, `outside start`, `outside end`, `center`, `above`, and
`below`; applicability depends on the mark.

For bars, `.auto_position("outside end")` first tries that preferred position,
then its inside/outside counterpart at the same endpoint, then omits the label
if neither fits. `.position(...)` chooses fixed placement. Use the preferred
inside/outside and start/end explicitly instead of inventing `position="auto"`.
The renderer handles inside contrast unless a color is explicitly supplied.

## Legends

Append `.legend()` to a mark column when colour identifies series or categories.
It adds a compact wrapping key above the table, alongside the title/subtitle.
Stacks, bars, points, ranges and strips share the method; each opted-in column
gets a group named after its rendered heading. Source names are automatic.
Use `.legend(["Actual", "Target"])` for ordered names or
`.legend({"target": "Budget"})` to override selected sources. A `None` name omits
an entry, useful for a connecting range behind several coloured points.
`.legend(False)` disables a key. Strip keys come from their `colors` mapping.
Use `.legend(outline=True)` for one thin box around the combined key.
Column headings are omitted for a single key and shown for multiple keys;
`column_names=True` or `False` overrides this per column.
Legends require fixed colours; per-row colour references do not identify
categories on their own. As with other additions, check installed capabilities
before using `.legend()` against an older published package.

## Domains and guides

Use `.scale(domain=(low, high), ...)` for a mark column's fixed track. Use
`.domain("name")` to pool compatible columns, or a reusable
`domain.numeric("name").bounds(low, high)` to fix shared endpoints. The shared
domain also works for heatmaps and sparklines. Put shared bounds on the domain
builder, not on each member's `.scale(domain=...)`.

Use fixed bounds when separate filtered views need comparability. A default
inferred range can change with filtering; sharing a name alone pools current
values rather than freezing them. Signed centered bars need a meaningful
symmetric domain when comparisons across views matter.

`.scale(axis=True, axis_position="top" | "bottom", gridlines=True)` puts the
axis outside body rows. Reference lines and bands belong on the mark column:
`.reference_line(70, color="#dc2626")` and
`.reference_band(60, 80, color="#fef3c7")`. Explicit band colors retain their
alpha; the default band is tinted. Do not add fake records for axes or guides.

## Comparisons and composition

```python
comparison = EvidentialTable(
    observations,
    columns=[
        col.text("item"),
        col.range("target", "actual", color="#0f766e", color_negative="#dc2626",
                  direction_marker=True)
            .point("target", color="#94a3b8", size=9)
            .point("actual", color="#2563eb", size=10, outline=False)
            .title("Target → Actual").scale(domain=(0, 100), axis=True),
    ],
    border=False,
)
```

`col.range` draws from the first endpoint to the second; `color_negative`
colors a decreasing connector and `direction_marker=True` adds its chevron.
Points support `outline=False` or a CSS outline color. Keep glyph styling
separate from `.cell_style(...)`, which styles the surrounding cell.

For several scalar point series, pass the fields or their display-name mapping
directly: `col.points({"target": "Target", "actual": "Actual"}, connect=True)`.
It chooses categorical colours automatically; `palette="viridis"` samples a
named range and a colour list supplies custom stops. `.legend()` uses the same
names and colours. The renderer calculates the connecting span, so data needs
no artificial minimum/maximum fields or connector entry in the legend.
Single-string `col.points("samples")` continues to read an array of observations.

Stack sources are additive segment magnitudes. `normalize="percent"` maps
the cumulative stack to 0–100; use a 0–100 axis, not 0–1, for that normalized
stack. A scalar fraction formatted with `pct1` instead uses 0–1. For diverging
stacks, inspect `diverge_at` and `neutral` semantics in the installed API.

## Sparklines and distributions

Sparkline types are `line`, `area`, `bar`, `points`, and `change`. Supply ordered
numbers, pairs, or objects with explicit `x`/`y` bindings. Nulls preserve gaps;
markers can be `True` or `"ends"`. `y_fmt` supplies tooltip units; inspection
expands abbreviated/rounded numbers to readable full values. Sparklines select
one observation by x-position. Signed-area tooltip swatches match the fill on
the observation's side of the reference.

All columns support `.tooltip(False)`, `.tooltip("@field")` and literal
multiline text. Hover delays are seconds: table
`settings(tooltips={"delay": 0.8, "text_delay": 1.5})`, or per-column
`.tooltip(delay=0)`. Defaults are instant graphics and 0.8s for text; keyboard
and touch inspection is immediate. Point plots can collect overlapping dots,
while stacks and strips inspect one segment. See notebook 55 for runnable examples.

- `type="change"` interprets input as signed changes/outcomes by default.
  For absolute observations such as `[5, 4, 8]`, set `delta=True` to compare
  adjacent values. The first comparison stays blank; missing values break
  adjacency. `steady=(low, high)` is inclusive and defaults to `(0, 0)`.
- Change gradients use `color_scale` and `color_domain`; the steady interval
  anchors the palette midpoint even on asymmetric domains.
- A signed area can use `reference=1, signed=True` to fill above/below a 100%
  baseline. Format fractions with `y_fmt="pct1"`. Share/fix domains explicitly
  when multiple rows need comparable vertical geometry.
- `col.distribution` expects a supplied density profile with `x` and `y`
  bindings. It is a density band, not a histogram or generic array plot.
  Add a median with `.point("median", ...)` on the same domain; compute the
  statistical estimate upstream and explain its units/normalization.

Allow chart columns room for readable marks and labels. Ordinary text/numeric
columns fit content; chart tracks use remaining space and minimum widths.
`stretch=False` makes a compact table; `width=` limits its container. Inspect
the rendered table at the target width rather than shortening source values
or clipping meaningful labels to hide a layout problem.
