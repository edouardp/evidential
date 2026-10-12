# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo",
#     "duckdb>=1.3",
#     "pyarrow>=17",
#     "evidential",
# ]
# ///
"""Column metadata drives the table: types set the format, descriptions set the header.

`EvidentialTable` reads column descriptions from wherever they live — DuckDB
`COMMENT ON COLUMN`, Arrow field metadata (which is how a description survives
Parquet and Feather), or an explicit `column_config={"...": {"comment": ...}}` —
and shows them as an immediate **ⓘ** tooltip in the header. Column types default
the format and alignment, so a normalised table needs no `column_config` at all.
"""

import marimo

__generated_with = "0.25.1"
app = marimo.App(width="full")


@app.cell
def _():
    import tempfile
    from pathlib import Path

    import duckdb
    import marimo as mo

    from evidential import EvidentialTable, duck

    return EvidentialTable, Path, duck, duckdb, mo, tempfile


@app.cell
def _(duckdb):
    connection = duckdb.connect()
    connection.execute(
        """
        CREATE TABLE orders AS
        SELECT
            order_id::INTEGER         AS order_id,
            placed_at::DATE           AS placed_at,
            region::VARCHAR           AS region,
            units::INTEGER            AS units,
            unit_price::DECIMAL(10,2) AS unit_price,
            discount::DOUBLE          AS discount,
            revenue::DOUBLE           AS revenue
        FROM (VALUES
            (1, DATE '2024-01-03', 'Americas',  12,  3.50, 0.05,   42.00),
            (2, DATE '2024-01-04', 'Europe',    40, 99.00, 0.00, 3960.00),
            (3, DATE '2024-01-06', 'Asia',       7,  0.50, 0.10,    3.15),
            (4, DATE '2024-01-09', 'Europe',     2, 12.25, 0.00,   24.50),
            (5, DATE '2024-01-11', 'Americas',   8,  7.13, 0.15,   48.47),
            (6, DATE '2024-01-18', 'Asia',     120,  1.10, 0.02,  129.36)
        ) AS t(order_id, placed_at, region, units, unit_price, discount, revenue)
        """
    )
    connection.execute("COMMENT ON TABLE orders IS 'Sample orders for the metadata demo'")
    for column, comment in [
        ("order_id", "Unique order identifier"),
        ("placed_at", "Date the order was placed"),
        ("region", "Sales region"),
        ("units", "Units sold"),
        ("unit_price", "Price per unit, in USD"),
        ("discount", "Discount rate applied (0-1)"),
        ("revenue", "Net revenue in USD"),
    ]:
        connection.execute(f"COMMENT ON COLUMN orders.{column} IS '{comment}'")
    return (connection,)


@app.cell
def _(mo):
    mo.md("""
    # Column metadata drives the table

    DuckDB hands back two useful kinds of metadata with every result:

    - **Column types** — `relation.types` and the Arrow schema (`INTEGER`,
      `DECIMAL(10,2)`, `DOUBLE`, `DATE`, `VARCHAR`, …).
    - **Column descriptions** — `COMMENT ON COLUMN`, read back from
      `duckdb_columns().comment`.

    `EvidentialTable` turns the type into sensible defaults (integers → `num0`,
    decimals → `num2`, numbers right-aligned, text left-aligned) and the
    description into the header **ⓘ**. Hovering it shows the text **immediately**
    (a custom tooltip, not the browser's delayed one), and the cursor is left
    alone. Nothing is configured below.
    """)
    return


@app.cell
def _(EvidentialTable, connection, mo):
    from_relation = mo.ui.anywidget(
        EvidentialTable(
            connection.table("orders"),
            title="con.table('orders') — inferred from the relation",
            search=True,
            row_shading=True,
        )
    )
    from_relation
    return


@app.cell
def _(EvidentialTable, connection, mo):
    rows = "\n".join(
        f"| `{column['name']}` | {column['type']} | {column.get('fmt') or 'auto'} "
        f"| {column['align']} | {column.get('info') or '—'} |"
        for column in EvidentialTable(connection.table("orders")).columns
    )
    mo.md(f"""
    ### What was inferred

    | Column | type | fmt | align | info |
    | --- | --- | --- | --- | --- |
    {rows}

    `con.table("orders")` is a *table relation*, so it can look up its own
    comments. The integer columns default to `num0`, `unit_price`
    (`DECIMAL(10,2)`) to `num2`, and `discount`/`revenue` (`DOUBLE`) keep the
    auto-scaling `num` format. A real identifier would override `fmt="id"` to
    drop the thousands separator.
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    ### Set a description yourself

    `column_config` wins over whatever the source says. The header description
    can be set with `info` or its aliases `comment` / `description`, so the same
    word as the database metadata works. Here `revenue` is overridden and
    `discount` is both documented and formatted as a percentage.
    """)
    return


