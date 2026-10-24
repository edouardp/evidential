# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo",
#     "duckdb>=1.3",
#     "evidential",
# ]
# ///
"""IMDb media: ~249k titles with ratings, genres, casts and budgets.

The BrightData IMDb-Media dataset, converted to Parquet with DuckDB (ZSTD,
Parquet v2, bloom filters on url/title/media_type) and read back with DuckDB,
shown with EvidentialTable: dotted-name column groups, a colour-scaled rating, a
bar-charted vote count, media-type chips, column statistics, a link column, a
pivot by decade, and a row-selection drill-down into the cast.

Point it at the Parquet with ``IMDB_PARQUET`` (default
``~/Downloads/imdb_media.parquet``); with no Parquet it falls back to
``IMDB_CSV`` (default ``~/Downloads/IMDB media.csv``).
"""

import marimo

__generated_with = "0.25.1"
app = marimo.App(width="full")


@app.cell
def _():
    import os
    from pathlib import Path

    import duckdb
    import marimo as mo

    from evidential import EvidentialTable, col, pivot_table

    return EvidentialTable, Path, col, duckdb, mo, os, pivot_table


@app.cell
def _(Path, duckdb, mo, os):
    parquet_path = Path(os.environ.get("IMDB_PARQUET", "~/Downloads/imdb_media.parquet")).expanduser()
    csv_path = Path(os.environ.get("IMDB_CSV", "~/Downloads/IMDB media.csv")).expanduser()
    parquet_literal = "'" + str(parquet_path).replace("'", "''") + "'"
    csv_literal = "'" + str(csv_path).replace("'", "''") + "'"

    if parquet_path.is_file():
        source, reader = "Parquet", f"read_parquet({parquet_literal})"
    elif csv_path.is_file():
        source, reader = "CSV", f"read_csv_auto({csv_literal}, header = true)"
    else:
        mo.stop(
            True,
            mo.md(
                f"No IMDb data. Put the Parquet at `{parquet_path}` (or set "
                f"`IMDB_PARQUET`), or set `IMDB_CSV` to `{csv_path}`."
            ),
        )

    connection = duckdb.connect()
    # Only the columns used below, so the scan stays quick.
    connection.execute(
        "CREATE TABLE media AS SELECT "
        "title, media_type, imdb_rating, imdb_rating_count, genres, "
        "details_release_date, popularity, url, review_count, review_rating, "
        "awards, boxoffice_budget, top_cast "
        f"FROM {reader}"
    )
    return connection, source


@app.cell
def _(mo):
    mo.md("""
    # IMDb media

    The BrightData **IMDb-Media** dataset, converted to **Parquet** with DuckDB
    (ZSTD, Parquet v2, `url`/`title`/`media_type` bloom filters) and read back
    with DuckDB, shown with `EvidentialTable`. It mixes the library's features on
    real data:

    - a **top-rated** ranking with a colour-scaled IMDb rating, a bar-charted
      vote count, media-type chips and a link on every title;
    - **dotted column names** (`"Rating.imdb"`, `"Release.year"`, …) grouped into
      nested headings, with the **Rating** group highlighted;
    - **column statistics** under each header, and a click-to-drill-down into
      the cast of any title.
    """)
    return


@app.cell
def _(connection, mo, source):
    films, types, y0, y1, avg_rating, rated = connection.sql(r"""
        SELECT count(*),
               count(DISTINCT media_type),
               min(year), max(year),
               round(avg(imdb_rating), 2),
               count(imdb_rating)
        FROM (
            SELECT media_type, imdb_rating,
                   try_cast(regexp_extract(details_release_date, '(\d{4})', 1) AS INTEGER) AS year
            FROM media
        )
    """).fetchone()
    mo.md(f"""
    | | |
    | --- | --- |
    | Loaded from | **{source}** |
    | Titles | **{films:,}** |
    | Rated on IMDb | **{rated:,}** |
    | Media types | **{types}** |
    | Release years | **{y0}–{y1}** |
    | Average rating | **{avg_rating}** / 10 |
    """)
    return


@app.cell
def _(EvidentialTable, col, connection, mo):
    top_rated = mo.ui.anywidget(
        EvidentialTable(
            connection.sql(r"""
                WITH parsed AS (
                    SELECT
                        title, url, media_type, imdb_rating, imdb_rating_count, popularity,
                        array_to_string(from_json(genres, '["VARCHAR"]'), ', ') AS genres,
                        try_cast(regexp_extract(details_release_date, '(\d{4})', 1) AS INTEGER) AS year
                    FROM media
                    WHERE imdb_rating IS NOT NULL AND imdb_rating_count IS NOT NULL
                )
                SELECT
                    row_number() OVER (ORDER BY imdb_rating DESC, imdb_rating_count DESC) AS rank,
                    title,
                    media_type        AS "Type.media",
                    genres            AS "Type.genres",
                    year              AS "Release.year",
                    imdb_rating       AS "Rating.imdb",
                    imdb_rating_count AS "Rating.votes",
                    popularity        AS "Buzz.popularity",
                    url               AS imdb
                FROM parsed
                WHERE imdb_rating_count >= 1000
                ORDER BY imdb_rating DESC, imdb_rating_count DESC
                --LIMIT 5000
            """),
            title="Top rated titles",
            subtitle="50,000+ votes. Click a row to see its cast; the Rating band is a column-group highlight",
            select="imdb",
            #column_stats=True,
            search=True,
            page_size=12,
            row_shading=3,
            columns=[
                col.integer("rank", title="#"),
                col.auto("title").link("imdb"),
                col.chip("Type.media"),
                col.text("Type.genres"),
                col.number("Release.year", fmt="yyyy"),
                col.group("Rating", [
                        col.number("Rating.imdb", fmt="num1")
                            .color(scale="rdylgn", min=0, max=10
                        ),
                        col.bar("Rating.votes", fit_to_data=True, color="#93c5fd", label=True),
                    ],
                    #highlight="#55006611",
                ),
                col.integer("Buzz.popularity", title="Popularity"),
                col.auto("imdb").hide(),
            ],
        )
    )
    top_rated
    return (top_rated,)


