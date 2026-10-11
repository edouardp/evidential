"""DuckDB connection helpers.

This module intentionally has no hard dependency on boto3: S3 credential
resolution is attempted only when :func:`attach_s3_tables` is called and boto3
is importable. Everything else works with a stock DuckDB install plus the
``httpfs`` extension.
"""

from __future__ import annotations

import os
from typing import Any

__all__ = [
    "connect",
    "configure_s3",
    "attach_s3_tables",
    "connect_s3_tables",
    "query",
]

DEFAULT_ALIAS = "s3tables"


def connect(database: str = ":memory:", *, extensions: tuple[str, ...] = ("httpfs",)) -> Any:
    """Open a DuckDB connection with the requested extensions loaded."""
    import duckdb

    connection = duckdb.connect(database)
    for extension in extensions:
        connection.execute(f"INSTALL {extension}; LOAD {extension};")
    return connection


def configure_s3(
    connection: Any,
    *,
    region: str | None = None,
    profile: str | None = None,
    secret_name: str = "evidence_s3",
) -> None:
    """Create a DuckDB S3 secret from the ambient AWS credentials.

    Uses boto3 when available (so ``AWS_PROFILE``/SSO/instance roles all work);
    otherwise falls back to the standard ``AWS_ACCESS_KEY_ID`` environment
    variables. Reads the region from the argument or ``AWS_REGION``.
    """
    region = region or os.environ.get("AWS_REGION") or os.environ.get("AWS_DEFAULT_REGION")
    access_key = secret_key = session_token = None
    try:
        import boto3  # type: ignore

        session = boto3.session.Session(
            profile_name=profile or os.environ.get("AWS_PROFILE"),
            region_name=region,
        )
        credentials = session.get_credentials()
        if credentials is not None:
            frozen = credentials.get_frozen_credentials()
            access_key = frozen.access_key
            secret_key = frozen.secret_key
            session_token = frozen.token
        region = region or session.region_name
    except ImportError:
        access_key = os.environ.get("AWS_ACCESS_KEY_ID")
        secret_key = os.environ.get("AWS_SECRET_ACCESS_KEY")
        session_token = os.environ.get("AWS_SESSION_TOKEN")
    if not (access_key and secret_key and region):
        raise RuntimeError(
            "Could not resolve AWS credentials/region for DuckDB. "
            "Set AWS_PROFILE (with boto3 installed) or the AWS_ACCESS_KEY_ID / "
            "AWS_SECRET_ACCESS_KEY / AWS_REGION environment variables."
        )
    token_clause = f", SESSION_TOKEN '{session_token}'" if session_token else ""
    connection.execute(
        f"""
        CREATE OR REPLACE SECRET {secret_name} (
            TYPE s3,
            KEY_ID '{access_key}',
            SECRET '{secret_key}'
            {token_clause},
            REGION '{region}'
        )
        """
    )


def attach_s3_tables(
    connection: Any,
    *,
    table_bucket_arn: str | None = None,
    region: str | None = None,
    alias: str = DEFAULT_ALIAS,
    configure_credentials: bool = True,
) -> str:
    """Attach an Amazon S3 Tables Iceberg catalog as ``alias``.

    The table bucket ARN comes from the argument or ``S3TABLES_TABLE_BUCKET_ARN``.
    """
    for extension in ("aws", "httpfs", "iceberg"):
        connection.execute(f"INSTALL {extension}; LOAD {extension};")
    if configure_credentials:
        configure_s3(connection, region=region)
    table_bucket_arn = table_bucket_arn or os.environ.get("S3TABLES_TABLE_BUCKET_ARN")
    if not table_bucket_arn:
        raise RuntimeError(
            "attach_s3_tables needs a table bucket ARN (pass table_bucket_arn= or set S3TABLES_TABLE_BUCKET_ARN)."
        )
    region = region or os.environ.get("AWS_REGION") or os.environ.get("AWS_DEFAULT_REGION")
    endpoint = f"https://s3tables.{region}.amazonaws.com/iceberg"
    connection.execute(
        f"""
        ATTACH '{table_bucket_arn}' AS {alias}
            (TYPE iceberg, ENDPOINT '{endpoint}', AUTHORIZATION_TYPE 'sigv4')
        """
    )
    return alias


def connect_s3_tables(**kwargs: Any) -> Any:
    """Open a DuckDB connection with the S3 Tables catalog attached."""
    connection = connect(extensions=())
    attach_s3_tables(connection, **kwargs)
    return connection


def query(connection: Any, sql: str) -> Any:
    """Run ``sql`` and return the result as a pyarrow Table."""
    return connection.sql(sql).to_arrow_table()