@app.cell
def _(EvidentialTable, connection, mo):
    overridden = mo.ui.anywidget(
        EvidentialTable(
            connection.table("orders"),
            title="column_config={...: {'comment': ...}}",
            row_shading=True,
            column_config={
                "revenue": {"comment": "Net revenue in USD (set in column_config)"},
                "discount": {"comment": "Discount rate (0-1)", "fmt": "pct0"},
            },
        )
    )
    overridden
    return


@app.cell
def _(mo):
    mo.md("""
    ### Parquet and Arrow field metadata

    Parquet has no standard per-column comment, but PyArrow stores the whole
    Arrow schema — including **field metadata** — in the file's `ARROW:schema`
    entry. So a `comment` (or `description` / `info`) field survives a Parquet
    round-trip and becomes the header description. Reading the same file through
    DuckDB's `read_parquet` loses it, because the metadata is not part of the
    result.
    """)
    return


@app.cell
def _(Path, tempfile):
    import pyarrow as pa
    import pyarrow.parquet as pq

    parquet_path = Path(tempfile.mkdtemp(prefix="evidential-")) / "cities.parquet"
    schema = pa.schema(
        [
            pa.field("city", pa.string(), metadata={"comment": "City name"}),
            pa.field("trips", pa.int64(), metadata={"description": "Completed trips"}),
            pa.field("revenue", pa.float64(), metadata={"comment": "Net revenue in USD"}),
        ],
        metadata={"description": "Cities demo"},
    )
    pq.write_table(
        pa.table(
            {
                "city": ["New York", "Los Angeles", "London"],
                "trips": [12040, 8320, 15600],
                "revenue": [412300.0, 287100.0, 523400.0],
            },
            schema=schema,
        ),
        parquet_path,
    )
    return parquet_path, pq


@app.cell
def _(EvidentialTable, mo, parquet_path, pq):
    from_parquet = mo.ui.anywidget(
        EvidentialTable(
            pq.read_table(parquet_path),
            title="pq.read_table('cities.parquet') — descriptions from Arrow field metadata",
            row_shading=True,
        )
    )
    from_parquet
    return


@app.cell
def _(EvidentialTable, connection, mo, parquet_path):
    via_duckdb = mo.ui.anywidget(
        EvidentialTable(
            connection.sql(f"SELECT * FROM read_parquet('{parquet_path}')"),
            title="con.sql('SELECT * FROM read_parquet(...)') — DuckDB does not carry the metadata",
        )
    )
    via_duckdb
    return


@app.cell
def _(mo):
    mo.md("""
    ### Raw SQL loses the source table

    `con.sql("SELECT ...")` produces an **unnamed** query relation: it no longer
    knows which table it came from, so comments cannot be looked up
    automatically. Fetch them with `duck.column_comments(con, "orders")` and
    merge them into `column_config`. The inferred **types** still apply either
    way, because they come from the Arrow schema.
    """)
    return


@app.cell
def _(EvidentialTable, connection, duck, mo):
    comments = {
        name: {"info": text} for name, text in duck.column_comments(connection, "orders").items()
    }
    from_sql = mo.ui.anywidget(
        EvidentialTable(
            connection.sql("SELECT * FROM orders"),
            title='con.sql("SELECT * FROM orders") + duck.column_comments',
            column_config=comments,
            row_shading=True,
        )
    )
    from_sql
    return


@app.cell
def _(mo):
    mo.md("""
    ### Notes

    - Prefer `con.table("name")` / `con.view("name")` when you want comments;
      the relation keeps its source name through `.limit()`, `.filter()` and
      `.select()`.
    - `duck.column_comments(con, "schema.table")` disambiguates across schemas.
    - Anything you set in `column_config` — including `comment` / `description`
      — still wins over the inferred default.
    """)
    return


if __name__ == "__main__":
    app.run()