@app.cell
def _(top_rated):
    selected = top_rated.widget.selected
    return (selected,)


@app.cell(expand_output=True)
def _(EvidentialTable, col, connection, mo):
    genres = mo.ui.anywidget(
        EvidentialTable(
            connection.sql("""
                WITH exploded AS (
                    SELECT unnest(from_json(genres, '["VARCHAR"]')) AS genre,
                           imdb_rating, imdb_rating_count
                    FROM media
                    WHERE imdb_rating IS NOT NULL
                )
                SELECT
                    genre,
                    count(*) AS films,
                    count(*) / (SELECT count(*) FROM media) AS "Share.films",
                    round(avg(imdb_rating), 2) AS "Rating.avg",
                    round(avg(imdb_rating_count))  AS "Rating.avg votes"
                FROM exploded
                GROUP BY genre
                HAVING count(*) >= 500
                ORDER BY films DESC
            """),
            title="Genres",
            subtitle="One film appears under each of its genres",
            page_size=20,
            row_shading=True,
            columns=[
                col.text("genre"),
                col.bar("films", format='num0', color="#93c5fd", label=True),
                col.percent("Share.films", decimals=1, title="Share"),
                col.number("Rating.avg", fmt="num2", title="Avg rating").color(
                    scale="rdylgn", min=0, max=10
                ),
                col.integer("Rating.avg votes", title="Avg votes"),
            ],
        )
    )
    genres
    return


@app.cell(expand_output=True)
def _(col, connection, mo, pivot_table):
    by_decade = mo.ui.anywidget(
        pivot_table(
            connection,
            r"""
            SELECT ((try_cast(regexp_extract(details_release_date, '(\d{4})', 1) AS INTEGER) / 10) * 10) AS decade,
                   media_type
            FROM media
            WHERE imdb_rating IS NOT NULL
              AND try_cast(regexp_extract(details_release_date, '(\d{4})', 1) AS INTEGER) BETWEEN 1950 AND 2029
            """,
            dimensions=["decade"],
            pivots=["media_type"],
            measures=["count(*) AS films"],
            total_label="All decades",
            title="Titles by decade and media type",
            page_size=12,
            dimension_config={"decade": col.number("decade", fmt="num", align="left")},
            measure_config={"films": col.bar("films", format='num0', color="#93c5fd", label=True)},
        )
    )
    by_decade
    return


@app.cell
def _():
    cast_sql = r"""
        WITH pick AS (
            SELECT from_json(top_cast, '[{"actor":"VARCHAR","character":"VARCHAR","link":"VARCHAR"}]') AS c
            FROM media
            WHERE url = $url
        )
        SELECT i AS no, c[i].actor AS actor, c[i].character AS role
        FROM pick, range(1, len(c) + 1) AS t(i)
        ORDER BY i
    """
    return (cast_sql,)


@app.cell
def _(EvidentialTable, cast_sql, col, connection, mo):
    # Created once (empty): clicking a title updates it in place via set_data, so
    # the table keeps its headers and size and never flickers.
    cast_table = mo.ui.anywidget(
        EvidentialTable(
            connection.sql(cast_sql, params={"url": ""}),
            title="Cast",
            empty_message="Click a title above to see its cast",
            page_size=10,
            row_shading=True,
            columns=[
                col.integer("no", title="#"),
                col.text("actor"),
                col.text("role"),
            ],
        )
    )
    cast_table
    return (cast_table,)


@app.cell
def _(cast_sql, cast_table, connection, selected):
    _ = cast_table.widget.set_data(connection.sql(cast_sql, params={"url": selected or ""}))
    _ = cast_table.widget.update_options(
        title=f"Cast — {selected}" if selected else "Cast",
        subtitle="Billed cast, in order" if selected else "Select a title above",
    )
    return


@app.cell
def _(mo):
    mo.md("""
    ### Notes

    - Dotted column names (`"Rating.imdb"`, `"Release.year"`, `"Type.media"`)
      build the nested headings, and `column_groups` adds the **Rating**
      highlight band on top.
    - `select="imdb"` makes rows clickable even though the `imdb` column is
      hidden; the title uses it as its link, and the cast table re-queries on
      `top_rated.widget.selected`.
    - The cast table is built once and updated with `set_data`, so it holds its
      headers and height while nothing is selected (see ADR-033).
    - `genres` and `top_cast` are JSON arrays stored as text; DuckDB unpacks them
      with `from_json(...)`.
    - The Parquet is built once from the CSV with DuckDB:
      `COPY (SELECT * FROM read_csv_auto('IMDB media.csv', header = true))` `TO
      'imdb_media.parquet' (FORMAT PARQUET, COMPRESSION ZSTD, COMPRESSION_LEVEL
      9, ROW_GROUP_SIZE 122880, PARQUET_VERSION V2, KV_METADATA {...})`. DuckDB
      does not write Parquet **bloom filters**, so a short PyArrow pass adds them
      afterwards (`bloom_filter_options={"url": ..., "title": ...,
      "media_type": True}`).
    """)
    return


if __name__ == "__main__":
    app.run()
